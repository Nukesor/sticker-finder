"""Config values for stickerfinder."""


class Config:
    """Config class for convenient configuration."""

    # Get your telegram api-key from @botfather
    TELEGRAM_API_KEY = None
    SQL_URI = 'sqlite:///stickerfinder.db'
    SENTRY_TOKEN = None


config = Config()
