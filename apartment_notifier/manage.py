import argparse

from apartment_notifier import settings
from apartment_notifier.store import JsonFileStore



if __name__ == '__main__':
    store, _created = JsonFileStore.load_or_create(settings.store)
    commands = {
        'set_onlinerby_url': store.set_onlinerby_url,
    }

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('command', choices=commands.keys())
    parser.add_argument('value')

    args = parser.parse_args()
    print(args)
    command = commands.get(args.command)
    command(args.value)
    store.save()
    print('Done')
