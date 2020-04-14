import logging.config

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
        if not store.get_onlinerby_url():
            raise RuntimeError('"onlinerby_url" is not set in store')
        self.parsers = [
            OnlinerbyParser(store.get_onlinerby_url())
        ]
        _LOGGER.info('Parsers: %s', self.parsers)

    def _init_filters(self):
        _LOGGER.debug('Initializing filters')
        onliner_seen_ids = set(store.get_onlinerby_seen_ids())
        self.filters = [
            lambda apartment: apartment.source == OnlinerbyParser.NAME and apartment.source_id not in onliner_seen_ids,
        ]
        _LOGGER.info('Filters: %s', self.filters)

    def _init_notifiers(self):
        _LOGGER.debug('Initializing notifiers')
        self.notifiers = []
        if settings.print_notifier:
            self.notifiers.append(PrintNotifier())
        if store.get_telegram_chat_id():
            self.notifiers.append(TelegramNotifier(settings.telegram_api_key, store.get_telegram_chat_id()))
        _LOGGER.info('Notifiers: %s', self.notifiers)

    def run(self):
        _LOGGER.info("Starting...")
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
        onliner_seen_ids = self.store.get_onlinerby_seen_ids()
        onliner_seen_ids.extend(apartment.source_id for apartment in new_apartments)
        self.store.set_onlinerby_seen_ids(onliner_seen_ids)
        _LOGGER.info('Finished...')


if __name__ == '__main__':
    logging.config.dictConfig(settings.LOGGING)
    store = JsonFileStore.load_or_create(settings.store)[0]
    runner = Runner(settings, store)
    runner.run()
