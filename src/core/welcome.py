"""Bienvenida: mensaje + tu imagen de res/images/welcome.<ext>"""
from io import BytesIO

from .config import BOT_NAME, IMAGES_DIR
from .i18n import t

EXTENSIONS = ["png", "jpg", "jpeg", "webp", "gif"]


def get_welcome_image() -> BytesIO | None:
    for ext in EXTENSIONS:
        path = IMAGES_DIR / f"welcome.{ext}"
        if path.exists():
            buf = BytesIO(path.read_bytes())
            buf.name = path.name
            return buf
    return None


def get_welcome_message(lang: str, nickname: str) -> str:
    return t(lang, "welcome_message", name=nickname, bot=BOT_NAME)


def get_intro_message(lang: str) -> str:
    return t(lang, "intro_message", name=BOT_NAME)
