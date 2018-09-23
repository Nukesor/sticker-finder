# Sticker finder

<p align="center">
    <img src="https://raw.githubusercontent.com/Nukesor/images/master/sticker_finder.png">
</p>

Available commands:

        /start Start the bot
        /stop Stop the bot
        /tag_pack Start to tag a whole pack

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
