#v1.0.0

## Additions


- All searches now consider your personal usage of Sticker Finder. This means that stickers that are previously chosen by you will now be further up in the search results.
- Just typing `@stfi_bot` will now show you your all time favorite stickers sorted the amount of usages.
- `/forget_set` Forget all usages of all stickers of a specific sticker pack. The sticker pack is determined by the latest sticker in this chat. This allows you to keep your favorite overview clean (feature mentioned above).
- Rewrite help texts (I'm happy about any feedback, please help me to make it easier to understand)

- Remove `/tag_set` function since this is handled by buttons by now.

- Several fixes all over the place
- Improved performance and error monitoring

#### Streamlining the tagging process:
- Replying to a sticker with `/tag [tags...]` will change this specific sticker's tags.
- Editing of a tag message will edit the tags of the sticker as well.
- Sending a new sticker while tagging random stickers or a specific set, will cancel the previous tagging process.
- Added a new button `Continue tagging this set` to jump right back to the last sticker you tagged.



## Admin/Maintenance additions

- `/show [file_id]` Command sends the corresponding sticker for the given Id
- Upgrade to Python-telegram-bot v12.0.0b1
