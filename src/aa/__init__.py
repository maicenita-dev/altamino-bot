"""Cliente global del bot. Los módulos hacen: from src.aa import client"""
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


client = Client(deviceId=_device_id())


# Prefijo de comandos. Para aceptar ambos: PREFIXES = ["!", "/"]
PREFIXES = ["!"]
_orig_command = client.command


def _command(commands):
    out = []
    for c in commands:
        base = c[1:] if c[:1] in ("/", "!") else c
        out.extend(p + base for p in PREFIXES)
    return _orig_command(out)


client.command = _command
