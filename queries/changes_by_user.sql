select * from change 
    join "user" on change.user_id = "user".id
    join sticker on change.sticker_file_id = sticker.file_id
    join sticker_set on sticker.sticker_set_name = sticker_set.name
where "user".username = ''
