import random
import string
from io import BytesIO
from captcha.image import ImageCaptcha

from dataclasses import dataclass

@dataclass
class CaptchaComponent:
    image: BytesIO
    password: str


class Captcha():
    def __init__(self, password_length: int = 4):
        self.captcha = ImageCaptcha(width = 280, height = 90)
        self.password_length = password_length

    def generate_captcha(self) -> CaptchaComponent:
        password = ''.join(random.choices(string.ascii_uppercase + string.digits, k = self.password_length))
        image_data = self.captcha.generate(password)

        image_bytes = BytesIO()
        image_bytes.write(image_data.read())
        image_bytes.seek(0)

        return CaptchaComponent(image = image_bytes, password = password)