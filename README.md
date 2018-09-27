# Stickerfinder

Stickerfinder is a telegram bot which allows you to find stickers via inline query and text/tags.
A basic text recognition is executed on all known stickers, to allow a nice sticker search.

Additionally there is a convenient way of tagging stickers or to modify a sticker search text (In case the text recognition failed.)

<p align="center">
    <img src="https://raw.githubusercontent.com/Nukesor/images/master/sticker_finder1.png">
    <img src="https://raw.githubusercontent.com/Nukesor/images/master/sticker_finder2.png">
</p>

Available commands:

        /help       Display help
        /tag [tags] Tag the last sticker posted in this chat
        /tag_set    Start to tag a whole set
        /next       Skip the current tag
        /cancel     Cancel all current tag actions

Feel free to host your own or to use mine: @std_bot


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
    cancel - Cancel all current tag actions
