"""Test emoji handling."""
from tests.helper import assert_sticker_contains_tags

from stickerfinder.models import Tag
from stickerfinder.helper.tag import tag_sticker, add_original_emojis


def test_original_emoji_stays_on_replace(session, user, sticker_set):
    """Original emojis will remain if tags are added in replace mode."""
    sticker = sticker_set.stickers[0]
    # Add an original emoji tag to the sticker
    tag = Tag('😲', True, True)
    sticker.tags.append(tag)
    sticker.original_emojis.append(tag)
    session.commit()

    # Now tag the sticker in replace mode
    tag_sticker(session, 'new_tag', sticker, user, replace=True)
    assert_sticker_contains_tags(sticker, ['new_tag', '😲'])
    assert len(sticker.tags) == 2
    assert sticker.original_emojis[0] in sticker.tags


def test_convert_tag_to_emoji(session, user, sticker_set):
    """Tags will be converted to emojis, if they appear in the original emojis."""
    sticker = sticker_set.stickers[0]
    # Add an original emoji tag to the sticker
    tag = Tag('😲', False, False)
    sticker.tags.append(tag)
    session.commit()

    assert not tag.emoji
    assert not tag.is_default_language

    # Now tag the sticker in replace mode
    add_original_emojis(session, sticker, '😲')
    session.commit()

    assert tag.emoji
    assert tag.is_default_language
    assert len(sticker.tags) == 1
    assert sticker.original_emojis[0] in sticker.tags
