# Sticker Finder

[![GitHub release](https://img.shields.io/github/tag/nukesor/sticker-finder.svg)](https://github.com/nukesor/sticker-finder/releases/latest)
[![Test status](https://travis-ci.org/Nukesor/sticker-finder.svg?branch=main)](https://travis-ci.org/Nukesor/sticker-finder)
[![MIT Licence](https://img.shields.io/badge/license-MIT-success.svg)](https://github.com/Nukesor/sticker-finder/blob/main/LICENSE.md)

## :warning: :warning: :warning:  State of the project :warning: :warning: :warning:

The project is **no longer actively** maintained!
I try to bump dependencies on a regular basis, but **I won't review or accept** any new pull requests!

If you started a successful fork of this repository that has been maintained over a longer period of time, feel free to contact me. I'll then point to your fork :).

:warning: :warning: :warning: :warning: :warning: :warning: :warning: :warning: :warning: :warning: :warning: :warning: :warning:

## Introduction

StickerFinder is a telegram bot for searching stickers (just like @gif).

You can search through community tags, on-image text, emojis and the sticker-set's title.
There are already more than 4100 searchable sticker sets with over 230k stickers.
In case the bot is missing some, you can easily add your own precious sets.

StickerFinder's search is super fast and features customized tagging as well as fuzzy searching!

<p align="center">
    <img src="https://raw.githubusercontent.com/Nukesor/images/main/sticker_finder1.png">
    <img src="https://raw.githubusercontent.com/Nukesor/images/main/sticker_finder2.png">
</p>

Feel free to host your own bot. There is an up-to-date postgreSQL database dump in the repository.

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
    /tag [tags] Tag the last sticker posted in this chat or the sticker you replied to
    /replace [tags] Replace the tags of the last sticker posted in this chat or the sticker you replied to
    /cancel     Cancel all current tag actions
    /forget_set Forget all usages of all stickers of a specific sticker pack. The sticker pack is determined by the latest sticker in this chat.

## Installation and starting

**This bot is developed for Linux.**

Windows isn't tested, but it shouldn't be too hard to make it compatible. Feel free to create a PR.

Dependencies:

- `poetry` to manage and install dependencies.
- [Just](https://github.com/casey/just) for convience.
- Stickerfinder uses postgres. Make sure the user has write/read rights.

1. Clone the repository:
        git clone git@github.com:nukesor/stickerfinder && cd stickerfinder
1. Execute `just setup` to install all dependencies.
1. Either start the stickerfinder once with `just run` or copy the `misc/stickerfinder.toml` manually to `~/.config/stickerfinder.toml`.
    Adjust all necessary values.
1. Run `just initdb` to initialize the database (or recreate it, if necessary) and set the migration stamp to the newest alembic head.
1. Import the database `pg_restore -O -j 4 -F c -d your_db_name name_of_the_dump`
1. Start the bot by running `just run`

## Botfather commands

```txt
help - Display help
tag - Tag the last sticker posted in this chat or the sticker you replied to
replace - Replace the tags of the last sticker posted in this chat or the sticker you replied to
report - Report something regarding the sticker set of the last sticker in the chat.
cancel - Cancel all current actions.
forget_set - Forget all usages of a sticker pack.
```

## Admin commands

This is just for people hosting a bot and those with `admin` permissions:

```txt
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
/authorize [user_id] Allow this user to access a secured instance.
```
