select sticker.file_id, change.international,
       sticker_set.name, sticker_set.title,
       change_added_tags.tag_name
    from change 
    join "user" on change.user_id = "user".id
    join change_added_tags on change_added_tags.change_id = change.id
    join sticker on change.sticker_file_id = sticker.file_id
    join sticker_set on sticker.sticker_set_name = sticker_set.name
where "user".id = ''
order by change.created_at;
