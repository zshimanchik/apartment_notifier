import logging
import sys

from apartment_notifier import settings
from apartment_notifier.notifiers import PrintNotifier
from apartment_notifier.parsers.onlinerby import OnlinerbyParser
from apartment_notifier.store import JsonFileStore

_LOGGER = logging.getLogger(__name__)



def main():
    _LOGGER.info('Starting...')
    store, _created = JsonFileStore.load_or_create(settings.store)
    _LOGGER.info(f'Store was {"created" if _created else "loaded"}')

    if not store.get_onlinerby_url():
        raise RuntimeError('"onlinerby_url" is not set in store. Perform `store.set_onlinerby_url(url)`')

    parsers = [
        OnlinerbyParser(store.get_onlinerby_url())
    ]

    onliner_seen_ids = set(store.get_onlinerby_seen_ids())
    filters = [
        lambda apartment: apartment.source == OnlinerbyParser.NAME and apartment.source_id not in onliner_seen_ids,
    ]

    notifiers = [
        PrintNotifier()
    ]

    new_apartments = []
    total_apartment_amount = 0

    for parser in parsers:
        _LOGGER.info('Parsing with %s', parser.NAME)
        for apartment in parser.parse():
            total_apartment_amount += 1
            if all(filter(apartment) for filter in filters):
                new_apartments.append(apartment)

    _LOGGER.info('Total apartment found: %s', total_apartment_amount)
    _LOGGER.info('New apartment amount: %s', len(new_apartments))
    for notifier in notifiers:
        _LOGGER.info('Notifying with %s', notifier.__class__.__name__)
        notifier.notify(new_apartments)

    onliner_seen_ids.update(apartment.source_id for apartment in new_apartments)
    store.set_onlinerby_seen_ids(onliner_seen_ids)
    store.save()
    _LOGGER.info('Finished...')


if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s [%(name)s:%(lineno)-3d] %(levelname)-7s: %(message)s'
    logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT, stream=sys.stdout)
    logging.getLogger('__main__').setLevel(logging.DEBUG)
    logging.getLogger('apartment_notifier').setLevel(logging.DEBUG)
    main()
