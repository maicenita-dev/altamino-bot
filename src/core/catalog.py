"""Catálogo de personajes (AniList): se descarga una vez y se guarda en data/."""
import json
import time
from asyncio import Lock, to_thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .config import DATA_DIR
from .storage import load_json, save_json

API = "https://graphql.anilist.co"
QUERY = ("query($p:Int){Page(page:$p,perPage:50){characters(sort:FAVOURITES_DESC)"
         "{id name{full} gender image{large} favourites "
         "media(perPage:1,sort:POPULARITY_DESC){nodes{title{romaji}}}}}}")
FILES = {
    "waifu": DATA_DIR / "catalog_waifu.json",
    "husbando": DATA_DIR / "catalog_husbando.json",
}
PAGES = 40
_lock = Lock()


def _post(page: int) -> list:
    body = json.dumps({"query": QUERY, "variables": {"p": page}}).encode()
    req = Request(API, data=body, headers={
        "Content-Type": "application/json", "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"})
    for _ in range(3):
        try:
            with urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode())["data"]["Page"]["characters"]
        except HTTPError as e:
            if e.code == 429:
                time.sleep(30)
                continue
            raise
    return []


def _build() -> None:
    out = {"waifu": [], "husbando": []}
    for page in range(1, PAGES + 1):
        try:
            chars = _post(page)
        except Exception as e:
            print("catálogo: página", page, "falló:", repr(e))
            time.sleep(5)
            continue
        for c in chars:
            key = {"Female": "waifu", "Male": "husbando"}.get(c.get("gender"))
            img = (c.get("image") or {}).get("large") or ""
            if not key or not img or "default" in img:
                continue
            nodes = ((c.get("media") or {}).get("nodes")) or []
            serie = nodes[0]["title"]["romaji"] if nodes else "?"
            out[key].append({"id": c["id"], "name": c["name"]["full"],
                             "series": serie, "img": img,
                             "fav": c.get("favourites") or 0})
        print("catálogo: página", page, "/", PAGES)
        time.sleep(1.2)
    for key, lst in out.items():
        lst.sort(key=lambda x: -x["fav"])
        n = len(lst)
        for i, ch in enumerate(lst):
            ch["rarity"] = 3 if i < n * 0.05 else 2 if i < n * 0.20 else 1 if i < n * 0.50 else 0
        save_json(FILES[key], lst)
        print("catálogo", key, ":", n, "personajes")


async def get_catalog(kind: str) -> list:
    data = load_json(FILES[kind], [])
    if data:
        return data
    async with _lock:
        data = load_json(FILES[kind], [])
        if not data:
            await to_thread(_build)
            data = load_json(FILES[kind], [])
    return data
