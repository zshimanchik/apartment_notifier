import logging.config

import arrow

from apartment_notifier import settings
from apartment_notifier.models import User
from apartment_notifier.notifiers.print import PrintNotifier
from apartment_notifier.notifiers.telegram import TelegramNotifier
from apartment_notifier.parsers.onlinerby import OnlinerbyParser

_LOGGER = logging.getLogger(__name__)


class Runner:
    def __init__(self, settings, user: User):
        self.settings = settings
        self.user = user
        self._init_parsers()
        self._init_filters()
        self._init_notifiers()

    def _init_parsers(self):
        _LOGGER.debug('Initializing parsers')
        if not self.user.onlinerby_url:
            raise RuntimeError('"onlinerby_url" is not set')
        self.parsers = [
            OnlinerbyParser(self.user.onlinerby_url)
        ]
        _LOGGER.info('Parsers: %s', self.parsers)

    def _init_filters(self):
        _LOGGER.debug('Initializing filters')
        self.filters = []
        last_check_datetime = self.user.last_check_datetime
        if last_check_datetime is not None:
            self.filters.append(lambda apartment: apartment.last_time_up >= last_check_datetime)
        _LOGGER.info('Filters: %s', self.filters)

    def _init_notifiers(self):
        _LOGGER.debug('Initializing notifiers')
        self.notifiers = []
        if self.settings.print_notifier:
            self.notifiers.append(PrintNotifier())
        if self.user.chat_id:
            self.notifiers.append(TelegramNotifier(self.settings.telegram_api_key, self.user.chat_id))
        _LOGGER.info('Notifiers: %s', self.notifiers)

    def run(self):
        _LOGGER.info("Starting...")
        current_check_datetime = arrow.now()
        new_apartments = []
        total_apartment_amount = 0

        for parser in self.parsers:
            _LOGGER.info('Parsing with %s', parser.NAME)
            for apartment in parser.parse():
                total_apartment_amount += 1
                if all(filter(apartment) for filter in self.filters):
                    new_apartments.append(apartment)

        _LOGGER.info('Total apartment found: %s', total_apartment_amount)
        _LOGGER.info('New apartment amount: %s', len(new_apartments))
        for notifier in self.notifiers:
            _LOGGER.info('Notifying with %s', notifier.__class__.__name__)
            notifier.notify(new_apartments)

        _LOGGER.info("Saving results")
        self.user.last_check_datetime = current_check_datetime
        self.user.save()
        _LOGGER.info('Finished...')


if __name__ == '__main__':
    from apartment_notifier.stores import JsonFileStore, FireStore, ObjectDoesNotExist
    logging.config.dictConfig(settings.LOGGING)
    # store = JsonFileStore(settings.store)
    store = FireStore()
    pk = 0
    try:
        user = store.get(pk)
    except ObjectDoesNotExist:
        print('Object does not exist. Create new:')
        chat_id = int(input('chat_id: '))
        onlinerby_url = input('onlinerby_url: ').strip()
        user = User(pk, chat_id, onlinerby_url=onlinerby_url, store=store)
        user.save()
    print(user)
    runner = Runner(settings, user)
    runner.run()
