import base64
import io
import os

import numpy as np
from PIL import Image

from api.open.captcha.config import *

__all__ = ["text2vector", "vector2text", "img2array",
           "checkpoints_dir", "InvalidCaptchaError"]


def text2vector(text):
    text_len = len(text)
    if text_len > CAPTCHA_LEN:
        raise ValueError("Max captcha is 4 chars!")

    vector = np.zeros(CHAR_SET_LEN * CAPTCHA_LEN)

    def char2pos(c):
        k = ord(c) - 48
        if k > 9:
            k = ord(c) - 55
            if k > 35:
                k = ord(c) - 61
                if k > 61:
                    raise ValueError("No map!")
        return k

    for i, c in enumerate(text):
        idx = i * CHAR_SET_LEN + char2pos(c)
        vector[idx] = 1
    return vector


def vector2text(vec):
    char_pos = vec.nonzero()[0]
    text = []
    for i, c in enumerate(char_pos):
        char_idx = c % CHAR_SET_LEN
        if char_idx < 10:
            char_code = char_idx + ord('0')
        elif char_idx < 36:
            char_code = char_idx - 10 + ord('A')
        elif char_idx < 62:
            char_code = char_idx - 36 + ord('a')
        else:
            raise ValueError('error')
        text.append(chr(char_code))
    return "".join(text)


class InvalidCaptchaError(OSError):
    pass


def img2array(image):
    try:
        if isinstance(image, str):
            img_bytes = base64.decodebytes(image.encode("utf8"))
            image = Image.open(io.BytesIO(img_bytes)).convert("L")
            image = np.array(image).flatten() / 255
        return image
    except OSError:
        raise InvalidCaptchaError()


def checkpoints_dir():
    return os.path.join(os.path.dirname(__file__), "checkpoints")
