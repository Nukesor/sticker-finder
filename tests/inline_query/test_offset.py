"""Offset payload creation tests."""
from stickerfinder.models import InlineQuery
from stickerfinder.telegram.inline_query import extract_info_from_offset, get_next_offset


def test_empty_offset():
    """Empyt offset should result in normal offset 0."""
    offset, fuzzy_offset, query_id = extract_info_from_offset('')
    assert query_id is None
    assert offset == 0
    assert fuzzy_offset is None


def test_strict_offset():
    """Extract data from an normal offset payload."""
    offset, fuzzy_offset, query_id = extract_info_from_offset('15235:50')
    assert query_id == 15235
    assert offset == 50
    assert fuzzy_offset is None


def test_fuzzy_offset():
    """Extract data from an fuzzy offset payload."""
    offset, fuzzy_offset, query_id = extract_info_from_offset('15235:100:0')
    assert query_id == 15235
    assert offset == 100
    assert fuzzy_offset == 0


def test_get_next_strict_offset(user):
    """Create a new strict offset payload."""
    inline_query = InlineQuery('test', user)
    inline_query.id = 123
    offset = 50
    matching_stickers = range(0, 50)

    next_offset = get_next_offset(inline_query, matching_stickers, offset, [], None)
    assert next_offset == '123:100'


def test_get_strict_finished_offset(user):
    """Create an offset payload that signals that strict search is done."""
    inline_query = InlineQuery('test', user)
    inline_query.id = 123
    offset = 50
    matching_stickers = range(0, 10)

    next_offset = get_next_offset(inline_query, matching_stickers, offset, [], None)
    assert next_offset == '123:60:0'


def test_get_next_fuzzy_offset(user):
    """Create a new fuzzy offset payload."""
    inline_query = InlineQuery('test', user)
    inline_query.id = 123
    offset = 60
    matching_stickers = []

    fuzzy_matching_stickers = range(0, 50)
    fuzzy_offset = 50

    next_offset = get_next_offset(inline_query, matching_stickers, offset, fuzzy_matching_stickers, fuzzy_offset)
    assert next_offset == '123:60:100'


def test_done_offset(user):
    """Create a new fuzzy offset payload."""
    inline_query = InlineQuery('test', user)
    inline_query.id = 123
    offset = 50
    matching_stickers = []

    fuzzy_matching_stickers = range(0, 30)
    fuzzy_offset = 50

    next_offset = get_next_offset(inline_query, matching_stickers, offset, fuzzy_matching_stickers, fuzzy_offset)
    assert next_offset == 'done'
