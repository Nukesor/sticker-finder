# Sticker Finder

[![GitHub release](https://img.shields.io/github/tag/nukesor/sticker-finder.svg)](https://github.com/nukesor/sticker-finder/releases/latest)
[![Test status](https://travis-ci.org/Nukesor/sticker-finder.svg?branch=master)](https://travis-ci.org/Nukesor/sticker-finder)
[![MIT Licence](https://img.shields.io/badge/license-MIT-success.svg)](https://github.com/Nukesor/sticker-finder/blob/master/LICENSE.md)
[![Paypal](https://github.com/Nukesor/images/blob/master/paypal-donate-blue.svg)](https://www.paypal.me/arnebeer/)
[![Patreon](https://github.com/Nukesor/images/blob/master/patreon-donate-blue.svg)](https://www.patreon.com/nukesor)

This telegram bot allows you to search your favorite stickers and discover new ones via inline query (just like @gif).

The inline query filters by looking at custom tags, detected text, emojis, sticker set name and title.
There already are about 4100 searchable sticker sets with over 230k stickers. And in case the bot is missing some, you can easily add your own precious sets.

Sticker finder is quite fast (about 0.1 sec for each search), supports custom tagging and features fuzzy searching!

There are several ways to conveniently tag stickers: You can tag either in a direct telegram conversation or on the fly in any other chat.
I even perform basic text recognition on all stickers to allow a nice sticker search by text (even though this doesn't work perfectly all the time).

And in case you get bored, you can go ahead and do some good by tagging a few random stickers with the `/tag_random` functionality.

<p align="center">
    <img src="https://raw.githubusercontent.com/Nukesor/images/master/sticker_finder1.png">
    <img src="https://raw.githubusercontent.com/Nukesor/images/master/sticker_finder2.png">
</p>

Feel free to host your own bot. There is postgreSQL database dump in the repository.

## Features

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


## Available commands

    /help       Display help
    /donations  Show information for donations
    /tag [tags] Tag the last sticker posted in this chat or the sticker you replied to
    /replace [tags] Replace the tags of the last sticker posted in this chat or the sticker you replied to
    /cancel     Cancel all current tag actions
    /forget_set Forget all usages of all stickers of a specific sticker pack. The sticker pack is determined by the latest sticker in this chat.

## Installation and starting

**This bot is developed for Linux.**

Windows isn't tested, but it shouldn't be too hard to make it compatible. Feel free to create a PR.

Dependencies:

- `poetry` to manage and install dependencies.
- Stickerfinder uses postgres. Make sure the user has write/read rights.

1. Clone the repository:
        git clone git@github.com:nukesor/stickerfinder && cd stickerfinder
2. Execute `poetry install` to install all dependencies.
3. Either start the stickerfinder once with `poetry run main.py` or copy the `stickerfinder.toml` manually to `~/.config/stickerfinder.toml` and adjust all necessary values.
4. Run `createdb $your_database_name` to initialize the database.

5. Import the database `pg_restore -O -j 4 -F c -d your_db_name name_of_the_dump`
6. If you plan to keep up to date, you need to set the dump's alemibic revision manually with `poetry run alembic stamp head`.
7. Now you can just execute `poetry run alembic upgrade head`, whenever you are updating from a previous version.
8. Start the bot `poetry run python main.py`

## Botfather commands

    help - Display help
    tag - Tag the last sticker posted in this chat or the sticker you replied to
    replace - Replace the tags of the last sticker posted in this chat or the sticker you replied to
    report - Report something regarding the sticker set of the last sticker in the chat.
    cancel - Cancel all current actions.
    forget_set - Forget all usages of a sticker pack.

## Dev commands

This is just for people hosting a bot and those with `admin` permissions:

    /ban Ban the last sticker posted in this chat.
    /unban Unban the last sticker posted in this chat.
    /make_admin [name|id] Make another user admin
    /ban_user [name|id] Ban a user
    /unban_user [name|id] Unban a user
    /tasks Start to process tasks in a maintenance chat

    /toggle_flag [maintenance|newsfeed] Flag a chat as a maintenance or newsfeed chat. Newsfeed chats get the first sticker of every new set that is added, while all tasks are send to maintenance chats.

    /broadcast [message] Send the message after this command to all users.
    /add_set [names...] Add multiple sets at once by `set_name` separated by newline
    /delete_set [name] Completely delete a set
    /show_sticker [file_id] Command sends the corresponding sticker for the given Id
    /show_id Show file id of sticker you replied to
