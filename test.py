#!/usr/bin/env python
"""Small helper script for debugging stuff."""

from stickerfinder.db import get_session
from stickerfinder.helper.plot import get_user_activity


session = get_session()
image = get_user_activity(session)
