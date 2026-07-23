# Multi-client Ultroid

`./startup` starts `multi_client.py` when `SESSION1` is set; otherwise it runs a single process.

## Environment

| Variables | Client | Log file |
|-----------|--------|----------|
| `API_ID`, `API_HASH`, `SESSION` | primary | `ultroid1.log` |
| `API_ID1`, `API_HASH1`, `SESSION1` | 2nd | `ultroid2.log` |
| … `SESSION5` | 6th | `ultroid6.log` |

Shared Redis (optional, applied to every process):

```
REDIS_URI=host:port
REDIS_PASSWORD=secret
```

## Notes

- Each client is a separate `python -m pyUltroid` process.
- Use distinct Telegram accounts (sessions) — do not reuse one session string on two IPs.
- Hosted platforms: set the same keys as config vars; do not rely on interactive setup.
