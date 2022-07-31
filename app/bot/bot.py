import logging
import time

import telebot
from telebot import types

from flask import Blueprint, request, abort

from app.config import Config

bp = Blueprint("bot", __name__)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(Config.API_TOKEN, threaded=False)


@bp.route(Config.WEBHOOK_URL_PATH, methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok"
    else:
        abort(403)


@bot.message_handler(commands=["start"])
def send_welcome(message: types.Message):
    bot.send_message(message.chat.id,
                     ("Hi there, I am Big Brother and I am watching for you.\n"
                      "Try to type /help to see all commands"))


@bot.message_handler(commands=["help"])
def send_welcome(message: types.Message):
    bot.reply_to(message, "For now there is only one command: /get_link which returns a link to your logger.")


@bot.message_handler(commands=["get_link"])
def send_id(message: types.Message):
    bot.reply_to(message,
                 Config.WEBHOOK_URL_BASE + "/logger" + f"/{message.from_user.id}")


# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.send_message(message.chat.id, "Idk this command, just type /help")


# Remove webhook, it fails sometimes the set if there is a previous webhook
# Uncomment to create webhook
"""
def create_webhook():
    bot.remove_webhook()
    time.sleep(0.1)
    # Set webhook
    bot.set_webhook(url=Config.WEBHOOK_URL_BASE + "/bot" + Config.WEBHOOK_URL_PATH)
"""
