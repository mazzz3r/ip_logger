import os
from dataclasses import dataclass


@dataclass
class Config:
    """
    Configuration for the application.
    """
    API_TOKEN = os.environ["API_TOKEN"]
    WEBHOOK_HOST = os.environ["WEBHOOK_HOST"]
    WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}"
    WEBHOOK_URL_PATH = f"/{API_TOKEN}/"
    INITIALIZED = os.environ.get("INITIALIZED", False)

    PROJECT_KEY: str = os.environ["PROJECT_KEY"]

    app_name = "Telegram Bot"
    app_version = "1.0"
    app_description = "A telegram bot for ip logger and deanonymization"
    app_author: str = "mazzz3r"
    app_author_email = "i@mazzz3r.ru"
