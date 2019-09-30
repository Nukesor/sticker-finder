"""Factories for creating new databse objects."""
from stickerfinder.models import User, Sticker, StickerSet, Tag


def user_factory(session, user_id, name, admin=False):
    """Create a user."""
    user = User(user_id, name)
    user.admin = admin
    session.add(user)
    session.commit()

    return user


def sticker_set_factory(session, name, stickers=None, tags=None):
    """Create a new sticker set."""
    sticker_set = StickerSet(name, [])
    sticker_set.complete = True
    sticker_set.reviewed = True
    if stickers:
        sticker_set.stickers = stickers

    session.add(sticker_set)
    session.commit()

    return sticker_set


def sticker_factory(session, file_id, tag_names=None, international=False):
    """Create a sticker and eventually add tags."""
    sticker = Sticker(file_id)
    if tag_names:
        for tag_name in tag_names:
            tag = Tag.get_or_create(session, tag_name, international, False)
            sticker.tags.append(tag)

    session.add(sticker)
    session.commit()
    return sticker
