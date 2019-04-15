"""Check the tag from text extraction logic."""
from stickerfinder.helper.tag import get_tags_from_text


def test_ignore_telegramme_links():
    """Ignore accidentally tagging with pack link, when choosing a telegram sticker pack from search."""
    tag_text = 'https://telegram.me/addstickers/cheloidesmemestash3'

    assert len(get_tags_from_text(tag_text)) == 0
