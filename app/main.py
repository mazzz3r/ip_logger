import os
import time
from flask import Flask, request, g

from app.bot import bp as bot_blueprint
from app.logger import bp as logger_blueprint
from app.logger.utilities import RegexConverter
from app.database import db
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.utils.logging_config import configure_logging
from app.config import Config


# Initialize logging
env = os.environ.get('FLASK_ENV', 'development')
loggers = configure_logging(env)
flask_logger = loggers['flask']
request_logger = loggers['request']
error_logger = loggers['error']

app = Flask(
    __name__,
    static_folder="../static",
    static_url_path="/static"
)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db.init_app(app)

# Create tables
with app.app_context():
    try:
        db.create_all()
        flask_logger.info("Database tables created successfully")
    except Exception as e:
        error_logger.error(f"Error creating database tables: {str(e)}", exc_info=True)

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",  # Use redis:// in production
)

app.url_map.converters['regex'] = RegexConverter
app.register_blueprint(logger_blueprint, url_prefix='/')
app.register_blueprint(bot_blueprint, url_prefix=Config.WEBHOOK_URL_PATH)

flask_logger.info(f"Application initialized in {env} mode")
flask_logger.info(f"Registered blueprints: logger, bot")

# Request logging
@app.before_request
def before_request():
    g.start_time = time.time()
    request_logger.info(f"Request started: {request.method} {request.path} from {request.remote_addr}")

@app.after_request
def after_request(response):
    # Calculate request duration
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        request_logger.info(
            f"Request completed: {request.method} {request.path} "
            f"- Status: {response.status_code} - Duration: {duration:.4f}s"
        )
    
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    request_logger.warning(f"404 error: {request.path} - Referrer: {request.referrer}")
    return "Page not found", 404

@app.errorhandler(500)
def internal_server_error(e):
    error_logger.error(f"500 error: {str(e)} - URL: {request.path}", exc_info=True)
    return "Internal server error", 500

@app.errorhandler(Exception)
def unhandled_exception(e):
    error_logger.critical(
        f"Unhandled exception: {str(e)} - "
        f"URL: {request.path} - Method: {request.method}",
        exc_info=True
    )
    return "Internal server error", 500

#  app.run()
