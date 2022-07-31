import os
from dataclasses import dataclass


@dataclass
class Config:
    """
    Configuration for the application.
    """
    API_TOKEN = os.environ.get("API_TOKEN", "YOUR TG API TOKEN HERE")
    WEBHOOK_HOST = os.environ.get("WEBHOOK_HOST", "YOUR_DOMAIN.COM")
    WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}"
    WEBHOOK_URL_PATH = f"/{API_TOKEN}/"

    app_name = "Telegram Bot"
    app_version = "1.0"
    app_description = "A telegram bot for ip logger and deanonymization"
    app_author: str = "mazzz3r"
    app_author_email = "i@mazzz3r.ru"
