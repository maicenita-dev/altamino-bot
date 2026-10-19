import asyncio
import os
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


async def main():
    await client.login(os.environ["ALTAMINO_EMAIL"], os.environ["ALTAMINO_PASSWORD"])
    print("Login OK, conectando socket...")
    await client.ws_connect()
    await asyncio.Event().wait()  # quedarse corriendo


if __name__ == "__main__":
    asyncio.run(main())
