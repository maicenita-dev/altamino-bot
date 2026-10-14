"""Cada reacción del bot -> un .gif local en res/gifs/"""
from io import BytesIO

from .config import GIFS_DIR

GIF_MAP = {
    "horoscopo": "horoscopo.gif",
    "roll": "roll.gif",
    "dice": "roll.gif",
    "flip": "flip.gif",
    "eightball": "8ball.gif",
    "ship": "ship.gif",
    "rps": "rps.gif",
    "marry": "marry.gif",
    "divorce": "divorce.gif",
}


def get_gif(key: str) -> BytesIO | None:
    """Devuelve el gif listo para send_media, o None si no existe."""
    filename = GIF_MAP.get(key)
    if not filename:
        return None
    try:
        buf = BytesIO((GIFS_DIR / filename).read_bytes())
    except FileNotFoundError:
        return None
    buf.name = filename  # altamino.py detecta el tipo por la extensión
    return buf
