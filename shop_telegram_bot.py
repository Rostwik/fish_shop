import os
import logging
import textwrap
from functools import partial

import redis
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

from logger_handler import TelegramLogsHandler
from dotenv import load_dotenv

from moltin import get_moltin_token, get_products, get_product, get_stock, get_price, get_product_image

logger = logging.getLogger('shop_tg_bot')

_database = None


def error_handler(bot, update, error):
    logger.error(f'Телеграм бот упал с ошибкой: {error}', exc_info=True)
    print(f'так так {update}')
    print(f'не так {error}')


def start(bot, update, client_id, client_secret):
    moltin_token = get_moltin_token(client_id, client_secret)
    products = get_products(moltin_token)

    keyboard = [[InlineKeyboardButton(
        product['attributes']['name'],
        callback_data=product['id']
    ) for product in products]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        f'Доброго денечка, {update.message.chat.username} ! \n Это рыбный магазин.',
        reply_markup=reply_markup,
    )

    return 'HANDLE_MENU'


def handle_menu(bot, update, client_id, client_secret):
    query = update.callback_query

    product_id = query.data
    moltin_token = get_moltin_token(client_id, client_secret)

    product = get_product(moltin_token, product_id)
    stock = get_stock(moltin_token, product_id)
    price = get_price(moltin_token, product_id)
    image_link = get_product_image(moltin_token, product_id)

    keyboard = [
        [InlineKeyboardButton('Назад', callback_data='Назад')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f'''
               {product["attributes"]["name"]}
               {price["USD"]["amount"]} USD per kg
               {stock} on stock
               {product["attributes"]["description"]}
               '''

    bot.send_photo(
        chat_id=query.message.chat_id,
        photo=image_link,
        caption=textwrap.dedent(text),
        reply_markup=reply_markup,
    )
    bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)

    return 'HANDLE_DESCRIPTION'


def handle_description(bot, update, client_id, client_secret):
    query = update.callback_query

    if query.data == 'Назад':
        return 'HANDLE_MENU'


def echo(bot, update):
    query = update.callback_query

    bot.edit_message_text(text="Selected option: {}".format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)

    return "ECHO"


def handle_users_reply(bot, update, client_id, client_secret):
    db = get_database_connection()

    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    elif not db.get(chat_id):
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Кажется Вы у нас впервые, запустите бота командой "/start"'
        )
        return
    else:
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        'START': partial(
            start,
            client_id=client_id,
            client_secret=client_secret
        ),
        'HANDLE_MENU': partial(
            handle_menu,
            client_id=client_id,
            client_secret=client_secret
        ),
        'HANDLE_DESCRIPTION': partial(
            handle_menu,
            client_id=client_id,
            client_secret=client_secret
        ),
        'ECHO': echo
    }
    state_handler = states_functions[user_state]

    next_state = state_handler(bot, update)
    db.set(chat_id, next_state)


def get_database_connection():
    global _database

    if _database is None:
        redis_bd_credentials = os.getenv('REDIS_BD_CREDENTIALS')
        _database = redis.from_url(redis_bd_credentials)
        _database.ping()
        # _database.flushdb()
    return _database


if __name__ == '__main__':
    load_dotenv()
    telegram_api_token = os.getenv('TELEGRAM_API_TOKEN')
    telegram_monitor_api_token = os.getenv('TELEGRAM_MONITOR_API_TOKEN')
    telegram_admin_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    client_id = os.getenv('MOLTIN_CLIENT_KEY')
    client_secret = os.getenv('SECRET_KEY')

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    logger_bot = telegram.Bot(token=telegram_monitor_api_token)
    logger.setLevel(logging.WARNING)
    logger.addHandler(TelegramLogsHandler(logger_bot, telegram_admin_chat_id))

    updater = Updater(telegram_api_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(
        CallbackQueryHandler(partial(handle_users_reply, client_id=client_id, client_secret=client_secret)))
    dispatcher.add_handler(
        MessageHandler(Filters.text, partial(handle_users_reply, client_id=client_id, client_secret=client_secret)))
    dispatcher.add_handler(
        CommandHandler('start', partial(handle_users_reply, client_id=client_id, client_secret=client_secret)))
    dispatcher.add_error_handler(error_handler)
    updater.start_polling()

    updater.idle()
