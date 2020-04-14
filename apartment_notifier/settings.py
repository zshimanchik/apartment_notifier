import os

store = os.environ['STORE']
telegram_api_key = os.environ['TELEGRAM_API_KEY']
print_notifier = os.environ.get('PRINT_NOTIFIER', 'false').lower() in ('1', 'true')


LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(name)s:%(lineno)-3d] %(levelname)-7s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
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
