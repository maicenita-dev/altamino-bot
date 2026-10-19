"""
Horóscopo diario (reemplaza tu horoscope.py anterior, ahora en es/en/ru).
Copiar a: src/aa/modules/horoscope.py
"""
from altamino import respObject

from src.aa import client
from src.utils import reply
from src.utils.wrappers.chat_settings import commands_enable_required
from src.core import deco
from src.core.ctx import args, lang_of, send_gif
from src.core.horoscope import get_horoscope
from src.core.i18n import HOROSCOPE_PHRASES, SIGN_NAMES, t


@client.command(["!horoscopo", "/horóscopo"])
@commands_enable_required()
async def cmd_horoscope(event: respObject.Event):
    lang = lang_of(event)
    r = get_horoscope(args(event))
    if not r["ok"]:
        options = ", ".join(SIGN_NAMES[lang][k] for k in r["signKeys"])
        return await reply(event, deco.horo(t(lang, "horoscope_notRecognized", options=options)))
    header = t(lang, "horoscope_header", sign=SIGN_NAMES[lang][r["signKey"]], date=r["dateISO"])
    await reply(event, deco.horo_result(header, HOROSCOPE_PHRASES[lang][r['phraseIndex']]),
                mentionUserIds=[event.message.author.userId])
    await send_gif(event, "horoscopo")
