update tag set language = 'russian'
    where tag.name in (
        select tag.name from tag
            join sticker_tag ON sticker_tag.tag_name = tag.name
            join sticker ON sticker.file_id = sticker_tag.sticker_file_id
            join change ON change.sticker_file_id = sticker.file_id
            join "user" on change.user_id = "user".id where "user".id = '168626269' and tag.emoji = False
        )
    and tag.emoji = False; 
