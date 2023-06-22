import math, os
from PIL import Image
from .tools import metadata, bash
from .tools import _unquote_text
from telethon.utils import get_extension

def resize_photo_sticker(photo):
    """Resize the given photo to 512x512 (for creating telegram sticker)."""
    image = Image.open(photo)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        image = image.resize(sizenew)
    else:
        maxsize = (512, 512)
        image.thumbnail(maxsize)
    return image


async def create_webm(file, name="video", remove=False):
    _ = await metadata(file)
    name += ".webm"
    h, w = _["height"], _["width"]
    if h == w != 512:
        h, w = 512, 512
    elif h > w:
        h, w = 512, -1
    else:
        h, w = -1, 512
    await bash(
        f'ffmpeg -i "{file}" -preset fast -an -to 00:00:03 -crf 30 -bufsize 256k -b:v {_["bitrate"]} -vf "scale={w}:{h},fps=30" -c:v libvpx-vp9 "{name}" -y'
    )
    if remove:
        os.remove(file)
    return name


async def convert_ffmpeg(input_, output):
    if output.endswith(".gif"):
        await bash(f"ffmpeg -i '{input_}' -an -sn -c:v copy '{output}.mp4' -y")
    else:
        await bash(f"ffmpeg -i '{input_}' '{output}' -y")
    return output


async def lottie_to_gif(file, output):
    await bash(f"lottie_convert.py '{_unquote_text(file)}' '{_unquote_text(output)}'")
    return output
