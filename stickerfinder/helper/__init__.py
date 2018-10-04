"""Some static stuff or helper functions for sticker finder bot."""


help_text = f"""To search for stickers just start typing @std_bot in any chat. You can search for stickers by keywords, emojis and stickerset titles.
I'll try to give you the best match depending on your search query :).

You can add stickersets by simply sending any sticker of the set to me in a direct conversation.
If I'm added to a group chat, I will automatically add all stickers posted in this chat!

If you already added a set, but can't find any sticker from it, you probably need to tag them first (or just search by the set name).
To tag a whole set send me the /tag_set command and a sticker from the set you want to tag.

The /tag command also allows to tag the last sticker posted in a chat.
This is great for ad hoc tagging of single stickers in group chats, but I need to be in this chat for this functionality to work.

I also try to detect text in stickers, but this turns out to be quite ambitious.
Don't expect this functionality to work reliably!

If you want to help the project and tag some stickers, just type /tag_random in a direct conversation with me :).

In case you encounter any bugs or you just want to look at the code and drop a star:
https://github.com/Nukesor/stickerfinder
"""

tag_text = f"""Now please send me tags for each sticker I'll send you.
Just write what describes this sticker best.
It would be awesome if you could also add the text in the sticker :).
"""


blacklist = set(['me', 'is', 'i', 'ya', 'you', 'are', 'a', 'too', 'of', 'we', 'he',
                 'she', 'it', 'them', 'have', 'to', 'my', 'the', "it's", 'will', 'and'])
