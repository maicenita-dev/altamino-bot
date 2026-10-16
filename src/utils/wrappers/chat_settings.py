from functools import wraps

_joined = set()


def commands_enable_required():
    """Antes de cada comando, el bot se une al chat si aún no lo hizo."""
    def deco(fn):
        @wraps(fn)
        async def wrapper(event, *a, **kw):
            chat_id = event.message.chatId
            if chat_id not in _joined:
                tgt = getattr(event, "sub_client", None) or event.client
                try:
                    await tgt.join_chat(chat_id)
                except Exception as e:
                    print("auto-join:", e)
                _joined.add(chat_id)
            return await fn(event, *a, **kw)
        return wrapper
    return deco
