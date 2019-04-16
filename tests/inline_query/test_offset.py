"""Offset payload creation tests."""
from stickerfinder.models import InlineQuery
from stickerfinder.telegram.inline_query.context import Context
from stickerfinder.telegram.inline_query.offset import (
    get_next_offset,
    get_next_set_offset,
)


def test_extract_empty_offset(user):
    """Empyt offset should result in normal offset 0."""
    context = Context('test', ['test'], user)
    context.extract_info_from_offset('')

    assert context.inline_query_id is None
    assert context.offset == 0
    assert context.fuzzy_offset is None


def test_extract_strict_offset(user):
    """Extract data from an normal offset payload."""
    context = Context('test', ['test'], user)
    context.extract_info_from_offset('15235:50')

    assert context.inline_query_id == 15235
    assert context.offset == 50
    assert context.fuzzy_offset is None


def test_extract_fuzzy_offset(user):
    """Extract data from an fuzzy offset payload."""
    context = Context('test', ['test'], user)
    context.extract_info_from_offset('15235:100:0')

    assert context.inline_query_id == 15235
    assert context.offset == 100
    assert context.fuzzy_offset == 0


def test_get_next_strict_offset(user):
    """Create a new strict offset payload."""
    context = Context('test', ['test'], user)
    context.inline_query_id = 123
    context.offset = 50
    matching_stickers = range(0, 50)

    next_offset = get_next_offset(context, matching_stickers, [])
    assert next_offset == '123:100'


def test_get_strict_finished_offset(user):
    """Create an offset payload that signals that strict search is done."""
    context = Context('test', ['test'], user)
    context.inline_query_id = 123
    context.offset = 50
    matching_stickers = range(0, 10)

    next_offset = get_next_offset(context, matching_stickers, [])
    assert next_offset == '123:60:0'


def test_get_next_fuzzy_offset(user):
    """Create a new fuzzy offset payload."""
    context = Context('test', ['test'], user)
    context.inline_query_id = 123
    context.offset = 60
    matching_stickers = []

    context.fuzzy_offset = 50
    fuzzy_matching_stickers = range(0, 50)

    next_offset = get_next_offset(context, matching_stickers, fuzzy_matching_stickers)
    assert next_offset == '123:60:100'


def test_done_offset(user):
    """Create a new fuzzy offset payload."""
    context = Context('test', ['test'], user)
    context.inline_query_id = 123
    context.offset = 50
    matching_stickers = []

    context.fuzzy_offset = 50
    fuzzy_matching_stickers = range(0, 30)

    next_offset = get_next_offset(context, matching_stickers, fuzzy_matching_stickers)
    assert next_offset == 'done'


def test_get_next_set_offset(user):
    """Create a new set offset payload."""
    context = Context('test', ['test'], user)
    context.inline_query_id = 123
    context.offset = 0
    matching_sets = range(0, 8)

    next_offset = get_next_set_offset(context, matching_sets)

    assert next_offset == '123:8'


def test_done_set_offset(user):
    """Create a new set offset payload."""
    context = Context('test', ['test'], user)
    context.offset = 5
    context.inline_query_id = 123

    matching_set = range(0, 4)
    next_offset = get_next_set_offset(context, matching_set)

    assert next_offset == 'done'
