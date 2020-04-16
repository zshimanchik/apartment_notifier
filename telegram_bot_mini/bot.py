from telegram_bot_mini.bot_api import TelegramBotApi


class Handler:
    def check_update(self, update) -> bool:
        raise NotImplemented

    def handle(self, api: TelegramBotApi, update):
        raise NotImplemented


class CommandHandler(Handler):
    def __init__(self, command, callback, help):
        self.command = command
        self.callback = callback
        self.help = help

    def check_update(self, update) -> bool:
        if update.get('message', {}).get('text') is not None:
            first_word = update['message']['text'].split(' ')[0]
            if '@' in first_word:
                first_word = first_word[:first_word.index('@')]
            if first_word == self.command:
                return True
        return False

    def handle(self, api, update):
        self.callback(api, update)


class Bot:
    def __init__(self, api: TelegramBotApi, fallback_callback=None, error_callback=None):
        self._api = api
        self.handlers = []
        self._fallback_callback = fallback_callback
        self._error_callback = error_callback

    def add_handler(self, handler: Handler):
        self.handlers.append(handler)

    def handle_update(self, update):
        try:
            for handler in self.handlers:
                if handler.check_update(update):
                    handler.handle(self._api, update)
                    break
            else:
                if self._fallback_callback is not None:
                    self._fallback_callback(self._api, update)
        except Exception as ex:
            if self._error_callback is not None:
                self._error_callback(self._api, update, ex)

    def generate_and_add_help_command(self):
        HELP_TEXT = '/help - выводит это меню'
        all_helps = '\n\t'.join(h.help for h in self.handlers if isinstance(h, CommandHandler) and h.help)
        message = f'Доступные команды:\n\t{HELP_TEXT}\n\t{all_helps}'

        def help_callback(api: TelegramBotApi, update):
            api.send_message(update['message']['chat']['id'], message)
        self.add_handler(CommandHandler('/help', help_callback, HELP_TEXT))

    def command(self, name, help):
        """Decorator that creates and adds CommandHandler"""
        def decor(callback):
            self.add_handler(CommandHandler(name, callback, help))
            return callback
        return decor

    def fallback(self, callback):
        """
        Could be used as decorator to register fallback callback that will be executed if no proper Handler was found
        """
        self._fallback_callback = callback
        return callback

    def error(self, callback):
        """
        Could be used as decorator to register error callback that will be executed if any exception raised
        during update handling
        """
        self._error_callback = callback
        return callback


