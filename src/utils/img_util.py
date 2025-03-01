import base64
from io import BytesIO

from PIL import Image


def convert_img_2_base64(image: Image) -> str:
    img_byte = _convert_img_2_binary(image)
    img_base64 = base64.b64encode(img_byte).decode()
    return img_base64


def _convert_img_2_binary(image: Image) -> bytes:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return buffered.getvalue()
