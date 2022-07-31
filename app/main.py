from flask import Flask
from app.logger import bp as logger_blueprint
from app.bot import bp as bot_blueprint, create_webhook


app = Flask(
    __name__,
    static_folder="../static",
    static_url_path="/static"
)

app.register_blueprint(logger_blueprint, url_prefix='/logger')
app.register_blueprint(bot_blueprint, url_prefix='/bot')
create_webhook()

#  app.run()
