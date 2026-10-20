"""
!join <link>  ->  el bot entra a la comunidad y/o al chat del link (también chats globales).
Ej: !join http://aminoapps.com/p/AbC123
"""
import time
from urllib.parse import urlparse

from altamino import respObject

from src.aa import client
from src.utils import reply
from src.utils.wrappers.chat_settings import commands_enable_required
from src.aa.modules.start import greeting
from src.core import deco
from src.core.config import DATA_DIR
from src.core.storage import load_json, save_json
from src.core.ctx import args, is_owner, lang_of

MSG = {
    "es": {
        "bad": "No pude leer ese link",
        "cooldown": "Esperá un poco antes de volver a usar este comando ({t})",
        "owner_only": "Solo el dueño del bot puede usar este comando",
        "joined_chat": "Listo, entré al chat",
        "joined_com": "Listo, entré a la comunidad",
        "error": "No pude entrar: {e}",
    },
    "en": {
        "bad": "I couldn't read that link",
        "cooldown": "Please wait a bit before using this command again ({t})",
        "owner_only": "Only the bot owner can use this command",
        "joined_chat": "Done, I joined the chat",
        "joined_com": "Done, I joined the community",
        "error": "Couldn't join: {e}",
    },
    "ru": {
        "bad": "Не удалось прочитать ссылку",
        "cooldown": "Подожди немного, прежде чем снова использовать эту команду ({t})",
        "owner_only": "Эту команду может использовать только владелец бота",
        "joined_chat": "Готово, я вошёл в чат",
        "joined_com": "Готово, я вошёл в сообщество",
        "error": "Не удалось войти: {e}",
    },
    "pt": {
        "bad": "Não consegui ler esse link",
        "cooldown": "Espere um pouco antes de usar este comando de novo ({t})",
        "joined_chat": "Pronto, entrei no chat",
        "joined_com": "Pronto, entrei na comunidade",
        "error": "Não consegui entrar: {e}",
        "owner_only": "Somente o dono do bot pode usar este comando",
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


JOIN_CD = 300           # segundos entre un uso y otro, por persona
JOIN_PER_DAY = 5        # máximo por persona cada 24 h
JOIN_PER_HOUR = 20      # máximo en total cada hora
JOIN_LOG = DATA_DIR / "join_log.json"
JOIN_HISTORY = DATA_DIR / "join_history.log"


def _fmt_wait(sec):
    sec = max(1, int(sec))
    h, m = sec // 3600, (sec % 3600) // 60
    if h:
        return f"{h}h {m}m"
    return f"{m}m {sec % 60}s" if m else f"{sec}s"


def _join_limit(event) -> int:
    """Segundos de espera si se pasó de algún límite (0 = puede). El dueño no tiene límites."""
    if is_owner(event):
        return 0
    uid = event.message.author.userId
    now = time.time()
    log = [x for x in load_json(JOIN_LOG, []) if now - x["t"] < 86400]
    mine = [x["t"] for x in log if x["u"] == uid]
    if mine and now - max(mine) < JOIN_CD:
        return int(JOIN_CD - (now - max(mine)))
    if len(mine) >= JOIN_PER_DAY:
        return int(86400 - (now - min(mine)))
    hour = [x["t"] for x in log if now - x["t"] < 3600]
    if len(hour) >= JOIN_PER_HOUR:
        return int(3600 - (now - min(hour)))
    return 0


def _log_join(event, link):
    now = time.time()
    a = event.message.author
    log = [x for x in load_json(JOIN_LOG, []) if now - x["t"] < 86400]
    log.append({"t": now, "u": a.userId})
    save_json(JOIN_LOG, log)
    with open(JOIN_HISTORY, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {a.userId} | {a.nickname or '?'} | {link[:150]}\n")


@client.command(["!join"])
@commands_enable_required()
async def cmd_join(event: respObject.Event):
    lang = lang_of(event)
    link = args(event)
    if not link:
        return await reply(event, greeting(lang))
    wait = _join_limit(event)
    if wait:
        return await reply(event, deco.join_msg("bad", _m(lang, "cooldown", t=_fmt_wait(wait))))
    _log_join(event, link)

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
