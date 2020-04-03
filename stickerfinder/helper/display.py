"""Helper for compiling text."""
from stickerfinder.telegram.keyboard import get_help_keyboard


def get_settings_text(user):
    """Compile the settings text for a specific user."""

    text = ["*User settings:*"]
    text.append("")

    if user.notifications:
        text.append(
            "*Notifications:* You'll receive updates about notifications and other info regarding the bot"
        )
    else:
        text.append(
            "*Notifications:* You won't get any messages regarding the bot and development"
        )

    text.append("")
    text.append("")
    text.append("")
    text.append("*Search Settings:*")
    text.append("")

    if user.international:
        text.append("*Language:* Show stickers from all languages")
    else:
        text.append("*Language:* Only show english stickers")

    if user.deluxe:
        text.append("*Deluxe:* Only show deluxe stickers")
    else:
        text.append("*Deluxe:* Show all stickeres")

    if user.nsfw:
        text.append("*NSFW:* Include nsfw content by default")
    else:
        text.append("*NSFW:* Hide nsfw content by default")

    if user.furry:
        text.append("*Furry:* Include furry content by default")
    else:
        text.append("*Furry:* Hide furry content by default")

    return "\n".join(text)


def get_help_text_and_keyboard(current_category):
    """Create the help message depending on the currently selected help category."""
    categories = [
        "Search",
        "Tagging",
        "Deluxe",
        "Language",
        "NSFW/Furry/Ban",
        "Bugs",
    ]

    help_texts = {}
    help_texts[
        "Search"
    ] = """*Sticker search:*
Start typing @stfi\_bot in any chat. You can search by pack name, tags, emoji and sometimes even text inside the sticker.


*Sticker pack search:*
Just add `set` or `pack` to your search e.g. `@stfi_bot kermit set`.


*Add sticker packs:*
*DISCLAIMER:* If you add a pack, it will be available to *ALL* users.

Send any sticker to me in a direct conversation and I'll add the whole pack.
The bot will tell you if it doesn't know this pack yet and you will get a notification when the sticker pack has been processed.
Please bear with us.
If the bot is added to a group chat, it will automatically add all stickers posted in this chat!

*Can't find a sticker?*
If you already added a pack, you probably need to tag stickers first (or just search by the pack name).
To tag a whole pack just send me a sticker from the pack you want to tag."""

    help_texts[
        "Tagging"
    ] = """*Tagging stickers:*

Just send the sticker you want to tag and start typing.
You can also reply to a sticker with `/tag [tags]` e.g. `/tag obi wan star wars hello there`.
If you want to replace tags, you need to reply to the sticker in question with `/replace [tags]`
Unless tagging with /replace, tags are always added on top of the existing ones.

*Tagging 101:*

Just try to describe the sticker as good as possible and add the text of the sticker: e.g. `obi wan star wars hello there`
When you're in the English mode, *PLEASE* only tag in English.
If you want to tag in another language, please use the international mode."""

    help_texts[
        "Language"
    ] = """*Language:*

The default language is English. Every sticker pack, that contains languages other than English will be flagged as international.
These stickers can only be found, when changing to international in your settings.
You can find lots of stuff in there, but it's not as good maintained as the /english section."""

    help_texts[
        "NSFW/Furry/Ban"
    ] = """*NSFW & Furry:*
Nude stickers and alike will be tagged with `nsfw` and can only be found when adding the word `nsfw` to your search.
Furry stuff also got its own tags (`fur` or `furry`), since there is an unreasonable amount of (nsfw) furry sticker packs.
In case I miss any, reply to the sticker with the /report command to make me look at it again.


*Sticker Ban:*
I'm trying to detect and ban inappropriate stickers, if I've missed something please, please report it by replying with /report to the sticker.


*User Ban:*
If you just Spam `asdf` while tagging or if you add hundreds of tags to your own sticker pack to gain popularity, you will get banned.
You'll also get banned if you repeatedly tag in other languages while being in /english mode.
When you're banned, you can't use the inline search any longer and all of your changes/tags will be reverted."""

    help_texts[
        "Bugs"
    ] = """⚠️ *There is an unknown bug that won't go away!!* 😩

I usually get a notification as soon as something breaks, but there might be some bugs that go unnoticed!
In case a bug isn't fixed in a day or two, please write a ticket on [GitHub](https://github.com/Nukesor/ultimate-poll-bot) or stop by my [support group](https://t.me/nukesors_projects)."""

    help_texts[
        "Deluxe"
    ] = """*Deluxe mode:*

A selected and well-curated (and well tagged) collection of sticker packs are marked as `deluxe`.
You can enable deluxe mode in your settings."""

    text = help_texts[current_category]
    keyboard = get_help_keyboard(categories, current_category)

    return text, keyboard
