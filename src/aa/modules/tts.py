"""
Texto a audio, ahora en el idioma de cada usuario.
Copiar a: src/aa/modules/tts.py
Requiere: pip install gTTS   (necesita internet)
"""
from asyncio import to_thread
from io import BytesIO

from gtts import gTTS
from altamino import respObject

from src.aa import client
from src.utils import reply
from src.utils.wrappers.chat_settings import commands_enable_required
from src.core.ctx import args, lang_of, target
from src.core.i18n import t

MAX_CHARS = 300


def _make_audio(text: str, lang: str) -> BytesIO:
    buf = BytesIO()
    gTTS(text=text, lang=lang).write_to_fp(buf)
    buf.seek(0)
    buf.name = "voz.mp3"  # altamino.py detecta el tipo de media por la extensión
    return buf


@client.command(["/tts", "/voz"])
@commands_enable_required()
async def cmd_tts(event: respObject.Event):
    lang = lang_of(event)
    text = args(event)
    if not text:
        return await reply(event, t(lang, "tts_needText"))
    if len(text) > MAX_CHARS:
        return await reply(event, f"Max {MAX_CHARS}.")
    try:
        audio = await to_thread(_make_audio, text, lang)
    except Exception as e:
        return await reply(event, t(lang, "tts_error", error=str(e)))
    await target(event).send_media(event.message.chatId, audio)
