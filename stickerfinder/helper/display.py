"""Helper for compiling text."""
from stickerfinder.i18n import i18n
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
    help_texts["Search"] = i18n.t("text.help.search")
    help_texts["Tagging"] = i18n.t("text.help.tagging")
    help_texts["Language"] = i18n.t("text.help.language")
    help_texts["NSFW/Furry/Ban"] = i18n.t("text.help.ban")
    help_texts["Bugs"] = i18n.t("text.help.bugs")
    help_texts["Deluxe"] = i18n.t("text.help.deluxe")

    text = help_texts[current_category]
    keyboard = get_help_keyboard(categories, current_category)

    return text, keyboard
