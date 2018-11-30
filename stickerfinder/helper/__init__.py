"""Some static stuff or helper functions for sticker finder bot."""


start_text = """Hey. This is the Sticker Finder Bot.

A quick introduction:
- For search just type '@stfi_bot something I want' anywhere.
- If you want ALL sticker packs, use /international to enable other languages than english.
- For tagging sticker packs use /tag_set, /tag_random or the keyboard.
- If you want 'nsfw' or 'furry' stuff, include those words in your search.

For a more detailed explanation (especially if you want to tag) use /help :)
"""


help_text = """<b>Search for stickers:</b>
Start typing @stfi_bot in any chat. You can search for stickers by keywords, emojis and pack titles and sometimes even recognized text.

<b>Add sticker packs:</b>
Send any sticker pack to me in a direct conversation and I'll add the whole pack.
The bot will tell you if I don't know this pack yet and you will get a notification when the sticker pack has been processed and reviewed.
If the bot is added to a group chat, it will automatically add all stickers posted in this chat!
It can take quite a while to review all new sticker packs, so please bear with me.
<b>DISCLAIMER:</b> If you add a pack, it will be available to <b>ALL</b> users.

<b>Can't find a sticker?</b>
If you already added a pack, you probably need to tag them first (or just search by the pack name).
To tag a whole pack just send me a sticker from the pack you want to tag.

<b>Language:</b>
The default language is English. Every sticker pack, that contains language which isn't English will be flagged as such.
These stickers can only be found, when changing your mode to "International". You can find lots of stuff in there, but it's not as good maintained as the "English" section.

<b>How to tag:</b>
Just try to describe the sticker as good as possible and add the text of the sticker: e.g. <i>"obi wan star wars hello there"</i>
If there already are tags on a sticker, you'll overwrite all existing tags.
<b>Please</b> only tag in English, when you're in the English mode. If you tag in any other language, please use the international mode.

<b>Tagging a single sticker:</b>
/tag allows to tag the last sticker posted in a chat e.g. <i>"/tag obi wan star wars hello there"</i>
This is great for ad hoc tagging of single stickers in group chats, but I need to be in the chat for this to work.

<b>Want to help?</b>
Tag some stickers :)! Just type /tag_random in a direct conversation with me.

<b>NSFW & Sticker Ban:</b>
I'm trying to detect and flag/ban inappropriate stickers. Nude stickers and alike will be tagged with nsfw and can only be found when using the nsfw tag.
In case I miss any, you can use the /vote_ban command to make me look at it again (Use it for both nsfw and ban).
Furry stuff also got its own tags (`fur` or `furry`), since there is an unreasonable amount of (nsfw) furry sticker packs.

<b>User Ban:</b>
If you just Spam `asdf` while tagging or if you add hundreds of tags to your own sticker pack to gain popularity, you will get banned.
You'll also get banned if you don't repeatedly tag in other languages while being in the "English" mode and vica versa.
When you're banned, you can't use the inline search any longer and all of your changes/tags will be reverted.

<b>Candy:</b>
I also try to detect text in stickers. Even though this turns out to be quite ambitious, it works really well in some cases.
But don't expect this functionality to work reliably!

In case you encounter any bugs or you just want to look at the code:
https://github.com/Nukesor/sticker-finder
"""

tag_text = """Now please send me tags for each sticker I'll send you.
Just write what describes this sticker best.
It would be awesome if you could also add the text in the sticker :).
"""

error_text = """An unknown error occurred. I probably just got a notification about this and I'll try to fix it as quickly as possible.
In case this error still occurs in a day or two, please report the bug to me :). The link to the Github repository is in the /help text.
"""

reward_messages = {
    10: '🎉🎉🎉 Nice! 🎉🎉🎉 \n You just tagged your 10th sticker!',
    25: "25 Stickers. \n You're getting faster!",
    50: '50 Stickers. \n Way to go!',
    100: '🎉🎉🎉 100 Stickers...🎉🎉🎉 \n Wow!',
    250: "250 Stickers! \n I think you can manage 1000, can you?",
    500: '500 Stickers! \n Halfway there!',
    1000: "🎉🎉🎉 1000 Stickers!!!!! 🎉🎉🎉 \n Get a life :D!",
    2000: "2000 Stickers.. \n It stops being funny",
    3000: "3000 Stickers.... \n You should really stop.",
}

blacklist = set([])

ignored_characters = set(['\n', ',', '.', '!', '?'])
