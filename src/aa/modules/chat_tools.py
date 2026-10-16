"""
Herramientas: !ask (IA), !trasl (traductor), !langset (idioma).
Copiar a: src/aa/modules/chat_tools.py
Requiere: pip install deep-translator
"""
from altamino import respObject

from src.aa import client
from src.utils import reply
from src.utils.wrappers.chat_settings import commands_enable_required
from src.core.ask import ask_ai
from src.core.ctx import args, lang_of, scope_of
from src.core.i18n import t
from src.core.lang import SUPPORTED, set_com_lang
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


def _quoted_text(event) -> str:
    rm = getattr(event.message, "replyMessage", None)
    if not rm:
        return ""
    if isinstance(rm, dict):
        return (rm.get("content") or "").strip()
    return (getattr(rm, "content", "") or "").strip()


@client.command(["/trasl"])
@commands_enable_required()
async def cmd_trasl(event: respObject.Event):
    lang = lang_of(event)
    parts = args(event).split(maxsplit=1)
    if not parts or parts[0].lower() not in SUPPORTED:
        return await reply(event, t(lang, "trasl_usage"))
    dest = parts[0].lower()
    text = parts[1] if len(parts) > 1 else _quoted_text(event)
    if not text:
        return await reply(event, t(lang, "trasl_usage"))
    try:
        await reply(event, await translate_text(text, dest))
    except Exception as e:
        print("trasl error:", repr(e))
        await reply(event, t(lang, "trasl_error") + f" ({type(e).__name__})")


def _is_staff(event) -> bool:
    role = getattr(event.message.author, "role", None)
    print("langset: role =", repr(role))
    try:
        return int(role or 0) >= 100
    except (TypeError, ValueError):
        return False


@client.command(["/langset"])
@commands_enable_required()
async def cmd_langset(event: respObject.Event):
    lang = lang_of(event)
    requested = args(event).lower()
    if requested not in SUPPORTED:
        return await reply(event, t(lang, "langset_usage"))
    if not await is_staff_ex(event):
        return await reply(event, t(lang, "langset_staff_only"))
    set_com_lang(scope_of(event), requested)
    await reply(event, t(requested, "langset_done", lang=requested))


from src.core.ctx import is_staff as _is_staff  # noqa: E402

from src.core.ctx import is_staff_ex  # noqa: E402
