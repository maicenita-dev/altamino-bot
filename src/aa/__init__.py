"""Cliente global del bot. Los módulos hacen: from src.aa import client"""
import fcntl
import functools
import os
import sys
import time

from altamino import AsyncClient as Client

from src.core.config import DATA_DIR
from src.core.storage import load_json, save_json

_DEVICE_FILE = DATA_DIR / "device.json"


def _device_id():
    """Guarda el deviceId para no generar uno nuevo en cada arranque."""
    did = load_json(_DEVICE_FILE, {}).get("deviceId")
    if did:
        return did
    from altamino.utils.generators import Generator
    did = Generator.gen_deviceId()
    save_json(_DEVICE_FILE, {"deviceId": did})
    return did


def _single_instance():
    """Evita dos copias del bot a la vez (el candado se libera solo al cerrarse)."""
    global _LOCK_FH
    fh = open(DATA_DIR / "bot.lock", "w")
    try:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("Ya hay otra copia del bot corriendo. Ciérrala (pkill -f main.py) y vuelve a intentar.")
        sys.exit(4)
    fh.write(str(os.getpid()))
    fh.flush()
    _LOCK_FH = fh


_LOCK_FH = None
_single_instance()

client = Client(deviceId=_device_id())


# Prefijo de comandos. Para aceptar ambos: PREFIXES = ["!", "/"]
PREFIXES = ["!"]
_orig_command = client.command


MAX_LEN = 1500
BURST, WINDOW, MUTE = 8, 10, 30
_RECENT = {}
_MUTED = {}


def _is_owner_id(uid) -> bool:
    return str(uid) in {str(o) for o in load_json(DATA_DIR / "owners.json", [])}


def _blocked(event) -> bool:
    """True si el comando se debe ignorar (spam, mensaje enorme o del propio bot)."""
    msg = event.message
    uid = getattr(msg.author, "userId", None)
    if not uid or uid == getattr(client, "userId", None):
        return True
    if isinstance(msg.content, str) and len(msg.content) > MAX_LEN:
        return True
    if _is_owner_id(uid):
        return False
    now = time.time()
    if _MUTED.get(uid, 0) > now:
        return True
    hist = [t for t in _RECENT.get(uid, []) if now - t < WINDOW]
    hist.append(now)
    _RECENT[uid] = hist
    if len(hist) > BURST:
        _MUTED[uid] = now + MUTE
        print("rate limit: silenciado", uid)
        return True
    return False


def _command(commands):
    out = []
    for c in commands:
        base = c[1:] if c[:1] in ("/", "!") else c
        out.extend(p + base for p in PREFIXES)
    base_decorator = _orig_command(out)

    def decorator(fn):
        @functools.wraps(fn)
        async def guarded(event):
            if _blocked(event):
                return
            return await fn(event)
        return base_decorator(guarded)

    return decorator


client.command = _command
