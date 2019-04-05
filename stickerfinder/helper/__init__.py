"""Some static stuff or helper functions for sticker finder bot."""


start_text = """Hey. This is Sticker Finder Bot.

*Sticker search:*
just type `@stfi_bot kermit` anywhere. You can search by pack name, tags, emoji and sometimes even text inside the sticker.

*Sticker pack search:*
Just add "set" or "pack" to your search e.g. `@stfi_bot kermit set`.

*Languages:*
If you want non-english sticker packs, use /international to enable other languages than english.

*Tagging:*
For tagging sticker packs just send me a sticker from the pack.

*Explicit content:*
If you want `nsfw` or `furry` stuff, include those words in your search.

*Help:*
For a more detailed explanation (especially if you want to tag) use /help :)
"""


admin_help_text = """Commands available to admins:

/ban Ban the last sticker posted in this chat.
/unban Ban the last sticker posted in this chat.
/ban\_user [name|id] Ban a user
/unban\_user [name|id] Unban a user
/make\_admin Make another user admin
/tasks Start to process tasks in a maintenance chat

/delete\_set Completely delete a set
/add\_set Add multiple sets at once by set\_name

/toggle\_flag [maintenance|newsfeed] Flag a chat as a maintenance or newsfeed chat. Newsfeed chats get the first sticker of every new set that is added, while all tasks are send to maintenance chats.

/stats Get some statistics
/refresh Refresh all stickerpacks.
/refresh\_ocr Refresh all stickerpacks including ocr.
/broadcast Send the message after this command to all users.
"""


help_text = """*Sticker search:*
Start typing @stfi\_bot in any chat. You can search by pack name, tags, emoji and sometimes even text inside the sticker.

*Sticker pack search:*
Just add `set` or `pack` to your search e.g. `@stfi_bot kermit set`.

*Add sticker packs:*
*DISCLAIMER:* If you add a pack, it will be available to *ALL* users.

Send any sticker to me in a direct conversation and I'll add the whole pack. The bot will tell you if it doesn't know this pack yet and you will get a notification when the sticker pack has been processed and accepted by us.
Since we need to review every single pack manually, it can take quite a while to review all new sticker packs (sometimes over 100 on a single day). Please bear with us.
If the bot is added to a group chat, it will automatically add all stickers posted in this chat!


*Can't find a sticker?*
If you already added a pack, you probably need to tag stickers first (or just search by the pack name).
To tag a whole pack just send me a sticker from the pack you want to tag.

*Language:*
The default language is English. Every sticker pack, that contains language which isn't English will be flagged as such.
These stickers can only be found, when changing your mode to /international. You can find lots of stuff in there, but it's not as good maintained as the /english section.

*How to tag:*
Just try to describe the sticker as good as possible and add the text of the sticker: e.g. `obi wan star wars hello there`
If there already are tags on a sticker, you'll overwrite all existing tags.
When you're in the English mode, *PLEASE* only tag in English. If you want to tag in another language, please use the international mode.

*Tagging a single sticker:*
/tag allows to tag the last sticker posted in a chat e.g. `/tag obi wan star wars hello there`.
Anyway you can also tag any other sticker by just replying to it with `/tag ...`.
This is great for ad hoc tagging of single stickers in group chats, but the bot needs to be in the chat for this to work.

*Want to help?*
Tag some stickers :)! Tag your favorite sticker packs or just type /tag\_random in a direct conversation with the bot.

*NSFW & Sticker Ban:*
I'm trying to detect and flag/ban inappropriate stickers. Nude stickers and alike will be tagged with `nsfw` and can only be found when addingi `nsfw` to your search.
In case I miss any, you can use the /vote\_ban command to make me look at it again (Use it for both nsfw and ban).
Furry stuff also got its own tags (`fur` or `furry`), since there is an unreasonable amount of (nsfw) furry sticker packs.

*User Ban:*
If you just Spam `asdf` while tagging or if you add hundreds of tags to your own sticker pack to gain popularity, you will get banned.
You'll also get banned if you repeatedly tag in other languages while being in /english mode.
When you're banned, you can't use the inline search any longer and all of your changes/tags will be reverted.

*Candy:*
I also try to detect text in stickers. Even though this turns out to be quite ambitious, it works really well in some cases.
But don't expect this functionality to work reliably!

In case you encounter any bugs or you just want to look at the code, feel free to check out my repository:
[Sticker Finder on Github](https://github.com/Nukesor/sticker-finder)
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
