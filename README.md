# Stickerfinder ([@StickerDiscoveryBot](https://t.me/StickerDiscoveryBot) or [@std_bot](https://t.me/std_bot) )

Stickerfinder aka StickerDiscoveryBot is a telegram bot which allows you to find your favorite stickers and discover new ones via inline query search (just like @gif).
You can easily add your own sticker sets and search existing ones (already over 12k).

Also there are several ways to conveniently tag stickers either in a direct telegram conversation or on the fly in any other chat.
I even perform a basic text recognition on all stickers to allow a nice sticker search by text (even though this doesn't work perfectly all the time).

In case you get bored, you can go ahead and do some good by tagging a few random stickers with the `/tag_random` functionality.

And yes, I know that `std` also stands for sexually transmitted diseases, but there are very few short bot names left and I couldn't be picky.
That's why there are two bot users ;). Choose whichever you want since they are practically the same bot.

<p align="center">
    <img src="https://raw.githubusercontent.com/Nukesor/images/master/sticker_finder1.png">
    <img src="https://raw.githubusercontent.com/Nukesor/images/master/sticker_finder2.png">
</p>

Feel free to host your own or to use mine on telegram: [@StickerDiscoveryBot](https://t.me/StickerDiscoveryBot) or [@std_bot](https://t.me/std_bot)

## Features:

- Inline query search by text, emoji, stickerset name and title.
- Tagging of single stickers or whole sets.
- Random tagging of stickers if you're bored.
- Sticker set addition in direct conversations.
- Sticker set addition when bot is added to groups.
- /vote_ban for inappropriate sticker sets.


## Available commands:

    /help       Display help
    /tag [tags] Tag the last sticker posted in this chat
    /tag_set    Start to tag a whole set
    /tag_random - Get a random sticker for tagging. Crowdsourcing :). Thanks for everybody doing this :)!
    /vote_ban [reason] Vote to ban the sticker set of the last sticker in the chat.
    /cancel     Cancel all current tag actions


## Installation and starting:

Clone the repository: 

    % git clone git@github.com:nukesor/stickerfinder && cd stickerfinder

Now copy the `stickerfinder/config.example.py` to `stickerfinder/config.py` and adjust all necessary values.
Finally execute following commands to install all dependencies and to start the bot:

    % make
    % ./venv/bin/activate
    % ./initdb.py
    % ./main.py


## Botfather commands

    help - Display help
    tag_set - Start to tag a whole set
    tag - Tag the last sticker posted in this chat
    tag_random - Get a random sticker for tagging. Crowdsourcing :). Thanks for everybody doing this :)!
    vote_ban - Vote to ban the sticker set of the last sticker in the chat.
    cancel - Cancel all current actions.


## Dev commands
This is just for people hosting a bot and those with `admin` permissions:

    /ban [name|id] Ban a user
    /unban [name|id] Unban a user
    /tasks Start to process tasks in a maintenance chat
    /flag_chat [ban|maintenance|newsfeed] Flag a chat as a maintenance, ban or newsfeed chat. Sticker send to ban chats are automatically banned. Newsfeed chats get the first sticker of every new set that is added.
    /stats Get some statistics
    /refresh Refresh all stickerpacks.
