import os, asyncio, time
from glob import glob
from typing import Any, Dict, List, Union

from contextlib import suppress
from database import udB
from core import LOGS
from core.remote import rm
from utilities.tools import translate
from utilities.tools import safe_load

_save_ = {}
languages = {}
PATH = "localization/strings/{}.yml"

def get_lang():
    return udB.get_key("language") or "en"

def load(lang):
    if not os.path.exists("localization/strings"):
        os.mkdir("localization/strings")
    
    rm.fetch_lang(lang)

    file = PATH.format(lang)
    if not os.path.exists(file):
        file = PATH.format("en")
    code = file.split("/")[-1].split("\\")[-1][:-4]
    try:
        languages[code] = safe_load(
            open(file, encoding="UTF-8"),
        )
    except Exception as er:
        LOGS.info(f"Error in {file[:-4]} language file")
        LOGS.exception(er)


load(get_lang())


def __get_string(key: str, lang=None) -> Any:
    if not lang:
        lang = get_lang()
    with suppress(KeyError):
        return languages[lang][key]
    if not languages.get("en"):
        load("en")
    eng_ = languages.get("en", {}).get(key)
    if not eng_:
        return f"Warning: could not load any string with the key `{key}`"
    try:
        return translate_and_update(eng_, lang, key)
    except TypeError:
            pass
    except Exception as er:
            LOGS.exception(er)
    return eng_

def get_string(key: str, *args, **kwargs):
    stringResponse = __get_string(key)
    if stringResponse and (args or kwargs):
        try:
            stringResponse = stringResponse.format(*args, **kwargs)
        except (IndexError, KeyError) as er:
            LOGS.exception(er)
            stringResponse = __get_string(key, "en").format(*args, **kwargs)
    return stringResponse


def translate_and_update(eng_, lang, key):
    tr = translate(eng_, target=lang)
    if eng_.count("{}") != tr.count("{}"):
        tr = eng_
    if languages.get(lang) is None:
        languages[lang] = {}
    languages[lang][key] = tr
    if not _save_.get(lang):
         _save_[lang] = 0
    _save_[lang] += 1
    if _save_[lang] > 10:
        save_dict_to_yaml(lang)
        _save_[lang] = 0
    return tr


def save_dict_to_yaml(lang: str):
    strings = languages[lang]
    path = PATH.format(lang)
    text = ""
    for key, value in strings.items():
        value = value.replace('"', "'").replace("\n", "\\n")
        text += f'{key}: "{value}"\n'
    if not text:
        return
    with open(path, "w") as file:
        file.write(text)


def get_help(key):
    if doc := get_string(f"help_{key}"):
        return get_string("cmda") + doc
