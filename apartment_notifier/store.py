import json

import arrow
from arrow import Arrow


class JsonFileStore:
    def __init__(self, data, filename):
        self.data = data
        self.filename = filename

    @staticmethod
    def load(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        return JsonFileStore(data, filename)

    @classmethod
    def load_or_create(cls, filename):
        try:
            return cls.load(filename), False
        except Exception:
            return cls({}, filename), True

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2)

    def get_onlinerby_seen_ids(self) -> list:
        return self.data.get('onlinerby_seen_ids', [])

    def set_onlinerby_seen_ids(self, seen_ids):
        self.data['onlinerby_seen_ids'] = list(seen_ids)
        self.save()

    def get_last_check_datetime(self) -> Arrow:
        value = self.data.get('last_check_datetime')
        return arrow.get(value) if value else value

    def set_last_check_datetime(self, value: Arrow):
        self.data['last_check_datetime'] = value.isoformat()
        self.save()

    def get_onlinerby_url(self):
        return self.data.get('onlinerby_url')

    def set_onlinerby_url(self, url):
        self.data['onlinerby_url'] = url
        self.save()

    def get_telegram_chat_id(self):
        return self.data.get('telegram_chat_id')

    def set_telegram_chat_id(self, value):
        self.data['telegram_chat_id'] = value
        self.save()
