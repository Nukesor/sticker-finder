# Stickerfinder (@std_bot)

Stickerfinder aka StickerDiscoveryBot is a telegram bot which allows you to find your favorite stickers and discover new ones via inline query and text/tags.
A basic text recognition is executed on all known stickers, to allow a nice sticker search by text.

Additionally there is a convenient way of tagging stickers and modifying the detected sticker text (In case the text recognition failed.)

<p align="center">
    <img src="https://raw.githubusercontent.com/Nukesor/images/master/sticker_finder1.png">
    <img src="https://raw.githubusercontent.com/Nukesor/images/master/sticker_finder2.png">
</p>

Feel free to host your own or to use mine: `@std_bot`

## Features:

    - Inline query search by text, tags, emoji, stickerset name and title.
    - Manual tagging of single stickers or whole sets.
    - Random tagging of stickers to help the project and the community.
    - Automatic sticker set detection when added to groups.
    - Manual sticker set detection when stickers are sent to direct conversation.
    - /vote_ban for inappropriate sticker sets.


## Available commands:

    /help       Display help
    /tag [tags] Tag the last sticker posted in this chat
    /tag_set    Start to tag a whole set
    /tag_random - Get a random sticker for tagging. Crowdsourcing :). Thanks for everybody doing this :)!
    /vote_ban [reason] Vote to ban the sticker set of the last sticker in the chat.
    /next       Skip the current tag
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
    next - Skip the current tag
    tag_set - Start to tag a whole set
    tag - Tag the last sticker posted in this chat
    tag_random - Get a random sticker for tagging. Crowdsourcing :). Thanks for everybody doing this :)!
    vote_ban - Vote to ban the sticker set of the last sticker in the chat.
    cancel - Cancel all current tag actions


## Dev commands
This is just for people hosting a bot and those with `admin` permissions:

    /ban [name|id] Ban a user
    /unban [name|id] Unban a user
    /flag_chat [ban|maintenance|newsfeed] Flag a chat as a maintenance, ban or newsfeed chat. Sticker send to ban chats are automatically banned. Newsfeed chats get the first sticker of every new set that is added.
    /stats Get some statistics
    /refresh Refresh all stickerpacks.
