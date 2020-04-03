"""Other context testing."""
from stickerfinder.telegram.inline_query.context import Context


def test_default_context_search(user):
    """A simple normal search should result in default values on the context object."""
    context = Context("test", "", user)

    assert context.mode == Context.STICKER_MODE
    assert context.nsfw is False
    assert context.furry is False


def test_favorite_search(user):
    """A simple normal search should result in default values on the context object."""
    context = Context("", "", user)
    assert context.mode == Context.FAVORITE_MODE


def test_special_flag_search(user):
    """A search with special keywords should result in a special search."""
    context = Context("nsfw fur furry test", "", user)

    assert context.mode == Context.STICKER_MODE
    assert context.nsfw is True
    assert context.furry is True

    assert len(context.tags) == 1
    assert context.tags[0] == "test"


def test_special_flag_favorite_search(user):
    """A special search without any additional keywords results in a favorite search."""
    context = Context("nsfw fur furry", "", user)

    assert context.mode == Context.FAVORITE_MODE
    assert context.nsfw is True
    assert context.furry is True

    assert len(context.tags) == 0


def test_sticker_set_search(user):
    """A simple normal search should result in default values on the context object."""
    context = Context("set pack test", "", user)

    assert context.mode == Context.STICKER_SET_MODE
    assert len(context.tags) == 1
    assert context.tags[0] == "test"
