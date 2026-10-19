"""Búsqueda de personajes: !buscar, !carta, !serie."""
import re
import unicodedata
from asyncio import to_thread

from altamino import respObject

from src.aa import client
from src.aa.modules.cards import RARITY, _download, _load
from src.core import deco
from src.core.catalog import get_catalog
from src.core.ctx import args, lang_of, scope_of, target
from src.utils import reply
from src.utils.wrappers.chat_settings import commands_enable_required

MSG = {
    "es": {
        "usage_search": "Escribí un nombre. Ej: !buscar miku",
        "usage_card": "Escribí el nombre del personaje. Ej: !carta Hatsune Miku",
        "usage_series": "Escribí el nombre de la serie. Ej: !serie Hazbin Hotel",
        "none": "No encontré personajes con ese nombre.",
        "none_series": "No encontré esa serie.",
        "results": "🔎 Resultados para «{q}»:",
        "series_title": "📺 {series} — {n} personajes ({free} libres)",
        "free": "libre",
        "owned": "de {nick}",
        "more": "…y {n} más",
        "others": "Más resultados: !buscar {q}",
    },
    "en": {
        "usage_search": "Write a name. Ex: !buscar miku",
        "usage_card": "Write the character's name. Ex: !carta Hatsune Miku",
        "usage_series": "Write the series name. Ex: !serie Hazbin Hotel",
        "none": "No characters found with that name.",
        "none_series": "Series not found.",
        "results": "🔎 Results for «{q}»:",
        "series_title": "📺 {series} — {n} characters ({free} free)",
        "free": "free",
        "owned": "owned by {nick}",
        "more": "…and {n} more",
        "others": "More results: !buscar {q}",
    },
    "ru": {
        "usage_search": "Напиши имя. Пример: !buscar miku",
        "usage_card": "Напиши имя персонажа. Пример: !carta Hatsune Miku",
        "usage_series": "Напиши название серии. Пример: !serie Hazbin Hotel",
        "none": "Персонажи с таким именем не найдены.",
        "none_series": "Серия не найдена.",
        "results": "🔎 Результаты по «{q}»:",
        "series_title": "📺 {series} — {n} персонажей (свободных: {free})",
        "free": "свободен",
        "owned": "у {nick}",
        "more": "…и ещё {n}",
        "others": "Другие результаты: !buscar {q}",
    },
}


def _m(lang, key, **kw):
    return (MSG.get(lang) or MSG["es"])[key].format(**kw)


def _norm(s: str) -> str:
    s = (s or "").lower().replace("ø", "o")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^\w ]+", " ", s).split())


def _words_match(qw: list, words: list, prefix: bool = True) -> bool:
    for q in qw:
        if not any(w == q or (prefix and len(q) >= 3 and w.startswith(q)) for w in words):
            return False
    return True


def _score(query: str, name: str, series: str = "") -> int:
    n = _norm(name)
    nw, qw = n.split(), query.split()
    if n == query:
        return 5
    if _words_match(qw, nw, prefix=False):
        return 4
    if len(query) >= 3 and n.startswith(query):
        return 3
    if _words_match(qw, nw):
        return 2
    if _words_match(qw, _norm(series).split()):
        return 1
    return 0


def _search(chars: list, text: str) -> list:
    q = _norm(text)
    if not q:
        return []
    hits = [(_score(q, c["name"], c["series"]), c) for c in chars]
    hits = [(sc, c) for sc, c in hits if sc]
    hits.sort(key=lambda x: (-x[0], -x[1]["rarity"], -(x[1].get("fav") or 0)))
    return [c for _, c in hits]


async def _all() -> list:
    return (await get_catalog("waifu")) + (await get_catalog("husbando"))


def _status(lang, db, ch) -> str:
    own = db["owners"].get(str(ch["id"]))
    if not own:
        return _m(lang, "free")
    return _m(lang, "owned", nick=db["users"].get(own["user"], {}).get("nick", "?"))


@client.command(["!buscar"])
@commands_enable_required()
async def cmd_buscar(event: respObject.Event):
    lang = lang_of(event)
    q = args(event).strip()
    if not q:
        return await reply(event, deco.search_usage(_m(lang, "usage_search")))
    hits = _search(await _all(), q)[:5]
    if not hits:
        return await reply(event, deco.notfound(_m(lang, "none")))
    db = _load(scope_of(event))
    lines = [f"{RARITY[c['rarity']]} {c['name']} · {c['series']} — {_status(lang, db, c)}"
             for c in hits]
    await reply(event, deco.search_results(_m(lang, "results", q=q), lines))


@client.command(["!carta"])
@commands_enable_required()
async def cmd_carta(event: respObject.Event):
    lang = lang_of(event)
    q = args(event).strip()
    if not q:
        return await reply(event, deco.card_usage(_m(lang, "usage_card")))
    hits = _search(await _all(), q)
    if not hits:
        return await reply(event, deco.notfound(_m(lang, "none")))
    ch = hits[0]
    db = _load(scope_of(event))
    try:
        await target(event).send_media(event.message.chatId, await to_thread(_download, ch["img"]), "image/jpeg")
    except Exception as e:
        print("carta imagen:", repr(e))
    extra = f"❤️ {ch['fav']}" if ch.get("fav") else f"🏷️ {ch.get('category', '')}"
    more = _m(lang, "others", q=q) if len(hits) > 1 else None
    await reply(event, deco.card(f"{RARITY[ch['rarity']]} {ch['name']}", f"📺 {ch['series']}",
                                 extra, f"👤 {_status(lang, db, ch)}", more))


@client.command(["!serie"])
@commands_enable_required()
async def cmd_serie(event: respObject.Event):
    lang = lang_of(event)
    raw = args(event).strip()
    q = _norm(raw)
    if not q:
        return await reply(event, deco.series_usage(_m(lang, "usage_series")))
    chars = [c for c in await _all() if q in _norm(c["series"])]
    if not chars:
        return await reply(event, deco.series_none(_m(lang, "none_series")))
    chars.sort(key=lambda c: (-c["rarity"], c["name"]))
    db = _load(scope_of(event))
    free = sum(1 for c in chars if str(c["id"]) not in db["owners"])
    names = {c["series"] for c in chars}
    series = names.pop() if len(names) == 1 else raw
    lines = [f"{RARITY[c['rarity']]} {c['name']} — {_status(lang, db, c)}" for c in chars[:20]]
    more = _m(lang, "more", n=len(chars) - 20) if len(chars) > 20 else None
    await reply(event, deco.series_list(
        _m(lang, "series_title", series=series, n=len(chars), free=free), lines, more))
