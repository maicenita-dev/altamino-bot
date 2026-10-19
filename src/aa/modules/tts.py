"""
Texto a audio, ahora en el idioma de cada usuario.
Requiere: pip install gTTS y ffmpeg
"""
import subprocess
from asyncio import to_thread
from io import BytesIO

from gtts import gTTS
from altamino import respObject

from src.aa import client
from src.utils import reply
from src.utils.wrappers.chat_settings import commands_enable_required
from src.core.ctx import args, lang_of, target
from src.core import deco
from src.core.i18n import t

MAX_CHARS = 300


def _make_audio(text: str, lang: str) -> BytesIO:
    mp3 = BytesIO()
    gTTS(text=text, lang=lang).write_to_fp(mp3)
    out = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-i", "pipe:0",
         "-c:a", "aac", "-b:a", "64k", "-f", "adts", "pipe:1"],
        input=mp3.getvalue(), capture_output=True, check=True,
    )
    buf = BytesIO(out.stdout)
    buf.name = "voz.aac"
    return buf


@client.command(["/tts", "/voz"])
@commands_enable_required()
async def cmd_tts(event: respObject.Event):
    lang = lang_of(event)
    text = args(event)
    if not text:
        return await reply(event, deco.tts(t(lang, "tts_needText")))
    if len(text) > MAX_CHARS:
        return await reply(event, deco.tts(t(lang, "tts_tooLong", max=MAX_CHARS)))
    try:
        audio = await to_thread(_make_audio, text, lang)
        await target(event).send_media(event.message.chatId, audio)
    except Exception as e:
        return await reply(event, deco.tts(t(lang, "tts_error", error=str(e))))
