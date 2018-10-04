"""Some static stuff or helper functions for sticker finder bot."""
from telegram import ReplyKeyboardMarkup


help_text = f"""<b>Search for stickers:</b>
Start typing @std_bot in any chat. You can search for stickers by keywords, emojis and stickerset titles.

<b>Add stickersets:</b>
Send any sticker set to me in a direct conversation, I'll add the whole set.
If I'm added to a group chat, I will automatically add all stickers posted in this chat!

<b>Can't find a sticker?</b>
If you already added a set, you probably need to tag them first (or just search by the set name).
To tag a whole set send /tag_set and a sticker from the set you want to tag.

<b>Tagging a single sticker:</b>
/tag allows to tag the last sticker posted in a chat.
This is great for ad hoc tagging of single stickers in group chats, but I need to be in this chat for this to work.

<b>Want to help?</b>
Tag some stickers :)! Just type /tag_random in a direct conversation with me.

<b>Candy:</b>
I also try to detect text in stickers, but this turns out to be quite ambitious.
Don't expect this functionality to work reliably!

In case you encounter any bugs or you just want to look at the code and drop a star:
https://github.com/Nukesor/stickerfinder
"""

tag_text = f"""Now please send me tags for each sticker I'll send you.
Just write what describes this sticker best.
It would be awesome if you could also add the text in the sticker :).
"""


blacklist = set(['me', 'is', 'i', 'ya', 'you', 'are', 'a', 'too', 'of', 'we', 'he',
                 'she', 'it', 'them', 'have', 'to', 'my', 'the', "it's", 'will', 'and'])

main_keyboard = ReplyKeyboardMarkup([['/help', '/tag_set', '/tag_random']],
                                    one_time_keyboard=True, resize_keyboard=True)
