"""
Casamientos. Copiar a: src/aa/modules/marry.py
Comandos: !marry @usuario, !divorce, !marriage
"""
from altamino import respObject

from src.aa import client
from src.utils import reply
from src.utils.wrappers.chat_settings import commands_enable_required
from src.core import marriage
from src.core.ctx import author_of, lang_of, members_of, mentioned_of, send_gif
from src.core.i18n import t


async def _resolve_target(event, author):
    """Completa el nickname del mencionado buscándolo en los miembros del chat."""
    mentioned = mentioned_of(event)
    if not mentioned:
        return None
    target = mentioned[0]
    for m in await members_of(event):
        if str(m["userId"]) == str(target["userId"]):
            target["nickname"] = m["nickname"]
    target["nickname"] = target["nickname"] or "?"
    return target


@client.command(["/marry"])
@commands_enable_required()
async def cmd_marry(event: respObject.Event):
    lang = lang_of(event)
    author = author_of(event)
    r = marriage.propose(author, await _resolve_target(event, author))
    status = r["status"]
    fields = {k: v for k, v in r.items() if k != "status"}
    await reply(event, t(lang, f"marry_{status}", **fields))
    if status == "married":
        await send_gif(event, "marry")


@client.command(["/divorce"])
@commands_enable_required()
async def cmd_divorce(event: respObject.Event):
    lang = lang_of(event)
    r = marriage.divorce(author_of(event))
    if r["status"] == "notMarried":
        return await reply(event, t(lang, "divorce_notMarried"))
    await reply(event, t(lang, "divorce_done", user=r["user"]))
    await send_gif(event, "divorce")


@client.command(["/marriage"])
@commands_enable_required()
async def cmd_marriage(event: respObject.Event):
    lang = lang_of(event)
    r = marriage.status(author_of(event), await members_of(event))
    if not r["married"]:
        return await reply(event, t(lang, "marriage_single"))
    await reply(event, t(lang, "marriage_married", partner=r["partner"] or "?"))
