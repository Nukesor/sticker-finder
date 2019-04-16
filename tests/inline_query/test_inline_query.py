"""Test inline query logic."""
import pytest

from stickerfinder.telegram.inline_query.context import Context
from stickerfinder.telegram.inline_query.search import (
    get_matching_stickers,
    get_matching_sticker_sets,
)


@pytest.mark.parametrize('query,first_score, second_score',
                         [('testtag', 1, 1),
                          ('awesome dumb', 0.75, 0.75),
                          ('testtag roflcopter', 2.00, 1.00),
                          ('awesome dumb testtag roflcopter', 2.75, 1.75),
                          ('awesome testtag roflcopter', 2.00, 1.75)])
def test_strict_sticker_search_set_order(session, strict_inline_search, user,
                                         query, first_score, second_score):
    """Test correct sticker set sorting order."""
    # Simple search which should get nearly all stickers from both sets
    context = Context(query, '', user)
    matching_stickers, fuzzy_matching_stickers, duration = get_matching_stickers(session, context)
    assert len(matching_stickers) == 50
    assert len(fuzzy_matching_stickers) == 0
    for i, result in enumerate(matching_stickers):
        # The stickers are firstly sorted by:
        # 1. score
        # 2. StickerSet.name
        # 3. Sticker.file_id
        #
        # Thereby we expect the `a_dumb_shit` set first (20 results), since the scores are the same
        # for both sets, but this set's name is higher in order.
        if i <= 20:
            assert result[0] == f'sticker_{i+40}'
            assert result[1] == first_score
            assert result[2] == 'a_dumb_shit'
        # Next we get the second set in order of the file_ids
        elif i > 20:
            # We need to subtract 21, since we now start to count file_ids from 0
            i = i-21
            # Also do this little workaround to prevent fucky number sorting here as well
            if i < 10:
                i = f'0{i}'
            assert result[0] == f'sticker_{i}'
            assert result[1] == second_score
            assert result[2] == 'z_mega_awesome'


def test_strict_sticker_search_set_score(session, strict_inline_search, user):
    """Test correct score calculation for sticker set titles."""
    # Simple search which should get nearly all stickers from both sets
    context = Context('awesome', '', user)
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


@pytest.mark.parametrize('query,score',
                         [('unique_oter', 0.67),
                          ('mega_awesme', 0.59)])
def test_fuzzy_sticker_search(session, strict_inline_search, user, query, score):
    """Test fuzzy search for stickers."""
    context = Context(query, '123:60:0', user)
    matching_stickers, fuzzy_matching_stickers, duration = get_matching_stickers(session, context)
    assert len(fuzzy_matching_stickers) == 40
    assert len(matching_stickers) == 0
    for i, result in enumerate(fuzzy_matching_stickers):
        # Also do this little workaround to prevent fucky number sorting here as well
        if i < 10:
            i = f'0{i}'
        assert result[0] == f'sticker_{i}'
        assert round(result[1], 2) == score

    # Make sure we instantly search for fuzzy stickers, if no normal stickers can be found on the first run
    context = Context(query, '', user)
    matching_stickers, fuzzy_matching_stickers, duration = get_matching_stickers(session, context)
    assert len(matching_stickers) == 0
    assert len(fuzzy_matching_stickers) == 40

    # Make sure we instantly search for fuzzy stickers, if no normal stickers can be found on a normal offset
    context = Context(query, '123:50', user)
    matching_stickers, fuzzy_matching_stickers, duration = get_matching_stickers(session, context)
    assert len(matching_stickers) == 0
    assert len(fuzzy_matching_stickers) == 40


def test_combined_sticker_search(session, strict_inline_search, user):
    """Test fuzzy search for stickers."""
    context = Context('roflcpter unique_other', '', user)
    matching_stickers, fuzzy_matching_stickers, duration = get_matching_stickers(session, context)
    assert len(matching_stickers) == 40
    assert len(fuzzy_matching_stickers) == 10

    for i, result in enumerate(matching_stickers):
        # Also do this little workaround to prevent fucky number sorting here as well
        if i < 10:
            i = f'0{i}'
        assert result[0] == f'sticker_{i}'
        assert round(result[1], 2) == 1

    for i, result in enumerate(fuzzy_matching_stickers):
        i += 40
        assert result[0] == f'sticker_{i}'
        assert round(result[1], 2) == 0.80
