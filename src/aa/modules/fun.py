"""
Minijuegos. Copiar a: src/aa/modules/fun.py
Comandos: /ping /roll /dice /flip /8ball /percent /ship /choose /rps
"""
from altamino import respObject

from src.aa import client
from src.utils import reply
from src.utils.wrappers.chat_settings import commands_enable_required
from src.core import games
from src.core.ctx import args, lang_of, members_of, send_gif
from src.core.i18n import EIGHTBALL_ANSWERS, RPS_NAMES, t


@client.command(["/ping"])
@commands_enable_required()
async def cmd_ping(event: respObject.Event):
    await reply(event, t(lang_of(event), "ping_result"))


@client.command(["/roll"])
@commands_enable_required()
async def cmd_roll(event: respObject.Event):
    r = games.roll()
    await reply(event, t(lang_of(event), "roll_result", **r))
    await send_gif(event, "roll")


@client.command(["/dice"])
@commands_enable_required()
async def cmd_dice(event: respObject.Event):
    raw = args(event)
    r = games.dice(int(raw) if raw.isdigit() else None)
    await reply(event, t(lang_of(event), "dice_result", **r))
    await send_gif(event, "dice")


@client.command(["/flip"])
@commands_enable_required()
async def cmd_flip(event: respObject.Event):
    r = games.coin()
    await reply(event, t(lang_of(event), "coin_heads" if r["result"] == "heads" else "coin_tails"))
    await send_gif(event, "flip")


@client.command(["/8ball"])
@commands_enable_required()
async def cmd_8ball(event: respObject.Event):
    lang = lang_of(event)
    r = games.eightball(args(event))
    if not r["ok"]:
        return await reply(event, t(lang, "eightball_noQuestion"))
    await reply(event, f"🎱 {EIGHTBALL_ANSWERS[lang][r['answerIndex']]}")
    await send_gif(event, "eightball")


@client.command(["/percent"])
@commands_enable_required()
async def cmd_percent(event: respObject.Event):
    lang = lang_of(event)
    r = games.percent(args(event))
    if not r["ok"]:
        return await reply(event, t(lang, "percent_prompt"))
    await reply(event, t(lang, "percent_result", what=r["what"], value=r["value"]))


@client.command(["/ship"])
@commands_enable_required()
async def cmd_ship(event: respObject.Event):
    lang = lang_of(event)
    r = games.ship(await members_of(event))
    if not r["ok"]:
        return await reply(event, t(lang, "ship_needMore"))
    await reply(event, t(lang, "ship_result", a=r["a"], b=r["b"], value=r["value"]))
    await send_gif(event, "ship")


@client.command(["/choose"])
@commands_enable_required()
async def cmd_choose(event: respObject.Event):
    lang = lang_of(event)
    r = games.choose(args(event))
    if not r["ok"]:
        return await reply(event, t(lang, "choose_needMore"))
    await reply(event, t(lang, "choose_result", choice=r["choice"]))


@client.command(["/rps"])
@commands_enable_required()
async def cmd_rps(event: respObject.Event):
    lang = lang_of(event)
    r = games.rps(args(event))
    if not r["ok"]:
        return await reply(event, t(lang, "rps_invalid"))
    names = RPS_NAMES[lang]
    await reply(event, t(lang, "rps_result", user=names[r["userChoice"]],
                         bot=names[r["botChoice"]], result=t(lang, f"rps_{r['result']}")))
    await send_gif(event, "rps")
