"""Test inline query logic."""
from tests.factories import sticker_set_factory, sticker_factory


def test_strict_inline_query(session):
    """Add new tags to a sticker."""
    stickers = []
    for i in range(0, 40):
        stickers.append(sticker_factory(session, f'sticker_{i}', ['testtag']))

    sticker_set = sticker_set_factory(session, 'cool_megaawesome_pack lol', stickers)
