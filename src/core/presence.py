"""Mantiene al bot "en línea" en todas las comunidades donde está."""
import asyncio

INTERVAL = 150      # segundos entre una ronda y la siguiente (bájalo si se ve intermitente)
PAUSE = 1.5         # pausa entre una comunidad y otra
_TASK = None


async def _joined_ids(client) -> list:
    ids, start = [], 0
    while start < 500:
        page = await client.get_joined_communities(start=start, size=25)
        if not page:
            break
        for c in page:
            cid = (getattr(c, "comId", None) or getattr(c, "ndcId", None)
                   or (getattr(c, "data", None) or {}).get("ndcId"))
            if cid:
                ids.append(cid)
        if len(page) < 25:
            break
        start += 25
    return list(dict.fromkeys(ids))


def _online_fn(client):
    fn = getattr(client, "online", None)
    if fn is not None:
        return fn
    from altamino.ws._async.actions import SocketActions
    return lambda cid: SocketActions.online(client, cid)


async def presence_loop(client):
    await asyncio.sleep(10)
    online, first = _online_fn(client), True
    while True:
        try:
            ids = await _joined_ids(client)
            if first:
                print(f"presence: en línea en {len(ids)} comunidades")
                first = False
            for cid in ids:
                try:
                    await online(cid)
                except Exception as e:
                    print("presence: falló", cid, repr(e)[:80])
                await asyncio.sleep(PAUSE)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print("presence error:", repr(e)[:100])
        await asyncio.sleep(INTERVAL)


def start_presence(client):
    global _TASK
    _TASK = asyncio.create_task(presence_loop(client))
    return _TASK
