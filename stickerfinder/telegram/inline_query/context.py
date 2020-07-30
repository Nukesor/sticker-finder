"""Object representing a inline query search for easier parameter handling."""
from stickerfinder.helper.tag import get_tags_from_text


class Context:
    """Object representing a inline query search for easier parameter handling."""

    STICKER_MODE = "sticker"
    STICKER_SET_MODE = "sticker_set"
    FAVORITE_MODE = "favorite"

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

        self.switched_to_fuzzy = False
        self.limit = None

    def __str__(self):
        """Debug string for class."""
        text = f"Context: {self.query}, {self.mode}"
        text += f"\nTags {self.tags}"
        text += f"\nOffsets: {self.offset}, {self.fuzzy_offset}"
        text += f"\nanimated, nsfw, furry: {self.animated}, {self.nsfw}, {self.furry}"
        return text

    def extract_info_from_offset(self, offset):
        """Extract all important information from the incoming offset payload."""
        # First incoming request, set the offset to 0
        if offset == "":
            self.offset = 0
        # Extract query_id, offset and possibly fuzzy_offset. They are sepparated by `:`
        else:
            splitted = offset.split(":")
            self.inline_query_id = int(splitted[0])
            self.offset = int(splitted[1])

            # It appears, we found all strictly matching stickers. Thereby we also got a fuzzy offset.
            if len(splitted) > 2:
                self.fuzzy_offset = int(splitted[2])

    def determine_special_search(self):
        """Check whether we should enter a special search mode."""
        # Handle animated mode
        self.nsfw = "ani" in self.tags or "animated" in self.tags
        # Handle nsfw mode
        self.nsfw = "nsfw" in self.tags
        # Handle furry mode
        self.furry = "fur" in self.tags or "furry" in self.tags

        # Switch to set mode
        if "set" in self.tags or "pack" in self.tags:
            self.mode = Context.STICKER_SET_MODE

        # Clean tags from special keywords
        keywords = ["pack", "set", "furry", "fur", "nsfw", "ani", "animated"]
        self.tags = [tag for tag in self.tags if tag not in keywords]

        # Check whether we should enter favorite mode
        if len(self.tags) == 0:
            self.mode = Context.FAVORITE_MODE

    def switch_to_fuzzy(self, limit):
        """We didn't get enough strict results and switched to fuzzy search."""
        self.switched_to_fuzzy = True
        self.fuzzy_offset = 0
        self.limit = limit
