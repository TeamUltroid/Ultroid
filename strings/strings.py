import sys
from os import listdir, path
from typing import Any, Dict, List, Union

from pyUltroid import udB, LOGS
try:
    from google_trans_new import google_translator
    Trs = google_translator()
except ImportError:
    LOGS.info("'google_trans_new' not installed!")
    Trs = None

try:
    from yaml import safe_load
except ModuleNotFoundError:
    LOGS.info("'pyYaml' not installed!\nPlease install it to use Ultroid.")
    sys.exit()

language = [udB.get_key("language") or "en"]
languages = {}

strings_folder = path.join(path.dirname(path.realpath(__file__)), "strings")

for file in listdir(strings_folder):
    if file.endswith(".yml"):
        code = file[:-4]
        try:
            languages[code] = safe_load(
                open(path.join(strings_folder, file), encoding="UTF-8"),
            )
        except Exception as er:
            LOGS.info(f"Error in {file[:-4]} language file")
            LOGS.exception(er)


def get_string(key: str) -> Any:
    lang = language[0]
    try:
        return languages[lang][key]
    except KeyError:
        try:
            en_ = languages["en"][key]
            if not Trs:
                return en_
            tr = Trs.translate(en_, lang_tgt=lang).replace("\ N", "\n")
            if en_.count("{}") != tr.count("{}"):
                tr = en_
            if languages.get(lang):
                languages[lang][key] = tr
            else:
                languages.update({lang: {key: tr}})
            return tr
        except KeyError:
            return f"Warning: could not load any string with the key `{key}`"
        except TypeError:
            pass
        except Exception as er:
            LOGS.exception(er)
        return languages["en"].get(key) or f"Failed to load language string '{key}'"


def get_languages() -> Dict[str, Union[str, List[str]]]:
    return {
        code: {
            "name": languages[code]["name"],
            "natively": languages[code]["natively"],
            "authors": languages[code]["authors"],
        }
        for code in languages
    }
