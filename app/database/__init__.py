from flask_sqlalchemy import SQLAlchemy
from app.utils.logging_config import get_db_logger

# Initialize logger
db_logger = get_db_logger()
db_logger.info("Initializing database module")

# Initialize SQLAlchemy
db = SQLAlchemy()
db_logger.info("SQLAlchemy initialized")

# Import models after db initialization to avoid circular imports
from app.database.models import User, Log
db_logger.info("Database models imported")
