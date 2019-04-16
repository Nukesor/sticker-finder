"""Object representing a inline query search for easier parameter handling."""


class Context():
    """Object representing a inline query search for easier parameter handling."""

    STRICT_MODE = 'strict'
    FUZZY_MODE = 'fuzzy'
    SET_MODE = 'set'

    def __init__(self, query, tags, user):
        """Create a new context instance."""
        self.query = query
        self.tags = tags
        self.user = user
        self.determine_special_search(tags)

        self.mode = None
        self.inline_query_id = None

        self.offset = None
        self.fuzzy_offset = None

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

    def determine_special_search(self, tags):
        """Check whether we should enter a special search mode."""
        # Handle special tags
        self.nsfw = 'nsfw' in tags
        self.furry = 'fur' in tags or 'furry' in tags

        # Switch to set mode
        if 'set' in tags or 'pack' in tags:
            self.mode = Context.SET_MODE
