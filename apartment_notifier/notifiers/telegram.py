from typing import List

import requests

from apartment_notifier.models import Apartment


class TelegramNotifier:
    def __init__(self, api_key, chat_id, soft_limit=15, hard_limit=400, bulk_size=50):
        self.api_key = api_key
        self.chat_id = chat_id
        self.soft_limit = soft_limit
        self.hard_limit = hard_limit
        self.bulk_size = bulk_size
        self.send_message_url = 'https://api.telegram.org/bot{}/sendMessage'.format(api_key)

    def notify(self, apartments: List[Apartment]):
        if len(apartments) < self.soft_limit:
            self._notify_verbose(apartments)
        elif len(apartments) < self.hard_limit:
            self._notify_in_bulk(apartments)
        else:
            self._notify_its_too_much(apartments)

    def _notify_verbose(self, apartments: List[Apartment]):
        for apartment in apartments:
            message = (
                f'Адрес: {apartment.location}\n'
                f'Цена: {apartment.price} {apartment.price_currency}\n'
                f'Дата обновления: {apartment.last_time_up}\n'
                f'Дата создания: {apartment.created_at}\n'
                f'Фото: {apartment.photo}\n'
                f'Ссылка: {apartment.link}'
            )
            self._send_tg_message(message)

    def _notify_in_bulk(self, apartments: List[Apartment]):
        message = (f"Я нашел {len(apartments)} новых квартир, но это больше чем {self.soft_limit}, "
                   f"поэтому скину тебе только ссылки:\n")
        for offset in range(0, len(apartments), self.bulk_size):
            message += '\n'.join(ap.link for ap in apartments[offset:offset+self.bulk_size])
            self._send_tg_message(message)
            message = ''

    def _notify_its_too_much(self, apartments: List[Apartment]):
        message = (f"Я нашел {len(apartments)} новых квартир. "
                   f"Это больше чем {self.hard_limit}, так что я не буду их показывать.")
        self._send_tg_message(message)

    def _send_tg_message(self, message):
        data = {"text": message, "chat_id": self.chat_id}
        response = requests.post(self.send_message_url, json=data)
        response.raise_for_status()
