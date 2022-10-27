from stickerfinder.helper.display import get_settings_text
from stickerfinder.models import InlineQuery, StickerUsage
from stickerfinder.telegram.keyboard import (
    get_settings_keyboard,
    get_user_delete_history_confirmation_keyboard,
)


def update_settings(context):
    """Update the settings message."""
    context.message.edit_text(
        get_settings_text(context.user),
        parse_mode="Markdown",
        reply_markup=get_settings_keyboard(context.user),
    )


def delete_history_confirmation(session, context):
    """Delete the whole search history of the user."""
    context.message.edit_text(
        "⚠️ *Do you really want to delete your history?* ⚠️",
        reply_markup=get_user_delete_history_confirmation_keyboard(),
        parse_mode="Markdown",
    )


def delete_history(session, context):
    """Delete the whole search history of the user."""
    session.query(StickerUsage).filter(StickerUsage.user_id == context.user.id).delete(
        synchronize_session=False
    )

    session.query(InlineQuery).filter(InlineQuery.user_id == context.user.id).delete(
        synchronize_session=False
    )

    update_settings(context)

    context.message.chat.send_message("History cleared")


def user_toggle_notifications(session, context):
    """Toggle the international flag of the user."""
    user = context.user
    user.notifications = not user.notifications
    session.commit()
    update_settings(context)


def user_toggle_international(session, context):
    """Toggle the international flag of the user."""
    user = context.user
    user.international = not user.international
    session.commit()
    update_settings(context)


def user_toggle_deluxe(session, context):
    """Toggle the deluxe flag of the user."""
    user = context.user
    user.deluxe = not user.deluxe
    session.commit()
    update_settings(context)


def user_toggle_nsfw(session, context):
    """Toggle the nsfw flag of the user."""
    user = context.user
    user.nsfw = not user.nsfw
    session.commit()
    update_settings(context)


def user_toggle_furry(session, context):
    """Toggle the furry flag of the user."""
    user = context.user
    user.furry = not user.furry
    session.commit()
    update_settings(context)
