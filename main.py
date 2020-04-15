import logging.config

from flask import Flask

from apartment_notifier import settings
from apartment_notifier.runner import Runner
from apartment_notifier.stores import FireStore

_LOGGER = logging.getLogger(__name__)
app = Flask(__name__)
store = FireStore()
logging.config.dictConfig(settings.LOGGING)


@app.route('/cron/check_apartments')
def check_apartments():
    _LOGGER.info("Starting Runner...")
    for user in store.all():
        _LOGGER.info("Starting runner for %s", user)
        runner = Runner(settings, user)
        runner.run()
    return 'OK'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
