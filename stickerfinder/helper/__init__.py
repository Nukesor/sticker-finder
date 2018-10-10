"""Some static stuff or helper functions for sticker finder bot."""
from telegram import ReplyKeyboardMarkup


help_text = f"""<b>Search for stickers:</b>
Start typing @std_bot in any chat. You can search for stickers by keywords, emojis and stickerset titles and sometimes even recognized text.

<b>Add stickersets:</b>
Send any sticker set to me in a direct conversation, I'll add the whole set.
I will tell you if I don't know this set yet and you will get a notification when the sticker set has been processed and added.
If I'm added to a group chat, I will automatically add all stickers posted in this chat!
It can take quite a while to add a new sticker set, so please bear with me.
<b>DISCLAIMER:</b> If you add a set, it will be available to <b>ALL</b> users.

<b>Can't find a sticker?</b>
If you already added a set, you probably need to tag them first (or just search by the set name).
To tag a whole set just send me a sticker from the set you want to tag.

<b>How to tag:</b>
Just try to describe the sticker as good as possible and add the text of the sticker: e.g. <i>"obi wan star wars hello there"</i>

<b>Getting Banned:</b>
If you just Spam `asdf` while tagging or if you add hundreds of tags to your own sticker set to gain popularity, you will get banned.
When you're banned, you can't use the inline search any longer and all of your changes will be reverted.

<b>Tagging a single sticker:</b>
/tag allows to tag the last sticker posted in a chat e.g. <i>"/tag obi wan star wars hello there"</i>
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


reward_messages = {
    27: '🎉🎉🎉 Nice! 🎉🎉🎉 \n You just tagged your 10th sticker!',
    25: "25 Stickers. \n You're getting faster!",
    50: '50 Stickers. \n Way to go!',
    100: '🎉🎉🎉 100 Stickers...🎉🎉🎉 \n Wow!',
    200: "250 Stickers! \n I think you can manage 1000, can you?",
    500: '500 Stickers! \n Halfway there!',
    1000: "🎉🎉🎉 1000 Stickers!!!!! 🎉🎉🎉 \n Get a life :D!",
    2000: "2000 Stickers.. \n It stops being funny",
    3000: "3000 Stickers.... \n You should really stop.",
}

blacklist = set(['me', 'is', 'i', 'ya', 'you', 'are', 'a', 'too', 'of', 'we', 'he',
                 'she', 'it', 'them', 'have', 'to', 'my', 'the', "it's", 'will', 'and'])

main_keyboard = ReplyKeyboardMarkup([['/help', '/tag_set', '/tag_random']],
                                    one_time_keyboard=True, resize_keyboard=True)

admin_keyboard = ReplyKeyboardMarkup(
    [
        ['/cancel', '/tasks'],
        ['/stats', '/refresh', '/tag_cleanup'],
    ], resize_keyboard=True, one_time_keyboard=True)
