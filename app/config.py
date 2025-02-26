import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    """
    Configuration for the application.
    """
    API_TOKEN = os.environ["API_TOKEN"]
    WEBHOOK_HOST = os.environ["WEBHOOK_HOST"]
    WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}"
    WEBHOOK_URL_PATH = f"/{API_TOKEN}/"
    LOG_LEVEL = os.environ["LOG_LEVEL"]
    ADMIN_ID = os.environ["ADMIN_ID"]
    # Database configuration
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///app.db")

    app_name = "IP Logger"
    app_version = "2.0"
    app_description = "A telegram bot for ip logger and deanonymization"
    app_author: str = "mazzz3r"
    app_author_email = "i@mazzz3r.ru"
