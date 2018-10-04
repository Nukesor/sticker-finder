"""Config values for stickerfinder."""


class Config:
    """Config class for convenient configuration."""

    # Get your telegram api-key from @botfather
    TELEGRAM_API_KEY = None
    SQL_URI = 'sqlite:///stickerfinder.db'
    SENTRY_TOKEN = None
    # Username of the admin
    ADMIN = 'Nukesor'
    # Run maintenance jobs. This is important if you want to run multiple instances of the bot
    RUN_JOBS = True


config = Config()
