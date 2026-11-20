# Plugin and assistant dependencies: Rust stand-ins

Surveyed on 2026-11-20 with `cargo 1.97.0`. Scope: the Python packages that `plugins/`, `assistant/`
and the helpers they call pull in, most of them for one plugin. Telethon, the database drivers and
the configuration packages are not covered here.

Nothing was compiled or run. Every rating comes from registry metadata, documentation and reading
source. Sources are abbreviated in the tables:

- **ci**: `cargo info <crate>` (existence, version, description, licence). Where it printed an older
  version followed by "(latest X)", X is given. **cs**: `cargo search`.
- **io**: the crates.io API (release dates, download counts).
- **src**: the crate's source as cargo downloaded it.
- **PyPI**: the PyPI JSON API. **sdist**: the package's source archive from PyPI.
- URLs: pages read on the survey date.

## Summary

- 32 packages were asked for. By fit: **good 11**, **partial 10**, **none 7**, **not verified 4**.
- Of the 7 `none`: `glitch-me` and `pyrogram` have no crate with the same function; `safety`, `enhancer`,
  `instagrapi`, `tgcrypto` and `lxml` have nothing to replace (app-specific code, or no call site in
  this checkout).
- The 4 `not verified` are Akinator, Twitter/X, the Cloudflare bypass and voice chats: unofficial
  APIs or a native media stack, none of which could be exercised here.
- 9 further third-party packages are imported from `plugins/` or `assistant/`: 6 good, 2 partial,
  and Telethon, which ADR-005 assigns to `research/telethon.md`.
- Plugins with the weakest stand-ins: the voice-chat plugin set (`vcbot/`, cloned at run time),
  `plugins/pdftools.py` (document scan), `plugins/twitter.py`, `assistant/games.py` (Akinator), the
  `sticker` search in `plugins/specialtools.py`, and the browser-driven commands (`rayso` in
  `plugins/beautify.py`, `webshot` in `plugins/tools.py`).
- Thirteen of the 32 are a front for a program, a native library or a web service that Rust would
  call directly ("Programs and services").

Fit: `good` = a maintained crate, or the same program or service, covers every call Ultroid makes.
`partial` = some calls are missing, or the output is known to differ. `none` = no crate found, or
nothing to replace (the note says which). `not verified` = a crate exists but its fit could not be
confirmed.

## The packages

| Package | Used by | Used for | Rust stand-in | Fit | Note and source |
| --- | --- | --- | --- | --- | --- |
| `akipy` | `assistant/games.py:20` | Akinator game: `start_game(child_mode=False)` (`:76`), `answer` (`:100`), `question`, `name_proposition`, `photo` (`:103-106`) | `akinator-rs` 0.1.13 | not verified | Unofficial API. Crate last released 2024-01-27 (io) and calls `/new_session`, `/answer_api` (src); akipy 1.7.1 (2026-10-21, PyPI) calls `/game`, `/answer`, `/exclude` (sdist). See "Unofficial APIs". |
| `twikit` | `plugins/twitter.py:33` | Login with username, e-mail, password and a cookie file (`:62-67`); `create_tweet` (`:83`), `get_tweet_by_id` (`:106`, `:172`), `get_user_by_screen_name` (`:130`) | `twikit-rs` 0.1.0; also `agent-twitter-client` 0.1.2, `xplore` 0.1.12 | not verified | All scrape X's private web API, as twikit does. `twikit-rs` has the four calls (src); one release (2026-06-09), 94 downloads, GPL-3.0-only (ci, io). See "Unofficial APIs". |
| `yt-dlp` | `pyUltroid/fns/ytdl.py:20`; callers `plugins/youtube.py:22`, `assistant/ytdl.py:29` | `extract_info` (`:258`), `download` (`:251`), search by `ytsearchN:` (`:48`) | the `yt-dlp` program; wrappers `yt-dlp` 2.10.0, `youtube_dl` 0.10.0 | good | Both crates run the executable and read its JSON (their READMEs); `yt-dlp` is GPL-3.0-only (ci). See "Programs and services". |
| `youtubesearchpython` | `pyUltroid/fns/ytdl.py:16` | `Playlist(id).videos` in `get_videos_link` (`:262-272`), which nothing in this checkout calls; `VideosSearch` is imported and unused | the `yt-dlp` program (`--flat-playlist -J`) | good | Search already goes through yt-dlp (`:45-48`). PyPI last release 2022-06-23; repository archived 2022-06-30 (github.com/alexmercerind/youtube-search-python). |
| `playwright` | `plugins/tools.py:50`, `plugins/beautify.py:115-116` | Full-page screenshot of a URL (`tools.py:436-440`); drive ray.so, click "Export as PNG", save the download (`beautify.py:151-178`) | `playwright-rs` 0.21.1; or `chromiumoxide` 0.9.1, `headless_chrome` 1.0.22 | good | Unofficial, pre-1.0 client of the same Playwright server (README). `screenshot` with `full_page`, `wait_for_load_state`, `query_selector`, `expect_download`, `Download::save_as` exist; `wait_for_selector` does not, `Locator::wait_for` does (src). |
| `htmlwebshot` | `plugins/misc.py:31`, `plugins/tools.py:54`, `plugins/writer.py:20` | HTML or URL to PNG: `WebShot(..).create_pic_async` (`misc.py:135-136`, `tools.py:447-450`, `writer.py:53-55`) | the `wkhtmltoimage` program; `wkhtmlapp` 1.2.1 wraps it | good | The package only runs `wkhtmltoimage` (sdist 0.1.2). That program's repository was archived on 2023-01-02 (github.com/wkhtmltopdf/wkhtmltopdf). |
| `img2html` | `plugins/misc.py:35` | `Img2HTMLConverter(char=..).convert(img)` (`:133-134`): HTML of coloured characters, then rendered by htmlwebshot | `artem` 3.0.0 | partial | `cs img2html`: no results. `artem` writes coloured ASCII as HTML but picks characters by brightness (README); img2html repeats the given characters, each coloured with its block's average (sdist 0.0.7). Ultroid installs a fork (`resources/startup/optional-requirements.txt:10`), not read. |
| `glitch-me` | `plugins/glitch.py:21` | The import is a probe; the work is the command `glitch_me gif --line_count 200 -f 10 -d 50` (`:37`) | none found | none | Not on PyPI (404); installed from github.com/1Danish-00/glitch_me (`:24`), which needs Pillow and tqdm (its `setup.py`). `png-glitch` 0.6.0 edits PNG scan lines (README) and has no GIF output (src). |
| `profanitydetector` | `plugins/_chatactions.py:25`, `plugins/nsfwfilter.py:22` | `detector(text)` returns `(word, found)` (`_chatactions.py:219`, `nsfwfilter.py:66`) | no crate needed: `reqwest` 0.13.5 and a loop | good | The whole package downloads a word list from `git.io/JZmJ6` on every call and compares whitespace-separated words, ignoring case (sdist 0.2). The link still redirects to a gist of 1,845 lines. `rustrict` 0.7.39 is another filter and would change results. |
| `qrcode` | `plugins/qrcode.py:28` | `QRCode(error_correction=ERROR_CORRECT_H)`, `QRCode(box_size=5)`, `make_image` (`:53-56`, `:79-82`) | `qrcode` 0.15.0 | good | `with_error_correction_level`, `module_dimensions`, `quiet_zone`, `image` feature (src, ci). Decoding in the same plugin is OpenCV. |
| `pypdf2` | `plugins/pdftools.py:55` | Split into one-page PDFs (`:87-96`), page text (`:146-171`), merge (`:347-353`) | `lopdf` 0.47.0 | partial | See "Other partial cases". |
| `cv2` | `plugins/imagetools.py:60`, `pdftools.py:33`, `qrcode.py:24`, `stickertools.py:32`, `tools.py:45`, `mediatools.py:37`; `pyUltroid/fns/tools.py:578`, `fns/misc.py:50` | Image effects, document scan, first video frame, QR decode | `opencv` 0.102.0; pure Rust: `image` 0.25.10, `imageproc` 0.27.0, `rqrr` 0.11.0, `kmeans_colors` 0.7.1 | partial | `opencv` binds the same C++ library and lists every call (src `docs/`), but needs OpenCV 4.x or 5.x and Clang at build time (README). The pure-Rust crates cover part. See "Image stack". |
| `skimage` | `plugins/pdftools.py:227`, `:296` | `threshold_local(gray, 11, offset=10, method="gaussian")` (`:239`, `:310`) | `imageproc` 0.27.0 `contrast::adaptive_threshold` | partial | scikit-image uses a weighted (Gaussian) local mean minus a constant (scikit-image.org API page); imageproc uses the plain mean of a square block (src). |
| `numpy` | `plugins/imagetools.py:64`, `pdftools.py:34`, `stickertools.py:36`; `pyUltroid/fns/tools.py:47`, `fns/misc.py:54` | `zeros`, `array`, `uint8`, `dstack`, `argmin`, `argmax`, `diff`, `sqrt` (`fns/tools.py:566-589`, `stickertools.py:399-405`) | `ndarray` 0.17.2, `ndarray-stats` 0.7.0 | good | Glue between OpenCV and Pillow buffers. `diff`, `stack` in `ndarray`; `argmin`, `argmax` in `ndarray-stats` (src). |
| `PIL` | 11 plugins (e.g. `plugins/resize.py:17`, `stickertools.py:40`, `writer.py:21`), `assistant/ytdl.py:14`, `pyUltroid/fns/tools.py:33`, `fns/misc.py:45` | Open, convert, resize, crop, paste, save; text on images; PNG, JPEG, WebP, ICO, PDF output | `image` 0.25.10, `imageproc` 0.27.0, `ab_glyph` 0.2.32; gaps: `webp` 0.3.1, `printpdf` 0.12.13, `csscolorparser` 0.9.2 | partial | See "Image stack". |
| `bs4` | `plugins/misc.py:28`, `search.py:29`, `specialtools.py:40`; `assistant/callbackstuffs.py:17`, `inlinestuff.py:15`; `pyUltroid/fns/misc.py:59` | Page scraping: `find_all`, `find`, `.text`, attributes, `findNext` (`plugins/misc.py:52-106`), always with `"html.parser"` | `scraper` 0.29.0 | partial | See "Other partial cases". |
| `tabulate` | `plugins/pmpermit.py:51` | One call: `tabulate(users, headers=[..], showindex="always")` (`:590`); a fallback exists (`:593`) | `tabulate-rs` 0.1.0; table crates `tabled` 0.22.0, `comfy-table` 8.0.1 | partial | `tabulate-rs` states parity with python-tabulate 0.9.0 and has `ShowIndex` (README, src); one release (2025-11-03), 147 downloads (io). PyPI tabulate is 0.10.0. The other two have their own styles. |
| `telegraph` | `pyUltroid/fns/tools.py:52`; used at `plugins/utilities.py:519`, `plugins/mediatools.py:52` | `Telegraph(token, domain="graph.org")`, `create_account`, `get_access_token`, `create_page` (`fns/tools.py:612-646`) | `telegraph-rs` 0.8.0-rc1 (stable 0.7.0); or `reqwest` 0.13.5 | good | Documented HTTPS API with `createAccount`, `createPage` (telegra.ph/api). The rc has `api_url` for another host and `html_to_node` (src); 0.7.0 was not read. |
| `catbox` | `plugins/__init__.py:28`, `assistant/callbackstuffs.py:24`, `pyUltroid/fns/misc.py:16` | `CatboxUploader().upload_file(path)` returns a URL (`plugins/__init__.py:54-56`); called from a dozen plugins | `catbox` 0.8.2 | good | Both post `reqtype=fileupload` to `catbox.moe/user/api.php` (sdist 2.9; crate src). Crate last released 2024-01-12 (io). |
| `cloudscraper` | `plugins/specialtools.py:43` | `create_scraper().get(..)` on combot.org (`:63`, `:272`), retried when the Cloudflare page comes back (`:278-281`) | `cloudscraper-rs` 0.2.0; also `ghostwire` 1.1.0, `flaresolverr-rs` 0.3.1 | not verified | See "Unofficial APIs". |
| `googleapiclient` (`apiclient`) | `pyUltroid/fns/gDrive.py:13-14`; used by `plugins/gdrive.py:33`, `assistant/callbackstuffs.py:20` | Drive API v2: `files().insert` with resumable upload, `get`, `get_media`, `list`, `permissions().insert` (`gDrive.py:82-238`) | `google-drive2` 7.0.0+20251218 | good | Generated from Google's `drive:v2` schema; has `FileInsertCall` with `upload_resumable`, `FileGetCall`, `FileListCall`, `PermissionInsertCall`, `File.title` (src). 145 recent downloads; `google-drive3` 7.0.0+20251218 is the v3 crate (io). |
| `oauth2client` | `pyUltroid/fns/gDrive.py:16-18` | Out-of-band OAuth flow (`:37`, `:54-69`), token file through `Storage` (`:55`, `:73`) | `yup-oauth2` 12.1.2 | partial | See "Other partial cases". PyPI last release 2018-09-07. |
| `httplib2` | `pyUltroid/fns/gDrive.py:15` | HTTP transport for the two rows above (`:75-78`) | none needed | good | `google-drive2` brings its own HTTP stack (`hyper-rustls` in its manifest). |
| `pytgcalls` | `pyUltroid/startup/loader.py:126` (import probe only) | The user is the VcBot repository cloned into `vcbot/` (`loader.py:135`): `GroupCallFactory`, `join`, `start_audio`, `stop` | `ntgcalls` 4.0.0-alpha01 (stable 3.0.7); `tgcalls` 0.4.0-beta1 (stable 0.3.0) | not verified | See "Programs and services". |
| `pyrogram` | `resources/session/ssgen.py:119` | Interactive login and `export_session_string()` (`:136-141`). The app reads Pyrogram strings itself, without the package (`pyUltroid/startup/connections.py:21`, `:46-67`) | none found | none | `cs pyrogram`: no results. Repository archived 2024-12-23, "no longer maintained or supported" (github.com/pyrogram/pyrogram). A Rust generator would use the library chosen under ADR-005; `MAP.md` keeps this unit in Python. |
| `black` | `plugins/devtools.py:27` | `black.format_str(cmd, mode=black.Mode())` on code given to `eval` (`:234-239`) | `ruff_python_formatter` 0.0.23 | partial | "This is an internal component crate of Ruff" (ci). Ruff's formatter is "designed as a drop-in replacement for Black"; on Black-formatted projects "> 99.9% of lines are formatted identically" (docs.astral.sh/ruff/formatter). Only relevant while `eval` runs Python (ADR-006). |
| `safety` | `pyUltroid/startup/__init__.py:97` | `from safety.tools import *`; `call_back()` is called at `plugins/bot.py:217`, `:336` and `assistant/callbackstuffs.py:323` | none needed | none | Not the PyPI package `safety`. See "`safety` and `enhancer`". |
| `enhancer` | `requirements.txt:9`, `resources/startup/optional-requirements.txt:8` | Never imported by that name: it is the distribution that installs the `safety` module | none needed | none | See "`safety` and `enhancer`". |
| `lottie` | no import; the script `lottie_convert.py` is run at `pyUltroid/fns/tools.py:763`, `:766`, `:791`, `plugins/stickertools.py:427`, `plugins/utilities.py:506` | Animated stickers: `.tgs` to and from `.json`, `.tgs` to webp, png, gif, mp4 (`fns/tools.py:968-982`) | `flate2` 1.1.11; `rlottie` 0.5.4, `lottieconv` 0.3.1 | partial | See "Programs and services". |
| `instagrapi` | nothing; `resources/startup/optional-requirements.txt:9` | Unused in this checkout: no `plugins/instagram.py`; the name survives in an exclusion list (`pyUltroid/__main__.py:65`) | none verified | none | Nothing to replace. Unofficial private API (PyPI summary). `qinstagram` 0.1.1, `rocketapi` 0.1.1, `instagram-scraper-rs` 0.1.0 exist (ci); none was read. |
| `tgcrypto` | nothing; `optional-requirements.txt:30`, and installed next to pyrogram by `resources/session/ssgen.py:124` | Unused in this checkout. It gives Pyrogram AES-256 in IGE, CTR and CBC modes (sdist README) | `grammers-crypto` 0.12.0; `aes` 0.9.4 with `ige` 0.2.1, `ctr` 0.10.1, `cbc` 0.2.1 | none | Nothing to replace: a Rust Telegram library carries its own crypto. `grammers-crypto` has `ige_encrypt`, `ige_decrypt` (src). |
| `lxml` | nothing; `optional-requirements.txt:16` | Unused in this checkout: every BeautifulSoup call passes `"html.parser"`. twikit lists it as a dependency (PyPI) | `libxml` 0.3.24 | none | Nothing to replace. `libxml` wraps the same libxml2 (ci). |

## Programs and services

For these packages the question is what to call, not which crate to pick.

| Python package | What it fronts | What a Rust program would call |
| --- | --- | --- |
| `yt-dlp` | It is the program; `YoutubeDL(opts)` is its Python API (`pyUltroid/fns/ytdl.py:251`, `:258`) | The `yt-dlp` executable: `-J` for metadata, `--flat-playlist` for search and playlists, `-f`, `-o`, `-x --audio-format --audio-quality`, `--embed-metadata`, `-u`, `-p` |
| `youtubesearchpython` | YouTube's web pages | The same `yt-dlp` executable |
| `playwright` | A Node.js server that drives Chromium, Firefox or WebKit | The same server through `playwright-rs`, or Chromium's DevTools protocol through `chromiumoxide` or `headless_chrome` |
| `htmlwebshot` | The `wkhtmltoimage` binary | The same binary, or a browser as above |
| `lottie` | python-lottie's `lottie_convert.py` script | gzip for `.tgs`, the rlottie C++ library for frames, `ffmpeg` for video |
| `glitch-me` | The `glitch_me` command | The same command |
| `pytgcalls` | Telegram's C++ call library (WebRTC) | A native call library through `ntgcalls`, plus `ffmpeg` |
| `catbox`, `telegraph`, the Drive stack, `profanitydetector` | HTTPS services | The same HTTPS endpoints |

**yt-dlp.** All the flags above are in its README (github.com/yt-dlp/yt-dlp). The README also lists a
standalone `yt-dlp_linux` binary, lists `ffmpeg` as "Required for merging separate video and audio
files", and says full YouTube support needs `yt-dlp-ejs` and a JavaScript runtime such as deno.
The crate `yt-dlp` 2.10.0 downloads yt-dlp and ffmpeg itself; `youtube_dl` 0.10.0 (last release
2024-04-16) runs a yt-dlp it is pointed at. Pure-Rust extractors exist (`rusty_ytdl` 0.7.4, last
release 2024-08-10; `rustypipe` 0.11.4, GPL-3.0) but handle YouTube only, and `yta`/`ytv` accept
"(youtube/any) link" (`plugins/youtube.py:10`).

**Browser.** Playwright's own bindings are JavaScript/TypeScript, Python, Java and .NET
(playwright.dev/docs/languages); `playwright-rs` is third-party. Its README describes "a thin JSON-RPC
client to the same server", a driver of about 130 MB with its own Node.js fetched by the build
script, and a separate browser install. `installer.sh:159-164` installs Playwright only when
`SETUP_PLAYWRIGHT` is set. The older crate `playwright` 0.0.20 was last released 2022-08-20.
`webshot` falls back from Playwright to wkhtmltoimage to a screenshot web API (`plugins/tools.py:434-458`).

**wkhtmltoimage.** `wkhtmlapp` 1.2.1 "depends on the wkhtmltopdf application" and notes that upstream
is "archived and unmaintained since 2023" (README). `wkhtmltopdf` 0.4.0, the library binding, was
last released 2021-05-04. `installer.sh` does not install the program.

**Lottie.** `.tgs` is gzip-compressed Lottie JSON (python-lottie 0.7.2 sdist, `exporters/core.py:25-32`),
so `.tgs` to and from `.json` needs only `flate2`. python-lottie rewrites the JSON as it converts, and
`destroy` edits that text with string replaces (`plugins/stickertools.py:427-445`), so the exact text
depends on the serialiser. For pixels, `rlottie` 0.5.4 binds the rlottie C++ library (vendored or
found with pkg-config, per its manifest) and `lottieconv` 0.3.1 writes GIF and WebP with it. No crate
was checked for MP4 output.

**Voice chats.** Nothing in this checkout calls `pytgcalls`. `loader.py:124-144` checks that it
imports, then clones github.com/TeamUltroid/VcBot, whose `__init__.py` uses `GroupCallFactory(..,
MTPROTO_CLIENT_TYPE.TELETHON)`, `join`, `start_audio`, `stop_video`, `stop`. That is the API of the
PyPI package `pytgcalls` (github.com/MarshalX/tgcalls), a layer over `tgcalls`, "a Python binding for
tgcalls C++ library" (PyPI). `installer.sh:176` pins `pytgcalls==3.0.0.dev23`; PyPI lists dev22 and
dev24 but no dev23, and the last upload is from 2023-01-09. The same line builds PyAV (`av`) from
source. The Rust crates come from a different project, NTgCalls ("Built from scratch in C++ using
Boost and libwebrtc"): `ntgcalls` exposes `create_call`, `connect`, `set_stream_sources`, `pause`,
`resume`, `stop` (src), is LGPL-3.0-only, and its `ntgcalls-sys` build script downloads prebuilt
static libraries (README). `tgcalls` 0.4.0-beta1 sits on `ntgcalls` and on `ferogram` 0.6.7, a Rust
Telegram client, and needs `ffmpeg` on the path (README). All three were first published in 2026
(io). The signalling goes through the Telegram client, so this depends on ADR-005.

**Google Drive.** `google-drive2` matches the v2 calls one to one; v3 renames `files.insert` to
`files.create` and `title` to `name` (developers.google.com/workspace/drive/api/guides/v2-to-v3-reference).

## Unofficial APIs

Any stand-in for these has the same fragility as the Python package: the service is not documented
and can change or block clients at any time.

- **Akinator.** `en.akinator.com/game` answered `403` with `cf-mitigated: challenge` from this
  environment, so neither wrapper could be tried. akipy 1.7.1 has an optional Cloudflare-challenge
  solver (sdist); `akinator-rs` has none and uses other paths (`/new_session`, `/answer_api`, a
  `srvN.akinator.com:<port>/ws` URL).
- **Twitter/X.** twikit "uses scraping and does not require an API key" (github.com/d60/twikit); its
  last PyPI release is 2.3.3 (2025-02-07). The three Rust scrapers have a password login and the
  calls Ultroid uses under their own names (src). `agent-twitter-client` was last released
  2024-12-26, `xplore` 2025-07-11. The official API has maintained clients (`twapi-v2` 0.27.0,
  2026-06-15) but needs developer keys in place of `TWITTER_USERNAME`, `TWITTER_EMAIL`,
  `TWITTER_PASSWORD` (`plugins/twitter.py:55`).
- **Cloudflare bypass.** `requirements.txt:13` asks for cloudscraper 1.2.71 or later; 1.2.71 is the
  newest on PyPI (2023-04-25). `cloudscraper-rs` calls itself "early-stage" (README; 420 downloads).
  `ghostwire` and `flaresolverr-rs` were first published in 2026 (453 and 408 downloads).
  `cloudflare-bypasser` 0.2.0 was last released 2020-03-04.
- **Instagram.** Nothing to port in this checkout. `rocketapi` is an SDK for the RocketAPI service
  (ci); `qinstagram` has one release (2026-04-12, 99 downloads).

## Image stack: `cv2`, `skimage`, `PIL`

Every OpenCV call below exists in `opencv` 0.102.0, which calls the same library. Its README says
"The API is usable, but unstable and not very battle-tested" and requires OpenCV and Clang on the
build machine. The right-hand column is what the pure-Rust crates offer (src). Pixel output was not
compared for any row.

| Call in Ultroid | `image` 0.25.10 / `imageproc` 0.27.0 |
| --- | --- |
| `imread`, `imwrite` (`plugins/imagetools.py:131`, `:180`) | `image::open`, `save` |
| `cvtColor` to grey (`imagetools.py:133`, `pdftools.py:238`), to YUV for Y (`pdftools.py:208-210`) | `imageops::grayscale`; weights not compared |
| `GaussianBlur` by kernel size (`imagetools.py:135`, `:158`, `pdftools.py:211`) | `imageops::blur`, `filter::gaussian_blur_f32`: both take sigma, not a kernel size |
| `bitwise_not` (`imagetools.py:137`) | `imageops::invert` |
| `flip`, `rotate` 180, `hconcat`, `vconcat` (`imagetools.py:142-154`) | `imageops::flip_horizontal`, `rotate180`; joining by `imageops::replace` on a larger image |
| BGR2RGB then HSV2BGR (`imagetools.py:139-140`), `divide(scale=256)` (`:160`), `copyMakeBorder` (`:263`) | no ready function; per-pixel code |
| `kmeans` (`imagetools.py:169-176`) | in neither; `kmeans_colors` 0.7.1 has `get_kmeans` |
| `resize` linear, nearest (`imagetools.py:286-287`), area (`tools.py:193`, `pdftools.py:207`) | `imageops::resize` with `Triangle`, `Nearest`; no area filter (`fast_image_resize` 6.2.0 has `Box`) |
| `VideoCapture(f).read()` for a first frame (`imagetools.py:96`, `stickertools.py:182`, `:479`, `pyUltroid/fns/tools.py:906`) | none; `ffmpeg`, already required (`installer.sh:56`) |
| `Canny(img, 50, 200, apertureSize=3)` (`pdftools.py:212`) | `edges::canny` adds its own blur (sigma 1.4) and uses the L2 gradient; OpenCV defaults to L1, so thresholds do not carry over |
| `findContours` external, `convexHull`, `approxPolyDP`, `arcLength`, `contourArea`, `drawContours` (`pdftools.py:213-223`) | `contours::find_contours` (all borders, each with `parent` and `BorderType`), `geometry::convex_hull`, `approximate_polygon_dp`, `arc_length`, `contour_area`, `drawing::draw_hollow_polygon_mut` |
| `getPerspectiveTransform`, `warpPerspective` (`pyUltroid/fns/tools.py:593-594`) | `Projection::from_control_points`, `warp` |
| `getRotationMatrix2D`, `warpAffine` (`pyUltroid/fns/misc.py:443-444`) | `rotate_about_center`, in radians, clockwise |
| `detailEnhance(sigma_s=10, sigma_r=0.15)` (`pdftools.py:242`, `:313`) | none found |
| `QRCodeDetector().detectAndDecode` (`plugins/qrcode.py:104-105`) | `rqrr` 0.11.0: `PreparedImage::prepare`, `detect_grids`, `decode` |
| skimage `threshold_local` (`pdftools.py:239`, `:310`) | `contrast::adaptive_threshold`: box mean, not Gaussian |

`plugins/converter.py:18` and `plugins/search.py:36` import `cv2` without calling it.

Pillow calls and what covers them:

- `open`, `new`, `convert`, `resize`, `crop`, `thumbnail`, `paste`, `save` to PNG, JPEG, ICO
  (`plugins/resize.py:59-61`, `pyUltroid/fns/tools.py:363-385`, `:809-829`, `:1015-1017`): `image` has
  `open`, `save`, `imageops::resize`, `crop`, `thumbnail`, `overlay`, `replace` and those three formats.
- WebP with `quality=95` (`plugins/stickertools.py:500`, `:522`): `image` encodes lossless WebP only
  ("If you need lossy encoding, you'll have to use libwebp", `codecs/webp/encoder.rs`); `webp` 0.3.1
  builds on `libwebp-sys`.
- `im.save("x.pdf")` (`plugins/pdftools.py:247`, `:318`): `image` has no PDF format; `printpdf` 0.12.13,
  or `lopdf` with its `embed_image` feature.
- `ImageFont.truetype`, `getbbox`, `textlength`, `ImageDraw.text` (`plugins/writer.py:74-81`,
  `pyUltroid/fns/tools.py:344-383`): `ab_glyph` loads fonts; `imageproc::drawing::text_size` and
  `draw_text_mut` measure and draw. `draw_text_mut` has no stroke parameter, and `logo` draws with
  `stroke_width` and `stroke_fill` (`pyUltroid/fns/tools.py:376-383`).
- `ImageDraw.pieslice` over a full circle (`plugins/stickertools.py:403`): `draw_filled_ellipse_mut`.
- `Image.new("RGB", size, name)` with a user-typed colour (`plugins/imagetools.py:193`):
  `csscolorparser` parses CSS names and hex; Pillow's own name table was not compared.

## Other partial cases

**PyPDF2.** `lopdf` has `Document::load`, `get_pages`, `delete_pages`, `extract_text(&[page])` and
`save` (src). Merging is an example file (`examples/merge.rs`), not one call. The "page as image"
command writes one-page PDFs named `.png` (`plugins/pdftools.py:91-96`), so no renderer is involved.
The plugin calls `numPages`, `getPage`, `addPage` and `extractText`; in PyPDF2 3.0.1, the last
release (2022-12-31), those raise `DeprecationError` (sdist `_utils.py:350-369`, `_reader.py:461-478`),
and `optional-requirements.txt:23` only sets a lower bound.

**BeautifulSoup.** `scraper` "provides an interface to Servo's html5ever and selectors crates"
(README): `Html::parse_document`, `Selector::parse`, `select`, `attr`, `text`. The regular
expressions Ultroid passes as attribute filters are plain substrings (`plugins/misc.py:52`, `:99`,
`pyUltroid/fns/misc.py:135`, `:195`), which `[attr*=..]` expresses (operator read in `selectors`
0.43.0 src; `scraper` 0.29.0 depends on 0.41.0). `findNext()` (`plugins/misc.py:105-106`) has no
counterpart and becomes a tree walk. html5ever builds the tree a browser would, while `html.parser`
"makes no attempt to create a well-formed HTML document" (crummy.com/software/BeautifulSoup/bs4/doc),
so `find_all("script")[41]` (`pyUltroid/fns/misc.py:87`) and `.tbody` (`plugins/misc.py:71`) can
land on other nodes.

**oauth2client.** `yup-oauth2` implements the installed-app flow with `Interactive`, `HTTPRedirect`
and `HTTPPortRedirect` return methods (src). Ultroid uses the out-of-band redirect, which Google
blocked for all existing production clients on 2023-01-31; the replacement is a loopback redirect
(developers.google.com/identity/protocols/oauth2/resources/oob-migration). The stored token is
oauth2client's own JSON, kept in a file and in `GDRIVE_AUTH_TOKEN` (`pyUltroid/fns/gDrive.py:41`,
`:55-56`). `yup-oauth2` has its own token file and a `TokenStorage` trait for custom storage (src);
nothing in it reads oauth2client's format.

## `safety` and `enhancer`

`enhancer` 0.3.4 (PyPI, 2022-02-10, 4 KB) installs one top-level module named `safety`; its
`safety/tools/__init__.py` exports `KEEP_SAFE`, `cleanup_cache` and `call_back` (sdist). The PyPI
package called `safety` is an unrelated vulnerability scanner with no `safety.tools` module (sdist
3.8.1). `cleanup_cache` blanks secrets in `Var`, `os.environ` and `sys.argv` and hides each client's
session; `call_back` puts them back before a restart. Nothing in this checkout calls `cleanup_cache`,
so `call_back()` restores nothing, and nothing sets the `refresh_auth` and `clear_auth` that
`pyUltroid/fns/FastTelethon.py:151`, `:164` try inside `except AttributeError`. The `KEEP_SAFE` the
plugins see is the one defined at `pyUltroid/fns/helper.py:82`. The package is 181 lines of
app-specific Python; no crate applies.

## Other third-party imports in `plugins/` and `assistant/`

| Package | Used by | Used for | Rust stand-in | Fit | Note and source |
| --- | --- | --- | --- | --- | --- |
| `aiohttp` | `plugins/aiwrapper.py:32`, `autopic.py:13`, `weather.py:23`, `assistant/manager/misc.py:11` | HTTP requests | `reqwest` 0.13.5 | good | ci. |
| `requests` | `plugins/__init__.py:13`, `search.py:28`, `specialtools.py:42` | HTTP requests | `reqwest` 0.13.5 | good | ci. |
| `apscheduler` | `plugins/autopic.py:150`, `plugins/nightmode.py:35` | An interval job (`autopic.py:153`) and two daily cron jobs (`nightmode.py:153-154`) | `tokio-cron-scheduler` 0.15.1 | good | `new_repeated_async`, `new_async`, `new_async_tz` (src). Its README says times are UTC unless a `_tz` call is used; apscheduler's default zone was not compared. |
| `git` (GitPython) | `plugins/_inline.py:13`, `plugins/bot.py:29` | Branch, remote URL, fetch, commits in `HEAD..upstream/<branch>` (`bot.py:74-76`, `_inline.py:238-241`) | `git2` 0.21.0; `gix` 0.90.0 | good | `open`, `init`, `head_detached`, `find_remote`, `fetch`, `revwalk`, `push_range` in `git2` (src). The app also runs the `git` program (`plugins/bot.py:222`). |
| `heroku3` | `plugins/usage.py:44`, `assistant/callbackstuffs.py:286` | App lookup, logs, restart, account id (`usage.py:46-47`, `:112`) | `heroku_rs` 0.6.0; or `reqwest` 0.13.5 | partial | Crate last released 2021-05-29 (io). The plugin already calls `api.heroku.com` directly for quota (`usage.py:118`). |
| `psutil` | `plugins/usage.py:73`, `:99` | CPU, memory, disk and network counters (`:77-81`) | `sysinfo` 0.40.4 | good | `global_cpu_usage`, `used_memory`, `total_space`, `total_received` (src). |
| `pytz` | `plugins/specialtools.py:39`, `plugins/weather.py:24`, `assistant/start.py:11` | `timezone(name)`, `all_timezones` (`weather.py:35-48`) | `chrono-tz` 0.10.4 | good | IANA database; `TZ_VARIANTS` lists every zone (src). |
| `yaml` (PyYAML) | `plugins/devtools.py:33` | `safe_load` on pip output (`:132`); an in-repo fallback exists (`pyUltroid/fns/tools.py:1063`) | `serde_yaml_ng` 0.10.0 | partial | Rated partial in `PLAN.md`; last release 2024-05-26 (io). |
| `telethon` | nearly every file | Telegram client | not covered here | | ADR-005 assigns it to `research/telethon.md`. |

## Not verified

- Nothing was built or run, so no crate was checked on Linux x86_64 or Termux, and no output (image
  pixels, QR modules, extracted PDF text, WebP bytes, table text) was compared with the Python result.
- `akinator-rs` against the live service: Akinator returned a Cloudflare challenge (403) from here.
- `twikit-rs`, `agent-twitter-client`, `xplore` against live X: no account. `twikit-rs` declares no
  repository.
- `cloudscraper-rs`, `ghostwire`, `flaresolverr-rs` against combot.org, and whether cloudscraper
  1.2.71 itself still passes it.
- `ntgcalls` and `tgcalls`: docs.rs shows "failed to build" for `ntgcalls` 3.0.7 and 4.0.0-alpha01
  and for `tgcalls` 0.3.0, so the API was read from source only. Whether `ntgcalls` can be driven
  from the Telegram library chosen later is open.
- `playwright-rs` against ray.so; download handling in `chromiumoxide` and `headless_chrome`.
- `telegraph-rs` 0.7.0 (stable): only the 0.8.0-rc1 source was read.
- `tabulate-rs` against python-tabulate 0.10.0; its stated parity is with 0.9.0.
- The API of `ruff_python_formatter`: only its registry entry and Ruff's formatter page were read.
- Whether Google has set an end date for Drive API v2: the page read does not say.
- `pytgcalls==3.0.0.dev23` is absent from PyPI's release list; whether it can be had elsewhere.
- Forks pinned in `optional-requirements.txt` (`buddhhu/img2html@c44170d`, `New-dev0/instagrapi@39df1b1`)
  were not read. The effect code of `glitch_me` was not read, only its README and `setup.py`.
- Whether an addon outside this checkout imports `instagrapi`: the UltroidAddons file list seen on
  GitHub was partial and showed none.
- Instagram crates (`qinstagram`, `rocketapi`, `instagram-scraper-rs`): existence only.
- `rlottie` rendering against python-lottie's; MP4 output from Lottie.
- Last-commit dates of the GitHub repositories named here: the fetched pages did not show them.
  Repositories could not be cloned; GitHub was read page by page.
- Fetches that gave nothing: `pypi.org/pypi/glitch-me/json` (404), `pypi.org/pypi/pytgcalls/3.0.0.dev23/json`
  (not found), the PyPDF2 3.0.0 changelog page (it does not mention the removed names; the 3.0.1
  source was read instead).
