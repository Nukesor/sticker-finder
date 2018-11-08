"""All helper for interaction with telegram."""
import time
import logging
from raven import breadcrumbs
from random import randrange
from telegram.error import TimedOut, NetworkError, BadRequest


def call_tg_func(tg_object: object, function_name: str,
                 args: list = None, kwargs: dict = None):
    """Call a tg object member function.

    We need to handle those calls in case we get rate limited.
    """
    _try = 0
    tries = 2
    exception = None
    while _try < tries:
        try:
            args = args if args else []
            kwargs = kwargs if kwargs else {}
            retrieved_object = getattr(tg_object, function_name)(*args, **kwargs)
            return retrieved_object

        except (TimedOut, NetworkError, BadRequest) as e:
            sleep_time = randrange(2, 5)
            logger = logging.getLogger()
            logger.info(f'Got exception waiting {sleep_time} secs.')
            time.sleep(sleep_time)
            breadcrumbs.record(data={'action': 'Socket timeout hit'}, category='info')

            time.sleep(sleep_time)
            _try += 1

            exception = e
            pass

    raise exception
