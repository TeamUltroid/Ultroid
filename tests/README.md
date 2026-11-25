Run the background-removal regression tests without Telegram credentials or API keys:

```sh
python -m unittest discover -s tests -v
```

Install `requirements.txt` and `Pillow` first. Provider calls are mocked; transport
tests use a local HTTP server. The tests import the real retrieval module. The
command handler is compiled from the checked-in source with application globals
replaced, avoiding plugin registration and a live Telegram session.
