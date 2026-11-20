# Port map: Ultroid

1 of 13 units have a Rust port; no original changed since it was recorded.

## Ports

| Unit | Crate | In Rust | Kept in the original | Cases | Last diff | Original |
| --- | --- | --- | --- | ---: | ---: | --- |
| `pyUltroid/fns/helper.py` | `rust/helper-rs` | `time_formatter`, `humanbytes`, `numerize` | `run_async`, `make_mention`, `inline_mention`, `un_plug`, `bash`, `updater`, `uploader`, `downloader`, `async_searcher`, `download_file`, `fast_download`, `mediainfo`, `progress`, `restart`, `shutdown`, `KEEP_SAFE` | 213 | 213/213 | unchanged |

## Not ported yet

In the order `analyze` suggests.

| Unit | Lines | Exports | Readiness |
| --- | ---: | ---: | ---: |
| `rust/harness/` | 77 | 3 | 77 |
| `strings/` | 68 | 4 | 77 |
| `resources/startup/` | 331 | 13 | 87 |
| `resources/session/` | 152 | 6 | 84 |
| `pyUltroid/dB/` | 616 | 94 | 61 |
| `multi_client.py` | 24 | 0 | 97 |
| `pyUltroid/` | 309 | 7 | 58 |
| `assistant/manager/` | 495 | 16 | 50 |
| `pyUltroid/_misc/` | 664 | 11 | 31 |
| `assistant/` | 2821 | 80 | 0 |
| `plugins/` | 14394 | 0 | 0 |
| `pyUltroid/startup/` | 1425 | 22 | 0 |

Regenerate with `rust-anything map --write`. Commit this file: when the original changes upstream, the next map marks every port whose recording it outdated.
