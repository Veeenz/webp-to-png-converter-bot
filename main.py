#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple Bot to reply to Telegram messages.

This program is dedicated to the public domain under the CC0 license.

This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import uuid
from PIL import Image
import requests
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN = "456882544:AAFROqKMzKfCMmralQ4mx-xqFGDo0THjDIc"
PATH_DIRECTORY = "tmp"
# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def download_sticker(stickerId):
    url = 'https://api.telegram.org/bot{}/getFile?file_id={}'.format(TOKEN, stickerId)
    logger.info(url)
    r = requests.get(url)
    if r.status_code != 200:
        return {'success': False, 'msg': 'Connection error'}
    data = r.json()
    if data['ok']:
        url = 'https://api.telegram.org/file/bot{}/{}'.format(TOKEN, data['result']['file_path'])
        logger.info(url)
        response = requests.get(url)
        if response.status_code == 200:
            path = PATH_DIRECTORY + '/' +uuid.uuid4().hex[0:8]+'.webp'
            with open(path, 'wb') as f:
                f.write(response.content)
        return {'success': True, 'msg': 'OK', 'path': path}

def convert_png(path):
    im = Image.open(path)
    im.load()
    alpha = im.split()[-1]
    im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
    mask = Image.eval(alpha, lambda a: 255 if a <=128 else 0)
    im.paste(255, mask)
    newPath = path.replace(".webp",".png")
    im.save(newPath, transparency=255)    
    return newPath
def echo(bot, update):
    """Echo the user message."""
    with open('random','w+') as opened:
        opened.write(str(update.message))
    result = download_sticker(update.message.sticker.file_id)
    if result['success']:
        image = convert_png(result['path'])
        bot.send_document(chat_id=update.message.chat.id, document=open(image, 'rb'))
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)



def main():
    """Start the bot."""
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.sticker, echo))
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()