"""/ask con la API gratuita de Pollinations (sin key; puede caerse o limitar)."""
import urllib.request
from asyncio import to_thread
from urllib.parse import quote


def _fetch(prompt: str) -> str:
    req = urllib.request.Request(
        "https://text.pollinations.ai/" + quote(prompt, safe=""),
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode("utf8").strip()


async def ask_ai(prompt: str) -> str | None:
    clean = (prompt or "").strip()
    if not clean:
        return None
    return await to_thread(_fetch, clean)
