"""
Minijuegos. Comandos: !ping !roll !dice !flip !8ball !percent !ship !choose !rps
"""
import random
import re
import time
from datetime import datetime, timedelta, timezone

from altamino import respObject

from src.aa import client
from src.utils import reply
from src.utils.wrappers.chat_settings import commands_enable_required
from src.core import deco, games
from src.core.config import BOT_VERSION
from src.core.ctx import args, lang_of, members_of, send_gif
from src.core.i18n import EIGHTBALL_ANSWERS, RPS_NAMES, t


async def _latency_ms() -> int:
    """Tiempo de una consulta ligera a Amino (aunque devuelva error, mide el viaje)."""
    t0 = time.perf_counter()
    try:
        await client.get_from_link("ping")
    except Exception:
        pass
    return round((time.perf_counter() - t0) * 1000)


@client.command(["!ping"])
@commands_enable_required()
async def cmd_ping(event: respObject.Event):
    lang = lang_of(event)
    ms = await _latency_ms()
    now = datetime.now(timezone(timedelta(hours=1))).strftime("%H:%M:%S")
    await reply(event, deco.ping(t(lang, "ping_result"),
                                 t(lang, "ping_version", version=BOT_VERSION),
                                 t(lang, "ping_latency", ms=ms),
                                 t(lang, "ping_time", time=now)))


@client.command(["!roll"])
@commands_enable_required()
async def cmd_roll(event: respObject.Event):
    r = games.roll()
    await reply(event, deco.roll(t(lang_of(event), "roll_result", **r)))
    await send_gif(event, "roll")


@client.command(["!dice"])
@commands_enable_required()
async def cmd_dice(event: respObject.Event):
    raw = args(event)
    r = games.dice(int(raw) if raw.isdigit() else None)
    await reply(event, deco.dice(t(lang_of(event), "dice_result", **r)))
    await send_gif(event, "dice")


@client.command(["!flip"])
@commands_enable_required()
async def cmd_flip(event: respObject.Event):
    r = games.coin()
    key = "coin_heads" if r["result"] == "heads" else "coin_tails"
    await reply(event, deco.flip(t(lang_of(event), key)))
    await send_gif(event, "flip")


@client.command(["!8ball"])
@commands_enable_required()
async def cmd_8ball(event: respObject.Event):
    lang = lang_of(event)
    r = games.eightball(args(event))
    if not r["ok"]:
        return await reply(event, deco.ball(t(lang, "eightball_noQuestion")))
    await reply(event, deco.ball(EIGHTBALL_ANSWERS[lang][r["answerIndex"]]))
    await send_gif(event, "eightball")


@client.command(["!percent"])
@commands_enable_required()
async def cmd_percent(event: respObject.Event):
    lang = lang_of(event)
    r = games.percent(args(event))
    if not r["ok"]:
        return await reply(event, deco.percent(t(lang, "percent_prompt")))
    await reply(event, deco.percent(t(lang, "percent_result", what=r["what"], value=r["value"])))


_INVIS = re.compile("[\u200b-\u200f\u202a-\u202e\u2066-\u2069]")


def _mention_names(event) -> list:
    """Apodos escritos con @ en el comando (admite espacios: @ex nihil)."""
    raw = _INVIS.sub("", args(event))
    return [x.strip() for x in raw.split("@")[1:] if x.strip()]


@client.command(["!ship"])
@commands_enable_required()
async def cmd_ship(event: respObject.Event):
    lang = lang_of(event)
    names = _mention_names(event)
    if len(names) >= 2:
        a, b = names[0], names[1]
    elif len(names) == 1:
        a, b = event.message.author.nickname or "?", names[0]
    else:
        r = games.ship(await members_of(event))
        if not r["ok"]:
            return await reply(event, deco.ship(t(lang, "ship_needMore")))
        a, b = r["a"], r["b"]
    value = random.randint(0, 100)
    await reply(event, deco.ship(t(lang, "ship_result", a=a, b=b, value=value)))
    await send_gif(event, "ship")


@client.command(["!choose"])
@commands_enable_required()
async def cmd_choose(event: respObject.Event):
    lang = lang_of(event)
    r = games.choose(args(event))
    if not r["ok"]:
        return await reply(event, deco.choose(t(lang, "choose_needMore")))
    await reply(event, deco.choose(t(lang, "choose_result", choice=r["choice"])))


@client.command(["!rps"])
@commands_enable_required()
async def cmd_rps(event: respObject.Event):
    lang = lang_of(event)
    r = games.rps(args(event))
    if not r["ok"]:
        return await reply(event, deco.rps(t(lang, "rps_invalid")))
    names = RPS_NAMES[lang]
    result = t(lang, f"rps_{r['result']}")
    await reply(event, deco.rps(t(lang, "rps_result", user=names[r["userChoice"]],
                                  bot=names[r["botChoice"]], result=result)))
    await send_gif(event, "rps")
