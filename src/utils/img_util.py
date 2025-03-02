import base64
from io import BytesIO

from PIL import Image


def convert_base64_2_img(image_b64) -> Image.Image:
    decoded_image = BytesIO(base64.b64decode(image_b64.encode()))
    decoded_image_rgb = Image.open(decoded_image).convert("RGB")
    return decoded_image_rgb


def convert_img_2_base64(image: Image) -> str:
    img_byte = convert_img_2_binary(image)
    img_base64 = base64.b64encode(img_byte).decode()
    return img_base64


def convert_img_2_binary(image: Image) -> bytes:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return buffered.getvalue()
