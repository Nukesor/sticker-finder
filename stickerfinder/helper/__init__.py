"""Some static stuff or helper functions for sticker finder bot."""


tag_format = """Your tag messages should be formatted like this:
tag1, tag2, tag3, tag4
The text inside the sticker.

or if you don't want to add text simply write:
tag1, tag2, tag3, tag4
"""

help_text = f"""To search for stickers just start typing @std_bot and you can now search for stickers by keywords or emojis.
I'll try to give you the best match depending on your keywords and emojis.

You can add sticker sets by simply sending any sticker of the set to me in a direct conversation.
If I'm added to a group chat, I will automatically add all stickers posted in this chat!

If you already added a set, but can't find any sticker from it, you probably need to tag them first (or search by the set name).
To tag a whole set send me the /tag_set command and a sticker from the set you want to tag.
If you want to skip a sticker during the tagging process just type /next.

The /tag command also allows to tag the last sticker posted in a chat.
This is great for ad hoc tagging of single stickers in group chats, but I need to be in this chat for this functionality to work.

I also try to detect text in stickers, but this turns out to be quite ambitious.
Don't expect this functionality to work reliably!

If you want to help the project and tag some stickers, just type /tag_random in a direct conversation with me :).

{tag_format}

In case you encounter any bugs or you just want to look at the code and drop a star:
https://github.com/Nukesor/stickerfinder
"""

tag_text = f"""Now please send tags and text for each sticker I'll send you.
If you don't want to edit a sticker, just send /next.
{tag_format}
"""
