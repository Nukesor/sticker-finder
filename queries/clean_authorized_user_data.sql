DELETE FROM "task";
DELETE FROM "change";
DELETE FROM chat
    WHERE not is_newsfeed
    AND not is_maintenance
    AND NOT EXISTS (SELECT * FROM "user" as u WHERE chat.id = u.id and u.authorized = True);
DELETE FROM inline_query
    WHERE NOT EXISTS (SELECT * FROM "user" as u WHERE inline_query.user_id = u.id and u.authorized = True);
DELETE FROM sticker_usage
    WHERE NOT EXISTS (SELECT * FROM "user" as u WHERE sticker_usage.user_id = u.id and u.authorized = True);
DELETE FROM report
    WHERE NOT EXISTS (SELECT * FROM "user" as u WHERE report.user_id = u.id and u.authorized = True);
DELETE FROM "user" where authorized = FALSE;
