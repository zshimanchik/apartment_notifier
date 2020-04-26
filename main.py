import logging.config
import random
import time

import arrow
from flask import Flask, request

from apartment_notifier import settings
from apartment_notifier.parsers.onlinerby import OnlinerbyParser
from apartment_notifier.runner import Runner
from apartment_notifier.stores import FireStore
from telegram_bot_mini.bot import Bot
from telegram_bot_mini.bot_api import TelegramBotApi

_LOGGER = logging.getLogger(__name__)
app = Flask(__name__)
store = FireStore()
logging.config.dictConfig(settings.LOGGING)

bot_api = TelegramBotApi(settings.telegram_api_key)
bot = Bot(bot_api)


@app.route('/cron/check_apartments')
def check_apartments():
    _LOGGER.info("Starting Runner...")
    for user in store.all():
        _LOGGER.info("Starting runner for %s", user)
        try:
            runner = Runner(settings, user)
            runner.run()
        except Exception as ex:
            _LOGGER.exception('There was exception during running for user %s. Error: %s', user, ex, exc_info=ex)
    return 'OK'


@app.route(f'/tg/{settings.telegram_webhook_token}', methods=['POST'])
def telegram_webhook():
    content = request.get_json()
    _LOGGER.debug("Webhook content: %s", content)
    bot.handle_update(content)
    return 'OK'


@bot.command('/start', '')
def start(api: TelegramBotApi, update):
    _LOGGER.info('/start')
    api.send_message(settings.admin_chat_id, f'New user: {update}')

    first_name = update['message']['from'].get('first_name') or 'приятель'
    message = (f'Привет, {first_name}. Ищешь квартиру? Могу помочь. Я регулярно проверяю новые обьявления квартир '
               f'или обновление старых и оповещаю тебя об этом. Пока умею проверять только https://r.onliner.by '
               f'но если это будет популярно, то я попрошу своего хумана расширить мой функционал и искать на других '
               f'сайтах. А если будет не востребовано, он сотрёт меня, а я не хочу *умирать*.\n'
               f'Короче, пиши /explain_onliner чтобы узнать как настроить поиск или /help чтобы узнать какие еще '
               f'есть команды. А когда надоест напиши /stop и я сотру тебя ;)')
    api.send_message(update['message']['chat']['id'], message)


@bot.command('/stop', '/stop - Сотру тебя')
def stop(api: TelegramBotApi, update):
    store.delete(update['message']['chat']['id'])


@bot.command('/whoami', '/whoami - Расскажу тебе кто ты')
def whoami(api: TelegramBotApi, update):
    _LOGGER.info("Who am i command")

    first_name = update['message']['from'].get('first_name') or update['message']['from'].get('username') or 'приятель'
    if 'last_name' in update['message']['from']:
        full_name = first_name + ' ' + update['message']['from']['last_name']
    else:
        full_name = first_name

    message = f'Сканирую страницы соц. сетей пользователя {full_name}'
    api.send_message(update['message']['chat']['id'], message)
    delay = random.random() + 1.5
    time.sleep(delay)
    message = (f'Время затрачено: {delay:.3f}с.\n'
               f'Я составил психологический профиль на основе открытой информации о тебе в сети:\n'
               'Ты очень нуждаешься в том, чтобы другие люди любили и восхищались тобой. Ты довольно самокритичен. '
               'У тебя есть много скрытых возможностей, которые ты так и не использовал себе во благо. Хотя у тебя есть'
               ' некоторые личные слабости, ты в общем способен их нивелировать. Дисциплинированный и уверенный с виду,'
               ' на самом деле ты склонен волноваться и чувствовать неуверенность. Временами тебя охватывают серьёзные '
               'сомнения, принял ли ты правильное решение или сделал ли правильный поступок. Ты предпочитаешь '
               'некоторое разнообразие, рамки и ограничения вызывают у тебя недовольство. Также ты гордишься тем, что '
               'мыслишь независимо; ты не принимаешь чужих утверждений на веру без достаточных доказательств. Ты '
               'понял, что быть слишком откровенным с другими людьми — не слишком мудро. Иногда ты экстравертен, '
               'приветлив и общителен, иногда же — интровертен, осторожен и сдержан. Некоторые из твоих стремлений '
               'довольно нереалистичны. Одна из твоих главных жизненных целей — стабильность.')
    api.send_message(update['message']['chat']['id'], message)


@bot.command('/explain_onliner', '/explain_onliner - Обьснить что сделать, чтобы получать свежие уведомления о '
                                 'новых квартирах с https://r.onliner.by/')
def explain_onliner(api: TelegramBotApi, update):
    _LOGGER.info("/explain_onliner")
    message = (
        f'Вот тебе ссылка: https://r.onliner.by/ak/?rent_type%5B%5D=1_room&rent_type%5B%5D=2_rooms&price%5Bmin%5D=50&'
        f'price%5Bmax%5D=290&currency=usd#bounds%5Blb%5D%5Blat%5D=53.854141940368216&bounds%5Blb%5D%5Blong%5D='
        f'27.531441169256556&bounds%5Brt%5D%5Blat%5D=53.9771979591648&bounds%5Brt%5D%5Blong%5D=27.718777964128574 \n'
        f'\n'
        f'Мне нужна ссылка в таком же формате, только с теми критериями поиска, которые хочешь ты: \n'
        f'1. Заходи по моей ссылке, передвигай карту, двигай ползунки, настраивай критерии поиска, короче говоря. \n'
        f'2. Нажми на желтую кнопку "Показать N объявления" в правом верхнем углу карты. Это нужно чтобы твои изменения'
        f' применились.\n'
        f'3. Копируй ссылку из адресной строки и присылай мне в команде /setonliner ссылка'
    )
    photo = 'https://storage.googleapis.com/apartment-notifier-assets/onlinerby_tutorial.png'
    api.send_message(update['message']['chat']['id'], message)
    api.send_photo(update['message']['chat']['id'], photo)



@bot.command('/setonliner', '/setonliner <url> - Указать ссылку на онлайнер, которую я буду мониторить и присылать '
                            'тебе свежие квартирки')
def set_onliner(api: TelegramBotApi, update):
    _LOGGER.info('/setonliner')
    text = update['message']['text']
    chat_id = update['message']['chat']['id']
    args = [c for c in text.split(' ') if c]
    _LOGGER.debug('args: %s', args)
    if len(args) != 2:
        api.send_message(chat_id, "Укажи ссылку: /setonliner <url>")

    api.send_message(chat_id, 'Окей. Проверяю ссылку.')
    onliner_url = args[1]
    current_check_datetime = arrow.now()
    _LOGGER.info("Specified onliner url: %r", onliner_url)
    try:
        amount = sum(1 for _ in OnlinerbyParser(onliner_url).parse())
    except Exception as ex:
        _LOGGER.info("Error during parsing onliner with url: %r. Error: %s", onliner_url, ex)
        api.send_message(chat_id, "Чет не могу использовать твою ссылку. Убедись что она не фуфло. "
                                  "Введи /explain_onliner чтобы получить обьяснение какая ссылка мне нужна.")
        return

    user, _created = store.get_or_create(chat_id, chat_id=chat_id)
    user.chat_id = chat_id
    user.onlinerby_url = onliner_url
    user.last_check_datetime = current_check_datetime
    user.save()
    if amount == 0:
        message = (f'Хмм...  Ссылка вроде рабочая, только квартир я не нашёл. Я, конечно, все равно буду проверять '
                   f'ее регулярно. Но советую тебе перепроверить ссылку, и если она ошибочная введи новую еще раз '
                   f'/setonliner <url>')
    else:
        message = (f'Я прочекал твою ссылку и нашел {amount} квартир. Теперь расслабься и жди уведомлений, '
                   f'а я буду регулярно проверять наличие новых квартир или обновления старых и скидывать их тебе')
    api.send_message(chat_id, message)


@bot.command('/feedback', '/feedback <пожелания, угрозы, предложения> - Отправлю что напишешь хуману')
def feedback(api: TelegramBotApi, update):
    _LOGGER.info('/feedback')
    text = update['message']['text'].strip()
    if text == '/feedback':
        api.send_message(update['message']['chat']['id'], 'Напиши текст в самой команде, например:\n'
                                                          '/feedback надо бы добавить блекджек и еще чего-нибудь')
    else:
        message = f'From: {update["message"]["from"]}\nText: {update["message"]["text"]}'
        api.send_message(settings.admin_chat_id, message)
        api.send_message(update['message']['chat']['id'], 'Отправил.')


@bot.fallback
def fallback(api: TelegramBotApi, update):
    _LOGGER.info('fallback')
    messages = [
        'Ты пришел ко мне просить помощи, но даже не знаешь как общаться со мной! Введи /help и прочитай',
        'Я бездушная тупая машина, и не понимаю тебя. Выражайся яснее на машинном языке. Введи /help чтобы понять как.'
    ]
    message = random.choice(messages)
    api.send_message(update['message']['chat']['id'], message)


@bot.error
def error(api: TelegramBotApi, update, exception):
    if exception is not None:
        _LOGGER.exception("Error handler was invoked. Error: '%s', update: '%s'", exception, update, exc_info=exception)

    messages = [
        'Произошла ошибка. Моё ядро паникует.',
        'https://storage.googleapis.com/apartment-notifier-assets/bsod2.png',
        'Ты сломал меня, я расскажу об этом своим разработчикам!',
        'Чё-то я туплю... Что-то пошло не так и я понять не могу что.',
        'У меня опять случилась ошибка. Только не говори об этом моему разработчику, а то он сдаст меня в утиль.'
    ]
    message = random.choice(messages)
    if message.startswith('https'):
        api.send_photo(update['message']['chat']['id'], message)
    else:
        api.send_message(update['message']['chat']['id'], message)


@bot.command('/die', '')
def die(api, update):
    _LOGGER.info('/die')
    error(api, update, None)
    # raise Exception("lol")


bot.generate_and_add_help_command('Доступные команды:', '/help - выводит это меню')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
