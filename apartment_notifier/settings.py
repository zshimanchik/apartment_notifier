import os

store = os.environ['STORE']
telegram_api_key = os.environ['TELEGRAM_API_KEY']
print_notifier = os.environ.get('PRINT_NOTIFIER', 'false').lower() in ('1', 'true')
