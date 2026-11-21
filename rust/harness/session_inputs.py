"""Session strings to try: for `rust/session-rs/make_inputs.py` and `fuzz_session.py`.

Real sessions cannot be used, so these are made the way the libraries make them: a Telethon
string session, and the three layouts Pyrogram has used, each with a made-up key. Around them:
the same strings with blanks, with characters changed, cut short or padded, and text that is no
session at all.
"""

import base64
import struct

PYROGRAM = {351: ">B?256sI?", 356: ">B?256sQ?", 362: ">BI?256sQ?"}
BLANKS = [" ", "\n", "\r\n", "\t", "\x0b", "\x1f", "\xa0", " ", "　"]
NOISE = "=!-_+/ \n.,:;*#@Aaz09é😀\x00"
PLAIN = ["", "1", "11", "0", "2", "hello", "1hello", " 1", "1 ", "None", "=", "====", "1====", "é", "1é"]


def key(rng, zero=False):
    return bytes(256) if zero else bytes(rng.randrange(256) for _ in range(256))


def encode(data):
    return base64.urlsafe_b64encode(data).decode("ascii")


def telethon(rng, v6=False, zero=False):
    address = bytes(rng.choice([0, 0, 0xFF, rng.randrange(256)]) for _ in range(16 if v6 else 4))
    if v6 and rng.random() < 0.3:
        address = bytes(10) + b"\xff\xff" + address[:4]  # an IPv4 address written as IPv6
    port = rng.choice([443, 80, 0, 65535, rng.randrange(65536)])
    dc = rng.choice([1, 2, 3, 4, 5, 0, 255, rng.randrange(256)])
    return "1" + encode(struct.pack(f">B{len(address)}sH256s", dc, address, port, key(rng, zero)))


def pyrogram(rng, length=None, zero=False):
    length = length or rng.choice(list(PYROGRAM))
    dc = rng.choice([1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 0, 6, 255])
    flag, user = rng.random() < 0.5, rng.randrange(2**32)
    if length == 351:
        data = struct.pack(PYROGRAM[351], dc, flag, key(rng, zero), user, not flag)
    elif length == 356:
        data = struct.pack(PYROGRAM[356], dc, flag, key(rng, zero), user * 2**20, not flag)
    else:
        data = struct.pack(PYROGRAM[362], dc, rng.randrange(2**32), flag, key(rng, zero), user * 2**20, not flag)
    return encode(data).rstrip("=")


def edited(rng, text):
    """`text` with a few characters dropped, added, swapped or replaced, or blanks around it."""
    chars = list(text)
    for _ in range(rng.choice([1, 1, 1, 2, 4])):
        at = rng.randrange(len(chars) + 1)
        kind = rng.randrange(7)
        if kind == 0 and chars:
            del chars[min(at, len(chars) - 1)]
        elif kind == 1:
            chars.insert(at, rng.choice(NOISE))
        elif kind == 2 and chars:
            chars[min(at, len(chars) - 1)] = rng.choice(NOISE)
        elif kind == 3:
            chars = [rng.choice(BLANKS)] * rng.randrange(1, 3) + chars
        elif kind == 4:
            chars += [rng.choice(BLANKS)] * rng.randrange(1, 3)
        elif kind == 5:
            chars = chars[:at]
        else:
            chars += ["="] * rng.randrange(1, 4)
    return "".join(chars)


def session(rng):
    """One string: a good session of some kind, or one that is nearly one, or plain text."""
    kind = rng.randrange(12)
    if kind == 0:
        return rng.choice(PLAIN + [rng.choice("1A!é =") * rng.choice([351, 352, 353, 354, 356, 362, 369])])
    good = [telethon(rng), telethon(rng), pyrogram(rng), pyrogram(rng), telethon(rng, v6=True),
            telethon(rng, zero=True), pyrogram(rng, zero=True)][kind % 7]  # fmt: skip
    return good if kind < 5 else edited(rng, good)
