"""Config values for stickerfinder."""
import logging
from datetime import timedelta


class Config:
    """Config class for convenient configuration."""

    # Get your telegram api-key from @botfather
    TELEGRAM_API_KEY = None
    SQL_URI = 'sqlite:///stickerfinder.db'
    SENTRY_TOKEN = None
    LOG_LEVEL = logging.INFO
    # Username of the admin
    ADMIN = 'Nukesor'
    # Run maintenance jobs. This is important if you want to run multiple instances of the bot
    RUN_JOBS = True
    # Only important if running multiple instances ( for logging )
    BOT_NAME = 'stickerfinder'

    # Use and configure nginx webhooks
    WEB_HOOK = False
    DOMAIN = 'https://example.com'
    TOKEN = 'token'
    CERT_PATH = './cert.pem'
    PORT = 5000

    # Performance/thread/db settings
    WORKER_COUNT = 16
    CONNECTION_COUNT = 20
    OVERFLOW_COUNT = 10

    # Job parameter
    USER_CHECK_INTERVAL = timedelta(days=1)
    USER_CHECK_RECHECK_INTERVAL = timedelta(days=2)
    USER_CHECK_COUNT = 200
    VOTE_BAN_COUNT = 1


config = Config()
