"""Test the normal tagging process."""
from tests.helper import assert_sticker_contains_tags

from stickerfinder.models import Tag
from stickerfinder.helper.tag import tag_sticker


def test_add_tags(session, user, sticker_set):
    """Add new tags to a sticker."""
    for sticker in sticker_set.stickers:
        # Create a new tag for each sticker
        tag_sticker(session, f'tag_{sticker.file_id}', sticker, user)

    session.commit()

    # Ensure that the mallicious user actually replaced the tag
    for sticker in sticker_set.stickers:
        assert sticker.tags[0].name == f'tag_{sticker.file_id}'

    # User got a new change
    assert len(user.changes) == len(sticker_set.stickers)

    for sticker in sticker_set.stickers:
        # Create a new tag for each sticker
        tag_sticker(session, f'tag_2_{sticker.file_id}', sticker, user)

    session.commit()

    # Ensure that the mallicious user actually replaced the tag
    for sticker in sticker_set.stickers:
        assert_sticker_contains_tags(sticker, [f'tag_{sticker.file_id}', f'tag_2_{sticker.file_id}'])
    assert len(user.changes) == len(sticker_set.stickers) * 2


def test_replace_sticker_tags(session, user, sticker_set, tags):
    """Replace tags of a sticker."""
    for sticker in sticker_set.stickers:
        # Replace the existing tag
        tag_sticker(session, f'new_tag_{sticker.file_id}', sticker, user, replace=True)

    session.commit()

    # Ensure the tag has been replaced
    for sticker in sticker_set.stickers:
        assert len(sticker.tags) == 1
        assert sticker.tags[0].name == f'new_tag_{sticker.file_id}'

    assert len(user.changes) == len(sticker_set.stickers) * 2


def test_add_duplicate_sticker_tags_in_other_language(session, user, sticker_set):
    """Add the same tag to a sticker, but in different languages.

    The tag should be converted from not_default to default,
    if somebody tags in default, but not the other way around.
    """
    # User should tag in not default language first
    user.is_default_language = False
    sticker = sticker_set.stickers[0]
    tag_sticker(session, 'language_test_tag', sticker, user, replace=True)

    session.commit()

    tag = session.query(Tag).get('language_test_tag')
    assert not tag.is_default_language

    # Add same tag to sticker, but this time in default language
    user.is_default_language = True
    tag_sticker(session, 'language_test_tag', sticker, user, replace=True)

    assert tag.is_default_language
    assert len(user.changes) == 1

    # Now tag in the not default language again. This shouldn't change anything now
    user.is_default_language = False
    tag_sticker(session, 'language_test_tag', sticker, user, replace=True)

    assert tag.is_default_language
    assert len(user.changes) == 1
