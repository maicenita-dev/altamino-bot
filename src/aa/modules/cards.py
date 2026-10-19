"""Cartas estilo Mudae. Datos separados por comunidad (o por chat global)."""
import random
import subprocess
from pathlib import Path
import time
from asyncio import Lock, to_thread
from io import BytesIO
from urllib.request import Request, urlopen

from altamino import respObject

from src.aa import client
from src.utils import reply
from src.utils.wrappers.chat_settings import commands_enable_required
from src.core import deco
from src.core.catalog import get_catalog
from src.core.config import DATA_DIR
from src.core.ctx import args, lang_of, scope_of, target
from src.core.storage import load_json, save_json

ROLLS = 10
WINDOW = 3 * 3600
CLAIM_CD = 3 * 3600
EXPIRE = 300
PER_PAGE = 15
RARITY = ["⚪", "🔵", "🟣", "🟡"]
WEIGHTS = [60, 25, 12, 3]
CARDS_DIR = DATA_DIR / "cards"
CARDS_DIR.mkdir(parents=True, exist_ok=True)
_lock = Lock()

MSG = {
    "es": {
        "no_rolls_1": "Ya usaste tus {n} tiradas",
        "no_rolls_2": "Se renuevan en {t}.",
        "no_catalog": "No pude cargar el catálogo de personajes.",
        "none_free": "Ya no quedan personajes libres.",
        "roll_left": "Tiradas restantes: {left}/{n}",
        "roll_claim": "Usá !claim para reclamarla (5 min).",
        "nothing": "No tenés ninguna tirada para reclamar (o ya venció).",
        "taken": "Alguien ya reclamó a ese personaje.",
        "wait": "Podés reclamar de nuevo en {t}.",
        "claimed": "{nick} reclamó a {name}",
        "empty": "Todavía no tenés personajes. Probá !waifu o !husbando.",
        "harem": "Colección de {nick} ({n}) — pág. {p}/{tp}",
        "top": "Top coleccionistas",
        "no_top": "Todavía nadie reclamó personajes.",
        "cd_rolls": "Tiradas: {left}/{n}",
        "cd_claim": "Reclamo: {claim}",
        "ready": "disponible ✅",
    },
    "en": {
        "no_rolls_1": "You used all {n} rolls",
        "no_rolls_2": "They reset in {t}.",
        "no_catalog": "I couldn't load the character catalog.",
        "none_free": "No free characters left.",
        "roll_left": "Rolls left: {left}/{n}",
        "roll_claim": "Use !claim to claim it (5 min).",
        "nothing": "You have no roll to claim (or it expired).",
        "taken": "Someone already claimed that character.",
        "wait": "You can claim again in {t}.",
        "claimed": "{nick} claimed {name}",
        "empty": "You have no characters yet. Try !waifu or !husbando.",
        "harem": "{nick}'s collection ({n}) — page {p}/{tp}",
        "top": "Top collectors",
        "no_top": "Nobody has claimed characters yet.",
        "cd_rolls": "Rolls: {left}/{n}",
        "cd_claim": "Claim: {claim}",
        "ready": "available ✅",
    },
    "ru": {
        "no_rolls_1": "Все {n} бросков использованы",
        "no_rolls_2": "Обновятся через {t}.",
        "no_catalog": "Не удалось загрузить каталог персонажей.",
        "none_free": "Свободных персонажей не осталось.",
        "roll_left": "Осталось бросков: {left}/{n}",
        "roll_claim": "Напиши !claim, чтобы забрать (5 мин).",
        "nothing": "Нечего забирать (или время вышло).",
        "taken": "Этого персонажа уже забрали.",
        "wait": "Забрать снова можно через {t}.",
        "claimed": "{nick} забрал(а) {name}",
        "empty": "У тебя пока нет персонажей. Попробуй !waifu или !husbando.",
        "harem": "Коллекция {nick} ({n}) — стр. {p}/{tp}",
        "top": "Топ коллекционеров",
        "no_top": "Пока никто никого не забрал.",
        "cd_rolls": "Броски: {left}/{n}",
        "cd_claim": "Забрать: {claim}",
        "ready": "доступно ✅",
    },
}


def _m(lang, key, **kw):
    return (MSG.get(lang) or MSG["es"])[key].format(**kw)


def _frame(emoji, lines):
    top = f"[c]°    ‿      ‿   ‿     ‿   {emoji}   ‿     ‿     ‿     ‿   °"
    return "\n".join([top, ""] + lines + ["", top])


DOT = "[c]💐̸֠᪲   ׄ  ۰   ⌒  ִ   "
TRI = "𑇡  〬  "
BOX = "⏝ׅ  ⿻  "
NOTICES = {"nothing": ("💔", DOT), "taken": ("🙀", DOT), "wait": ("⏱️", DOT),
           "empty": ("💟", BOX), "none_free": ("💔", TRI)}


def _notice(lang, kind, **kw):
    if kind == "no_rolls":
        return _frame("⏱️", ["[c]✿ ⃝🫠ㅤㅤׅ" + _m(lang, "no_rolls_1", n=ROLLS), "",
                             DOT + _m(lang, "no_rolls_2", t=kw["t"])])
    emoji, pre = NOTICES[kind]
    return _frame(emoji, [pre + _m(lang, kind, **kw)])


def _top_msg(lang, lines):
    title = "[cu]🏆 ᩥㅤ✿ㅤ" + _m(lang, "top") + "ㅤ♡ㅤᲘᲘ"
    return _frame("💘", [title, ""] + [TRI + x for x in lines])


def _fmt(sec: float) -> str:
    sec = max(0, int(sec))
    h, m = sec // 3600, (sec % 3600) // 60
    if h:
        return f"{h}h {m}m"
    return f"{m}m" if m else "<1m"


def _load(scope):
    return load_json(CARDS_DIR / f"{scope}.json", {"owners": {}, "users": {}})


def _save(scope, db):
    save_json(CARDS_DIR / f"{scope}.json", db)


def _user(db, event):
    uid = event.message.author.userId
    u = db["users"].setdefault(uid, {"rolls": 0, "roll_start": 0, "claim_at": 0, "last": None})
    u["nick"] = event.message.author.nickname or "?"
    return uid, u


def _refresh(u, now):
    if now - u["roll_start"] >= WINDOW:
        u["roll_start"], u["rolls"] = now, 0


def _download_raw(url: str) -> BytesIO:
    if not url.startswith("http"):
        path = Path(url)
        buf = BytesIO(path.read_bytes())
        buf.name = path.name
        return buf
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=20) as r:
        buf = BytesIO(r.read())
    ext = url.split("?")[0].rsplit(".", 1)[-1].lower()
    buf.name = "card." + (ext if ext in ("jpg", "jpeg", "png", "webp", "gif") else "jpg")
    return buf


CUSTOM_CHANCE = 0.25
CAT_GROUPS = {"cartoon": {"hazbin", "helluva"}}


def _in_cat(c, cat):
    if cat == "anime":
        return not c.get("custom")
    mine = c.get("category")
    return mine == cat or mine in CAT_GROUPS.get(cat, ())


def _pick(catalog, owners, cat=None):
    free = [c for c in catalog if str(c["id"]) not in owners]
    if cat:
        free = [c for c in free if _in_cat(c, cat)]
    else:
        custom = [c for c in free if c.get("custom")]
        if custom and random.random() < CUSTOM_CHANCE:
            free = custom
    if not free:
        return None
    tier = random.choices([0, 1, 2, 3], weights=WEIGHTS)[0]
    return random.choice([c for c in free if c["rarity"] == tier] or free)


FAV_CHANCE = [0.05, 0.04, 0.025, 0.01]


def _fav_boost(db, u, uid, catalog, cat):
    """Favorito: probabilidad extra de que salga si está libre."""
    fav = u.get("fav")
    if not fav:
        return None
    fid = str(fav["id"])
    own = db["owners"].get(fid)
    if own:
        if own["user"] != uid:
            u["fav"], u["fav_at"] = None, 0
        return None
    ch = next((c for c in catalog if str(c["id"]) == fid), None)
    if ch is None or (cat and not _in_cat(ch, cat)):
        return None
    return ch if random.random() < FAV_CHANCE[ch["rarity"]] else None


async def _roll(event, kind, cat=None):
    lang, scope = lang_of(event), scope_of(event)
    async with _lock:
        db = _load(scope)
        uid, u = _user(db, event)
        now = time.time()
        _refresh(u, now)
        if u["rolls"] >= ROLLS:
            _save(scope, db)
            return await reply(event, _notice(lang, "no_rolls", t=_fmt(u["roll_start"] + WINDOW - now)))
        try:
            catalog = await get_catalog(kind)
        except Exception as e:
            print("cards catálogo:", repr(e))
            catalog = []
        if not catalog:
            return await reply(event, deco.cards_error(_m(lang, "no_catalog")))
        ch = _fav_boost(db, u, uid, catalog, cat) or _pick(catalog, db["owners"], cat)
        if ch is None:
            return await reply(event, _notice(lang, "none_free"))
        u["rolls"] += 1
        u["last"] = {"id": ch["id"], "kind": kind, "name": ch["name"],
                     "series": ch["series"], "rarity": ch["rarity"], "t": now}
        _save(scope, db)
        left = ROLLS - u["rolls"]
    chat_id = event.message.chatId
    try:
        await target(event).send_media(chat_id, await to_thread(_download, ch["img"]), "image/jpeg")
    except Exception as e:
        print("cards imagen:", repr(e))
    top = "[c]°    ‿      ‿   ‿     ‿   💟   ‿     ‿     ‿     ‿   °"
    d = "⏝ׅ  ⿻  "
    text = "\n".join([
        top, "",
        d + f"{RARITY[ch['rarity']]} {ch['name']}",
        d + f"📺 {ch['series']}",
        d + (f"❤️ {ch['fav']}" if ch.get("fav") else f"🏷️ {ch.get('category', '')}"),
        "",
        d + _m(lang, "roll_left", left=left, n=ROLLS),
        d + _m(lang, "roll_claim"),
        "", top,
    ])
    await reply(event, text)


@client.command(["!waifu"])
@commands_enable_required()
async def cmd_waifu(event: respObject.Event):
    await _roll(event, "waifu", args(event).strip().lower() or None)


@client.command(["!husbando"])
@commands_enable_required()
async def cmd_husbando(event: respObject.Event):
    await _roll(event, "husbando", args(event).strip().lower() or None)


@client.command(["!claim"])
@commands_enable_required()
async def cmd_claim(event: respObject.Event):
    lang, scope = lang_of(event), scope_of(event)
    async with _lock:
        db = _load(scope)
        uid, u = _user(db, event)
        now = time.time()
        last = u.get("last")
        if not last or now - last["t"] > EXPIRE:
            u["last"] = None
            _save(scope, db)
            return await reply(event, _notice(lang, "nothing"))
        if str(last["id"]) in db["owners"]:
            u["last"] = None
            _save(scope, db)
            return await reply(event, _notice(lang, "taken"))
        if now < u.get("claim_at", 0):
            return await reply(event, _notice(lang, "wait", t=_fmt(u["claim_at"] - now)))
        db["owners"][str(last["id"])] = {
            "user": uid, "kind": last["kind"], "name": last["name"],
            "series": last["series"], "rarity": last["rarity"], "t": now}
        u["claim_at"] = now + CLAIM_CD
        u["last"] = None
        _save(scope, db)
        nick = u["nick"]
    top = "[c]°    ‿      ‿   ‿     ‿   💘   ‿     ‿     ‿     ‿   °"
    d = "𖹭🪷ㅤᢄ︧ ꢶᝳ  ֟፝ ᳕   ̨ꢶ︨ᢃㅤ"
    await reply(event, "\n".join([
        top, "",
        d + _m(lang, "claimed", nick=nick, name=last["name"]),
        "", top,
    ]))


@client.command(["!harem"])
@commands_enable_required()
async def cmd_harem(event: respObject.Event):
    lang, scope = lang_of(event), scope_of(event)
    db = _load(scope)
    uid = event.message.author.userId
    mine = [dict(c, _id=k) for k, c in db["owners"].items() if c["user"] == uid]
    if not mine:
        return await reply(event, _notice(lang, "empty"))
    mine.sort(key=lambda c: (-c["rarity"], c["name"]))
    arg = args(event).strip()
    tp = (len(mine) + PER_PAGE - 1) // PER_PAGE
    p = min(max(int(arg), 1), tp) if arg.isdigit() else 1
    rows = mine[(p - 1) * PER_PAGE: p * PER_PAGE]
    nick = event.message.author.nickname or "?"
    top = "[c]°    ‿      ‿   ‿     ‿   💘   ‿     ‿     ‿     ‿   °"
    d = "𑇡  〬  "
    title = _m(lang, "harem", nick=nick, n=len(mine), p=p, tp=tp)
    favid = str((db["users"].get(uid, {}).get("fav") or {}).get("id", ""))
    lines = [d + f"{RARITY[c['rarity']]} {c['name']}" + (" ⭐" if c["_id"] == favid else "")
             for c in rows]
    await reply(event, "\n".join(
        [top, "", "[cu]🎨 ᩥㅤ✿ㅤ" + title + "ㅤ♡ㅤᲘᲘ", ""] + lines + ["", top]))


@client.command(["!top"])
@commands_enable_required()
async def cmd_top(event: respObject.Event):
    lang, scope = lang_of(event), scope_of(event)
    db = _load(scope)
    counts = {}
    for c in db["owners"].values():
        counts[c["user"]] = counts.get(c["user"], 0) + 1
    if not counts:
        return await reply(event, _top_msg(lang, [_m(lang, "no_top")]))
    best = sorted(counts.items(), key=lambda kv: -kv[1])[:10]
    lines = [f"{i}. {db['users'].get(uid, {}).get('nick', '?')} — {n}"
             for i, (uid, n) in enumerate(best, 1)]
    await reply(event, _top_msg(lang, lines))


@client.command(["!cooldown"])
@commands_enable_required()
async def cmd_cooldown(event: respObject.Event):
    lang, scope = lang_of(event), scope_of(event)
    async with _lock:
        db = _load(scope)
        uid, u = _user(db, event)
        now = time.time()
        _refresh(u, now)
        _save(scope, db)
    wait = u.get("claim_at", 0) - now
    claim = _fmt(wait) if wait > 0 else _m(lang, "ready")
    await reply(event, deco.cooldown(_m(lang, "cd_rolls", left=ROLLS - u["rolls"], n=ROLLS),
                                     _m(lang, "cd_claim", claim=claim)))


def _download_ffmpeg(url: str) -> BytesIO:
    """Respaldo con ffmpeg: descarga la imagen y la convierte a JPG (Amino solo acepta jpg/png/gif)."""
    raw = _download_raw(url)
    data = raw.getvalue()
    r = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-i", "pipe:0", "-frames:v", "1",
         "-vf", "scale='min(700,iw)':-2", "-pix_fmt", "yuvj420p", "-q:v", "3",
         "-f", "mjpeg", "pipe:1"],
        input=data, capture_output=True)
    if r.returncode != 0 or not r.stdout:
        print("cards: ffmpeg falló:", r.stderr[-200:])
        return raw
    print("cards img:", len(data), "->", len(r.stdout), "bytes")
    buf = BytesIO(r.stdout)
    buf.name = "card.jpg"
    return buf


def _flatten_jpg(data: bytes):
    """Pone la imagen sobre fondo blanco (quita la transparencia) y la guarda como JPG."""
    try:
        from PIL import Image
    except ImportError:
        return None
    im = Image.open(BytesIO(data))
    im.seek(0)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.getchannel("A"))
        im = bg
    else:
        im = im.convert("RGB")
    im.thumbnail((700, 1400))
    out = BytesIO()
    im.save(out, "JPEG", quality=88)
    return out.getvalue()


def _download(url: str) -> BytesIO:
    raw = _download_raw(url)
    data = raw.getvalue()
    try:
        jpg = _flatten_jpg(data)
    except Exception as e:
        print("cards: Pillow falló:", repr(e))
        jpg = None
    if jpg:
        print("cards img:", len(data), "->", len(jpg), "bytes (Pillow)")
        buf = BytesIO(jpg)
        buf.name = "card.jpg"
        return buf
    return _download_ffmpeg(url)
