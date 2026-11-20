"""The database value format, as data in and data out (ADR-004, ADR-007).

Every backend stores text. `set_key` writes `str(value)` and `get_key` reads it back with
`ast.literal_eval`, keeping the text when that fails. These two functions drive the original's
`_BaseDatabase` so the format can be recorded.
"""

from fixture import canon, describe, has_set_order, udB


def read_stored(text: str) -> list:
    """The type and `repr` of what `get_key` returns for a key whose stored text is `text`."""
    udB.wipe()
    udB.raw["KEY"] = text
    return describe(udB.get_key("KEY"))


def write_value(value) -> list:
    """What `set_key` keeps for `value` (type and `repr`) and the text it stores."""
    udB.wipe()
    udB.set_key("KEY", value)
    kept, stored = udB.get_key("KEY"), udB.raw["KEY"]
    if has_set_order(kept):
        # CPython prints a set in the order of its hash table, which for text changes from one
        # run to the next. That order is not part of the format, so it is taken out here.
        stored = canon(kept)
    # A lone surrogate cannot be written out as UTF-8, so it is shown as its escape.
    return describe(kept) + [stored.encode("utf-8", "backslashreplace").decode("utf-8")]
