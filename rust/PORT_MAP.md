# Port map: Ultroid

8 of 19 units have a Rust port; no original changed since it was recorded.

## Ports

| Unit | Crate | In Rust | Kept in the original | Cases | Last diff | Original |
| --- | --- | --- | --- | ---: | ---: | --- |
| `pyUltroid/fns/helper.py` | `rust/helper-rs` | `time_formatter`, `humanbytes`, `numerize` | `run_async`, `make_mention`, `inline_mention`, `un_plug`, `bash`, `updater`, `uploader`, `downloader`, `async_searcher`, `download_file`, `fast_download`, `mediainfo`, `progress`, `restart`, `shutdown`, `KEEP_SAFE` | 213 | 213/213 | unchanged |
| `pyUltroid/fns/tools.py` | `rust/tools-rs` | `get_msg_button`, `text_set`, `stdr`, `cmd_regex_replace`, `get_chat_and_msgid` | `get_ofox`, `json_parser`, `is_url_ok`, `metadata`, `set_attributes`, `create_tl_btn`, `format_btn`, `saavn_search`, `webuploader`, `get_all_files`, `get_paste`, `get_google_images`, `get_chatbot_reply`, `check_filename`, `genss`, `duration_s`, `order_points`, `four_point_transform`, `telegraph_client`, `make_html_telegraph`, `Carbon`, `get_file_link`, `get_stored_file`, `translate`, `safe_load`, `LogoHelper`, `LottieException`, `TgConverter` | 809 | 809/809 | unchanged |
| `rust/harness/command.py` | `rust/command-rs` | `command`, `assistant`, `inline` | - | 9301 | 9301/9301 | unchanged |
| `rust/harness/dbaccess.py` | `rust/dbaccess-rs` | `run` | - | 949 | 949/949 | unchanged |
| `rust/harness/dbvalue.py` | `rust/dbvalue-rs` | `read_stored`, `write_value` | - | 4394 | 4394/4394 | unchanged |
| `rust/harness/language.py` | `rust/strings-rs` | `run` | - | 1716 | 1716/1716 | unchanged |
| `rust/harness/launch.py` | `rust/launch-rs` | `plan` | - | 1714 | 1714/1714 | unchanged |
| `rust/harness/session.py` | `rust/session-rs` | `check`, `parse` | - | 1382 | 1382/1382 | unchanged |

## Whole app

| Glue | Runs |
| --- | --- |
| `rust/app/src/units/launch.rs` | Rust only |

## Not ported yet

In the order `analyze` suggests.

| Unit | Lines | Exports | Readiness |
| --- | ---: | ---: | ---: |
| `strings/` | 68 | 4 | 77 |
| `resources/startup/` | 331 | 13 | 87 |
| `resources/session/` | 152 | 6 | 84 |
| `pyUltroid/dB/` | 616 | 94 | 59 |
| `multi_client.py` | 24 | 0 | 97 |
| `pyUltroid/` | 309 | 7 | 57 |
| `assistant/manager/` | 495 | 16 | 50 |
| `pyUltroid/_misc/` | 664 | 11 | 29 |
| `assistant/` | 2821 | 80 | 0 |
| `plugins/` | 14394 | 0 | 0 |
| `pyUltroid/startup/` | 1425 | 22 | 0 |

Regenerate with `rust-anything map --write`. Commit this file: when the original changes upstream, the next map marks every port whose recording it outdated.
