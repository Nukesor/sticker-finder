# v1.1.0


**Features**
- Tags will now be added to the existing tags, instead of replacing the old ones.
- Replacing tags can be done by using `/replace [tags]`
- Fixed the issue causing rapid incremental updates in the first bulk of stickers. (If not enough stickers are found in strict search, fuzzy search will be performed immediately instead of waiting for the next query).
- The favorites view is now implemented for nsfw and furry stuff as well. (Just type nothing)
- /deluxe Mode. We started to collect the (in our opinion) very best and pristine sticker packs out there.
    You can now choose to only see this carefully curated set of stickers with the /deluxe command.
    If you want to see everything again, just type /deluxe again.
- /tag_random will now prioritize deluxe sets.


**Admin/Maintenance additions**
- /test\_broadcast function to preview a broadcast text.
- I finally added testing :3 
- Add a LOT of tests
- Lots of bug/behaviour fixes and adjustments


# v1.0.0

**Personal favorites:**
- Just typing @stfi\_bot will now show you your all time favorite stickers ordered by frequency of use.
- Stickers that were previously chosen by you will now be further up in the search results.
- Help texts have been partially rewritten and clarified. I'm happy about any feedback, please help me to make it easier to understand.
- Added /forget\_set command to help you remove unwanted sticker packs from your favorites.

**Tagging improvements:**
- Replying to a sticker with `/tag [tags...]` will change this specific sticker's tags.
- Editing of a tag message will edit the tags of the sticker as well.
- Sending a new sticker while tagging random stickers or a specific pack, will cancel the previous tagging process.
- Added a new button `Continue tagging this set` to jump right back to the last sticker you tagged.

**General stuff:**
- Remove /tag\_set function since this is handled by buttons by now.
- Several fixes all over the place
- Improved performance and even better error monitoring

**Admin/Maintenance additions**
- `/show [file_id]` Command sends the corresponding sticker for the given Id
- Upgrade to Python-telegram-bot v12.0.0b1
