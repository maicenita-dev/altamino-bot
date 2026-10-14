"""
ÚNICO lugar que toca la API de altamino.py para datos "extra" (nickname,
miembros del chat, menciones, enviar gifs). Si algo falla al probar,
se ajusta acá y listo: el resto del bot no se entera.

Lo que YA está confirmado por tus horoscope.py / tts.py:
  event.message.content / .author.userId / .chatId
  event.sub_client or event.client  ->  .send_media(chatId, archivo)
Lo que está ADIVINADO (marcado con  # ??? ):
  nickname del autor, listar miembros, menciones.
"""
from .gifs import get_gif
from .lang import get_lang


def args(event) -> str:
    return (event.message.content or "").strip()


def target(event):
    return event.sub_client or event.client


def lang_of(event) -> str:
    return get_lang(event.message.author.userId)


def author_of(event) -> dict:
    a = event.message.author
    return {"userId": a.userId, "nickname": getattr(a, "nickname", None) or "?"}  # ???


def mentioned_of(event) -> list:
    """Usuarios mencionados en el mensaje (Amino los manda en extensions.mentionedArray)."""
    ext = getattr(event.message, "extensions", None) or {}  # ???
    arr = ext.get("mentionedArray", []) if isinstance(ext, dict) else getattr(ext, "mentionedArray", [])
    out = []
    for m in arr or []:
        uid = m.get("uid") if isinstance(m, dict) else getattr(m, "uid", None)
        if uid:
            out.append({"userId": uid, "nickname": None})
    return out


async def members_of(event) -> list:
    """Miembros del chat como [{"userId", "nickname"}]."""
    tgt = target(event)
    chat_id = event.message.chatId
    # ??? probamos nombres comunes de método hasta encontrar uno que exista
    for name in ("get_chat_users", "get_chat_members", "get_chat_threads_users"):
        fn = getattr(tgt, name, None)
        if fn is None:
            continue
        res = await fn(chat_id)
        users = getattr(res, "profileList", None) or getattr(res, "members", None) or res
        return [
            {"userId": getattr(u, "userId", None) or getattr(u, "uid", None),
             "nickname": getattr(u, "nickname", None) or "?"}
            for u in users
        ]
    return []


async def send_gif(event, key: str) -> None:
    """Manda el gif de la reacción; en silencio si no existe el archivo."""
    gif = get_gif(key)
    if gif is not None:
        try:
            await target(event).send_media(event.message.chatId, gif)
        except Exception:
            pass
