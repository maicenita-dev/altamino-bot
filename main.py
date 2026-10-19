import asyncio
import collections
import logging
import os
import time
from pathlib import Path


def load_env(path=".env"):
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip("'\""))


load_env()

from src.aa import client  # noqa: E402
# importar los módulos los registra
from src.aa.modules import chat_tools, fun, horoscope, join, marry, start, tts, welcome_events, debug_where, cards, cards_search, cards_extra  # noqa: E402,F401


class _WSWatchdog(logging.Handler):
    """Si el socket falla muchas veces seguidas, cierra el bot (run.sh lo reinicia con login nuevo)."""
    LIMIT, WINDOW = 8, 600

    def __init__(self):
        super().__init__(level=logging.ERROR)
        self.fails = collections.deque()

    def emit(self, record):
        try:
            if "connect failed" not in record.getMessage():
                return
            now = time.time()
            self.fails.append(now)
            while self.fails and now - self.fails[0] > self.WINDOW:
                self.fails.popleft()
            if len(self.fails) >= self.LIMIT:
                print("Socket caído demasiado tiempo: reiniciando para iniciar sesión de nuevo...", flush=True)
                os._exit(3)
        except Exception:
            pass


_watchdog = _WSWatchdog()
logging.getLogger().addHandler(_watchdog)
_lib_log = logging.getLogger("altamino")
if not _lib_log.propagate:
    _lib_log.addHandler(_watchdog)


async def main():
    await client.login(os.environ["ALTAMINO_EMAIL"], os.environ["ALTAMINO_PASSWORD"])
    print("Login OK, conectando socket...")
    await client.ws_connect()
    await asyncio.Event().wait()  # quedarse corriendo


if __name__ == "__main__":
    asyncio.run(main())
