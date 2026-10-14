"""Horóscopo diario: calcula signo y frase (por índice), sin idioma."""
import unicodedata
from datetime import date

SIGN_KEYS = [
    "aries", "tauro", "geminis", "cancer", "leo", "virgo",
    "libra", "escorpio", "sagitario", "capricornio", "acuario", "piscis",
]
PHRASE_COUNT = 8  # debe coincidir con HOROSCOPE_PHRASES en i18n.py


def _hash(s: str) -> int:
    h = 0
    for ch in s:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return h


def _normalize(raw: str) -> str:
    s = unicodedata.normalize("NFD", (raw or "").lower().strip())
    return "".join(c for c in s if not unicodedata.combining(c))  # géminis -> geminis


def get_horoscope(raw_sign: str) -> dict:
    key = _normalize(raw_sign)
    if key not in SIGN_KEYS:
        return {"ok": False, "signKeys": SIGN_KEYS}
    iso = date.today().isoformat()
    return {"ok": True, "signKey": key, "dateISO": iso,
            "phraseIndex": _hash(f"{iso}-{key}") % PHRASE_COUNT}
