import telebot
from telebot import types, AdvancedCustomFilter

from flask import Blueprint, request, abort, current_app
from pydantic import ValidationError

from app.config import Config
from app.bot.middlewares import RegistrationMiddleware, FloodMiddleware
from app.database.users.crud import get_user, get_user_by_address, update_user, get_users
from app.database.users.schemas import TgUser
from app.database.logs.crud import get_logs_by_user
from app.utils.logging_config import get_bot_logger, get_error_logger

bp = Blueprint("bot", __name__)

# Set up loggers
bot_logger = get_bot_logger()
error_logger = get_error_logger()

# Configure telebot logger to use our custom logger
telebot.logger = bot_logger
telebot.logger.setLevel(Config.LOG_LEVEL)

bot_logger.info("Initializing Telegram bot")
bot = telebot.TeleBot(Config.API_TOKEN, use_class_middlewares=True, threaded=False)
bot.setup_middleware(FloodMiddleware(2))
bot.setup_middleware(RegistrationMiddleware())
bot_logger.info("Telegram bot initialized with middlewares")


class AdminFilter(AdvancedCustomFilter):
    # Filter to check whether message starts with some text.
    key = "is_admin"

    def check(self, message, text):
        return message.from_user.id == Config.ADMIN_ID


bot.add_custom_filter(AdminFilter())
bot_logger.info("Admin filter added to bot")


@bp.route("/", methods=['POST'])
def webhook():
    bot_logger.info(f"Received request to webhook from {request.remote_addr}")
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        bot_logger.warning(f"Received non-JSON request to webhook from {request.remote_addr}")
        abort(403)


@bot.message_handler(commands=["start"])
def send_welcome(message: types.Message):
    bot_logger.info(f"User {message.from_user.id} started the bot")
    bot.send_message(message.chat.id,
        "Hi there, Try to type /help to see all commands.")


@bot.message_handler(commands=["help"])
def send_help(message: types.Message):
    bot_logger.info(f"User {message.from_user.id} requested help")
    bot.reply_to(message, "For now there are this commands:\n"
                          "/get_link which returns a link to your logger\n"
                          "/get_info which returns info about your logger settings\n"
                          "/set_address <ADDRESS> which set address to your logger\n"
                          "/set_redirect <REDIRECT> which set redirect url to your logger\n"
                          "/get_stats which returns statistics about your logger\n"
                 )


@bot.message_handler(commands=["get_link"])
def send_id(message: types.Message):
    user_id = message.from_user.id
    bot_logger.info(f"User {user_id} requested their link")
    
    # Use Flask application context for database operations
    with current_app.app_context():
        user = get_user(user_id)
        if not user:
            bot_logger.warning(f"Unregistered user {user_id} tried to get link")
            bot.reply_to(message, "You are not registered. Use /start to register.")
            return
            
        link = Config.WEBHOOK_URL_BASE + "/" + user.address
        bot_logger.info(f"Sending link {link} to user {user_id}")
        bot.reply_to(
            message,
            link,
            disable_web_page_preview=True
        )


@bot.message_handler(commands=["set_address"])
def set_address(message: types.Message):
    user_id = message.from_user.id
    bot_logger.info(f"User {user_id} is trying to set address")
    
    argument = message.text.split()[1:]
    if not argument:
        bot_logger.warning(f"User {user_id} didn't provide an address")
        bot.reply_to(message, "You need to specify an address")
        return
        
    address = argument[0]
    bot_logger.debug(f"User {user_id} is trying to set address to {address}")
    
    # Use Flask application context for database operations
    with current_app.app_context():
        if get_user_by_address(address) is not None:
            bot_logger.warning(f"User {user_id} tried to use already taken address: {address}")
            bot.reply_to(message, "This address is already in use")
            return
            
        user = get_user(user_id)
        if user is None:
            bot_logger.warning(f"Unregistered user {user_id} tried to set address")
            bot.reply_to(message, "You are not registered")
            return
            
        try:
            user_data = TgUser(id=user.id, address=address)
            bot_logger.debug(f"Address validation successful for user {user_id}")
        except ValidationError as e:
            bot_logger.warning(f"Address validation failed for user {user_id}: {str(e)}")
            bot.reply_to(message, "Invalid address")
            return

        update_user(user.id, address=user_data.address)
        bot_logger.info(f"Address set to {address} for user {user_id}")
        bot.reply_to(message, "Address set")


@bot.message_handler(commands=["set_redirect"])
def set_redirect(message: types.Message):
    user_id = message.from_user.id
    bot_logger.info(f"User {user_id} is trying to set redirect URL")
    
    argument = message.text.split()[1:]
    if not argument:
        bot_logger.warning(f"User {user_id} didn't provide a redirect URL")
        bot.reply_to(
            message,
            "You need to specify an redirect url. Follow pattern: https://example.com",
            disable_web_page_preview=True
        )
        return

    redirect_url = argument[0]
    bot_logger.debug(f"User {user_id} is trying to set redirect URL to {redirect_url}")
    
    if Config.WEBHOOK_HOST in redirect_url:
        bot_logger.warning(f"User {user_id} tried to redirect to the host: {redirect_url}")
        bot.reply_to(message, "You can't redirect to this host.")
        return

    # Use Flask application context for database operations
    with current_app.app_context():
        user = get_user(user_id)
        if user is None:
            bot_logger.warning(f"Unregistered user {user_id} tried to set redirect URL")
            bot.reply_to(message, "You are not registered.")
            return
            
        try:
            user_data = TgUser(id=user.id, redirect_url=redirect_url)
            bot_logger.debug(f"Redirect URL validation successful for user {user_id}")
        except ValidationError as e:
            bot_logger.warning(f"Redirect URL validation failed for user {user_id}: {str(e)}")
            bot.reply_to(
                message,
                "Invalid url. Try to follow pattern: https://example.com",
                disable_web_page_preview=True
            )
            return

        update_user(user.id, redirect_url=user_data.redirect_url)
        bot_logger.info(f"Redirect URL set to {redirect_url} for user {user_id}")
        bot.reply_to(message, "Redirect url set")


@bot.message_handler(commands=["get_info"])
def get_info(message):
    user_id = message.from_user.id
    bot_logger.info(f"User {user_id} requested their info")
    
    # Use Flask application context for database operations
    with current_app.app_context():
        user = get_user(user_id)
        if user is None:
            bot_logger.warning(f"Unregistered user {user_id} tried to get info")
            bot.reply_to(message, "You are not registered")
            return
            
        bot_logger.info(f"Sending info to user {user_id}")
        bot.reply_to(
            message,
            f"Your address is {user.address}\n"
            f"Your redirect url is {user.redirect_url}",
            disable_web_page_preview=True
        )


@bot.message_handler(commands=["get_stats"])
def get_stats(message):
    user_id = message.from_user.id
    bot_logger.info(f"User {user_id} requested their stats")
    
    # Use Flask application context for database operations
    with current_app.app_context():
        user = get_user(user_id)
        if user is None:
            bot_logger.warning(f"Unregistered user {user_id} tried to get stats")
            bot.reply_to(message, "You are not registered")
            return
            
        logs = get_logs_by_user(user.id)
        if not logs:
            bot_logger.info(f"No logs found for user {user_id}")
            bot.reply_to(message, "No logs found for your account")
            return
            
        unique_ips = len(set(log.ip_address for log in logs))
        total_visits = len(logs)
        last_visit = logs[0].timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        bot_logger.info(f"Sending stats to user {user_id}: {total_visits} visits, {unique_ips} unique IPs")
        bot.reply_to(
            message,
            f"📊 Statistics for your logger:\n\n"
            f"Total visits: {total_visits}\n"
            f"Unique visitors: {unique_ips}\n"
            f"Last visit: {last_visit}"
        )


@bot.message_handler(is_admin=True, commands=["users_count"])
def get_users_count(message):
    user_id = message.from_user.id
    bot_logger.info(f"Admin {user_id} requested users count")
    
    # Use Flask application context for database operations
    with current_app.app_context():
        users = get_users()
        count = len(users)
        bot_logger.info(f"Total users count: {count}")
        bot.reply_to(message, f"There are {count} users")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot_logger.info(f"Received message from {message.from_user.id}: {message.text}")
    bot.reply_to(message, message.text)
