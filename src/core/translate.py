"""/trasl: Google gtx -> MyMemory -> IA del bot (ask_ai)."""
import json
from asyncio import to_thread
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SUPPORTED = ["es", "en", "ru", "pt"]
NAMES = {"es": "Spanish", "en": "English", "ru": "Russian", "pt": "Portuguese"}


def _get_json(url: str) -> object:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))


def _gtx(text: str, target: str) -> str:
    data = _get_json("https://translate.googleapis.com/translate_a/single?" + urlencode(
        {"client": "gtx", "sl": "auto", "tl": target, "dt": "t", "q": text}))
    return "".join(p[0] for p in data[0] if p and p[0])


def _mymemory(text: str, target: str) -> str:
    data = _get_json("https://api.mymemory.translated.net/get?" + urlencode(
        {"q": text, "langpair": f"Autodetect|{target}"}))
    out = data["responseData"]["translatedText"]
    if not out or "MYMEMORY WARNING" in out:
        raise RuntimeError("mymemory sin resultado")
    return out


def _free(text: str, target: str) -> str:
    for fn in (_gtx, _mymemory):
        try:
            return fn(text, target)
        except Exception as e:
            print(f"trasl {fn.__name__} falló:", repr(e))
    raise RuntimeError("servicios gratuitos no disponibles")


async def translate_text(text: str, target: str) -> str:
    if target not in SUPPORTED:
        raise ValueError(f"Idioma no soportado: {target}")
    try:
        return await to_thread(_free, text, target)
    except Exception:
        from src.core.ask import ask_ai
        prompt = (f"Translate the following text to {NAMES[target]}. "
                  f"Reply with only the translation, nothing else:\n\n{text}")
        out = await ask_ai(prompt)
        if not out:
            raise RuntimeError("sin traducción")
        return out.strip()
