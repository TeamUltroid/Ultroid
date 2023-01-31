from contextlib import suppress
from database import udB
from telegraph import Telegraph

def get_client():
    _api = udB.get_key("_TELEGRAPH_TOKEN")
    return Telegraph(_api, domain="graph.org")

def upload_file(path):
    if path.endswith("webp"):
        with suppress(ImportError):
            from PIL import Image
            Image.open(path).save(path, "PNG")
    return f"https://graph.org{get_client().upload_file(path)[-1]}"