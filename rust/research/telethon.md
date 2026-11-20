# Telethon replacement: evidence for ADR-005

Researched 2026-11-20. This file reports findings; it does not choose a library.

Read for it: Telethon 1.44.0 (TL layer 227) and telethon-patch 0.3.1 as installed from PyPI;
the grammers 0.12.0 crates (TL layer 233) as published on crates.io on 2026-11-08; core.telegram.org.

## Summary

- Ultroid's use of Telethon: 78 of 155 Python files import it; 448 handler registrations; 1,588 send/edit call sites, of which 33 lines name a parse mode; 22 conversations; 45 raw request classes at 92 invoke sites; 39 error classes; a parallel file transfer (up to 20 connections) built on Telethon private API.
- grammers 0.12.0 (MIT OR Apache-2.0) has user and bot login, messages, media, participants, dialogs, callback and inline queries and raw `invoke`. All 45 raw requests exist in its schema with the constructor ids Telethon 1.44.0 uses.
- grammers has no handler registry, filters or command patterns, no conversation API, no `ChatAction` event, no string session, no Bot-API file ids, no progress callbacks and no typed error classes. Ultroid uses every one of these.
- Defaults differ from Telethon and change output silently: text is plain unless `.markdown()` is called; its markdown is CommonMark (`__x__` is bold, `~~x~~` is not parsed, a single newline has no handler); link previews are off; one flood-wait retry instead of five.
- grammers is pre-1.0 with four 0.x releases in 2026. The project states that minor releases change the TL layer and that the raw API is outside semantic versioning. It is on layer 233; Ultroid is pinned to a Telethon on layer 227.
- Session: every field of a Telethon string session has a public slot in `grammers-session`, but grammers documents no Telethon import and no login was attempted here. "No new login" is not verified.
- TDLib has Rust bindings, but it is a C++ client library with its own database, and its documented interface is its own TDLib API (`td_api.tl`). The pure-Rust MTProto clients that advertise handlers and conversations (ferogram, vaegram) were first published in 2026.
- Nothing here was run against Telegram: this environment has no account (ADR-001). Every grammers status below comes from reading the published source and docs.

## Source keys

A key expands to a path or URL by replacing its prefix. Line numbers refer to the versions named above.

| Key | Expands to |
| --- | --- |
| `U/` | the root of this repository |
| `T/` | `site-packages/telethon/` of the Python environment (Telethon 1.44.0) |
| `P/` | `site-packages/telethonpatch/` of the Python environment (telethon-patch 0.3.1) |
| `GC/` | `https://docs.rs/crate/grammers-client/0.12.0/source/` |
| `GM/` | `https://docs.rs/crate/grammers-mtsender/0.12.0/source/` |
| `GS/` | `https://docs.rs/crate/grammers-session/0.12.0/source/` |
| `GT/` | `https://docs.rs/crate/grammers-tl-types/0.12.0/source/` |

`cargo info <crate>` unpacks the same grammers files under `~/.cargo/registry/src/index.crates.io-*/<crate>-0.12.0/`; line numbers were read there.
Status words: **supported** = an API for it exists in 0.12.0; **partial** = part of it, the gap is named; **missing** = no API; **not verified** = could not be confirmed.

## 1. What Ultroid uses from Telethon

All counts are textual matches in the 155 `.py` files outside `rust/`. Run from the repository root:

```sh
G() { grep -rE --include='*.py' --exclude-dir=rust --exclude-dir=.git "$@" . ; }
N() { G -o "\.$1\(" | wc -l; }                  # call sites of a method name
G -l '^\s*(from|import) telethon' | wc -l       # 78 files import telethon or telethonpatch
G '^\s*(from|import) telethon' | wc -l          # 217 import statements
```

### 1.1 Events

```sh
G -o '^\s*@ultroid_cmd\(' | wc -l    # 293  user-account commands -> NewMessage (+ MessageEdited)
G -o '^\s*@asst_cmd\(' | wc -l       # 17   bot commands -> NewMessage
G -o '^\s*@callback\(' | wc -l       # 100  CallbackQuery; 34 match by regex: G -A2 '^\s*@callback\(' | grep -c 're\.compile'
G -o '^\s*@in_pattern\(' | wc -l     # 24   InlineQuery
N on                                 # 14   client.on(...); total 448 registrations in source
G -o '\bNewMessage\(' | wc -l        # 45   same command: MessageEdited 2, CallbackQuery 1, InlineQuery 1, ChatAction 7, Raw 2
G -o 'StopPropagation' | wc -l       # 2
G -o '\b(Album|UserUpdate|MessageRead|MessageDeleted|JoinRequest)\b' | wc -l    # 0 (events.GroupCall: 0)
N add_event_handler; N add_handler; N remove_event_handler; N list_event_handlers   # 12, 23, 3, 2
```

- One `@ultroid_cmd` registers up to five handlers at run time: owner `NewMessage`, sudo `NewMessage`, `MessageEdited` when `TAKE_EDITS` is set, and two bot-side `NewMessage` handlers for manager and dual mode (`U/pyUltroid/_misc/_decorators.py:238-332`).
- Filter arguments in use: `pattern`, `incoming`, `outgoing`, `forwards`, `func`, `chats`, `blacklist_chats`, `from_users`. Patterns are compiled by `compile_pattern` and matched with `re.match` against the raw text (`U/pyUltroid/_misc/_decorators.py:58-66`, `T/events/newmessage.py:159`).
- `Raw` is used for `UpdateMessagePollVote` (`U/assistant/games.py:303`) and `UpdateUserName` (`U/plugins/_chatactions.py:224`).
- Event attributes read most often (`G -o '\.NAME\b' | wc -l`): `chat_id` 357, `pattern_match` 200, `sender_id` 144, `data_match` 24.

### 1.2 Client and message methods

The count for each method name is `N name`; for each keyword argument it is `G -o '\bNAME=' | wc -l`.

| Group | Call sites |
| --- | --- |
| Send, edit, delete | `send_message` 210 (94 on a conversation object), `reply` 105, `respond` 25, `edit` 338, `eor` 677 as a method plus 154 as free `eor(`/`eod(`, `delete` 149, `try_delete` 13, `edit_message` 10, `delete_messages` 7, `forward_to` 6, `forward_messages` 1, `pin_message` 2, `unpin_message` 2 |
| Files and media | `send_file` 69, `download_media` 85 (44 with no argument, 11 with `thumb=`), `upload_file` 11 (4 are the catbox uploader), `download_file` 2, `download_profile_photo` 2, `fast_uploader` 18, `fast_downloader` 8 |
| Keyword arguments | `thumb` 64, `reply_to` 55, `link_preview` 53, `force_document` 42, `caption` 30, `attributes` 16, `supports_streaming` 16, `progress_callback` 8, `allow_cache` 7, `silent` 6, `schedule` 4 |
| Conversation | `conversation` 22 (19 in `assistant/`, 3 in `plugins/`), `get_response` 36, `wait_event` 9 |
| Inline, user side | `inline_query` 13, `click` 16 (14 on inline results with `reply_to`, `hide_via`, `silent`; 2 are Playwright) |
| Inline and callbacks, bot side | `answer` 99, `builder.article` 36, `builder.document` 2, `builder.photo` 1 |
| Iteration | `get_messages` 16, `iter_messages` 8, `get_dialogs` 8, `iter_dialogs` 5, `iter_participants` 5, `get_participants` 4, `get_profile_photos` 3, `iter_profile_photos` 1 |
| Entity resolution | `get_entity` 71, `parse_id` 33 (wraps `get_peer_id`), `get_input_entity` 3, `get_reply_message` 140, `get_chat` 21, `get_sender` 19, `get_input_chat` 3 |
| Chat administration | `edit_permissions` 26, `kick_participant` 17, `get_permissions` 6, `edit_folder` 5, `send_read_acknowledge` 5, `edit_admin` 2, `delete_dialog` 1, `action` 1 |

### 1.3 Raw API, buttons, parse modes, helpers, errors

```sh
G -oh '\b[A-Z][A-Za-z0-9]+Request\b' | sort -u | wc -l                 # 45 distinct request classes
G -o 'await ([A-Za-z_.]*client|ultroid_bot|asst|self|bot)\(' | wc -l   # 92 invoke sites (22 files with -l)
G -oh '\btypes\.[A-Z][A-Za-z0-9]+' | sort -u | wc -l                   # 36 TL types as types.X; 74 distinct with the 54 imported ones
G -oh '\bButton\.[a-z_]+\(' | sort | uniq -c                           # inline 224, url 36, switch_inline 19, mention 2
G -o '\bbuttons=' | wc -l                                              # 199
G 'parse_mode' | wc -l                                                 # 33 lines: "html"/"HTML" 28, "md" 2, a variable 3
echo $(( $(G -o '\.(send_message|reply|respond|edit|eor|edit_message|send_file)\(' | wc -l) + $(G -o '(^|[^.A-Za-z_])(eor|eod)\(' | wc -l) ))   # 1588
for f in get_display_name get_peer_id pack_bot_file_id resolve_bot_file_id get_input_document get_appropriated_part_size get_input_location; do G -o "\b$f\(" | wc -l; done   # 32 7 7 3 3 2 1
G -o '\.message_link\b' | wc -l                                        # 10 (telethonpatch property)
```

- Request classes by namespace: channels 12 (CreateChannel, DeleteChannel, EditAdmin, EditPhoto, GetAdminedPublicChannels, GetFullChannel, GetParticipant, GetParticipants, InviteToChannel, JoinChannel, LeaveChannel, UpdateUsername), messages 11 (AddChatUser, CreateChat, EditChatDefaultBannedRights, ExportChatInvite, GetAllStickers, GetFullChat, GetHistory, GetStickerSet, ReportSpam, SetHistoryTTL, UploadMedia), phone 5 (CreateGroupCall, DiscardGroupCall, EditGroupCallTitle, GetGroupCall, InviteToGroupCall), contacts 3 (Block, GetBlocked, Unblock), upload 3 (GetFile, SaveBigFilePart, SaveFilePart), auth 2, photos 2, stickers 2, stories 2, account 1, users 1 (GetFullUser), `InvokeWithLayer`.
- Raw requests receive bare ids and usernames, for example `getchat(event.chat_id)` (`U/plugins/vctools.py:35`) and `InviteToChannelRequest(int(channel), [asst.me.username])` (`U/pyUltroid/startup/funcs.py:311`). Telethon resolves them before sending (`T/client/users.py:44`, `T/tl/functions/channels.py:804`).
- Parse mode: all send/edit sites that do not name one use Telethon's client default, which is markdown (`T/client/telegrambaseclient.py:417`).
- Sessions: the user account is a `StringSession` built from the `SESSION` variable; Telethon strings of length 353 are accepted and Pyrogram strings of length 351, 356 or 362 are converted (`U/pyUltroid/startup/connections.py:21-68`). The bot account is the SQLite file session `asst` (`U/pyUltroid/__init__.py:85`). An optional third client comes from `VC_SESSION` (`U/pyUltroid/startup/connections.py:77-95`).
- Error classes: 39 distinct (37 imported, 2 as `errors.X`). 30 are 400-class, 4 are 403-class, plus `FloodWaitError`, `AuthKeyDuplicatedError`, the base `BadRequestError`, and two that are not RPC errors: `AlreadyInConversationError`, `AuthKeyNotFound`.

Distinct imported names per module (gives 54 types, 37 errors, 43 request classes, 5 `telethon.utils` names, 5 event classes):

```sh
python3 - <<'EOF'
import ast,os,collections
c=collections.defaultdict(set)
for d,ds,fs in os.walk('.'):
    ds[:]=[x for x in ds if x not in('.git','rust','__pycache__')]
    for f in fs:
        if f.endswith('.py'):
            for n in ast.walk(ast.parse(open(os.path.join(d,f),encoding='utf-8').read())):
                if isinstance(n,ast.ImportFrom) and n.module and n.module.startswith('telethon'):
                    c[n.module]|={a.name for a in n.names}
for m in sorted(c): print(len(c[m]),m,sorted(c[m]))
EOF
```

### 1.4 Custom pieces

| Piece | What it does | Source |
| --- | --- | --- |
| `UltroidClient(TelegramClient)` | Subclass. `start_client` logs in with a session or bot token and maps `ApiIdInvalidError`, `AuthKeyDuplicatedError`, `AuthKeyNotFound`, `AccessToken*Error` to a log line and `sys.exit()`. Adds `add_handler` (skips duplicates), `run_in_loop`, `run`, `full_name`, `uid`, `parse_id`, `utils`. | `U/pyUltroid/startup/BaseClient.py:28-252` |
| `fast_uploader`, `fast_downloader` | Wrap FastTelethon; in-memory upload cache keyed on size, path, name and account kind; progress callback only above 5 MiB (upload) and 10 MiB (download). | `U/pyUltroid/startup/BaseClient.py:98-216` |
| `FastTelethon.py` (404 lines, copied from mautrix-telegram) | Opens extra `MTProtoSender` connections: 20 above 100 MiB, else `ceil(size / 100 MiB * 20)`. Exports and imports authorization for other DCs. Uses `SaveBigFilePart` above 10 MiB. Calls Telethon private members `_call`, `_get_dc`, `_connection`, `_init_request`, `_proxy`, `_log`. | `U/pyUltroid/fns/FastTelethon.py:84,173-179,254-274,286` |
| `Message.eor`, `Message.try_delete` | Monkey-patched onto Telethon's `Message`. `eor` edits own messages and replies to others, with `link_preview=False`. | `U/pyUltroid/_misc/_wrappers.py:17-65` |
| telethonpatch 0.3.1 (504 lines) | Monkey-patches `TelegramClient.__getattr__` (call any request by name), 13 client methods (group calls, reactions, topics, join, photos), the alias `TelegramClient.read`, `Button.mention`, `Button.web`, `Message.message_link`, `Message.comment`, `Message.react`, `events.JoinRequest`, `events.GroupCall`. Used in this repository: `message_link` 10, `Button.mention` 2, everything else 0. | `P/__init__.py`, `P/methods.py`, `P/custom.py`, `P/events.py` |
| Telethon pin | `telethon>=1.44.0,<1.45`, with the comment that telethon-patch imports button types removed in 1.45. | `U/requirements.txt:2-3` |

## 2. grammers

### 2.1 The project

| Item | Finding | Source |
| --- | --- | --- |
| Crates | `grammers-client`, `-session`, `-mtsender`, `-mtproto`, `-crypto`, `-tl-types`, `-tl-gen` 0.12.0; `grammers-tl-parser` 2.0.0. License MIT OR Apache-2.0. Repository `https://codeberg.org/Lonami/grammers`. | `cargo info <crate>` |
| Releases | 13 since 2020-01-31, all 0.x. In 2026: 0.9.0 (02-21), 0.10.0 (07-02), 0.11.0 (10-15), 0.12.0 (11-08). Repository head is the 0.12.0 commit `e61cf858`. | https://crates.io/api/v1/crates/grammers-client ; https://codeberg.org/Lonami/grammers |
| Own status statement | "It works! The high-level interface is slowly taking shape". | https://codeberg.org/Lonami/grammers/raw/branch/master/README.md |
| Release policy | "The library is in development, but new releases are only cut rarely." A git dependency is recommended; "traits across versions are not always compatible". | `GC/README.md` |
| Raw API and layer | Raw types are "not part of the semantic versioning"; "While patch versions won't change the layer, minor versions will". `Client::invoke` "may break during minor version changes". One layer at a time. | `GC/src/lib.rs:66-80`, `GC/src/client/net.rs:73-78` |
| Layer | 233. Telethon 1.44.0 is 227. | `GT/tl/api.tl:1`; `T/tl/alltlobjects.py:5` |
| Audit | "As far as I know, this code has not been audited". | Codeberg README, as above |
| Contributions | "Please only submit issues and pull requests authored entirely by you or other fellow humans." | Codeberg README, as above |
| Open work | 4 open issues, 24 closed. Open: #17 `updateShortMessage` yields empty PeerMap; #29 panic when getting difference; #32 `catch_up = true` fetches every saved channel one by one; #45 `MessageFwdHeader` unpopulated. 31 `TODO` markers in `grammers-client/src` (`grep -rn TODO`). | https://codeberg.org/Lonami/grammers/issues |
| Accounts | Users: `request_login_code`, `sign_in`, `check_password` (2FA). Bots: `bot_sign_in`. | `GC/src/client/auth.rs:185,242,339,416` |
| Updates | Pull model: `SenderPool { runner, handle, updates }`, then `client.stream_updates(updates, UpdatesConfiguration { catch_up })` and `UpdateStream::next()`. Ordered; gaps resolved if the peers are in the session cache. State is saved only by `sync_update_state()`. | `GC/src/client/updates.rs:29-69`, `GC/examples/echo.rs` |
| Update buffer | 100 updates by default. "When the channel is full, newly received updates are **dropped**." | `GM/src/configuration.rs:63-67,156`, `GM/src/sender_pool.rs:544` |
| File transfer | `upload_file`, `upload_stream`, `download_media`, `iter_download`. Chunks of 512 KiB. Above 10 MiB, 4 concurrent workers. The pool looks up one connection per DC id and creates one only if none exists. | `GC/src/client/files.rs:31-34,212,248,390`, `GM/src/sender_pool.rs:334` |
| Session storages | `SqliteSession` ("This is the recommended option."; needs `libsql`) and `MemorySession`. No string storage. | `GS/src/storages/mod.rs`, `GS/src/storages/sqlite.rs:33`, `GS/Cargo.toml` |
| Same author as Telethon | Both list Lonami Exo as author. Telethon's update-gap module has the same description, nearly word for word, and the same constants (0.5 s gap wait, 15 min timeout, channel-difference limits 100 and 100000). | `GC/Cargo.toml`, `site-packages/telethon-1.44.0.dist-info/METADATA`; `T/_updates/messagebox.py:1-46`; `GS/src/message_box/mod.rs:9-34`, `GS/src/message_box/defs.rs:36,49`, `GM/src/updates_receiver.rs:25-26` |

### 2.2 Feature by feature

Counts in the first column are from section 1. The rendered API lists the same methods and variants: https://docs.rs/grammers-client/0.12.0/grammers_client/client/struct.Client.html and https://docs.rs/grammers-client/0.12.0/grammers_client/update/enum.Update.html.

| Ultroid feature | grammers 0.12.0 | Status | Source |
| --- | --- | --- | --- |
| `NewMessage`, `MessageEdited` delivery | `Update::NewMessage(Message)`, `Update::MessageEdited(Message)` | supported | `GC/src/update/update.rs:23-27` |
| Filters: `pattern`, `incoming`, `outgoing`, `chats`, `forwards`, `func`, `from_users` | None. The caller tests `Message::outgoing()`, `text()`, `peer_id()`, `forward_header()` itself. | missing | `GC/src/message/message.rs:145,246,311,383` |
| `CallbackQuery` (100) | `Update::CallbackQuery`: `data()`, `sender_id()`, `load_message()`, `answer().text()/.alert()/.cache_time()/.edit()/.respond()/.reply()`; also for inline messages. No matching on `data`. | partial | `GC/src/update/callback_query.rs:45-250` |
| `InlineQuery` (24), result builders (39) | `Update::InlineQuery`: `text()`, `offset()`, `answer(results).gallery()/.private()/.cache_time()/.next_offset()/.switch_pm()`. Only an `Article` builder; photo and document results must be raw `InputBotInlineResult`. No pattern matching. | partial | `GC/src/update/inline_query.rs:65-176` |
| `ChatAction` (7) | No variant. Service messages arrive inside `Update::NewMessage` and expose `Message::action()`; other chat updates arrive as `Update::Raw`. | missing | `GC/src/update/update.rs:53-110`, `GC/src/message/message.rs:28,619` |
| `Raw` (2) | `Update::Raw(Raw)`, derefs to `tl::enums::Update`. Variants may be moved out of `Raw` in minor releases. | supported | `GC/src/update/update.rs:41-48`, `GC/src/update/raw.rs` |
| Handler registry, `client.on`, add/remove/list handlers, `StopPropagation` (448 registrations) | None. One stream per client; the application dispatches. | missing | `GC/src/client/updates.rs:29-34`; `grep -rni handler` and `grep -rni dispatcher` over `<grammers-client>/src` return nothing |
| `send_message`, `reply`, `respond` | `Client::send_message(peer, InputMessage)`, `Message::reply`, `Message::respond`. Peer must be a `PeerRef`. | supported | `GC/src/client/messages.rs:593`, `GC/src/message/message.rs:653,689` |
| `edit`, `edit_message` | `Client::edit_message`, `Message::edit`; both return `()`, not the edited message. | supported | `GC/src/client/messages.rs:846-851`, `GC/src/message/message.rs:743` |
| `delete`, `delete_messages`, forward, pin, unpin | `delete_messages` (up to 100 ids), `Message::delete`, `forward_messages`, `Message::forward_to`, `pin_message`, `unpin_message`. | supported | `GC/src/client/messages.rs:873,903,951,1237,1256` |
| `send_file` (69) and its arguments | `upload_file` or `upload_stream`, then `InputMessage::photo`, `document`, `file`, `thumbnail`, `attribute`, `mime_type`, `copy_media`, `photo_url`, `document_url`; `send_album`. No single polymorphic call, no progress parameter, no Bot-API file id input, no upload cache. | partial | `GC/src/message/input_message.rs:200-384`, `GC/src/client/files.rs:390,500`, `GC/src/client/messages.rs:726` |
| `download_media` (85) | `Client::download_media(&d, path)`, `Message::download_media(path)`, `iter_download`. A path is required. No progress parameter. Thumbnails through `Photo::thumbs()`, `Document::thumbs()`. | partial | `GC/src/client/files.rs:162,212`, `GC/src/message/message.rs:855`, `GC/src/media/media.rs:196,351` |
| FastTelethon parallel transfer (26 call sites) | Built in at 4 workers above 10 MiB (see 2.1). Whether a transfer with more connections can be built on the exported `grammers_mtsender::{Sender, connect_with_auth}` is not verified. | partial | `GC/src/client/files.rs:33-34`, `GM/src/lib.rs:38` |
| `download_profile_photo`, profile photo iteration | `Peer::photo(big)` then `download_media`; `iter_profile_photos`. | supported | `GC/src/peer/mod.rs:198`, `GC/src/client/chats.rs:609` |
| `conversation` (22), `get_response`, `wait_event` | None. | missing | `grep -rni conversation <grammers-client>/src` returns 20 lines, all doc comments |
| `inline_query` (13) and `click` (14) | `Client::inline_query(bot, query)` and `InlineResult::send(peer)`. `send` hard-codes `reply_to: None`, `hide_via: false`, `silent: false` and returns `()`; `query_id` is private. | partial | `GC/src/client/bots.rs:21-41,155` |
| Buttons: inline 224, url 36, switch_inline 19, mention 2 | `Button::data`, `Button::url`, `Button::switch` (same chat), `Button::switch_elsewhere`, `Button::webview`, `ReplyMarkup::from_buttons`. User-profile button only through the public `Button.raw` field and `inlineButtonTypeUserProfile`. | supported; mention partial | `GC/src/message/button.rs:15-104`, `GC/src/message/reply_markup.rs:67`, `GT/tl/api.tl` |
| `parse_mode="html"` (28) | Feature `html` (html5ever). Tags: `b`, `strong`, `i`, `em`, `s`, `del`, `u`, `blockquote`, `details`, `code`, `pre`, `a`, `time`. Ultroid's sources use `b`, `strong`, `code`, `a`, `u`, `pre`. No `tg-emoji`. | supported | `GC/src/parsers/html.rs:57-142` |
| Markdown, Telethon's default (about 1,555 sites) | Feature `markdown` (pulldown-cmark). Different dialect; see trap 2. | partial | `GC/src/parsers/markdown.rs:21-130` |
| Participants | `iter_participants(chat)` with `.total()` and `.filter()`; the filter "will apply only on large `Channel` and not small groups". | supported | `GC/src/client/chats.rs:82,220-221,450` |
| Dialogs | `iter_dialogs()`. "Bot accounts will receive an error response when using this method". | supported for users | `GC/src/client/dialogs.rs:140,158` |
| Message history | `iter_messages`, `search_messages` (`query`, `filter`, `sent_by_self`, dates), `get_messages_by_id`. No filter for an arbitrary sender. | partial | `GC/src/client/messages.rs:397,1081,1103,1148` |
| `get_entity`, `get_input_entity`, `parse_id` (107) | `resolve_username(&str)` (network call, documented as expensive), `resolve_peer(PeerRef)`, `Session::peer_ref(PeerId)`, `PeerId::from_bot_api_dialog_id`, `PeerId::to_ambient_ref`. No one call that accepts a username, id, phone, link or `"me"`. | partial | `GC/src/client/chats.rs:370-382,625`, `GS/src/session.rs:67`, `GS/src/peer.rs:186,302` |
| `edit_permissions`, `kick_participant`, `edit_admin`, `get_permissions` | `set_banned_rights`, `kick_participant`, `set_admin_rights`, `get_permissions`. | supported | `GC/src/client/chats.rs:477,534,575,686` |
| `edit_folder` (5) | None. Raw `folders.editPeerFolders` is in the schema. | missing | `GT/tl/api.tl` |
| `send_read_acknowledge`, `delete_dialog`, `action` | `mark_as_read`, `clear_mentions`, `delete_dialog`, `action()`. | supported | `GC/src/client/dialogs.rs:183,226`, `GC/src/client/chats.rs:908` |
| Raw requests (45 classes, 92 sites) | `Client::invoke(&request)`. All 45 names (47 TL methods; two names exist in two namespaces) are in the layer-233 schema with the constructor id of Telethon 1.44.0. Arguments must be complete `Input*` values. | supported | `GC/src/client/net.rs:91`, `GT/tl/api.tl`; script below |
| TL types (74 names, 72 constructors) | 69 keep their constructor id; `User`, `Channel`, `UserFull` differ between the layers. `keyboardButtonCallback`, `keyboardButtonUrl`, `keyboardButtonSwitchInline`, `inputKeyboardButtonUserProfile`, `keyboardButtonSimpleWebView` are absent from layer 233. | supported, shapes differ | `GT/tl/api.tl`; same method as the script below |
| `StringSession` | None (see section 3). | missing | `GS/src/storages/mod.rs` |
| `disconnect()` then `connect()` on one client | `Client::disconnect()` quits the sender pool for every client sharing it. There is no `connect()`. | partial | `GC/src/client/auth.rs:493-496` |
| `get_display_name` (32) | `User::full_name()`; `Peer::name()` returns only the first name for users. | partial | `GC/src/peer/user.rs:142`, `GC/src/peer/mod.rs:156` |
| `get_peer_id` and stored chat ids | `PeerId` uses the Bot-API dialog id format (user id, negated chat id, channel id plus 1000000000000 negated), the same as Telethon's marked ids. | supported | `GS/src/peer.rs:23-25,186-196`; `T/utils.py:1005-1050`; https://core.telegram.org/api/bots/ids |
| `pack_bot_file_id`, `resolve_bot_file_id` (10) | None. | missing | `grep -rni bot_file <grammers-client>/src` returns nothing |
| Error classes (39) | One `InvocationError::Rpc(RpcError { code, name, value, caused_by })`, tested with `.is("NAME")` or a leading or trailing `*`. No type per error. | partial | `GM/src/errors.rs:69-170` |
| Several accounts in one process (user, bot, optional third) | Documented shape is one `SenderPool` and one session per client; a session "should not be reused by multiple pools at the same time". Nothing read addresses several pools in one process. | not verified | `GM/src/lib.rs:20-22`, `GM/src/sender_pool.rs:247` |
| Subclassing and monkey-patching (`UltroidClient`, `Message.eor`) | `Client` and `Message` are structs; equivalents are wrapper types or extension traits written in the port. | not applicable | `GC/src/client/client.rs:35` |

Schema check for the raw requests (run from the repository root with a Python that has Telethon 1.44.0; prints 47 lines, all `same`):

```python
import re,sys,subprocess
from telethon.tl.alltlobjects import tlobjects
api=open(sys.argv[1]).read().split('---functions---')[1]      # argv[1]: <grammers-tl-types-0.12.0>/tl/api.tl
ids={m[1]:int(m[2],16) for m in re.finditer(r'^([\w.]+)#([0-9a-f]+) ',api,re.M)}
used=set(subprocess.run("grep -rhoE --include=*.py --exclude-dir=rust '\\b[A-Z][A-Za-z0-9]+Request\\b' .",shell=True,capture_output=True,text=True).stdout.split())
for o in tlobjects.values():
    if o.__name__ in used and '.functions' in o.__module__:
        ns=o.__module__.split('functions')[1].strip('.'); n=o.__name__[:-7]
        tl=(ns+'.' if ns else '')+n[0].lower()+n[1:]
        print(tl,'same' if ids.get(tl)==o.CONSTRUCTOR_ID else 'DIFFERENT')
```

## 3. Session compatibility

What the Telethon string holds: the character `1`, then URL-safe base64 of `struct.pack('>B4sH256s', dc_id, ip, port, auth_key)` (16-byte IP for IPv6). That is 263 bytes, 352 base64 characters, 353 with the prefix. It holds no user id, no peer cache and no update state (`T/sessions/string.py:9-63`, `T/sessions/memory.py:39-40,95`).

What `grammers-session` 0.12.0 documents:

| Fact | Source |
| --- | --- |
| A session holds "Permanent Authorization Keys bound to each datacenter", datacenter addresses, update state and cached peers. | `GS/src/lib.rs:9-19` |
| `DcOption { id: i32, ipv4: SocketAddrV4, ipv6: SocketAddrV6, auth_key: Option<[u8; 256]> }`, all fields public. | `GS/src/types.rs:22-45` |
| `SessionData { home_dc, dc_options, peer_infos, updates_state }`, all public; `MemorySession: From<SessionData>`; `SessionData::import_to(&session)` copies into any storage. | `GS/src/session_data.rs:18-66`, `GS/src/storages/memory.rs:25` |
| `Session::set_home_dc_id` and `Session::set_dc_option` are public trait methods. On the latter: "Should also be used after generating permanent authentication keys to a datacenter." | `GS/src/session.rs:36,48-53` |
| The sender connects with a stored key when `dc_option.auth_key` is `Some`. | `GM/src/sender_pool.rs:450-451` |
| `Client::is_authorized()` is `updates.getState` not answering 401. | `GC/src/client/auth.rs:105-111` |
| The documentation does not mention Telethon or string sessions. | https://docs.rs/grammers-session/0.12.0/grammers_session/ ; `grep -rni telethon` over `src/` and `README.md` of the four crates returns nothing |

Findings:

- Each field of the string has a slot: `dc_id` to `home_dc` and `DcOption.id`, the key to `DcOption.auth_key`, IP and port to `DcOption.ipv4`/`ipv6` (grammers also has built-in addresses for DC 1 to 5, `GS/src/dc_options.rs`). Ultroid's Pyrogram conversion keeps only `dc_id` and the key, so the same mapping covers it.
- Loading the key is not a documented import path and was not run. Whether Telegram then accepts requests without a new login is **not verified**.
- An import skips two things grammers does at login: caching the own user with `is_self: Some(true)` and storing the first update state (`GC/src/client/auth.rs:113-146`). The update receiver asks for the initial state only when the session knows the own user (`GM/src/updates_receiver.rs:100-101`). The effect of skipping them is not verified.
- If the server answers 404 for a stored key, the pool connects again without it and saves the new key in its place (`GM/src/sender_pool.rs:458-462`, `:393-394`). Telethon raises `AuthKeyNotFound`, which Ultroid turns into "String session expired" and exit (`U/pyUltroid/startup/BaseClient.py:73-78`).
- The `SESSION` variable must stay a Telethon or Pyrogram string (ADR-004). grammers has no string storage, so the decoding is code the port has to own.
- Using one key from the Python and the Rust process at the same time is not verified to be safe. Telegram emits `AUTH_KEY_DUPLICATED` when a non-media DC detects that "an authorized session is sending requests in parallel" "from two separate TCP connections, from the same or different IP addresses"; after it the user "must generate a new auth key and login again" (https://core.telegram.org/api/errors). Telethon's text for the error is "used under two different IP addresses simultaneously" (`T/errors/rpcerrorlist.py:149-152`). grammers says a session "should not be reused by multiple pools at the same time" (`GM/src/sender_pool.rs:247`).
- Access hashes "may not be reused across different accounts or different login/auth sessions of the same account" (https://core.telegram.org/api/peers), so cached hashes are valid only with the login they were obtained under. The string session carries no peer cache; the bot's SQLite session file has an `entities` table (`T/sessions/sqlite.py:86`).
- The bot account needs no import: `bot_sign_in(token, api_hash)` is not interactive (`GC/src/client/auth.rs:185`).

Third-party converters, found with `cargo search grammers`, versions from `cargo info`, descriptions from each crate's README; none was run:

| Crate | Version | What its README says | grammers target |
| --- | --- | --- | --- |
| `opentele2-core` + `opentele2-grammers` | 2.0.0 | Handles "Telethon string sessions and `.session` files"; "grammers 0.11 sessions are in `opentele2-grammers`". | grammers 0.11 |
| `grammpars` | 0.1.0 | Offline conversion "between Telegram Desktop `tdata`, Telethon SQLite (schema 8), and grammers SQLite (schema 1)". String sessions are not mentioned. | not stated |
| `grammers-stringsession` | 0.1.1 | A base64 string format for grammers sessions with its own 3-byte header. "Inspired by" Telethon's `StringSession`; it does not claim to read Telethon strings. | `~0.9.0`, `~0.10.0` |

## 4. Alternatives

### 4.1 TDLib from Rust

TDLib is Telegram's own client library in C++ (Boost Software License; version 1.8.70 in its README's example).
Documented differences from Telethon:

- "TDLib takes care of all network implementation details, encryption and local data storage" (https://core.telegram.org/tdlib). It is used through C functions; "for most use cases we suggest to use the JSON interface" (https://raw.githubusercontent.com/tdlib/td/master/README.md).
- Its interface is the TDLib API in `td_api.tl`, "the descriptions of all available TDLib methods and classes" (https://core.telegram.org/tdlib/getting-started). That page describes no way to send MTProto TL requests. Whether each of Ultroid's 45 raw requests and 74 TL types has a TDLib counterpart is not verified.
- Login is a state machine that starts at `authorizationStateWaitTdlibParameters`; the application passes `api_id`, `api_hash` and a `database_directory` for TDLib's own database (same page). No import of an existing auth key is described there: not verified.
- Building needs a C++17 compiler, OpenSSL, zlib, gperf and CMake (TDLib README). To talk to Telegram, every crate below needs the `tdjson` library at link or run time.

| Crate | Version (`cargo info`) | License | Last release | What the crate says | Source |
| --- | --- | --- | --- | --- | --- |
| `tdlib-rs` | 1.4.0 | MIT OR Apache-2.0 | 2026-04-12 | Wrapper with generated types. "Current supported TDLib version: 1.8.61". Can download a prebuilt TDLib for Linux, macOS, Windows (x86_64, arm64). | https://crates.io/crates/tdlib-rs/1.4.0 |
| `rtdlib` | 1.8.70 | MIT | 2026-11-05 | "Rust types for TDLib" 1.8.69; the `sys` feature links `libtdjson`; a dev build "peaks at about 6 GB RSS". | https://crates.io/crates/rtdlib/1.8.70 |
| `telegram-client` | 1.8.70 | MIT | 2026-11-05 | Client with async API on `rtdlib`; needs `libtdjson` 1.8.69. | https://crates.io/crates/telegram-client/1.8.70 |
| `tdlib` | 0.10.0 | MIT OR Apache-2.0 | 2023-09-24 | Wrapper; requires system `tdjson` 1.8.19 (`[package.metadata.system-deps]`). | https://crates.io/crates/tdlib/0.10.0 |
| `rust-tdlib` | 0.4.3 | MIT | 2023-04-09 | "Currently, supports tdlib v1.8.0." | https://crates.io/crates/rust-tdlib/0.4.3 |

FFI and type crates verified with `cargo info` only, READMEs not read: `tdjson` 0.2.2, `tdjson-sys` 0.1.5, `tdlib-sys` 0.2.0, `tdlib-json-sys` 0.1.0, `tdlib-futures` 0.1.0, `tdlib-types` 0.1.0, `tdlib-bindgen` 0.3.0, `fuyubot-tdlib-sys` 0.1.3. `cargo search` lists `tdlib-rust` 0.0.0, but `cargo info tdlib-rust` reports it is not in the registry.

### 4.2 Other MTProto implementations in Rust

Found with `cargo search mtproto`; versions and licenses from `cargo info`; feature statements are each project's own README and were not checked against its code.

| Crate | Version | License | First and last release | What the README states | Source |
| --- | --- | --- | --- | --- | --- |
| `ferogram` | 0.6.7 | MIT OR Apache-2.0 | 2026-03-29, 2026-11-10 (27 versions) | Layer 233. Bots and users; "a dispatcher with composable filters, FSM for multi-step conversations", string/SQLite sessions, parallel transfers with progress, raw `invoke()`. | https://crates.io/crates/ferogram/0.6.7 |
| `vaegram` | 0.3.0 | Apache-2.0 | 2026-10-27, 2026-11-14 (3 versions, 102 downloads) | Layer 233. `on_*` handlers with filters; conversations with `ask`, `listen`, `wait_for_click`; `invoke` for raw functions; transfers over several connections. | https://crates.io/crates/vaegram/0.3.0 |
| `layer-client` | 0.5.0 | MIT OR Apache-2.0 | 2026-02-21, 2026-04-12 (15 versions) | "This project is no longer maintained or supported"; points to ferogram (same author). | https://crates.io/crates/layer-client/0.5.0 |
| `blazegram` | 0.4.2 | MIT | 2026-03-10, 2026-04-16 (5 versions) | "Declarative Telegram bot framework", built on `grammers-client`. | https://crates.io/crates/blazegram/0.4.2 |

Release dates are from `https://crates.io/api/v1/crates/<name>`. Checked with `cargo info` only and not read further: `tellers-mtproto` 0.1.0+layer.223 ("Generated Rust types"), `clacks_mtproto` 0.0.5 ("minimal wrappers for telegram's mtproto serialization"), `compio-mtproto` 0.1.0, `mtproto` 0.0.0, `mini-telegram` 0.1.17 (describes itself as an MTProto server).
Structural difference from Telethon as the READMEs of ferogram and vaegram describe them: both have handler registration with filters and a conversation mechanism built in, which grammers leaves to the application.

## 5. Semantic traps

Each item: what Telethon does, what grammers does by default, what in Ultroid depends on it.

1. **Entity offsets are UTF-16 code units.** "UTF-16 is used when computing the length and offsets of entities"; code points outside the BMP "count as 2" (https://core.telegram.org/api/entities). Telethon converts with `add_surrogate` (`T/helpers.py:39-49`). grammers counts with `encode_utf16().count()` in its parsers (`GC/src/parsers/common.rs:21-23`), but `Message::fmt_entities()` returns the raw offsets with the note "TODO correct the offsets and lengths to match the byte offsets" (`GC/src/message/message.rs:467-468`). Rust `str` indexes bytes. Ultroid slices by entity in `get_entities_text` (2 sites) and forwards raw entities to a quote API (`U/pyUltroid/fns/misc.py:335-341`).
2. **Markdown dialect.** Telethon: `**` bold, `__` italic, `~~` strike, `` ` `` code, ```` ``` ```` pre, `[text](url)`; the parser "does not support nesting", removes the delimiters and link syntax, strips leading and trailing whitespace, and leaves the rest of the text, newlines included, as typed (`T/extensions/markdown.py:2,17-25,61-133`). grammers: CommonMark through `pulldown_cmark::Parser::new`, with arms only for text, code, strong, emphasis, link, code block, hard break and paragraph end; everything else falls into `_ => {}` (`GC/src/parsers/markdown.rs:28-130`). Its own test maps `__strong__` to bold (`:284`). There is no arm for strikethrough or for `Event::SoftBreak` ("A soft line break.", https://docs.rs/pulldown-cmark/0.13.6/pulldown_cmark/enum.Event.html), so a single `\n` inside a paragraph adds nothing to the output text. This is read from the source and not run. Ultroid: of 494 keys in `strings/strings/en.yml`, 142 lines contain `\n` (`grep -c '\\n'`) and 2 use `__` (`grep -c '__'`); there are 24 language files.
3. **Default parse mode.** Telethon parses every outgoing text as markdown unless told otherwise (`T/client/telegrambaseclient.py:417`). In grammers a `&str` becomes `InputMessage::new().text(..)`, plain text (`GC/src/message/input_message.rs:406-412`); `.markdown()` and `.html()` are opt-in features. About 1,555 Ultroid call sites rely on the default.
4. **`event.text` is not the raw text.** Telethon's `Message.text` is "formatted using the client's default parse mode", so entities come back as markdown; `raw_text` is the plain text (`T/tl/custom/message.py:395-426`). grammers' `Message::text()` is the plain text; `markdown_text()` emits CommonMark (`_` for italic) and drops underline and strike (`GC/src/message/message.rs:383,411-419`, `GC/src/parsers/markdown.rs:176-214`). Ultroid reads `.text` on event-like variables 183 times and `.raw_text` 3 times (`G -o '\b(event|ult|e|reply|r|msg|message|x|ok|wt|rep|replied|reply_message|res|response)\.text\b' | wc -l`). Notes store `wt.text`, that is Telethon-dialect markdown, in the database (`U/plugins/notes.py:59-63`, `U/pyUltroid/dB/notes_db.py:15-21`), and ADR-004 keeps stored values unchanged.
5. **Link previews.** Telethon: `link_preview=True` on `send_message` and `edit_message` (`T/client/messages.py:636,1094`). grammers: `link_preview` defaults to `false` (`GC/src/message/input_message.rs:21-27`, `GC/src/client/messages.rs:629`). Ultroid's `eor` already defaults to `False`; `reply`, `respond`, `send_message` and `edit` (678 sites) use Telethon's default unless they pass `link_preview=` (53 uses in the code base).
6. **Flood wait.** Telegram: 420 `FLOOD_WAIT_X`, "A wait of X seconds is required" (https://core.telegram.org/api/errors). Telethon sleeps and retries when X is at most `flood_sleep_threshold` (60), up to `request_retries` (5), remembers the wait per request type and refuses early, and retries server errors after 2 s (`T/client/telegrambaseclient.py:255,260`, `T/client/users.py:46-58,70,104,121`). grammers' default `AutoSleep` has threshold 60 s, `tries` 1, treats I/O errors as a 1 s flood, and does not retry 500s (`GM/src/configuration.rs:176-208`). The error is `RpcError { code: 420, name: "FLOOD_WAIT", value: Some(x) }`, not a class (`GM/src/errors.rs:85-92`). Ultroid's own handler disconnects the user client, sleeps `seconds + 10` and reconnects (`U/pyUltroid/_misc/_decorators.py:128-143`); grammers has no reconnect on the same client (2.2).
7. **Update gaps and state.** Telegram: a gap "must be filled", after waiting "up to 0.5 seconds", with `updates.getDifference` or `getChannelDifference`; also after 15 minutes without updates (https://core.telegram.org/api/updates). Both libraries implement this. Differences: grammers resolves a channel gap only if the channel's hash is in the session ("cannot getChannelDifference as we're missing its hash", `GM/src/updates_receiver.rs:60-80`; `GC/src/client/updates.rs:63-65` recommends calling `iter_dialogs` once after login); it drops updates when its 100-slot buffer is full, where Telethon's queue is unbounded (`T/client/telegrambaseclient.py:430`); it saves state only on `sync_update_state()`. `catch_up` is off by default in both (`T/client/telegrambaseclient.py:270`, `GM/src/configuration.rs:163-167`); with it on, open issue #32 reports hundreds of sequential `getChannelDifference` calls at start (https://codeberg.org/Lonami/grammers/issues/32).
8. **Peers and access hashes.** An `access_hash` is "required to interact with peers" (https://core.telegram.org/api/peers). Telethon feeds every RPC result into its entity cache (`T/client/users.py:83,93`) and resolves an id, username, phone or link in several steps, ending with a network call (`T/client/users.py:418-472`); with a `StringSession` that cache lives in memory only (`T/sessions/memory.py:39`). grammers wants a `PeerRef` (id plus hash) for every call and caches peers only from "the high-level methods" (`GC/src/client/client.rs:39-44`), not from raw `invoke` results. Open issue #17 (https://codeberg.org/Lonami/grammers/issues/17): private messages arriving as `updateShortMessage` carry no peers, so `sender()` and `peer()` return `None` unless cached. Ultroid passes stored integer ids and usernames directly in 107 resolver calls and in raw requests.
9. **User and bot surfaces differ.** `messages.getInlineBotResults` and `messages.getDialogs`: "Only users can use this method" (https://core.telegram.org/method/messages.getInlineBotResults, https://core.telegram.org/method/messages.getDialogs). Reply markup works only for bots (`GC/src/message/input_message.rs:140-141`). `getChannelDifference` limits differ (https://core.telegram.org/method/updates.getChannelDifference). Ultroid runs both kinds of account in one process and shows buttons from the user account by querying its own bot inline and clicking the result; `BOTMODE`, `USER_MODE` and `DUAL_MODE` change which client handles what (`U/pyUltroid/__init__.py:54-97`).
10. **Service messages.** Telethon's `NewMessage` skips them ("We don't care about MessageService's here", `T/events/newmessage.py:101`) and `ChatAction` reports joins, leaves, pins and title changes (`T/events/chataction.py:35-111`). grammers builds `Update::NewMessage` from any message, service messages included (`GC/src/update/update.rs:53-110`). A port that treats every `NewMessage` as text would run command and filter logic on service messages.
11. **Outgoing and sender.** Telethon sets `out = True` on messages in Saved Messages that are not forwards (`T/tl/custom/message.py:326-329`); grammers returns the raw `out` flag (`GC/src/message/message.rs:145-151`). For an outgoing private message without `from_id`, grammers' `sender_id()` is the sentinel `PeerId::self_user()`, which has no numeric id (`GC/src/message/message.rs:272-291`, `GS/src/peer.rs:165,245-246`). Ultroid decides who may run a command from `ult.out` and `ult.sender_id` (`U/pyUltroid/_misc/_decorators.py:96-106`).
12. **Dispatch order and errors.** Telethon runs each update in its own task, calls matching handlers in registration order, stops on `StopPropagation`, and logs handler exceptions (`T/client/updates.py:289,590-618`). `conversation()` hooks into the same dispatcher, defaults to a 60 s timeout and is exclusive per chat (`T/client/updates.py:572-588`, `T/client/dialogs.py:480-483`). None of this exists in grammers; the echo example spawns one task per update (`GC/examples/echo.rs`).
13. **Layer drift.** Raw types move with every grammers minor release (2.1). Ultroid is pinned below Telethon 1.45 because of telethon-patch, and the button constructors it still imports are gone from layer 233 (2.2).
14. **Stored Bot-API file ids.** `pack_bot_file_id` is called at 7 sites (notes, filters, snips, greetings, assistant commands, button posts); notes write the result to the database (`U/plugins/notes.py:58-63`). The string is run-length-encoded base64 of `struct.pack('<iiqqb', type, dc_id, id, access_hash, 2)` for documents and carries no file reference (`T/utils.py:1236-1281`). ADR-004 keeps stored values unchanged, so the port needs its own encoder and decoder. Files can also need a fresh reference: `FILE_REFERENCE_EXPIRED` (https://core.telegram.org/api/files); grammers notes "TODO handle maybe FILEREF_UPGRADE_NEEDED" (`GC/src/client/files.rs:100`).
15. **Return values and names.** `Message::edit` and `InlineResult::send` return `()` where Telethon returns the message (Ultroid keeps one such result to delete later, `U/plugins/pmpermit.py:302`). `download_media()` with no argument picks a file name in Telethon and returns the path (`T/client/downloads.py:332-357`); grammers requires a path (44 Ultroid sites pass none).

## Not verified

- Anything at run time. No request was sent to Telegram. A test account is needed (ADR-001).
- That a Telethon auth key loaded into `DcOption.auth_key` keeps the user logged in, and that updates work after such an import. Confirm with a test account: build `SessionData` from a string session, call `is_authorized()`, send and receive.
- Whether Telegram requires the same `api_id` or `initConnection` values for an existing key. No statement found on the pages read (`/api/errors`, `/api/peers`, `/api/updates`).
- Whether Python (Telethon) and Rust (grammers) can hold the same key at the same time during a gradual migration.
- grammers markdown behaviour for single newlines, `~~`, `__` and other CommonMark constructs on Ultroid's real strings. Confirm with a unit test of `parse_markdown_message` over `strings/strings/*.yml`.
- Transfer speed of grammers (4 workers, one connection per DC) against FastTelethon (up to 20 connections), and whether more connections can be opened through `grammers-mtsender`.
- grammers' behaviour after a dropped network connection; only the `ConnectionClosed` marker was seen (`GS/src/message_box/defs.rs:158-160`).
- Several grammers clients (user, bot, optional third account) running in one process.
- Feature claims of ferogram and vaegram (READMEs only), and whether either reads Telethon sessions.
- TDLib: a counterpart for each raw request, import of an existing key, and building `tdjson` for Termux (ADR-010).
- grammers on Termux/Android: the source has an Android branch for locale detection (`GM/src/configuration.rs:134`); no build was attempted.
- Telethon and telethon-patch use in code outside this checkout (the UltroidAddons repository, the `vcbot` addon and `pytgcalls`, `U/pyUltroid/startup/loader.py:124-144`).
- A changelog for grammers: none found in the repository's top-level listing, so the breaking changes between 0.9 and 0.12 were not reviewed.
- READMEs and sources of the low-level TDLib FFI crates and of `tellers-mtproto`, `clacks_mtproto`, `compio-mtproto`, `mtproto`, `mini-telegram`.
- The third-party session converters in section 3: none was built or run, and none targets grammers 0.12 by its own statement.
