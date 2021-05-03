import requests
import base64
from PIL import Image
import os
from userbot.utils import admin_cmd
from userbot import bot as borg
@ultroid_cmd(pattern=r"zombie")
async def zumbie(event):
    await event.delete()
    sed = await event.get_reply_message()
    img = await borg.download_media(sed.media)
    r = requests.post(
        'https://deepgrave-image-processor-no7pxf7mmq-uc.a.run.app/transform',
        files={
            'image': open(img, 'rb'),
        },
    )
    imgdata = base64.b64decode(r.text)
    filename = 'zombie.jpg'  
    with open(filename, 'wb') as f:
        f.write(imgdata)
    im=Image.open(filename)
    import cv2   
    img = cv2.imread(filename)
    height = img.shape[0]
    width = img.shape[1]
    width_cutoff = width // 2
    s2 = img[:, width_cutoff:]
    cv2.imwrite(filename, s2)
    await event.client.send_file(event.chat_id, "zombie.jpg", force_document=False, reply_to=event.reply_to_msg_id)

    os.remove("image.jpg")
    os.remove("zombie.jpg")