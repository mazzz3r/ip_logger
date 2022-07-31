from flask import Flask
from app.logger import bp as logger_blueprint
from app.bot import bp as bot_blueprint


app = Flask(__name__)

app.register_blueprint(logger_blueprint, url_prefix='/logger')
app.register_blueprint(bot_blueprint, url_prefix='/bot')

#  app.run()
