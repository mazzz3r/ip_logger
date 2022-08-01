from flask import Flask

from app.bot import bp as bot_blueprint
from app.logger import bp as logger_blueprint
from app.database import Base, engine
from app.database import models
from app.logger.utilities import RegexConverter


Base.metadata.create_all(engine)

app = Flask(
    __name__,
    static_folder="../static",
    static_url_path="/static"
)

app.url_map.converters['regex'] = RegexConverter
app.register_blueprint(logger_blueprint, url_prefix='/')
app.register_blueprint(bot_blueprint, url_prefix='/bot')

#  app.run()
