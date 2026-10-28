"""!imagine / !imagen / !img: genera imágenes con IA (Pollinations, sin clave)."""
import base64
import json
import subprocess
import random
import re
import time
import unicodedata
from asyncio import Semaphore, to_thread
from io import BytesIO
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from altamino import respObject

from src.aa import client
from src.aa.modules.cards import _flatten_jpg, _fmt
from src.core.config import DATA_DIR
from src.core.ctx import args, is_owner, lang_of, target
from src.core.storage import load_json, save_json
from src.utils import reply
from src.utils.wrappers.chat_settings import commands_enable_required

COOLDOWN = 60        # segundos entre una imagen y otra, por persona
PER_DAY = 10         # máximo por persona cada 24 h (el dueño no tiene límites)
MAX_PROMPT = 300
LOG = DATA_DIR / "imagen_log.json"
HISTORY = DATA_DIR / "imagen_history.log"
_busy = Semaphore(1)

ADULT_SUFFIX = ", mature adult, 30 years old, adult face, adult body proportions"
_NEG = quote("child, kid, toddler, baby, teen, young, youthful, childlike, loli, shota, schoolgirl", safe="")

_WORDS = set("""
nino nina ninos ninas bebe bebes infante infantil adolescente adolescentes menor menores
crianca criancas menino menina meninos meninas
child children kid kids baby babies toddler teen teens teenager teenagers underage minor minors preschool kindergarten
loli lolis lolicon shota shotacon schoolgirl schoolboy colegiala colegial
ребенок ребёнок дети девочка мальчик малыш подросток лоли шота
nsfw nude nudes naked desnudo desnuda desnudos desnudas nua nuas nu porn porno pornografia hentai erotic erotico erotica sexo sex sexual sexy
порно эротика секс голая голый обнажен обнажена
""".split())
_PHRASES = ("little girl", "little boy", "young girl", "young boy", "school girl", "school boy",
            "menor de edad", "jardin de infantes", "de primaria", "pequena", "pequeno")


def _is_blocked(prompt: str) -> bool:
    t = unicodedata.normalize("NFKD", prompt.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    if set(re.findall(r"\w+", t)) & _WORDS:
        return True
    return any(x in t for x in _PHRASES)


PEOPLE_OWNER_ONLY = True      # True: solo el dueño pide imágenes con personas o personajes
_PEOPLE = set("""
princess princesa princesse prince principe girl boy woman women man men person people persona personas gente human humano humana
character characters personaje personajes personagem personagens anime manga chica chico chicas chicos mujer mujeres hombre hombres
dancer dancers bailarina bailarin bailarinas ballerina queen reina king rey knight caballero mage mago maga witch bruja wizard elf elfa elfo
fairy hada couple pareja portrait retrato selfie face rostro cara warrior guerrero guerrera ninja samurai idol singer cantante cosplay
maid mucama lady dama gentleman vampire vampiro vampira angel demon demonio mermaid sirena
pessoa pessoas mulher mulheres homem homens garota garoto rainha rei fada casal bruxa feiticeiro cantora cantor guerreira
принцесса принц девушка парень женщина мужчина человек люди персонаж аниме королева король ведьма фея пара портрет танцовщица балерина
""".split())


def _mentions_people(prompt: str) -> bool:
    t = unicodedata.normalize("NFKD", prompt.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return bool(set(re.findall(r"\w+", t)) & _PEOPLE)

MSG = {
    "es": {
        "usage": "Escribí qué querés ver. Ej: !imagine un gato astronauta",
        "wait": "Esperá un poco antes de pedir otra imagen ({t})",
        "limit": "Llegaste al máximo de imágenes por hoy ({n}). Volvé en {t}.",
        "working": "🎨 Generando «{prompt}»... en la cola gratuita puede tardar 1 o 2 minutos.",
        "error": "No pude generar la imagen, intentá de nuevo en un rato.",
        "blocked": "Esa descripción no está permitida. Probá con otra.",
        "no_people": "Por ahora solo se pueden pedir imágenes sin personas (paisajes, animales, objetos). Probá con otra descripción.",
    },
    "en": {
        "usage": "Write what you want to see. Ex: !imagine an astronaut cat",
        "wait": "Please wait a bit before asking for another image ({t})",
        "limit": "You reached today's image limit ({n}). Come back in {t}.",
        "working": "🎨 Generating «{prompt}»... the free queue can take 1-2 minutes.",
        "error": "I couldn't generate the image, try again in a while.",
        "blocked": "That description isn't allowed. Try a different one.",
        "no_people": "For now only images without people are allowed (landscapes, animals, objects). Try a different description.",
    },
    "ru": {
        "usage": "Напиши, что хочешь увидеть. Пример: !imagine кот-астронавт",
        "wait": "Подожди немного перед следующим изображением ({t})",
        "limit": "Ты достиг(ла) дневного лимита изображений ({n}). Возвращайся через {t}.",
        "working": "🎨 Создаю «{prompt}»... в бесплатной очереди это может занять 1–2 минуты.",
        "error": "Не удалось создать изображение, попробуй позже.",
        "blocked": "Такое описание не разрешено. Попробуй другое.",
        "no_people": "Пока можно запрашивать только изображения без людей (пейзажи, животные, предметы). Попробуй другое описание.",
    },
    "pt": {
        "usage": "Escreva o que você quer ver. Ex: !imagine um gato astronauta",
        "wait": "Espere um pouco antes de pedir outra imagem ({t})",
        "limit": "Você atingiu o limite de imagens de hoje ({n}). Volte em {t}.",
        "working": "🎨 Gerando «{prompt}»... na fila gratuita pode levar 1 ou 2 minutos.",
        "error": "Não consegui gerar a imagem, tente de novo daqui a pouco.",
        "blocked": "Essa descrição não é permitida. Tente outra.",
        "no_people": "Por enquanto só são permitidas imagens sem pessoas (paisagens, animais, objetos). Tente outra descrição.",
    },
}


def _m(lang, key, **kw):
    return (MSG.get(lang) or MSG["es"])[key].format(**kw)


def _check(uid):
    """(clave, segundos) si se pasó de algún límite; (None, 0) si puede."""
    now = time.time()
    mine = [x["t"] for x in load_json(LOG, []) if x["u"] == uid and now - x["t"] < 86400]
    if mine and now - max(mine) < COOLDOWN:
        return "wait", int(COOLDOWN - (now - max(mine)))
    if len(mine) >= PER_DAY:
        return "limit", int(86400 - (now - min(mine)))
    return None, 0


def _record(uid, nick, prompt):
    now = time.time()
    log = [x for x in load_json(LOG, []) if now - x["t"] < 86400]
    log.append({"t": now, "u": uid})
    save_json(LOG, log)
    with open(HISTORY, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {uid} | {nick} | {prompt[:200]}\n")


def _candidates(prompt):
    q = quote(prompt, safe="")
    base = f"nologo=true&negative_prompt={_NEG}&seed={random.randint(1, 10**6)}&referrer=emma-bot"
    return [
        f"https://image.pollinations.ai/prompt/{q}?width=768&height=768&model=flux&{base}",
        f"https://image.pollinations.ai/prompt/{q}?width=512&height=512&model=turbo&{base}",
        f"https://pollinations.ai/p/{q}?width=512&height=512&{base}",
    ]


def _generate_pollinations(prompt):
    last = None
    for url in _candidates(prompt):
        for _ in range(2):
            try:
                with urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=90) as r:
                    data = r.read()
                if len(data) < 2000:
                    raise RuntimeError("respuesta vacía")
                jpg = None
                try:
                    jpg = _flatten_jpg(data)
                except Exception as e:
                    print("imagen: Pillow falló:", repr(e))
                buf = BytesIO(jpg or data)
                buf.name = "imagen.jpg"
                print("imagen: ok con", url.split("?")[0][:45], "|", url.split("model=")[-1][:5])
                return buf
            except Exception as e:
                last = e
                print("imagen: falló", url.split("?")[0][:45], "|", url.split("model=")[-1][:5], repr(e)[:70])
                time.sleep(3)
    raise last


_MAGIC = (b"\xff\xd8\xff", b"\x89PNG", b"GIF8")


def _to_jpg(data: bytes) -> bytes:
    """Comprueba que sea una imagen y la convierte a JPG (lo que acepta Amino)."""
    head = data[:12]
    if not (head.startswith(_MAGIC) or (head[:4] == b"RIFF" and head[8:12] == b"WEBP")):
        raise RuntimeError("no es una imagen: " + data[:120].decode("utf-8", "ignore").replace("\n", " "))
    jpg = None
    try:
        jpg = _flatten_jpg(data)
    except Exception as e:
        print("imagen: Pillow falló:", repr(e)[:80])
    if not jpg:
        r = subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-i", "pipe:0", "-frames:v", "1",
             "-vf", "scale='min(700,iw)':-2", "-pix_fmt", "yuvj420p", "-q:v", "4",
             "-f", "mjpeg", "pipe:1"], input=data, capture_output=True)
        jpg = r.stdout
        if r.returncode != 0 or not jpg:
            raise RuntimeError("no pude convertir: " + r.stderr[-100:].decode("utf-8", "ignore"))
    return jpg


HORDE = "https://aihorde.net/api/v2"
HORDE_KEY = "0000000000"       # clave anónima; con una cuenta gratis de aihorde.net (clave propia) es más rápida
HORDE_WAIT = 600               # segundos máximos de espera en la cola
HORDE_NEG = ("child, kid, toddler, baby, teen, young, youthful, childlike, loli, shota, schoolgirl, "
             "big head, nsfw, nude, deformed, lowres, bad anatomy, watermark, text")
PROVIDER = "horde"             # "horde" (lento, respeta los prompts negativos) o "pollinations"


def _horde(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = Request(HORDE + path, data=data, method=method, headers={
        "apikey": HORDE_KEY, "Client-Agent": "emma-bot:1.0:altamino",
        "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8") or "{}")
    except HTTPError as e:
        raise RuntimeError(f"horde {e.code}: {e.read()[:200]!r}")


def _generate_horde(prompt):
    job = _horde("POST", "/generate/async", {
        "prompt": prompt + " ### " + HORDE_NEG,
        "params": {"width": 512, "height": 512, "steps": 25, "cfg_scale": 7,
                   "sampler_name": "k_euler_a", "n": 1, "karras": True},
        "nsfw": False, "censor_nsfw": True, "r2": True, "slow_workers": True,
    })
    jid = job["id"]
    print("imagen: en cola en AI Horde", jid[:8])
    start, done = time.time(), False
    try:
        while time.time() - start < HORDE_WAIT:
            time.sleep(5)
            st = _horde("GET", f"/generate/check/{jid}")
            if st.get("faulted"):
                raise RuntimeError("horde: el trabajo falló")
            if st.get("done"):
                done = True
                break
        if not done:
            raise RuntimeError("horde: tiempo agotado")
        res = _horde("GET", f"/generate/status/{jid}")
    except Exception:
        try:
            _horde("DELETE", f"/generate/status/{jid}")
        except Exception:
            pass
        raise
    gens = res.get("generations") or []
    if not gens or gens[0].get("censored"):
        raise RuntimeError("horde: imagen vacía o censurada")
    img = gens[0]["img"]
    if img.startswith("http"):
        with urlopen(Request(img, headers={"User-Agent": "Mozilla/5.0"}), timeout=60) as r:
            data = r.read()
    else:
        data = base64.b64decode(img)
    buf = BytesIO(_to_jpg(data))
    buf.name = "imagen.jpg"
    print("imagen: ok con AI Horde,", int(time.time() - start), "s")
    return buf


def _generate(prompt):
    return _generate_horde(prompt) if PROVIDER == "horde" else _generate_pollinations(prompt)


@client.command(["!imagine", "!imagen", "!img"])
@commands_enable_required()
async def cmd_imagine(event: respObject.Event):
    lang = lang_of(event)
    prompt = args(event).strip()[:MAX_PROMPT]
    if not prompt:
        return await reply(event, _m(lang, "usage"))
    a = event.message.author
    if not is_owner(event):
        key, wait = _check(a.userId)
        if key:
            return await reply(event, _m(lang, key, t=_fmt(wait), n=PER_DAY))
    blocked = _is_blocked(prompt)
    _record(a.userId, a.nickname or "?", ("[BLOQUEADO] " if blocked else "") + prompt)
    if blocked:
        return await reply(event, _m(lang, "blocked"))
    if PEOPLE_OWNER_ONLY and not is_owner(event) and _mentions_people(prompt):
        return await reply(event, _m(lang, "no_people"))
    await reply(event, _m(lang, "working", prompt=prompt[:80]))
    try:
        async with _busy:
            buf = await to_thread(_generate, prompt + ADULT_SUFFIX)
        try:
            await target(event).send_media(event.message.chatId, buf, "image/jpeg")
        except Exception as e:
            if type(e).__name__ != "RequestedNoLongerExists":
                raise
            print("imagen: Amino devolvió RequestedNoLongerExists al enviar; la imagen suele llegar igual")
    except Exception as e:
        print("imagen error:", repr(e)[:150])
        await reply(event, _m(lang, "error"))
