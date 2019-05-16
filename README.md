# Sticker Finder ([@stfi_bot](https://t.me/stfi_bot))

[![Paypal](https://github.com/Nukesor/images/blob/master/paypal-donate-blue.svg)](https://www.paypal.me/arnebeer/)
[![Patreon](https://github.com/Nukesor/images/blob/master/patreon-donate-blue.svg)](https://www.patreon.com/nukesor)

This telegram bot allows you to search your favorite stickers and discover new ones via inline query (just like @gif).

The inline query filters by looking at custom tags, detected text, emojis, sticker set name and title.
There already are about 3100 searchable sticker sets with over 150k stickers. And in case the bot is missing some, you can easily add your own precious sets.

Sticker finder is quite fast (about 0.1 sec for each search), supports custom tagging and features fuzzy searching!

There are several ways to conveniently tag stickers: You can tag either in a direct telegram conversation or on the fly in any other chat.
I even perform basic text recognition on all stickers to allow a nice sticker search by text (even though this doesn't work perfectly all the time).

And in case you get bored, you can go ahead and do some good by tagging a few random stickers with the `/tag_random` functionality.

<p align="center">
    <img src="https://raw.githubusercontent.com/Nukesor/images/master/sticker_finder1.png">
    <img src="https://raw.githubusercontent.com/Nukesor/images/master/sticker_finder2.png">
</p>

Feel free to host your own or to use mine on telegram: [@stfi_bot](https://t.me/stfi_bot)

## Features:

- Inline query search by tags, text, emoji, sticker set name and title.
- A dedicated search for sticker packs. Just add `pack` or `set` to your search e.g. `@stfi_bot kermit set`.
- Fuzzy searching to match similar words or typos.
- Individual search results (If you use a sticker often you will see it on top.)
- Tagging of single stickers or whole sets.
- NSFW and Furry filter. Use `nsfw` or `fur` tag to explicitly search for this stuff.
- Sticker set addition in direct conversations or when the bot is added to groups.
- Random tagging of stickers if you're bored.
- `/report [reason]` Report a sticker set for some reason.
- A minimalistic mode for groups that don't want user interaction (I already host one with the name [@stfil_bot](https://t.me/stfil_bot)).


## Available commands:

    /help       Display help
    /tag [tags] Tag the last sticker posted in this chat
    /tag_random Get a random sticker for tagging. Crowdsourcing :). Thanks for everybody doing this :)!
    /random_set Get a random sticker set.
    /skip       Skip the current sticker
    /cancel     Cancel all current tag actions
    /english    Only english sticker sets and tags
    /international Get sticker sets from all all languages.
    /toggle_deluxe Only get the very best sticker packs. (Restricts the search drastically)
    /forget_set Forget all usages of all stickers of a specific sticker pack. The sticker pack is determined by the latest sticker in this chat.


## Installation and starting:

1. You will need to install `poetry` to install all dependencies.
2. Clone the repository: 

        % git clone git@github.com:nukesor/stickerfinder && cd stickerfinder

3. Now copy the `stickerfinder/config.example.py` to `stickerfinder/config.py` and adjust all necessary values.
4. Finally execute following commands to install all dependencies and to start the bot:

    % poetry install
    % poetry run initdb.py
    % poetry run main.py

5. When you are updating from a previous version just execute `poetry run alembic upgrade head`.


## Botfather commands

    help - Display help
    tag - Tag the last sticker posted in this chat
    tag_random - Get a random sticker for tagging. Thanks for doing this :)!
    random_set - The bot sends you a random sticker set.
    skip - Skip the current sticker
    report - Report something regarding the sticker set of the last sticker in the chat.
    cancel - Cancel all current actions.
    english - Only english sticker sets and tags
    international - Get sticker sets from all all languages.
    toggle_deluxe - Only get the very best sticker packs. (Restricts the search drastically)


## Dev commands
This is just for people hosting a bot and those with `admin` permissions:

    /ban Ban the last sticker posted in this chat.
    /unban Unban the last sticker posted in this chat.
    /ban_user [name|id] Ban a user
    /unban_user [name|id] Unban a user
    /tasks Start to process tasks in a maintenance chat
    /make_admin [name|id] Make another user admin

    /delete_set [name] Completely delete a set
    /show [file_id]` Command sends the corresponding sticker for the given Id
    /add_set [names...] Add multiple sets at once by `set_name` separated by newline

    /toggle_flag [maintenance|newsfeed] Flag a chat as a maintenance or newsfeed chat. Newsfeed chats get the first sticker of every new set that is added, while all tasks are send to maintenance chats.

    /stats Get some statistics
    /refresh Refresh all stickerpacks.
    /refresh_ocr Refresh all stickerpacks including ocr.
    /broadcast [message] Send the message after this command to all users.
