"""
ÚNICO lugar que toca la API de altamino.py para datos "extra" (nickname,
miembros del chat, menciones, enviar gifs). Todo verificado contra
altamino 1.1.6.2:
  Message: content, chatId, author (UserProfile: userId, nickname)
  Event: client, sub_client (se crea solo desde el comId del chat)
  get_chat_users(chatId, start, size) -> list[UserProfile]
"""
from .gifs import get_gif
from .lang import get_lang

PAGE = 100
MAX_MEMBERS = 500


def args(event) -> str:
    return (event.message.content or "").strip()


def target(event):
    return event.sub_client or event.client


def lang_of(event) -> str:
    return get_lang(event.message.author.userId, scope_of(event))


def author_of(event) -> dict:
    a = event.message.author
    return {"userId": a.userId, "nickname": a.nickname or "?"}


def mentioned_of(event) -> list:
    """Usuarios mencionados (Amino los manda en extensions.mentionedArray)."""
    return [{"userId": uid, "nickname": None}
            for uid in (event.message.mentionUserIds or []) if uid]


async def members_of(event) -> list:
    """Miembros del chat como [{"userId", "nickname"}], paginando."""
    tgt = target(event)
    chat_id = event.message.chatId
    out, start = [], 0
    while start < MAX_MEMBERS:
        try:
            page = await tgt.get_chat_users(chat_id, start=start, size=PAGE)
        except Exception as e:
            print("members_of error:", repr(e))
            break
        if not page:
            break
        out.extend({"userId": u.userId, "nickname": u.nickname or "?"} for u in page)
        if len(page) < PAGE:
            break
        start += PAGE
    if len(out) < 2:
        out = await _members_fallback(event, out)
    return out


async def send_gif(event, key: str) -> None:
    """Manda el gif de la reacción; en silencio si no existe el archivo."""
    gif = get_gif(key)
    if gif is not None:
        try:
            await target(event).send_media(event.message.chatId, gif)
        except Exception:
            pass


def scope_of(event) -> str:
    """Clave de datos: id de comunidad, o 'g<chatId>' para chats globales."""
    if event.comId:
        return str(event.comId)
    return "g" + str(event.message.chatId)


def is_staff(event) -> bool:
    """Staff de la comunidad (rol >= 100) o dueño del bot (data/owners.json)."""
    from .config import DATA_DIR
    from .storage import load_json
    a = event.message.author
    try:
        if int(getattr(a, "role", 0) or 0) >= 100:
            return True
    except (TypeError, ValueError):
        pass
    owners = load_json(DATA_DIR / "owners.json", [])
    return str(a.userId) in {str(o) for o in owners}


import time as _time  # noqa: E402

from altamino import respObject as _ro  # noqa: E402

_HOSTS: dict = {}


async def _chat_hosts(event) -> set:
    """Anfitrión + co-anfitriones del chat del evento (caché de 5 min)."""
    chat_id = event.message.chatId
    hit = _HOSTS.get(chat_id)
    if hit and _time.time() - hit[0] < 300:
        return hit[1]
    ids = set()
    try:
        path = (f"/x{event.comId}/s/chat/thread/{chat_id}" if event.comId
                else f"/g/s/chat/thread/{chat_id}")
        resp = await event.client.req.make_async_request("GET", path)
        chat = _ro.Chat(await resp.json())
        if chat.author and chat.author.userId:
            ids.add(str(chat.author.userId))
        for c in chat.coHosts or []:
            ids.add(str(c.get("uid") if isinstance(c, dict) else c))
        _HOSTS[chat_id] = (_time.time(), ids)
        print("hosts", chat_id, ids)
    except Exception as e:
        print("hosts error:", repr(e))
    return ids


async def is_staff_ex(event) -> bool:
    """Staff de la comunidad, dueño del bot, o anfitrión/co-anfitrión de ESTE chat."""
    if is_staff(event):
        return True
    return str(event.message.author.userId) in await _chat_hosts(event)



async def _members_fallback(event, current):
    """Si get_chat_users no sirve (chats globales), usa los miembros que trae el chat."""
    try:
        chat_id = event.message.chatId
        path = (f"/x{event.comId}/s/chat/thread/{chat_id}" if event.comId
                else f"/g/s/chat/thread/{chat_id}")
        resp = await event.client.req.make_async_request("GET", path)
        chat = _ro.Chat(await resp.json())
        out = [{"userId": u.userId, "nickname": u.nickname or "?"}
               for u in chat.membersSummary if u.userId]
        print("members fallback:", len(out))
        return out or current
    except Exception as e:
        print("members fallback error:", repr(e))
        return current


def is_owner(event) -> bool:
    """Dueño del bot (lista en data/owners.json)."""
    from .config import DATA_DIR
    from .storage import load_json
    owners = load_json(DATA_DIR / "owners.json", [])
    return str(event.message.author.userId) in {str(o) for o in owners}
