import os

_TRUE_LIST = ('1', 'true', 'yes', 'y')
store = os.environ.get('STORE', 'store.json')
telegram_api_key = os.environ['TELEGRAM_API_KEY']
telegram_webhook_token = os.environ['TELEGRAM_WEBHOOK_TOKEN']
print_notifier = os.environ.get('PRINT_NOTIFIER', 'false').lower() in _TRUE_LIST
exclude_log_time = os.environ.get('EXCLUDE_LOG_TIME', 'false').lower() in _TRUE_LIST


LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(name)s:%(lineno)-3d] %(levelname)-7s: %(message)s',
        },
        'verbose_without_time': {
            'format': '[%(name)s:%(lineno)-3d] %(levelname)-7s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose_without_time' if exclude_log_time else 'verbose',
            # 'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        '__main__': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'apartment_notifier': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}
