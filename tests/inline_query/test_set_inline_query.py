"""Test inline query logic."""
from stickerfinder.telegram.inline_query.context import Context
from stickerfinder.telegram.inline_query.search import get_matching_sticker_sets


def test_strict_sticker_search_set_order(
    session, tg_context, strict_inline_search, user
):
    """Test correct sticker set sorting order."""
    # Simple search which should get nearly all stickers from both sets
    context = Context(tg_context, "testtag set", "", user)
    assert context.mode == Context.STICKER_SET_MODE

    matching_sets, duration = get_matching_sticker_sets(session, context)
    assert len(matching_sets) == 2

    first_set = matching_sets[0]
    assert first_set[0].name == "z_mega_awesome"
    assert first_set[1] == 40

    second_set = matching_sets[1]
    assert second_set[0].name == "a_dumb_shit"
    assert second_set[1] == 20
