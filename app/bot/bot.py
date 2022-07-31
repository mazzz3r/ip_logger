from flask import Blueprint, request, abort
import telebot
import logging
import time

from app.config import Config

bp = Blueprint("bot", __name__)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(Config.API_TOKEN)


@bp.route(Config.WEBHOOK_URL_PATH, methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ""
    else:
        abort(403)


@bot.message_handler(commands=["help", "start"])
def send_welcome(message):
    bot.reply_to(message,
                 ("Hi there, I am EchoBot.\n"
                  "I am here to echo your kind words back to you."))


# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, message.text)


# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

time.sleep(0.1)

# Set webhook
bot.set_webhook(url=Config.WEBHOOK_URL_BASE + "/bot" + Config.WEBHOOK_URL_PATH)