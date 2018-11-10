SELECT * FROM inline_query
    JOIN inline_query_request ON inline_query_request.inline_query_id = inline_query.id
    ORDER BY inline_query.created_at DESC LIMIT 800;
