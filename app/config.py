from dataclasses import dataclass


@dataclass
class Config:
    """
    Configuration for the application.
    """
    API_TOKEN = "your api token here from @botfather"
    WEBHOOK_HOST = "your_host.com"
    WEBHOOK_PORT = 80
    WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}"
    WEBHOOK_URL_PATH = f"/{API_TOKEN}/"

    app_name = "Telegram Bot"
    app_version = "0.0.1"
    app_description = "A telegram bot for ip logger and deanonymization"
    app_author: str = "mazzz3r"
    app_author_email = "i@mazzz3r.ru"
