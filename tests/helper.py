"""Module for testing helper functions."""


def assert_sticker_contains_tags(sticker, tags):
    """Check whether the given list of tags exists on the sticker."""
    existing_tags = set([tag.name for tag in sticker.tags])

    assert len(tags) == len(existing_tags)
    assert len(set(tags) - existing_tags) == 0
