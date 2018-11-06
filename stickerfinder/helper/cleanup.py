from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.keyboard import admin_keyboard
from stickerfinder.models import (
    Tag,
)


def tag_cleanup(session, update):
    """Do some cleanup tasks for tags."""
    from stickerfinder.helper import blacklist

    all_tags = session.query(Tag).all()
    count = 0
    call_tg_func(update.message.chat, 'send_message', [f'Found {len(all_tags)} tags'])
    for tag in all_tags:
        # Remove all tags in the blacklist
        if tag.name in blacklist:
            session.delete(tag)

            continue

        # Split multi word tags into single word tags and delete the old tags
        splitted = tag.name.split(' ')
        if len(splitted) > 1:
            new_tags = []
            for word in splitted:
                new_tag = Tag.get_or_create(session, word)
                new_tags.append(new_tag)

            for sticker in tag.stickers:
                for new_tag in new_tags:
                    if new_tag not in sticker.tags:
                        sticker.tags.append(new_tag)

            session.delete(tag)

        count += 1
        if count % 1000 == 0:
            progress = f'Processed {len(all_tags)} tags. ({len(all_tags) - count} remaining)'
            call_tg_func(update.message.chat, 'send_message', [progress])

    call_tg_func(update.message.chat, 'send_message', ['Tag cleanup finished.'], {'reply_markup': admin_keyboard})
