"""Test fuzzy inline query logic."""
import pytest

from stickerfinder.telegram.inline_query.context import Context
from stickerfinder.telegram.inline_query.search import get_matching_stickers


def test_combined_sticker_search(session, tg_context, strict_inline_search, user):
    """Test whether combined search of fuzzy and strict search works."""
    context = Context(tg_context, "roflcpter unique-other", "", user)
    matching_stickers, fuzzy_matching_stickers, duration = get_matching_stickers(
        session, context
    )
    # Context properties have been properly set
    assert context.switched_to_fuzzy
    assert context.limit == 10
    assert context.fuzzy_offset == 0

    # Sticker result counts are correct
    assert len(matching_stickers) == 40
    assert len(fuzzy_matching_stickers) == 10

    for i, result in enumerate(matching_stickers):
        # Also do this little workaround to prevent fucky number sorting here as well
        print(result)
        if i < 10:
            i = f"0{i}"
        assert result[1] == f"sticker_{i}"
        assert round(result[4], 2) == 1

    for i, result in enumerate(fuzzy_matching_stickers):
        i += 40
        assert result[1] == f"sticker_{i}"
        assert round(result[4], 2) == 0.62


@pytest.mark.parametrize("query,score", [("unique-oter", 0.67), ("mega-awesme", 0.59)])
def test_fuzzy_sticker_search(
    session, tg_context, strict_inline_search, user, query, score
):
    """Test fuzzy search for stickers."""
    context = Context(tg_context, query, "123:60:0", user)
    matching_stickers, fuzzy_matching_stickers, duration = get_matching_stickers(
        session, context
    )
    assert len(fuzzy_matching_stickers) == 40
    assert len(matching_stickers) == 0
    for i, result in enumerate(fuzzy_matching_stickers):
        # Also do this little workaround to prevent fucky number sorting here as well
        if i < 10:
            i = f"0{i}"
        assert result[1] == f"sticker_{i}"
        assert round(result[4], 2) == score

    # Make sure we instantly search for fuzzy stickers, if no normal stickers can be found on the first run
    context = Context(tg_context, query, "", user)
    matching_stickers, fuzzy_matching_stickers, duration = get_matching_stickers(
        session, context
    )
    assert len(matching_stickers) == 0
    assert len(fuzzy_matching_stickers) == 40

    # Make sure we instantly search for fuzzy stickers, if no normal stickers can be found on a normal offset
    context = Context(tg_context, query, "123:50", user)
    matching_stickers, fuzzy_matching_stickers, duration = get_matching_stickers(
        session, context
    )
    assert len(matching_stickers) == 0
    assert len(fuzzy_matching_stickers) == 40


@pytest.mark.parametrize("query, score", [("longstrin", 0.75), ("/longstrin", 0.75)])
def test_similar_fuzzy_tags_search(
    session, tg_context, fuzzy_inline_search, user, query, score
):
    """Test fuzzy search for stickers with similar tags.

    This test is here to ensure that stickers won't show up multiple times in search,
    if there are multiple tags on the sticker that match to a single search word.
    """
    context = Context(tg_context, query, "123:0:0", user)
    matching_stickers, fuzzy_matching_stickers, duration = get_matching_stickers(
        session, context
    )

    assert len(fuzzy_matching_stickers) == 20
    assert len(matching_stickers) == 0

    for i, result in enumerate(fuzzy_matching_stickers):
        # Also do this little workaround to prevent fucky number sorting here as well
        if i < 10:
            i = f"0{i}"
        assert result[1] == f"sticker_{i}"
        assert round(result[4], 2) == score
