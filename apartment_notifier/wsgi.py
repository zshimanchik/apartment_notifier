import logging.config

from flask import Flask

from apartment_notifier import settings
from apartment_notifier.main import Runner
from apartment_notifier.store import JsonFileStore

_LOGGER = logging.getLogger(__name__)
app = Flask(__name__)
store, _created = JsonFileStore.load_or_create(settings.store)
logging.config.dictConfig(settings.LOGGING)


@app.route('/cron/check_apartments')
def check_apartments():
    _LOGGER.info("Starting Runner...")
    runner = Runner(settings, store)
    runner.run()
    return 'OK'
