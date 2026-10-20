"""Traduce al portugués (pt-BR) los textos de las cartas.

Uso (con el bot encendido o apagado, no importa):
    python -m src.core.translate_pt            # usa la caché y sigue donde quedó
    python -m src.core.translate_pt --force    # rehace todo desde cero

Genera:
    src/core/pt_cards.py   los textos en portugués (los módulos de cartas lo cargan solos)
    data/pt_review.txt     para revisar: primero lo dudoso, luego todo
Correcciones manuales: data/pt_overrides.json  ->  {"cards:no_rolls_1": "texto"}
"""
import ast
import json
import pprint
import re
import sys
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .config import DATA_DIR, ROOT

MODULES = {
    "cards": ROOT / "src/aa/modules/cards.py",
    "cards_search": ROOT / "src/aa/modules/cards_search.py",
    "cards_extra": ROOT / "src/aa/modules/cards_extra.py",
}
CACHE = DATA_DIR / "pt_cache.json"
OVERRIDES = DATA_DIR / "pt_overrides.json"   # correcciones manuales: {"cards:clave": "texto"}
REVIEW = DATA_DIR / "pt_review.txt"
OUT = ROOT / "src/core/pt_cards.py"
MARKER = "# --- pt (generado) ---"

TOKEN = re.compile(r"\{[A-Za-z0-9_]+\}|![A-Za-z0-9]+|<[A-Za-z]+>")
ANGLE = {"<name>": "<nome>"}
BAD_WORDS = ("<html", "rate limit", "too many requests", "queue full", "mymemory warning",
             "internal server error", "bad gateway")

PROMPT = ("Translate this chat-bot message from English to Brazilian Portuguese (pt-BR). "
          "Friendly, informal tone; address the user as 'você'. "
          "Keep every token like ZX1Z exactly as written, and keep emojis and symbols unchanged. "
          "Do not translate words that start with '!'. "
          "Reply with ONLY the translation, no quotes, no notes.\n\nMessage: ")


def load_msg(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "MSG" for t in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError(f"no encontré MSG en {path}")


def protect(text):
    toks = []

    def sub(m):
        toks.append(m.group(0))
        return f"ZX{len(toks)}Z"
    return TOKEN.sub(sub, text), toks


def restore(text, toks):
    for i, tok in enumerate(toks, 1):
        text = text.replace(f"ZX{i}Z", ANGLE.get(tok, tok))
    return text


def valid(src, out, toks):
    if not out or len(out) > 3 * len(src) + 20:
        return False
    low = out.lower()
    if any(w in low for w in BAD_WORDS):
        return False
    if len(re.findall(r"ZX\d+Z", out)) != len(toks):
        return False
    if any(out.count(f"ZX{i}Z") != 1 for i in range(1, len(toks) + 1)):
        return False
    letters = re.sub(r"ZX\d+Z|[^A-Za-z]", "", src)
    if len(letters) > 12 and out.strip().lower() == src.strip().lower():
        return False  # no tradujo nada
    return True


def _json(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))


def via_ia(p):
    from .ask import _fetch
    out = _fetch(PROMPT + p).strip().strip('"“”`').strip()
    out = re.sub(r"^(translation|tradução|traducao)\s*:\s*", "", out, flags=re.I)
    return " ".join(out.split())


def via_mymemory(p):
    d = _json("https://api.mymemory.translated.net/get?"
              + urlencode({"q": p, "langpair": "en|pt-BR"}))
    return d["responseData"]["translatedText"]


def via_google(p):
    d = _json("https://translate.googleapis.com/translate_a/single?"
              + urlencode({"client": "gtx", "sl": "en", "tl": "pt", "dt": "t", "q": p}))
    return "".join(x[0] for x in d[0] if x and x[0])


BACKENDS = [("IA", via_ia), ("MyMemory", via_mymemory), ("Google", via_google)]


def translate(text):
    p, toks = protect(text)
    for name, fn in BACKENDS:
        for _ in range(2):
            try:
                out = fn(p)
            except Exception as e:
                print("     ", name, "falló:", repr(e)[:80])
                time.sleep(3)
                continue
            if valid(p, out, toks):
                return restore(out, toks), name
            print("     ", name, "respuesta no válida:", out[:70])
            time.sleep(1)
    return None, None


def main():
    force = "--force" in sys.argv
    cache = {}
    if not force and CACHE.exists():
        cache = json.loads(CACHE.read_text(encoding="utf-8"))
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    overrides = {}
    if OVERRIDES.exists():
        overrides = json.loads(OVERRIDES.read_text(encoding="utf-8"))

    sources = {m: load_msg(p) for m, p in MODULES.items()}
    total = sum(len(v["es"]) for v in sources.values())
    result, rows, n = {}, [], 0
    for mod, msg in sources.items():
        es, en = msg["es"], msg.get("en", msg["es"])
        result[mod] = {}
        for key, es_text in es.items():
            n += 1
            src = en.get(key, es_text)
            ck = f"{mod}:{key}"
            hit = cache.get(ck)
            if ck in overrides:
                pt, by = overrides[ck], "manual"
            elif hit and hit["src"] == src and hit.get("pt"):
                pt, by = hit["pt"], hit["by"]
            else:
                print(f"[{n}/{total}] {mod}.{key}")
                pt, by = translate(src)
                if pt:
                    cache[ck] = {"src": src, "pt": pt, "by": by}
                    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
                    time.sleep(1.5)
                else:
                    pt, by = es_text, "SIN TRADUCIR (se usa español)"
            result[mod][key] = pt
            rows.append((mod, key, src, pt, by))

    OUT.write_text('"""Generado por translate_pt.py (se vuelve a generar, no lo edites a mano)."""\n\nPT = '
                   + pprint.pformat(result, width=100, sort_dicts=False) + "\n", encoding="utf-8")

    dudosos = [r for r in rows if r[4] not in ("IA", "manual")]
    lines = ["== REVISAR (no los tradujo la IA) ==", ""]
    for mod, key, src, pt, by in dudosos:
        lines += [f"{mod}.{key}  [{by}]", f"  EN: {src}", f"  PT: {pt}", ""]
    lines += ["", "== TODOS ==", ""]
    for mod, key, src, pt, by in rows:
        lines += [f"{mod}.{key}", f"  EN: {src}", f"  PT: {pt}", ""]
    REVIEW.write_text("\n".join(lines), encoding="utf-8")

    for mod, path in MODULES.items():
        s = path.read_text(encoding="utf-8")
        if MARKER not in s:
            s += (f'\n\n{MARKER}\nfrom src.core.pt_cards import PT as _PT  # noqa: E402\n'
                  f'MSG["pt"] = _PT["{mod}"]\n')
            path.write_text(s, encoding="utf-8")

    sin = [f"{m}.{k}" for m, k, _, _, by in rows if by.startswith("SIN")]
    print(f"\nListo: {len(rows)} textos. Dudosos: {len(dudosos)}. Sin traducir: {len(sin)}")
    if sin:
        print("Sin traducir (salen en español):", ", ".join(sin))
    print("Revisión en:", REVIEW)


if __name__ == "__main__":
    main()
