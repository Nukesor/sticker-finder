"""Helper functions for tagging."""
from sqlalchemy import func
from collections import OrderedDict

from stickerfinder.sentry import sentry
from stickerfinder.enum import TagMode
from stickerfinder.telegram.keyboard import (
    get_main_keyboard,
    get_tagging_keyboard,
    get_fix_sticker_tags_keyboard,
)
from stickerfinder.i18n import i18n
from stickerfinder.models import (
    Change,
    Tag,
    Sticker,
    StickerSet,
    ProposedTags,
)


ignored_characters = set(["\n", ",", ".", "!", "?", "'", "@", "#", "*", "[", "_"])


def current_sticker_tags_message(sticker, user, send_set_info=False):
    """Create a message displaying the current text and tags."""
    # Check if both user and sticker set are using the default language
    international = user.international or sticker.sticker_set.international

    language = "international" if international else "english"
    if sticker.has_tags_for_language(international):
        message = (
            f"Current {language} tags are: \n{sticker.tags_as_text(international)}"
        )
    else:
        return f"There are no {language} tags for this sticker"

    if send_set_info:
        set_info = f"From sticker set: {sticker.sticker_set.title} ({sticker.sticker_set.name}) \n"
        return set_info + message

    return message


def send_tag_messages(chat, tg_chat, user, send_set_info=False):
    """Send next sticker and the tags of this sticker."""
    # If we don't have a message, we need to add the inline keyboard to the sticker
    # Otherwise attach it to the following message.
    message = current_sticker_tags_message(
        chat.current_sticker, user, send_set_info=send_set_info
    )
    keyboard = get_tagging_keyboard(chat)

    if not message:
        response = tg_chat.send_sticker(
            chat.current_sticker.file_id, reply_markup=keyboard
        )

        chat.last_sticker_message_id = response.message_id

    else:
        tg_chat.send_sticker(chat.current_sticker.file_id)

    if message:
        response = tg_chat.send_message(message, reply_markup=keyboard)
        chat.last_sticker_message_id = response.message_id


def handle_next(session, bot, chat, tg_chat, user):
    """Handle the /next call or the 'next' button click."""
    # We are tagging a whole sticker set. Skip the current sticker
    if chat.tag_mode == TagMode.sticker_set.value:
        # Check there is a next sticker
        stickers = chat.current_sticker.sticker_set.stickers
        for index, sticker in enumerate(stickers):
            if sticker == chat.current_sticker and index + 1 < len(stickers):
                # We found the next sticker. Send the messages and return
                chat.current_sticker = stickers[index + 1]
                send_tag_messages(chat, tg_chat, user)

                return

        # There are no stickers left, reset the chat and send success message.
        chat.current_sticker.sticker_set.completely_tagged = True
        send_tagged_count_message(session, bot, user, chat)
        tg_chat.send_message(
            "The full sticker set is now tagged.", reply_markup=get_main_keyboard(user)
        )
        chat.cancel(bot)

    # Find a random sticker with no changes
    elif chat.tag_mode == TagMode.random.value:
        base_query = (
            session.query(Sticker)
            .outerjoin(Sticker.changes)
            .join(Sticker.sticker_set)
            .filter(Change.id.is_(None))
            .filter(StickerSet.international.is_(False))
            .filter(StickerSet.banned.is_(False))
            .filter(StickerSet.nsfw.is_(False))
            .filter(StickerSet.furry.is_(False))
        )
        # Let the users tag the deluxe sticker set first.
        # If there are no more deluxe sets, just tag another random sticker.
        # Remove the favoring of deluxe stickers until the deluxe pool is bigger again.
        #        sticker = base_query.filter(StickerSet.deluxe.is_(True)) \
        #            .order_by(func.random()) \
        #            .limit(1) \
        #            .one_or_none()
        #        if sticker is None:
        sticker = base_query.order_by(func.random()).limit(1).one_or_none()

        # No stickers for tagging left :)
        if not sticker:
            tg_chat.send_message(
                "It looks like all stickers are already tagged :).",
                reply_markup=get_main_keyboard(user),
            )
            chat.cancel(bot)
            return

        # Found a sticker. Send the messages
        chat.current_sticker = sticker
        send_tag_messages(chat, tg_chat, user, send_set_info=True)


def initialize_set_tagging(session, bot, tg_chat, name, chat, user):
    """Initialize the set tag functionality of a chat."""
    sticker_set = StickerSet.get_or_create(session, name, chat, user)
    if sticker_set.complete is False:
        return "Sticker set {name} is currently being added."

    # Chat now expects an incoming tag for the next sticker
    chat.tag_mode = TagMode.sticker_set.value
    chat.current_sticker = sticker_set.stickers[0]

    tg_chat.send_message(i18n.t("text.tagging.send_tags"))
    send_tag_messages(chat, tg_chat, user)


def get_tags_from_text(text, limit=15):
    """Extract and clean tags from incoming string."""
    original_text = text
    text = text.lower().strip()

    # Remove the /tag command
    if text.startswith("/tag"):
        text = text[4:]

    # Remove #request tag
    if text.startswith("#request"):
        text = text[8:]

    # Split and strip
    tags = [tag.strip() for tag in text.split(" ") if tag.strip() != ""]

    # Remove words or links that are undesired
    partial_word_blacklist = [
        "telegramme",
        "telegram.me",
        "tme/",
        "t.me",
        "https://",
        "http://",
        "addstickers",
        "randomset",
    ]

    def contains_partial_word(tag):
        for word in partial_word_blacklist:
            if word in tag:
                return True
        return False

    tags = [tag for tag in tags if not contains_partial_word(tag)]

    # Clean the text
    def remove_ignored_chars(tag):
        for ignored in ignored_characters:
            tag = tag.replace(ignored, "")
        return tag

    tags = [remove_ignored_chars(tag) for tag in tags]

    # Remove tags accidentally added while using an inline bots
    if len(tags) > 0 and original_text.startswith("@") and "bot" in tags[0]:
        tags.pop(0)

    # Deduplicate tags
    tags = list(OrderedDict.fromkeys(tags))

    filtered_tags = []
    # Remove characters that occur more than three times consecutively
    for tag in tags:
        count = 0
        prev_char = None
        new_tag = ""
        for char in tag:
            if prev_char == char:
                count += 1
                if count < 3:
                    new_tag += char
            else:
                prev_char = char
                count = 0
                new_tag += char

        filtered_tags.append(new_tag)

    return filtered_tags[:15]


def send_tagged_count_message(session, bot, user, chat):
    """Send a user a message that displays how many stickers he already tagged."""
    if chat.tag_mode in [TagMode.sticker_set.value, TagMode.random.value]:
        count = (
            session.query(Sticker)
            .join(Sticker.changes)
            .filter(Change.user == user)
            .count()
        )

        bot.send_message(user.id, f"You already tagged {count} stickers. Thanks!")


def tag_sticker(
    session,
    text,
    sticker,
    user,
    tg_chat=None,
    chat=None,
    message_id=None,
    replace=False,
    single_sticker=False,
):
    """Tag a single sticker."""
    # Extract all texts from message and clean/filter them
    raw_tags = get_tags_from_text(text)

    # No tags, early return
    if len(raw_tags) == 0:
        return

    # Only use the first few tags. This should prevent abuse from tag spammers.
    if len(raw_tags) > 10:
        raw_tags = raw_tags[:10]
        tg_chat.send_message(
            "Please don't send that many tags. Try to describe everything as brief as possible."
        )

    # Inform us if the user managed to hit a special count of changes
    if tg_chat and len(user.changes) in [10, 25, 50, 100, 250, 500, 1000, 2000, 3000]:
        achievement_message = i18n.t(f"text.tagging.achievements.{len(user.changes)}")
        tg_chat.send_message(achievement_message)

        # Uncomment if you want to see if users hit milestones
        # sentry.capture_message(
        #    f"User hit {len(user.changes)} changes!",
        #    extra={
        #        "user": user.username,
        #        "user_id": user.id,
        #        "changes": len(user.changes),
        #    },
        # )

    # List of tags that are newly added to this sticker
    new_tags = []
    # List of all new tags (raw_tags, but with resolved entities)
    # We need this, if we want to replace all tags
    incoming_tags = []

    international = user.international or sticker.sticker_set.international
    # Initialize the new tags array with the tags don't have the current language setting.
    for raw_tag in raw_tags:
        incoming_tag = Tag.get_or_create(session, raw_tag, international, False)
        incoming_tags.append(incoming_tag)

        # Add the tag to the list of new tags, if it doesn't exist on this sticker yet
        if incoming_tag not in sticker.tags:
            new_tags.append(incoming_tag)

    # We got no new tags
    if len(new_tags) == 0 and replace is False:
        session.commit()
        return

    # List of removed tags. This is only used, if we actually replace the sticker's tags

    removed_tags = []
    # Remove replace old tags
    if replace:
        # Merge the original emojis, since they should always be present on a sticker
        incoming_tags = incoming_tags + sticker.original_emojis
        # Find out, which stickers have been removed
        removed_tags = [tag for tag in sticker.tags if tag not in incoming_tags]
        sticker.tags = incoming_tags
    else:
        for new_tag in new_tags:
            sticker.tags.append(new_tag)

    # Create a change for logging
    change = Change(
        user,
        sticker,
        international,
        new_tags,
        removed_tags,
        chat=chat,
        message_id=message_id,
    )
    session.add(change)

    session.commit()

    # Change the inline keyboard to allow fast fixing of the sticker's tags
    if tg_chat and chat and not single_sticker and chat.last_sticker_message_id:
        keyboard = get_fix_sticker_tags_keyboard(chat.current_sticker.file_unique_id)
        tg_chat.bot.edit_message_reply_markup(
            tg_chat.id, chat.last_sticker_message_id, reply_markup=keyboard
        )


def add_original_emojis(session, sticker, raw_emojis):
    """Add the original emojis to the sticker's tags and to the original_emoji relationship."""
    for raw_emoji in raw_emojis:
        emoji = Tag.get_or_create(session, raw_emoji, False, True)

        if emoji not in sticker.tags:
            sticker.tags.append(emoji)

        if emoji not in sticker.original_emojis:
            sticker.original_emojis.append(emoji)


def handle_request_reply(file_unique_id, update, session, chat, user):
    """Handle group request stickers."""
    if update.message.reply_to_message is None:
        return

    tags_message = update.message.reply_to_message.text
    if tags_message is None:
        return

    if tags_message.lower().startswith("#") or tags_message.lower().startswith(
        "request"
    ):
        proposed_tags = ProposedTags(tags_message, file_unique_id, user, chat)
        session.add(proposed_tags)
        session.commit()
