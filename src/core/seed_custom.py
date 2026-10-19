"""Catálogo propio: Vocaloid/UTAU/fanloids y Hazbin Hotel/Helluva Boss.
Se ejecuta una vez:  python -m src.core.seed_custom
Fila: (categoría, nombre, género, rareza 0-3[, título en la wiki])
"""
import json
import re
import subprocess
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .config import DATA_DIR
from .storage import save_json

IMG_DIR = DATA_DIR / "cards_img"
OUT = DATA_DIR / "catalog_custom.json"

WIKIS = {
    "hazbin": "hazbinhotel.fandom.com",
    "helluva": "helluvaboss.fandom.com",
    "vocaloid": "vocaloid.fandom.com",
    "utau": "vocaloid.fandom.com",
    "fanloid": "vocaloid.fandom.com",
}
SERIES = {"hazbin": "Hazbin Hotel", "helluva": "Helluva Boss",
          "vocaloid": "Vocaloid", "utau": "UTAU", "fanloid": "Fanloid"}
OK_TYPES = {"Vocaloid", "UTAU", "OtherVoiceSynthesizer", "CeVIO", "SynthesizerV", "Character"}

SEED = [
    # Hazbin Hotel
    ("hazbin", "Charlie Morningstar", "waifu", 2),
    ("hazbin", "Vaggie", "waifu", 2),
    ("hazbin", "Angel Dust", "husbando", 3),
    ("hazbin", "Alastor", "husbando", 3),
    ("hazbin", "Husk", "husbando", 2),
    ("hazbin", "Niffty", "waifu", 1),
    ("hazbin", "Lucifer Morningstar", "husbando", 2),
    ("hazbin", "Lilith Morningstar", "waifu", 1),
    ("hazbin", "Sir Pentious", "husbando", 2),
    ("hazbin", "Cherri Bomb", "waifu", 2),
    ("hazbin", "Vox", "husbando", 2),
    ("hazbin", "Valentino", "husbando", 2),
    ("hazbin", "Velvette", "waifu", 1),
    ("hazbin", "Adam", "husbando", 1),
    ("hazbin", "Lute", "waifu", 1),
    ("hazbin", "Emily", "waifu", 1),
    ("hazbin", "Carmilla Carmine", "waifu", 1),
    ("hazbin", "Rosie", "waifu", 1),
    ("hazbin", "Zestial", "husbando", 1),
    ("hazbin", "Arackniss", "husbando", 1),
    ("hazbin", "Abel", "husbando", 0),
    ("hazbin", "Baxter", "husbando", 0),
    ("hazbin", "Molly", "waifu", 0),
    # Helluva Boss
    ("helluva", "Blitzo", "husbando", 3, "Blitzø"),
    ("helluva", "Moxxie", "husbando", 2),
    ("helluva", "Millie", "waifu", 2),
    ("helluva", "Loona", "waifu", 3),
    ("helluva", "Stolas", "husbando", 3),
    ("helluva", "Octavia", "waifu", 1),
    ("helluva", "Fizzarolli", "husbando", 2),
    ("helluva", "Striker", "husbando", 1),
    ("helluva", "Verosika Mayday", "waifu", 2),
    ("helluva", "Asmodeus", "husbando", 1),
    ("helluva", "Stella", "waifu", 1),
    ("helluva", "Barbie Wire", "waifu", 1),
    ("helluva", "Crimson", "husbando", 1),
    ("helluva", "Via", "waifu", 0),
    ("helluva", "Mammon", "husbando", 1),
    ("helluva", "Andrealphus", "husbando", 1),
    ("helluva", "Queen Bee", "waifu", 1),
    ("helluva", "Chaz", "husbando", 0),
    ("helluva", "Tex", "husbando", 0),
    ("helluva", "Cash Buckett", "husbando", 0),
    # Vocaloid
    ("vocaloid", "Hatsune Miku", "waifu", 3),
    ("vocaloid", "Kagamine Rin", "waifu", 3),
    ("vocaloid", "Kagamine Len", "husbando", 3),
    ("vocaloid", "Megurine Luka", "waifu", 2),
    ("vocaloid", "MEIKO", "waifu", 2),
    ("vocaloid", "KAITO", "husbando", 2),
    ("vocaloid", "GUMI", "waifu", 2),
    ("vocaloid", "IA", "waifu", 2),
    ("vocaloid", "Kamui Gakupo", "husbando", 1),
    ("vocaloid", "Hiyama Kiyoteru", "husbando", 1),
    ("vocaloid", "Kaai Yuki", "waifu", 1),
    ("vocaloid", "SF-A2 Miki", "waifu", 1),
    ("vocaloid", "Otomachi Una", "waifu", 1),
    ("vocaloid", "Yuzuki Yukari", "waifu", 1),
    ("vocaloid", "Oliver", "husbando", 1),
    ("vocaloid", "Fukase", "husbando", 1),
    # UTAU
    ("utau", "Kasane Teto", "waifu", 3),
    ("utau", "Defoko", "waifu", 1),
    ("utau", "Namine Ritsu", "husbando", 1),
    ("utau", "Momone Momo", "waifu", 1),
    # Fanloids
    ("fanloid", "Yowane Haku", "waifu", 2),
    ("fanloid", "Akita Neru", "waifu", 2),
    ("fanloid", "Honne Dell", "husbando", 1),
    ("fanloid", "Sukone Tei", "waifu", 1),
    ("fanloid", "Hatsune Mikuo", "husbando", 2),
]


UA = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36")


def _get(url, referer=None, tries=3):
    headers = {"User-Agent": UA, "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9"}
    if referer:
        headers["Referer"] = referer
    last = None
    for i in range(tries):
        try:
            with urlopen(Request(url, headers=headers), timeout=25) as r:
                return r.read(), r.headers.get("Content-Type", "")
        except HTTPError as e:
            last = e
            if e.code in (403, 429, 503):
                time.sleep(4 * (i + 1))
                continue
            raise
    raise last


def _wiki_image(domain, title):
    q = urlencode({"action": "query", "titles": title, "prop": "pageimages",
                   "piprop": "original", "redirects": 1, "format": "json"})
    data, _ = _get(f"https://{domain}/api.php?{q}")
    for page in json.loads(data.decode()).get("query", {}).get("pages", {}).values():
        src = (page.get("original") or {}).get("source")
        if src:
            return src
    return None


def _wiki_search_image(domain, name):
    q = urlencode({"action": "query", "generator": "search", "gsrsearch": name,
                   "gsrlimit": 3, "prop": "pageimages", "piprop": "original", "format": "json"})
    data, _ = _get(f"https://{domain}/api.php?{q}")
    pages = json.loads(data.decode()).get("query", {}).get("pages", {}).values()
    for page in sorted(pages, key=lambda p: p.get("index", 99)):
        src = (page.get("original") or {}).get("source")
        if src:
            return src
    return None


def _vocadb_image(name):
    q = urlencode({"query": name, "maxResults": 8, "fields": "MainPicture", "lang": "English"})
    data, _ = _get("https://vocadb.net/api/artists?" + q)
    items = [it for it in json.loads(data.decode()).get("items", [])
             if it.get("artistType") in OK_TYPES]
    items.sort(key=lambda it: 0 if it.get("name", "").lower() == name.lower() else 1)
    for it in items:
        pic = it.get("mainPicture") or {}
        url = pic.get("urlOriginal") or pic.get("urlThumb")
        if url:
            return url
    return None


def _candidates(cat, name, title):
    steps = []
    if cat in ("vocaloid", "utau", "fanloid"):
        steps.append(lambda: _vocadb_image(name))
    steps.append(lambda: _wiki_image(WIKIS[cat], title))
    steps.append(lambda: _wiki_search_image(WIKIS[cat], title))
    if title != name:
        steps.append(lambda: _wiki_search_image(WIKIS[cat], name))
    seen = set()
    for step in steps:
        try:
            url = step()
        except Exception as e:
            print("   búsqueda falló:", repr(e))
            continue
        if url and url not in seen:
            seen.add(url)
            yield url


def _save_image(url, key):
    ref = "https://vocadb.net/" if "vocadb" in url else "https://hazbinhotel.fandom.com/"
    data, ctype = _get(url, referer=ref)
    if len(data) < 500:
        print("  imagen muy pequeña:", len(data), "bytes,", ctype)
        return None
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        ext = "png"
    elif data[:3] == b"\xff\xd8\xff":
        ext = "jpg"
    elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        ext = "webp"
    elif data[:4] == b"GIF8":
        ext = "gif"
    else:
        print("  formato desconocido:", ctype, data[:8])
        return None
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    path = IMG_DIR / f"{key}.{ext}"
    path.write_bytes(data)
    return str(path)


def build():
    try:
        old = {c["id"]: c for c in json.loads(OUT.read_text(encoding="utf-8"))}
    except Exception:
        old = {}
    out, missing = [], []
    for row in SEED:
        cat, name, gender, rarity = row[:4]
        title = row[4] if len(row) > 4 else name
        cid = "c_" + cat + "_" + re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        prev = old.get(cid)
        if prev and Path(prev["img"]).exists():
            prev.update(rarity=rarity, gender=gender)
            out.append(prev)
            print("ya estaba:", name)
            continue
        img = None
        for url in _candidates(cat, name, title):
            print("  ", name, "->", url[:90])
            try:
                img = _save_image(url, cid)
            except Exception as e:
                print("  falló:", repr(e))
                img = None
            if img:
                break
        time.sleep(2.5)
        if not img:
            missing.append(name)
            print("sin imagen:", name)
            continue
        out.append({"id": cid, "name": name, "series": SERIES[cat], "img": img,
                    "fav": 0, "rarity": rarity, "gender": gender,
                    "category": cat, "custom": True})
        print("ok:", name)
    save_json(OUT, out)
    print("\nListo:", len(out), "personajes.", len(missing), "sin imagen:", ", ".join(missing))


if __name__ == "__main__":
    build()
