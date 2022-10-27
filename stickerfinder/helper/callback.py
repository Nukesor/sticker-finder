from stickerfinder.enum import CallbackResult, CallbackType


def build_data(name, payload="", action=0):
    """Callback to easily build callback payloads."""
    callback_type = CallbackType[name].value
    if action != 0:
        try:
            action = CallbackResult[action].value
        except KeyError:
            action = action
    return f"{callback_type}:{payload}:{action}"


def build_set_data(name, sticker_set, action=0):
    """Callback to easily build callback payloads for sticker sets."""
    callback_type = CallbackType[name].value
    if action != 0:
        try:
            action = CallbackResult[action].value
        except KeyError:
            action = action

    return f"{callback_type}:{sticker_set.name}:{action}"


def build_user_data(name, user, action=0):
    """Callback to easily build callback payloads for users."""
    callback_type = CallbackType[name].value
    if action != 0:
        action = CallbackResult[action].value
    return f"{callback_type}:{user.id}:{action}"
