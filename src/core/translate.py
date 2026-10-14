"""/trasl con deep-translator (Google Translate, no oficial)."""
from asyncio import to_thread

from deep_translator import GoogleTranslator

SUPPORTED = ["es", "en", "ru"]


def _translate(text: str, target: str) -> str:
    return GoogleTranslator(source="auto", target=target).translate(text)


async def translate_text(text: str, target: str) -> str:
    if target not in SUPPORTED:
        raise ValueError(f"Idioma no soportado: {target}")
    return await to_thread(_translate, text, target)
