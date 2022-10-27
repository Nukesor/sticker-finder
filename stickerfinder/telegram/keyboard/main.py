from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from stickerfinder.helper.callback import build_data


def get_main_keyboard(user):
    """Get the main keyboard for the current user."""
    buttons = [
        [
            InlineKeyboardButton(
                text="⚙️ Settings", callback_data=build_data("settings_open")
            )
        ]
    ]
    if user.admin:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="⚙️ Admin Settings",
                    callback_data=build_data("admin_settings_open"),
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="? Tag random stickers ?", callback_data=build_data("tag_random")
            )
        ]
    )
    buttons.append(
        [InlineKeyboardButton(text="🤔 Help", callback_data=build_data("help_open"))]
    )

    keyboard = InlineKeyboardMarkup(buttons)
    return keyboard


def get_help_keyboard(categories, current_category):
    """Get the done keyboard for options during poll creation."""
    rows = []
    current_row = []
    while len(categories) > 0:
        category = categories.pop(0)
        payload = build_data("switch_help", action=category)
        text = category
        if category == current_category:
            text = f"[ {category} ]"
        button = InlineKeyboardButton(text, callback_data=payload)

        if len(current_row) < 3:
            current_row.append(button)
        else:
            rows.append(current_row)
            current_row = [button]

    rows.append(current_row)

    main_payload = build_data("main_menu")
    rows.append([InlineKeyboardButton(text="Back", callback_data=main_payload)])

    return InlineKeyboardMarkup(rows)
