"""Test inline query logic with sticker usages."""
from tests.factories import user_factory

from stickerfinder.models import Sticker, StickerUsage
from stickerfinder.telegram.inline_query.context import Context
from stickerfinder.telegram.inline_query.search import get_matching_stickers


def test_normal_search_with_single_usage(session, strict_inline_search, user):
    """Test correct score calculation for sticker set titles with a single sticker usage."""
    # Simple search which should get nearly all stickers from both sets
    context = Context('awesome', '', user)

    used_sticker = session.query(Sticker).get('sticker_00')
    assert used_sticker is not None

    sticker_usage = StickerUsage(user, used_sticker)
    sticker_usage.usage_count = 1
    session.add(sticker_usage)
    session.commit()

    matching_stickers, fuzzy_matching_stickers, duration = get_matching_stickers(session, context)
    assert len(matching_stickers) == 40
    assert len(fuzzy_matching_stickers) == 0

    for i, result in enumerate(matching_stickers):
        if i == 0:
            assert result[0] == 'sticker_00'
            assert result[1] == 1.0
            assert result[2] == 'z_mega_awesome'
        else:
            # Also do this little workaround to prevent fucky number sorting here as well
            if i < 10:
                i = f'0{i}'
            assert result[0] == f'sticker_{i}'
            assert result[1] == 0.75
            assert result[2] == 'z_mega_awesome'


def test_search_with_usage_from_another_user(session, strict_inline_search, user):
    """Test correct score calculation for sticker set titles with a single sticker usage."""
    # Simple search which should get nearly all stickers from both sets
    context = Context('awesome', '', user)
    other_user = user_factory(session, 100, 'other_user')

    used_sticker = session.query(Sticker).get('sticker_00')
    assert used_sticker is not None

    sticker_usage = StickerUsage(other_user, used_sticker)
    sticker_usage.usage_count = 1
    session.add(sticker_usage)
    session.commit()

    matching_stickers, fuzzy_matching_stickers, duration = get_matching_stickers(session, context)
    assert len(matching_stickers) == 40
    assert len(fuzzy_matching_stickers) == 0

    for i, result in enumerate(matching_stickers):
        # Also do this little workaround to prevent fucky number sorting here as well
        if i < 10:
            i = f'0{i}'
        assert result[0] == f'sticker_{i}'
        assert result[1] == 0.75
        assert result[2] == 'z_mega_awesome'
