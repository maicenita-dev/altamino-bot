"""Idioma preferido de cada usuario (persistente)."""
from .config import DATA_DIR
from .storage import load_json, save_json

DB_PATH = DATA_DIR / "lang.json"
DEFAULT_LANG = "es"
SUPPORTED = ["es", "en", "ru"]


def get_lang(user_id: str) -> str:
    return load_json(DB_PATH, {}).get(str(user_id), DEFAULT_LANG)


def set_lang(user_id: str, lang: str) -> bool:
    if lang not in SUPPORTED:
        return False
    db = load_json(DB_PATH, {})
    db[str(user_id)] = lang
    save_json(DB_PATH, db)
    return True
