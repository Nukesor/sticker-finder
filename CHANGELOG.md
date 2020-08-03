## [2.1.0] - 2020-08-04

### Changed

- SIGNIFICANTLY improve query speed by utilizing PTB's integrated cache.
- Migrate all long texts to a yaml and add a i18n library.
- Remove legacy telegram call wrapper
- Significantly improve error handling
- Switch to Sentry's new official sdk

### Fixed

- A bug where fuzzy search didn't work, if no strict results were previously found.
- Refactoring errors that were introduced when convering a class to an enum.

## [2.0.0] - 2020-07-30

**THIS RELEASE INTRODUCES BREAKING CHANGES**
This is the first real release in quite a while.
The project really didn't follow semantical versioning and there weren't even real releases for the last versions.

The project will now stick to the semver standard and keep the changelog up-to-date.

### Added

- Support for animated stickers.
- Flag that allows to run the bot in private mode.
- Flag to automatically accept new sticker sets.
- Flag to restrict inline search to authorized users.

### Changed

- Use Black for code formatting.

### Fixed

- Finally support new `file_id` and `file_unique_id` format recently introduced by Telegram.
- Updated to new python-telegram-bot version.
- Fixed serial usage for unique sticker ids.

## [1.2.0]

### Added

- Complete UX revamp.
- Interactive main-/settings-menu.
- Support for animated stickers.
- `/delete_history` function. The bot will forget everything you every searched for.
- Permanently enabled searches for nsfw and furry stuff.
- Removal of many invalid/stupid/link/spam tags.
- Tags with many consecutive characters (`loooooool`) will be reduced to a maximum of 3 consecutive letters (`loool`). The same is applied for search words.

### Change

- Performance speedup for fuzzy queries.

### Fixed

- Telegram sometimes randomly changes file_ids of stickers. This led to major loss of usage statistics and tags.
- Fix a problem with the main keyboard.
- Fix a bug where search would break if a sticker had two very similar tags during fuzzy search
- Fix a bug where search would break due to super long sticker set names

## [1.1.0]

### Added

- The favorites view is now implemented for nsfw and furry stuff as well.
- Tags will now be added to the existing tags, instead of replacing the old ones
- Replacing tags can be done by using `/replace [tags]`
- You can reply to a sticker with `/replace [tags...]` and replace those tags
- If a sticker is replied to a request message (in a group chat) e.g. `#request kermit` or simply `#kermit`, the respective stickers will be tagged with the request's tags. This feature is mainly for [StickersChat](t.me/stickersChat)

- deluxe Mode. We started to collect the (in our opinion) very best and pristine sticker packs out there.
    You can now choose to only see this carefully curated set of stickers with the `/toggle_deluxe` command.  
    If you want to see everything again, just type `/deluxe` again.  
    (This mode will take some time to become really good, since we need to look at all of the 4000 sticker packs again -.-)  
- `/tag_random` will now prioritize deluxe sets.

- `/test_broadcast` function to preview a broadcast text.
- Adding tests

### Fixed

- Replying to a sticker with `/tag [tags...]` now actually works
- Fixed the issue causing rapid incremental updates in the first bulk of stickers. (If not enough stickers are found in strict search, fuzzy search will be performed immediately instead of waiting for the next query).
- Fix a bug, where stickers showed up at the end of the search, if they have been used by other people, but not by yourself
- Lots of bug/behaviour fixes and adjustments

## [1.0.0] - 2019-04-05

### Added

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

- `/show [file_id]` Command sends the corresponding sticker for the given Id

### Changed

- Upgrade to Python-telegram-bot v12.0.0b1
- Remove `/tag_set` function since this is handled by buttons by now.
- Improved performance and even better error monitoring

### Fixed

- Several fixes all over the place
