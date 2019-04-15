"""Telegram bot error handling."""
import traceback
from telegram.error import (
    BadRequest,
    NetworkError,
    TimedOut,
    Unauthorized,
)

from stickerfinder.sentry import sentry


def error_callback(update, context):
    """Handle generic errors from telegram."""
    try:
        raise context.error
    except (TimedOut, NetworkError):
        pass
    except BadRequest as e:
        # An update for a reply keyboard has failed
        # (probably due to button spam since the message already has been updated)
        if 'Message is not modified' in str(e): # noqa
            return
        # It took to long to send the inline query response.
        # Probably due to slow network on client side.
        elif str(e) == 'Query_id_invalid': # noqa
            return

        traceback.print_exc()
        sentry.captureException()
    # A user banned the bot Just ignore this.
    # This probably happens due to sending a message during maintenance work
    except Unauthorized:
        pass

    except BaseException:
        traceback.print_exc()
        sentry.captureException()
