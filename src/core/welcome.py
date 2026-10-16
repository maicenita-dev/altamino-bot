"""Bienvenida: texto por defecto o personalizado por chat + imagen res/images/welcome.<ext>"""
from io import BytesIO

from .config import BOT_NAME, DATA_DIR, IMAGES_DIR
from .i18n import t
from .storage import load_json, save_json

EXTENSIONS = ["png", "jpg", "jpeg", "webp", "gif"]
DB_PATH = DATA_DIR / "welcome.json"


def _key(com_id, chat_id) -> str:
    return f"{com_id or 0}:{chat_id}"


def get_cfg(com_id, chat_id) -> dict:
    return load_json(DB_PATH, {}).get(_key(com_id, chat_id), {})


def _update(com_id, chat_id, **changes) -> None:
    db = load_json(DB_PATH, {})
    k = _key(com_id, chat_id)
    cfg = db.get(k, {})
    cfg.update(changes)
    db[k] = cfg
    save_json(DB_PATH, db)


def set_text(com_id, chat_id, text: str) -> None:
    _update(com_id, chat_id, text=text, enabled=True)


def set_enabled(com_id, chat_id, flag: bool) -> None:
    _update(com_id, chat_id, enabled=flag)


def reset(com_id, chat_id) -> None:
    db = load_json(DB_PATH, {})
    db.pop(_key(com_id, chat_id), None)
    save_json(DB_PATH, db)


def is_enabled(com_id, chat_id) -> bool:
    return get_cfg(com_id, chat_id).get("enabled", True)


def get_welcome_image() -> BytesIO | None:
    for ext in EXTENSIONS:
        path = IMAGES_DIR / f"welcome.{ext}"
        if path.exists():
            buf = BytesIO(path.read_bytes())
            buf.name = path.name
            return buf
    return None


def get_welcome_message(lang: str, nickname: str, com_id=None, chat_id=None) -> str:
    custom = get_cfg(com_id, chat_id).get("text") if chat_id else None
    if custom:
        return custom.replace("{name}", nickname).replace("{bot}", BOT_NAME)
    return t(lang, "welcome_message", name=nickname, bot=BOT_NAME)


def get_intro_message(lang: str) -> str:
    return t(lang, "intro_message", name=BOT_NAME)
