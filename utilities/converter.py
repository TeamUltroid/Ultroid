import math
from PIL import Image


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