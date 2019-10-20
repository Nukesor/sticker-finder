"""Some static stuff or helper functions for sticker finder bot."""


start_text = """Hi!
Here some basic information on how to use the bot!
If you're interested, there is more detailed info in the help section.

🔎 *Sticker search:*
just type `@stfi_bot kermit` anywhere. You can search by pack name, tags, emoji and sometimes even text inside the sticker.

🔎 *Sticker pack search:*
Just add "set" or "pack" to your search e.g. `@stfi_bot kermit set`.

🌐 *Languages:*
If you want non-English sticker packs, use /international to enable other languages than English.

✒️ *Tagging:*
To tag a specfic sticker pack just send me any sticker from the pack.
To tag a specfic sticker just send me the sticker and start typing e.g. `obi wan kenobi star wars`.
Check out the help page for more information 🙂.

❌ *Explicit content:*
If you want `nsfw` or `furry` stuff, include those words in your search or enable them permanently in your settings.

🤔 *Help:*
For a more detailed explanation (especially if you want to tag) check out the /help :)
If you still have questions, stop by my [support group](https://t.me/nukesors_projects).

🥳*Donations:*
The whole project is *for free*, *open-source* on [Github](https://github.com/Nukesor/sticker-finder) and hosted on a server I'm currently renting. I really appreciate any help I can get! 🙏
"""


admin_help_text = """Commands available to admins:

/ban Ban the last sticker posted in this chat.
/unban Ban the last sticker posted in this chat.
/ban\_user [name|id] Ban a user
/unban\_user [name|id] Unban a user
/make\_admin Make another user admin
/tasks Start to process tasks in a maintenance chat

/delete\_set Completely delete a set
/add\_set Add multiple sets at once by /set\_name
/show\_sticker [file_id] Show the sticker for this file id
/show\_id Show the fild_id of the sticker you replied to

/toggle\_flag [maintenance|newsfeed] Flag a chat as a maintenance or newsfeed chat. Newsfeed chats get the first sticker of every new set that is added, while all tasks are send to maintenance chats.


/stats Get some statistics
/refresh Refresh all stickerpacks.
/refresh\_ocr Refresh all stickerpacks including ocr.
/broadcast Send the message after this command to all users.
"""

donations_text = """
Hi! ☺️

My name is Arne Beer (@Nukesor) and I'm the developer of the Sticker Finder.

StickerFinder is my first big telegram bot, and I'm super excited to see it being used by so many people! ❤️

I really like the idea of giving the community the power to create a _huge_ and _intuitive_ sticker library and I hope that this project will become one of the best and most used Sticker Bots out there!

The project is *non-profit*, *open-source* on [Github](https://github.com/Nukesor/sticker-finder) and hosted on a server I'm currently renting.
Right now I usually invest between 5-20 hours a week into developing and maintaining my projects.

I really appreciate anything that keeps me and my server running ☺️, especially if this means that I can put more time into optimizations and developing features!

🌟 Thank you for using the bot! 🌟

Find me on [Patreon](https://www.patreon.com/nukesor) and [Paypal](https://www.paypal.me/arnebeer).
If you have any questions, stop by my [support group](https://t.me/nukesors_projects).

Have great day!
"""


tag_text = """Now please send me tags for each sticker I'll send you.
Just try to use words that describe this sticker best.
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
