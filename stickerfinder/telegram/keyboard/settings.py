"""Maintenance related keyboards."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from stickerfinder.helper.callback import build_user_data, build_data


def get_settings_keyboard(user):
    """Get the inline keyboard for settings."""
    international_payload = build_user_data("user_toggle_international", user)
    deluxe_payload = build_user_data("user_toggle_deluxe", user)
    nsfw_payload = build_user_data("user_toggle_nsfw", user)
    furry_payload = build_user_data("user_toggle_furry", user)
    notification_payload = build_data("user_toggle_notifications")
    delete_history_payload = build_data("user_delete_history_confirmation")
    main_payload = build_data("main_menu")

    if user.notifications:
        notification_text = "📩 Disable notifications"
    else:
        notification_text = "📩 Enable notifications"

    if user.international:
        international_text = "🌐 English-only sticker"
    else:
        international_text = "🌐 Include non-english stickers"

    if user.deluxe:
        deluxe_text = "🌟 Include non-deluxe sticker"
    else:
        deluxe_text = "🌟 Only show deluxe sticker"

    if user.nsfw:
        nsfw_text = "❌ Hide nsfw"
    else:
        nsfw_text = "💦 Include nsfw by default"

    if user.furry:
        furry_text = "Hide furry"
    else:
        furry_text = "Include furry by default"

    buttons = [
        [
            InlineKeyboardButton(
                text=notification_text, callback_data=notification_payload
            )
        ],
        [
            InlineKeyboardButton(
                text=international_text, callback_data=international_payload
            )
        ],
        [InlineKeyboardButton(text=deluxe_text, callback_data=deluxe_payload)],
        [InlineKeyboardButton(text=nsfw_text, callback_data=nsfw_payload)],
        [InlineKeyboardButton(text=furry_text, callback_data=furry_payload)],
        [
            InlineKeyboardButton(
                text="⚠️ Delete history ⚠️", callback_data=delete_history_payload
            )
        ],
        [InlineKeyboardButton(text="Back", callback_data=main_payload)],
    ]

    return InlineKeyboardMarkup(buttons)


def get_admin_settings_keyboard(user):
    """Get the inline keyboard for admin settings."""
    main_payload = build_data("main_menu")

    buttons = [
        [InlineKeyboardButton(text="Stats", callback_data=build_data("admin_stats"))],
        [
            InlineKeyboardButton(
                text="Cleanup", callback_data=build_data("admin_cleanup")
            )
        ],
        [InlineKeyboardButton(text="Plot", callback_data=build_data("admin_plot"))],
        [
            InlineKeyboardButton(
                text="Refresh all sticker", callback_data=build_data("admin_refresh")
            )
        ],
        [
            InlineKeyboardButton(
                text="Refresh all sticker + OCR",
                callback_data=build_data("admin_refresh_ocr"),
            )
        ],
        [InlineKeyboardButton(text="Back", callback_data=main_payload)],
    ]

    return InlineKeyboardMarkup(buttons)


def get_user_delete_history_confirmation_keyboard():
    """Ask the user if they really want to delete the history."""
    buttons = [
        [
            InlineKeyboardButton(
                text="⚠️ Permanently delete history ⚠️",
                callback_data=build_data("user_delete_history"),
            )
        ],
        [InlineKeyboardButton(text="back", callback_data=build_data("settings_open"))],
    ]

    return InlineKeyboardMarkup(buttons)
