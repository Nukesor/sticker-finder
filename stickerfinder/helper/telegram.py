"""All helper for interaction with telegram."""
import time
import logging
import telegram
from raven import breadcrumbs
from random import randrange

from stickerfinder.sentry import sentry


def call_tg_func(tg_object: object, function_name: str,
                 args: list = None, kwargs: dict = None):
    """Call a tg object member function.

    We need to handle those calls in case we get rate limited.
    """
    _try = 0
    tries = 5
    exception = None
    while _try < tries:
        try:
            args = args if args else []
            kwargs = kwargs if kwargs else {}
            retrieved_object = getattr(tg_object, function_name)(*args, **kwargs)
            return retrieved_object

        except telegram.error.BadRequest as e:
            if e.message == 'Chat not found':
                if _try == 0:
                    sentry.captureMessage('First try: Chat not found.', level='info')
                elif _try == 1:
                    sentry.captureMessage('Second try: Chat not found.', level='info')
                elif _try == 2:
                    sentry.captureMessage('Third try: Chat not found.', level='info')
                elif _try == 3:
                    sentry.captureMessage('Forth try: Chat not found.', level='info')
                elif _try == 4:
                    sentry.captureMessage('Fifth try: Chat not found.', level='info')
                time.sleep(1)
            else:
                raise e

            exception = e
            _try += 1
        except telegram.error.TimedOut as e:
            sleep_time = randrange(2, 5)
            logger = logging.getLogger()
            logger.info(f'Hit socket timeout waiting {sleep_time} secs.')
            time.sleep(sleep_time)
            breadcrumbs.record(data={'action': 'Socket timeout hit'}, category='info')

            time.sleep(sleep_time)
            _try += 1

            exception = e
            pass

    raise exception
