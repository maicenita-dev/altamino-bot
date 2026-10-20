"""Cartas: favorito (!fav), liberar (!liberar) y rarezas (!rarezas)."""
import time

from altamino import respObject

from src.aa import client
from src.aa.modules.cards import (FAV_CHANCE, WEIGHTS, _fmt, _load, _lock,
                                  _save, _user)
from src.aa.modules.cards_search import _norm, _score
from src.core import deco
from src.core.catalog import get_catalog
from src.core.ctx import args, lang_of, scope_of
from src.utils import reply
from src.utils.wrappers.chat_settings import commands_enable_required

FAV_COOLDOWN = 24 * 3600
CONFIRM_SECONDS = 30
_pending = {}

MSG = {
    "es": {
        "no_fav": "Todavía no tenés un favorito. Elegí uno con !fav <nombre>.",
        "current": "⭐ Tu favorito: {name} · {series} ({chance}% extra por tirada)",
        "wait": "Podés cambiar tu favorito en {t}.",
        "none": "No encontré personajes con ese nombre.",
        "taken": "{name} ya es de {nick}. Elegí otro.",
        "set": "⭐ {name} es ahora tu favorito. Tiene {chance}% extra de salir en cada tirada.",
        "set_owned": "⭐ {name} es ahora tu favorito. Ya es tuyo, así que aparece con ⭐ en !harem.",
        "off": "Quitaste tu favorito.",
        "lib_usage": "Escribí el nombre del personaje. Ej: !liberar Hatsune Miku",
        "lib_none": "No tenés ningún personaje con ese nombre.",
        "lib_confirm": "¿Seguro que querés liberar a {name}? Volvé a escribir !liberar {name} en {s} segundos para confirmar.",
        "lib_done": "{nick} liberó a {name}. Ya está libre para que otros lo reclamen.",
        "title": "Rarezas de las cartas",
        "common": "⚪ Común — {p}% de las tiradas",
        "rare": "🔵 Rara — {p}% de las tiradas",
        "epic": "🟣 Épica — {p}% de las tiradas",
        "legendary": "🟡 Legendaria — {p}% de las tiradas",
        "note": "La rareza depende de la popularidad del personaje: cuanto más querido, más raro. En Vocaloid, UTAU, fanloids, Hazbin Hotel y Helluva Boss la rareza está elegida a mano.",
        "fav_note": "Tu favorito (!fav) tiene un extra de probabilidad de salir: ⚪ {c0}% · 🔵 {c1}% · 🟣 {c2}% · 🟡 {c3}%.",
    },
    "en": {
        "no_fav": "You don't have a favorite yet. Pick one with !fav <name>.",
        "current": "⭐ Your favorite: {name} · {series} ({chance}% extra per roll)",
        "wait": "You can change your favorite in {t}.",
        "none": "No characters found with that name.",
        "taken": "{name} already belongs to {nick}. Pick another one.",
        "set": "⭐ {name} is now your favorite. It has a {chance}% extra chance to show up on each roll.",
        "set_owned": "⭐ {name} is now your favorite. It's already yours, so it shows with ⭐ in !harem.",
        "off": "You removed your favorite.",
        "lib_usage": "Write the character's name. Ex: !liberar Hatsune Miku",
        "lib_none": "You don't have a character with that name.",
        "lib_confirm": "Are you sure you want to release {name}? Write !liberar {name} again within {s} seconds to confirm.",
        "lib_done": "{nick} released {name}. It's free now for others to claim.",
        "title": "Card rarities",
        "common": "⚪ Common — {p}% of rolls",
        "rare": "🔵 Rare — {p}% of rolls",
        "epic": "🟣 Epic — {p}% of rolls",
        "legendary": "🟡 Legendary — {p}% of rolls",
        "note": "Rarity depends on how popular the character is: the more loved, the rarer. For Vocaloid, UTAU, fanloids, Hazbin Hotel and Helluva Boss, rarity is set by hand.",
        "fav_note": "Your favorite (!fav) has an extra chance to show up: ⚪ {c0}% · 🔵 {c1}% · 🟣 {c2}% · 🟡 {c3}%.",
    },
    "ru": {
        "no_fav": "У тебя пока нет любимого персонажа. Выбери: !fav <имя>.",
        "current": "⭐ Твой любимый: {name} · {series} (+{chance}% за бросок)",
        "wait": "Сменить любимого можно через {t}.",
        "none": "Персонажи с таким именем не найдены.",
        "taken": "{name} уже у {nick}. Выбери другого.",
        "set": "⭐ {name} теперь твой любимый. Дополнительный шанс выпасть в каждом броске: {chance}%.",
        "set_owned": "⭐ {name} теперь твой любимый. Он уже твой, поэтому в !harem отмечен ⭐.",
        "off": "Ты убрал(а) любимого персонажа.",
        "lib_usage": "Напиши имя персонажа. Пример: !liberar Hatsune Miku",
        "lib_none": "У тебя нет персонажа с таким именем.",
        "lib_confirm": "Точно освободить {name}? Напиши !liberar {name} ещё раз в течение {s} сек. для подтверждения.",
        "lib_done": "{nick} освободил(а) {name}. Теперь его могут забрать другие.",
        "title": "Редкость карт",
        "common": "⚪ Обычная — {p}% бросков",
        "rare": "🔵 Редкая — {p}% бросков",
        "epic": "🟣 Эпическая — {p}% бросков",
        "legendary": "🟡 Легендарная — {p}% бросков",
        "note": "Редкость зависит от популярности персонажа: чем любимее, тем реже. Для Vocaloid, UTAU, фанлоидов, Hazbin Hotel и Helluva Boss редкость задана вручную.",
        "fav_note": "У твоего любимого (!fav) есть дополнительный шанс выпасть: ⚪ {c0}% · 🔵 {c1}% · 🟣 {c2}% · 🟡 {c3}%.",
    },
}


def _m(lang, key, **kw):
    return (MSG.get(lang) or MSG["es"])[key].format(**kw)


def _pct(x: float) -> str:
    return f"{x * 100:g}"


async def _find(text):
    """Mejor coincidencia en los dos catálogos: (género, personaje) o None."""
    q = _norm(text)
    best = None
    for kind in ("waifu", "husbando"):
        for c in await get_catalog(kind):
            sc = _score(q, c["name"], c["series"])
            if sc:
                key = (sc, c["rarity"], c.get("fav") or 0)
                if best is None or key > best[0]:
                    best = (key, kind, c)
    return (best[1], best[2]) if best else None


@client.command(["!fav"])
@commands_enable_required()
async def cmd_fav(event: respObject.Event):
    lang, scope = lang_of(event), scope_of(event)
    arg = args(event).strip()
    async with _lock:
        db = _load(scope)
        uid, u = _user(db, event)
        now = time.time()
        fav = u.get("fav")
        if fav:
            own = db["owners"].get(str(fav["id"]))
            if own and own["user"] != uid:      # otra persona lo reclamó
                u["fav"], u["fav_at"], fav = None, 0, None
        wait = u.get("fav_at", 0) + FAV_COOLDOWN - now

        if not arg:
            _save(scope, db)
            if not fav:
                return await reply(event, deco.fav_none(_m(lang, "no_fav")))
            text = _m(lang, "current", name=fav["name"], series=fav["series"],
                      chance=_pct(FAV_CHANCE[fav["rarity"]]))
            more = _m(lang, "wait", t=_fmt(wait)) if wait > 0 else None
            return await reply(event, deco.fav_current(text, more))

        if arg.lower() == "off":
            u["fav"] = None
            _save(scope, db)
            return await reply(event, deco.fav_off(_m(lang, "off")))

        found = await _find(arg)
        if not found:
            _save(scope, db)
            return await reply(event, deco.notfound(_m(lang, "none")))
        kind, ch = found
        fid = str(ch["id"])
        own = db["owners"].get(fid)
        if own and own["user"] != uid:
            _save(scope, db)
            nick = db["users"].get(own["user"], {}).get("nick", "?")
            return await reply(event, deco.fav_taken(_m(lang, "taken", name=ch["name"], nick=nick)))
        same = bool(fav) and str(fav["id"]) == fid
        if not same and wait > 0:
            _save(scope, db)
            return await reply(event, deco.fav_wait(_m(lang, "wait", t=_fmt(wait))))
        if not same:
            u["fav"] = {"id": ch["id"], "name": ch["name"], "series": ch["series"],
                        "rarity": ch["rarity"], "kind": kind}
            u["fav_at"] = now
        _save(scope, db)
        owned = bool(own)
    text = _m(lang, "set_owned" if owned else "set", name=ch["name"],
              chance=_pct(FAV_CHANCE[ch["rarity"]]))
    await reply(event, deco.fav_owned(text) if owned else deco.fav_set(text))


@client.command(["!liberar", "!release"])
@commands_enable_required()
async def cmd_liberar(event: respObject.Event):
    lang, scope = lang_of(event), scope_of(event)
    arg = args(event).strip()
    if not arg:
        return await reply(event, deco.lib("usage", _m(lang, "lib_usage")))
    async with _lock:
        db = _load(scope)
        uid, u = _user(db, event)
        q = _norm(arg)
        hits = []
        for cid, c in db["owners"].items():
            if c["user"] == uid:
                sc = _score(q, c["name"])          # solo por nombre
                if sc:
                    hits.append((sc, c["rarity"], cid, c))
        if not hits:
            _save(scope, db)
            return await reply(event, deco.lib("none", _m(lang, "lib_none")))
        hits.sort(key=lambda h: (-h[0], -h[1]))
        _, _, cid, c = hits[0]
        key, now = (scope, uid), time.time()
        pend = _pending.get(key)
        if pend and pend[0] == cid and now - pend[1] <= CONFIRM_SECONDS:
            del db["owners"][cid]
            _pending.pop(key, None)
            _save(scope, db)
            return await reply(event, deco.lib("done", _m(lang, "lib_done", nick=u["nick"], name=c["name"])))
        _pending[key] = (cid, now)
        _save(scope, db)
    await reply(event, deco.lib("confirm", _m(lang, "lib_confirm", name=c["name"], s=CONFIRM_SECONDS)))


@client.command(["!rarezas", "!rarity"])
@commands_enable_required()
async def cmd_rarezas(event: respObject.Event):
    lang = lang_of(event)
    total = sum(WEIGHTS)
    names = ["common", "rare", "epic", "legendary"]
    lines = [_m(lang, k, p=round(100 * w / total)) for k, w in zip(names, WEIGHTS)]
    chances = {f"c{i}": _pct(c) for i, c in enumerate(FAV_CHANCE)}
    await reply(event, deco.rarities(_m(lang, "title"), lines, _m(lang, "note"),
                                     _m(lang, "fav_note", **chances)))


# --- pt (generado) ---
from src.core.pt_cards import PT as _PT  # noqa: E402
MSG["pt"] = _PT["cards_extra"]
