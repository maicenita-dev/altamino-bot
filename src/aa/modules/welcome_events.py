"""Bienvenida automática + !setwelcome (solo staff)."""
from altamino import respObject

from src.aa import client
from src.utils import reply
from src.utils.wrappers.chat_settings import commands_enable_required
from src.core.ctx import args, lang_of, target
from src.core.welcome import (get_cfg, get_welcome_image, get_welcome_message,
                              is_enabled, reset, set_enabled, set_text)

MSG = {
    "es": {
        "staff": "Solo el staff puede cambiar la bienvenida.",
        "usage": "Uso: !setwelcome <texto> · !setwelcome off · on · reset\nPodés usar {name} (quien entra) y {bot}.",
        "saved": "Bienvenida guardada para este chat ✅",
        "off": "Bienvenida desactivada en este chat.",
        "on": "Bienvenida activada en este chat.",
        "reset": "Bienvenida restaurada al texto por defecto.",
        "current": "Bienvenida actual:",
        "default": "Se usa la bienvenida por defecto.",
    },
    "en": {
        "staff": "Only staff can change the welcome message.",
        "usage": "Usage: !setwelcome <text> · !setwelcome off · on · reset\nYou can use {name} (who joins) and {bot}.",
        "saved": "Welcome message saved for this chat ✅",
        "off": "Welcome message disabled in this chat.",
        "on": "Welcome message enabled in this chat.",
        "reset": "Welcome message restored to the default.",
        "current": "Current welcome message:",
        "default": "The default welcome message is used.",
    },
    "ru": {
        "staff": "Менять приветствие может только персонал.",
        "usage": "Использование: !setwelcome <текст> · !setwelcome off · on · reset\nМожно использовать {name} (кто зашёл) и {bot}.",
        "saved": "Приветствие сохранено для этого чата ✅",
        "off": "Приветствие в этом чате отключено.",
        "on": "Приветствие в этом чате включено.",
        "reset": "Приветствие сброшено на стандартное.",
        "current": "Текущее приветствие:",
        "default": "Используется стандартное приветствие.",
    },
}


def _m(lang, key):
    return (MSG.get(lang) or MSG["es"])[key]


def _is_staff(event) -> bool:
    try:
        return int(getattr(event.message.author, "role", 0) or 0) >= 100
    except (TypeError, ValueError):
        return False


@client.event("on_group_member_join")
async def on_member_join(event: respObject.Event):
    try:
        print("welcome evento:", str(event.data)[:300])
        user = event.message.author
        chat_id = event.message.chatId
        if not user.userId or user.userId == getattr(client, "userId", None):
            return
        if not is_enabled(event.comId, chat_id):
            return
        lang = lang_of(event)
        nick = user.nickname or "?"
        await reply(event, get_welcome_message(lang, nick, event.comId, chat_id))
        img = get_welcome_image()
        if img is not None:
            try:
                await target(event).send_media(chat_id, img)
            except Exception as e:
                print("welcome: no pude enviar la imagen:", repr(e))
    except Exception as e:
        print("welcome error:", repr(e))


@client.command(["/setwelcome"])
@commands_enable_required()
async def cmd_setwelcome(event: respObject.Event):
    lang = lang_of(event)
    if not await is_staff_ex(event):
        return await reply(event, _m(lang, "staff"))
    com_id, chat_id = event.comId, event.message.chatId
    arg = args(event)
    low = arg.lower()
    if not arg:
        cur = get_cfg(com_id, chat_id).get("text")
        head = _m(lang, "current") + "\n" + cur if cur else _m(lang, "default")
        return await reply(event, head + "\n\n" + _m(lang, "usage"))
    if low == "off":
        set_enabled(com_id, chat_id, False)
        return await reply(event, _m(lang, "off"))
    if low == "on":
        set_enabled(com_id, chat_id, True)
        return await reply(event, _m(lang, "on"))
    if low == "reset":
        reset(com_id, chat_id)
        return await reply(event, _m(lang, "reset"))
    set_text(com_id, chat_id, arg)
    await reply(event, _m(lang, "saved"))


from src.core.ctx import is_staff as _is_staff  # noqa: E402

from src.core.ctx import is_staff_ex  # noqa: E402
