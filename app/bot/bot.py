import logging

import telebot
from telebot import types

from flask import Blueprint, request, abort
from pydantic import ValidationError

from app.config import Config
from app.bot.middlewares import FloodMiddleware, RegistrationMiddleware
from app.database.crud import get_user, get_user_by_address, update_user
from app.database.schemas import TgUser

bp = Blueprint("bot", __name__)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(Config.API_TOKEN, use_class_middlewares=True)
bot.setup_middleware(FloodMiddleware(2))
bot.setup_middleware(RegistrationMiddleware())


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
    bot.reply_to(message, "For now there are this commands:\n"
                          "/get_link which returns a link to your logger\n"
                          "/get_info which returns info about your logger settings\n"
                          "/set_address <ADDRESS> which set address to your logger\n"
                          "/set_redirect <REDIRECT> which set redirect url to your logger\n"
                 )


@bot.message_handler(commands=["get_link"])
def send_id(message: types.Message):
    user = get_user(message.from_user.id)
    bot.reply_to(
        message,
        Config.WEBHOOK_URL_BASE + "/" + user.address,
        disable_web_page_preview=True
    )


@bot.message_handler(commands=["set_address"])
def set_address(message: types.Message):
    argument = message.text.split()[1:]
    if not argument:
        bot.reply_to(message, "You need to specify an address")
        return
    address = argument[0]
    if get_user_by_address(address) is not None:
        bot.reply_to(message, "This address is already in use")
        return
    user = get_user(message.from_user.id)
    if user is None:
        bot.reply_to(message, "You are not registered")
        return
    try:
        TgUser(id=user.id, address=address)
    except ValidationError:
        bot.reply_to(message, "Invalid address")
        return

    user.address = address
    update_user(user)
    bot.reply_to(message, "Address set")


@bot.message_handler(commands=["set_redirect"])
def set_redirect(message: types.Message):
    argument = message.text.split()[1:]
    if not argument:
        bot.reply_to(
            message,
            "You need to specify an redirect url. Follow pattern: https://example.com",
            disable_web_page_preview=True
        )
        return

    redirect_url = argument[0]
    if Config.WEBHOOK_HOST in redirect_url:
        bot.reply_to(message, "You can't redirect to this host.")
        return

    user = get_user(message.from_user.id)
    if user is None:
        bot.reply_to(message, "You are not registered.")
        return
    try:
        TgUser(id=user.id, redirect_url=redirect_url)
    except ValidationError:
        bot.reply_to(
            message,
            "Invalid url. Try to follow pattern: https://example.com",
            disable_web_page_preview=True
        )
        return

    user.redirect_url = redirect_url
    update_user(user)
    bot.reply_to(message, "Address set")


@bot.message_handler(commands=["get_info"])
def get_info(message):
    user = get_user(message.from_user.id)
    if user is None:
        bot.reply_to(message, "You are not registered")
        return
    bot.reply_to(
        message,
        f"Your address is {user.address}\n"
        f"Your redirect url is {user.redirect_url}",
        disable_web_page_preview=True
    )


# Remove webhook, it fails sometimes the set if there is a previous webhook
# Uncomment to create webhook
"""
def create_webhook():
    bot.remove_webhook()
    time.sleep(0.1)
    # Set webhook
    bot.set_webhook(url=Config.WEBHOOK_URL_BASE + "/bot" + Config.WEBHOOK_URL_PATH)
"""
