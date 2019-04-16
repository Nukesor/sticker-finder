"""Object representing a inline query search for easier parameter handling."""
from stickerfinder.helper.tag import get_tags_from_text


class Context():
    """Object representing a inline query search for easier parameter handling."""

    STICKER_MODE = 'sticker'
    STICKER_SET_MODE = 'sticker_set'
    FAVORITE_MODE = 'favorite'

    def __init__(self, query, offset_payload, user):
        """Create a new context instance."""
        self.query = query
        self.tags = get_tags_from_text(query, limit=10)
        self.user = user
        self.mode = Context.STICKER_MODE
        self.determine_special_search()

        self.inline_query_id = None
        self.offset = None
        self.fuzzy_offset = None
        self.extract_info_from_offset(offset_payload)

    def extract_info_from_offset(self, offset):
        """Extract all important information from the incoming offset payload."""
        # First incoming request, set the offset to 0
        if offset == '':
            self.offset = 0
        # Extract query_id, offset and possibly fuzzy_offset. They are sepparated by `:`
        else:
            splitted = offset.split(':')
            self.inline_query_id = int(splitted[0])
            self.offset = int(splitted[1])

            # It appears, we found all strictly matching stickers. Thereby we also got a fuzzy offset.
            if len(splitted) > 2:
                self.fuzzy_offset = int(splitted[2])

    def determine_special_search(self):
        """Check whether we should enter a special search mode."""
        # Handle special tags
        self.nsfw = 'nsfw' in self.tags
        self.furry = 'fur' in self.tags or 'furry' in self.tags

        # Switch to set mode
        if 'set' in self.tags or 'pack' in self.tags:
            self.mode = Context.STICKER_SET_MODE
            for tag in ['pack', 'set']:
                if tag in self.tags:
                    self.tags.remove(tag)
        elif len(self.tags) == 0:
            self.mode = Context.FAVORITE_MODE
