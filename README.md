# Sticker Finder ([@stfi_bot](https://t.me/stfi_bot))

Sticker Finder is a telegram bot which allows you to search your favorite stickers and discover new ones via inline query (just like @gif).

The inline query filters by looking at custom tags, detected text, emojis, sticker set name and title.
There already are about 1700 sticker sets with over 80000 stickers, that can be searched. And in case the bot is missing some, you can easily add your own precious sets.

Sticker finder is quite fast (about 0.1 sec for each search), supports custom tagging, features fuzzy searching and  allows tagging in multiple languages!

There are several ways to conveniently tag stickers: You can tag either in a direct telegram conversation or on the fly in any other chat.
I even perform a basic text recognition on all stickers to allow a nice sticker search by text (even though this doesn't work perfectly all the time).

And in case you get bored, you can go ahead and do some good by tagging a few random stickers with the `/tag_random` functionality.

<p align="center">
    <img src="https://raw.githubusercontent.com/Nukesor/images/master/sticker_finder1.png">
    <img src="https://raw.githubusercontent.com/Nukesor/images/master/sticker_finder2.png">
</p>

Feel free to host your own or to use mine on telegram: [@stfi_bot](https://t.me/stfi_bot)

## Features:

- Inline query search by tags, text, emoji, stickerset name and title.
- Fuzzy searching to match similar words or typos.
- Multi language support (with English as default and fallback)
- Tagging of single stickers or whole sets.
- NSFW and Furry filter. Use `nsfw` or `fur` tag to explicitly search for this stuff.
- Random tagging of stickers if you're bored.
- Sticker set addition in direct conversations.
- Sticker set addition when bot is added to groups.
- /vote_ban for inappropriate sticker sets.
- A minimalistic mode for groups that don't want user interaction (I already host one with the name [@stfil_bot](https://t.me/stfil_bot))


## Available commands:

    /help       Display help
    /tag [tags] Tag the last sticker posted in this chat
    /tag_set    Start to tag a whole set
    /tag_random Get a random sticker for tagging. Crowdsourcing :). Thanks for everybody doing this :)!
    /random_set Get a random sticker set.
    /skip       Skip the current sticker
    /language   Set your language.
    /new_language [language] Propose a new language (In case I missed something).
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


When you are updating from a previous version do a `alembic upgrade head` instead of `./initdb.py`. `./initdb.py` always wipes your db.

## Botfather commands

    help - Display help
    tag_set - Start to tag a whole set
    tag - Tag the last sticker posted in this chat
    tag_random - Get a random sticker for tagging. Thanks for doing this :)!
    random_set - The bot sends you a random sticker set.
    skip - Skip the current sticker
    language - Set your language.
    new_language - Propose a new language (In case I missed something).
    vote_ban - Vote to ban the sticker set of the last sticker in the chat.
    cancel - Cancel all current actions.


## Dev commands
This is just for people hosting a bot and those with `admin` permissions:

    /ban [name|id] Ban a user
    /unban [name|id] Unban a user
    /tasks Start to process tasks in a maintenance chat
    /toggle_flag [ban|maintenance|newsfeed] Flag a chat as a maintenance, ban or newsfeed chat. Sticker send to ban chats are automatically banned. Newsfeed chats get the first sticker of every new set that is added.
    /stats Get some statistics
    /refresh Refresh all stickerpacks.
    /refresh_ocr Refresh all stickerpacks and refresh ocr.
