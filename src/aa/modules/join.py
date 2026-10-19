"""
!join <link>  ->  el bot entra a la comunidad y/o al chat del link (también chats globales).
Ej: !join http://aminoapps.com/p/AbC123
"""
from urllib.parse import urlparse

from altamino import respObject

from src.aa import client
from src.utils import reply
from src.utils.wrappers.chat_settings import commands_enable_required
from src.aa.modules.start import greeting
from src.core import deco
from src.core.ctx import args, is_owner, lang_of

MSG = {
    "es": {
        "bad": "No pude leer ese link",
        "owner_only": "Solo el dueño del bot puede usar este comando",
        "joined_chat": "Listo, entré al chat",
        "joined_com": "Listo, entré a la comunidad",
        "error": "No pude entrar: {e}",
    },
    "en": {
        "bad": "I couldn't read that link",
        "owner_only": "Only the bot owner can use this command",
        "joined_chat": "Done, I joined the chat",
        "joined_com": "Done, I joined the community",
        "error": "Couldn't join: {e}",
    },
    "ru": {
        "bad": "Не удалось прочитать ссылку",
        "owner_only": "Эту команду может использовать только владелец бота",
        "joined_chat": "Готово, я вошёл в чат",
        "joined_com": "Готово, я вошёл в сообщество",
        "error": "Не удалось войти: {e}",
    },
}


def _m(lang, key, **kw):
    return (MSG.get(lang) or MSG["es"])[key].format(**kw)


def _code(link: str) -> str:
    return link.strip().split("?")[0].rstrip("/").split("/")[-1]


def _candidates(link: str) -> list:
    link = link.strip()
    path = urlparse(link).path.strip("/")
    alt = ["http://aminoapps.com/" + path] if path else []
    if "/c/" in link:
        out = [link] + alt + [_code(link)]
    else:
        out = [_code(link), link] + alt
    return list(dict.fromkeys(out))


@client.command(["!join"])
@commands_enable_required()
async def cmd_join(event: respObject.Event):
    lang = lang_of(event)
    if not is_owner(event):
        return await reply(event, deco.join_msg("bad", _m(lang, "owner_only")))
    link = args(event)
    if not link:
        return await reply(event, greeting(lang))

    bad = deco.join_msg("bad", _m(lang, "bad"))
    info = None
    for cand in _candidates(link):
        try:
            res = await client.get_from_link(cand)
            print("join resolve", cand, "->", getattr(res, "data", res))
        except Exception as e:
            print("join resolve falló", cand, repr(e))
            continue
        if getattr(res, "comId", None) or getattr(res, "objectId", None):
            info = res
            break
    if info is None:
        return await reply(event, bad)

    com_id = getattr(info, "comId", None) or 0
    obj_id = getattr(info, "objectId", None)
    is_chat = bool(obj_id) and (getattr(info, "objectType", None) == 12 or not com_id)

    try:
        if com_id:
            try:
                await client.join_community(com_id)
            except Exception:
                pass  # normalmente: ya estaba dentro
            if is_chat:
                await client.get_community_client(com_id).join_chat(obj_id)
                return await reply(event, deco.join_msg("chat", _m(lang, "joined_chat")))
            return await reply(event, deco.join_msg("com", _m(lang, "joined_com")))
        if is_chat:  # chat global
            await client.join_chat(obj_id)
            return await reply(event, deco.join_msg("chat", _m(lang, "joined_chat")))
        await reply(event, bad)
    except Exception as e:
        await reply(event, deco.join_msg("err", _m(lang, "error", e=str(e)[:150])))
