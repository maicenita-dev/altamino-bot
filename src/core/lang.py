"""Idioma por comunidad (lo cambia el staff); respaldo: idioma personal."""
from .config import DATA_DIR
from .storage import load_json, save_json

DB_PATH = DATA_DIR / "lang.json"        # por usuario (anterior)
COM_PATH = DATA_DIR / "lang_com.json"   # por comunidad
DEFAULT_LANG = "es"
SUPPORTED = ["es", "en", "ru", "pt"]


def _key(com_id) -> str:
    return str(com_id or 0)


def get_lang(user_id: str, com_id=None) -> str:
    com = load_json(COM_PATH, {}).get(_key(com_id))
    if com in SUPPORTED:
        return com
    return load_json(DB_PATH, {}).get(str(user_id), DEFAULT_LANG)


def set_lang(user_id: str, lang: str) -> bool:
    if lang not in SUPPORTED:
        return False
    db = load_json(DB_PATH, {})
    db[str(user_id)] = lang
    save_json(DB_PATH, db)
    return True


def set_com_lang(com_id, lang: str) -> bool:
    if lang not in SUPPORTED:
        return False
    db = load_json(COM_PATH, {})
    db[_key(com_id)] = lang
    save_json(COM_PATH, db)
    return True
