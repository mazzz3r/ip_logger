# IP Logger & Deanonymization Tool

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Flask](https://img.shields.io/badge/flask-3.1.0-red.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.38-blue.svg)

A powerful IP logging and deanonymization tool with Telegram bot integration. This application allows you to create personalized tracking links that collect detailed information about visitors, including IP address, geolocation, browser details, device information, and more.


## 🔍 How It Works

1. Create a tracking link using the Telegram bot
2. Share the link with your target
3. When the target visits the link, the application collects information about them
4. The collected information is sent to you via Telegram in a single, updated message
5. The target is redirected to your specified URL
6. View statistics about your visitors using the Telegram bot

## 🔒 Privacy & Legal Considerations

This tool is intended for educational purposes only. Please ensure you comply with all applicable laws and regulations regarding data collection and privacy when using this application. Always obtain proper consent before collecting information about individuals.


## 🚀 Features

- **Personalized Tracking Links**: Create custom links for tracking visitors
- **Telegram Bot Integration**: Receive real-time notifications via Telegram
- **Comprehensive Data Collection**:
  - IP address and geolocation (country, region, city)
  - Browser and platform details (using modern APIs)
  - Screen resolution
  - Battery status (charging percentage, charging status)
  - VPN/Proxy detection
  - AdBlock detection
  - Device memory and CPU cores
  - WebGL information
  - Canvas fingerprint
  - Connection type
  - Language and timezone
- **Custom Redirects**: Set custom redirect URLs for your tracking links
- **User Management**: Manage multiple tracking links through the Telegram bot
- **Statistics**: View visitor statistics through the Telegram bot
- **Persistent Storage**: All logs are stored in a database (SQLite for development, PostgreSQL for production)
- **Comprehensive Logging System**: Detailed logging for debugging, monitoring, and troubleshooting


## 📋 Requirements

- Python 3.11+
- Flask 3.1.0
- PyTelegramBotAPI 4.26.0
- SQLAlchemy 2.0.38
- Pydantic 2.10.6
- Flask-Limiter 3.3.0
- PostgreSQL (for production)
- Other dependencies listed in `requirements.txt`

## 🔧 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mazzz3r/logger.git
   cd logger
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables (or create a `.env` file based on `.env.example`):
   ```bash
   export API_TOKEN="your_telegram_bot_token"
   export WEBHOOK_HOST="your_webhook_host"
   export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
   export ADMIN_ID="your_telegram_user_id"
   ```

4. Run the application:
   ```bash
   gunicorn app.main:app
   ```

## 🤖 Telegram Bot Commands

- `/start` - Start the bot
- `/help` - Show available commands
- `/get_link` - Get your personalized tracking link
- `/set_address <ADDRESS>` - Set a custom address for your tracking link
- `/set_redirect <URL>` - Set a custom redirect URL for your tracking link
- `/get_info` - Get information about your current settings
- `/get_stats` - Get statistics about your logger
- `/users_count` - (Admin only) Get the total number of users

## 📊 Logging System

The application includes a comprehensive logging system that provides detailed information about the application's operation. Logs are stored in the `logs` directory and are rotated to prevent excessive disk usage.

### Log Files

- **app.log**: General application logs
- **flask.log**: Flask-specific logs
- **bot.log**: Telegram bot logs
- **db.log**: Database operation logs
- **requests.log**: HTTP request logs
- **error.log**: Error logs
- **critical.log**: Critical error logs
- **ip_logger.log**: IP logger-specific logs

### Log Levels

You can configure the log level using the `LOG_LEVEL` environment variable:

- **DEBUG**: Detailed debugging information
- **INFO**: General information about the application's operation (default)
- **WARNING**: Warnings about potential issues
- **ERROR**: Error information
- **CRITICAL**: Critical errors that may cause the application to fail

## 🏗️ Project Structure

```
logger/
├── app/
│   ├── bot/
│   │   ├── bot.py           # Telegram bot implementation
│   │   ├── middlewares.py   # Bot middlewares
│   │   └── __init__.py
│   ├── database/
│   │   ├── logs/            # Log management
│   │   │   ├── crud.py      # Log database operations
│   │   ├── users/           # User management
│   │   │   ├── crud.py      # User database operations
│   │   │   └── schemas.py   # User data models
│   │   ├── models.py        # SQLAlchemy models
│   │   └── __init__.py
│   ├── logger/
│   │   ├── logger.py        # Logger implementation
│   │   ├── utilities.py     # Helper functions
│   │   └── __init__.py
│   ├── utils/
│   │   ├── logging_config.py # Logging configuration
│   │   └── __init__.py
│   ├── config.py            # Application configuration
│   ├── main.py              # Flask application setup
│   └── __init__.py
├── logs/                    # Application logs
├── static/
│   └── js/                  # Client-side JavaScript
│       ├── index.js
│       ├── index1.js
│       └── index2.js
├── templates/
│   └── index.html           # HTML template
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── .env.example             # Example environment variables
├── .dockerignore            # Docker ignore file
├── .gitignore               # Git ignore file
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```


## 👨‍💻 Author

- **mazzz3r** - [GitHub](https://github.com/mazzz3r)
- Email: i@mazzz3r.ru

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.