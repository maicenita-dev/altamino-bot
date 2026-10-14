"""
Herramientas: /ask (IA), /trasl (traductor), /langset (idioma).
Copiar a: src/aa/modules/chat_tools.py
Requiere: pip install deep-translator
"""
from altamino import respObject

from src.aa import client
from src.utils import reply
from src.utils.wrappers.chat_settings import commands_enable_required
from src.core.ask import ask_ai
from src.core.ctx import args, lang_of
from src.core.i18n import t
from src.core.lang import SUPPORTED, set_lang
from src.core.translate import translate_text


@client.command(["/ask"])
@commands_enable_required()
async def cmd_ask(event: respObject.Event):
    lang = lang_of(event)
    question = args(event)
    if not question:
        return await reply(event, t(lang, "ask_needQuestion"))
    try:
        answer = await ask_ai(question)
    except Exception:
        return await reply(event, t(lang, "ask_error"))
    await reply(event, answer or t(lang, "ask_error"))


@client.command(["/trasl"])
@commands_enable_required()
async def cmd_trasl(event: respObject.Event):
    lang = lang_of(event)
    parts = args(event).split(maxsplit=1)
    if len(parts) < 2 or parts[0].lower() not in SUPPORTED:
        return await reply(event, t(lang, "trasl_usage"))
    try:
        await reply(event, await translate_text(parts[1], parts[0].lower()))
    except Exception:
        await reply(event, t(lang, "trasl_error"))


@client.command(["/langset"])
@commands_enable_required()
async def cmd_langset(event: respObject.Event):
    requested = args(event).lower()
    if requested not in SUPPORTED:
        return await reply(event, t(lang_of(event), "langset_usage"))
    set_lang(event.message.author.userId, requested)
    await reply(event, t(requested, "langset_done", lang=requested))
