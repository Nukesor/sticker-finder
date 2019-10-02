# v1.2.0

**Features**
- Complete UX revamp
- Interactive main-/settings-menu
- Support for animated stickers
- `/delete_history` function. The bot will forget everything you every searched for.
- Permanently enabled searches for nsfw and furry stuff
- Removal of many invalid/stupid/link/spam tags
- Tags with many consecutive characters (`loooooool`) will be reduced to a maximum of 3 consecutive letters (`loool`). The same is applied for search words


__Maintenance__
- Speed and clean up fuzzy query.

__Bug fixes__
- Telegram sometimes randomly changes file_ids of stickers. This led to major loss of usage statistics and tags.
- Fix a problem with the main keyboard.
- Fix a bug where search would break if a sticker had two very similar tags during fuzzy search
- Fix a bug where search would break due to super long sticker set names

# v1.1.0

**Features**

__Bug fixes__
- Replying to a sticker with `/tag [tags...]` now actually works
- Fixed the issue causing rapid incremental updates in the first bulk of stickers. (If not enough stickers are found in strict search, fuzzy search will be performed immediately instead of waiting for the next query).
- Fix a bug, where stickers showed up at the end of the search, if they have been used by other people, but not by yourself

__Other Stuff__
- The favorites view is now implemented for nsfw and furry stuff as well. (Just type nothing)
- Tags will now be added to the existing tags, instead of replacing the old ones
- Replacing tags can be done by using `/replace [tags]`
- You can reply to a sticker with `/replace [tags...]` and replace those tags
- If a sticker is replied to a request message (in a group chat) e.g. `#request kermit` or simply `#kermit`, the respective stickers will be tagged with the request's tags (after being reviewed by me). This feature is mainly for [StickersChat](t.me/stickersChat)

__Deluxe Mode__
- deluxe Mode. We started to collect the (in our opinion) very best and pristine sticker packs out there.
    You can now choose to only see this carefully curated set of stickers with the `/toggle_deluxe` command.  
    If you want to see everything again, just type `/deluxe` again.  
    (This mode will take some time to become really good, since we need to look at all of the 4000 sticker packs again -.-)  
- /tag_random will now prioritize deluxe sets.

**Admin/Maintenance additions**
- `/test_broadcast` function to preview a broadcast text.
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
- Remove `/tag_set` function since this is handled by buttons by now.
- Several fixes all over the place
- Improved performance and even better error monitoring

**Admin/Maintenance additions**
- `/show [file_id]` Command sends the corresponding sticker for the given Id
- Upgrade to Python-telegram-bot v12.0.0b1
