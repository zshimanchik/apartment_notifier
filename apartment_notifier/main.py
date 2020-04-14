import logging.config

import arrow

from apartment_notifier import settings
from apartment_notifier.notifiers.print import PrintNotifier
from apartment_notifier.notifiers.telegram import TelegramNotifier
from apartment_notifier.parsers.onlinerby import OnlinerbyParser
from apartment_notifier.store import JsonFileStore

_LOGGER = logging.getLogger(__name__)


class Runner:
    def __init__(self, settings, store):
        self.settings = settings
        self.store = store
        self._init_parsers()
        self._init_filters()
        self._init_notifiers()

    def _init_parsers(self):
        _LOGGER.debug('Initializing parsers')
        if not self.store.get_onlinerby_url():
            raise RuntimeError('"onlinerby_url" is not set in store')
        self.parsers = [
            OnlinerbyParser(self.store.get_onlinerby_url())
        ]
        _LOGGER.info('Parsers: %s', self.parsers)

    def _init_filters(self):
        _LOGGER.debug('Initializing filters')
        self.filters = []
        last_check_datetime = self.store.get_last_check_datetime()
        if last_check_datetime is not None:
            self.filters.append(lambda apartment: apartment.last_time_up >= last_check_datetime)
        _LOGGER.info('Filters: %s', self.filters)

    def _init_notifiers(self):
        _LOGGER.debug('Initializing notifiers')
        self.notifiers = []
        if self.settings.print_notifier:
            self.notifiers.append(PrintNotifier())
        if self.store.get_telegram_chat_id():
            self.notifiers.append(TelegramNotifier(self.settings.telegram_api_key, self.store.get_telegram_chat_id()))
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
        self.store.set_last_check_datetime(current_check_datetime)
        _LOGGER.info('Finished...')


if __name__ == '__main__':
    logging.config.dictConfig(settings.LOGGING)
    store = JsonFileStore.load_or_create(settings.store)[0]
    runner = Runner(settings, store)
    runner.run()
