import requests


class TelegramBotApi:
    def __init__(self, token):
        self._token = token
        self.base_url = 'https://api.telegram.org/bot{}'.format(token)

    def send_message(self, chat_id, message, keyboard=None):
        data = {"text": message, "chat_id": chat_id}
        if keyboard is not None:
            data['reply_markup'] = {"keyboard": keyboard}
        url = self.base_url + "/sendMessage"
        response = requests.post(url, json=data)
        response.raise_for_status()

    def send_photo(self, chat_id, photo, keyboard=None):
        data = {"photo": photo, "chat_id": chat_id}
        if keyboard is not None:
            data['reply_markup'] = {"keyboard": keyboard}
        url = self.base_url + "/sendPhoto"
        response = requests.post(url, json=data)
        response.raise_for_status()
