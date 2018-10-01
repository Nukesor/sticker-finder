"""Some static stuff or helper functions for sticker finder bot."""


tag_format = """Your tag messages should be formatted like this:

tag1, tag2, tag3, tag4
Some random text maybe what's inside the sticker.

or if you don't want to add text simply write:

tag1, tag2, tag3, tag4
"""

help_text = """To search for stickers just start typing '@std_bot' and you can now search for stickers by key words or emojis.
Stickerfinder tries to give you the best match depending on your key words.

You can add sticker sets by simply sending any sticker of the set to me in a direct conversation.

If you already added a set, but can't find any sticker from it, you probably need to tag them first.
To tag a whole set send me the /tag_set command and a sticker from the set you want to tag.
If you want to skip a sticker during the tagging process send me the /next command.

The /tag command allows to tag the last sticker posted in a channel.
This is great ad hoc tagging of single stickers in group channels, but I need to be added to this chat for this functionality to work.

Stickerbot tries to detect text in stickers, but this turns out to be more difficult than expected.
Thereby don't expect this functionality to work reliably.

{tag_format}


If you encounter any bugs or if you just want to look at the code and drop a star:
https://github.com/Nukesor/stickerfinder
"""

tag_text = f"""Now please send tags and text for each sticker I'll send you.
If you don't want to edit a sticker, just send /next.
{tag_format}
"""
