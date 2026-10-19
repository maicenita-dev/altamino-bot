"""!start, !help, !ayuda: el bot se presenta y muestra sus comandos (en inglés)."""
from altamino import respObject

from src.aa import client
from src.utils import reply
from src.utils.wrappers.chat_settings import commands_enable_required
from src.core.config import BOT_NAME

TEXT = """[c]ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚ྀི̣︶˚̣  ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚̣
[C]💜ᩧㅤ⿻  ׁ   ꒰    Hi! I'm {bot}

[C]💜ᩧㅤ⿻  ׁ   ꒰    I'm already in the chat. Here's what I can do:

[cbu]🎮ᩧㅤ⿻  ׁ   ꒰    Games
[CI]!roll !dice !flip !8ball !percent !ship !choose !rps

[cbu]💍ᩧㅤ⿻  ׁ   ꒰    Couples
[CI]!marry @user · !divorce · !marriage

[cbu]🌸ᩧㅤ⿻  ׁ   ꒰    Anime
[CI]!waifu · !husbando · !claim
!harem · !top · !cooldown
!buscar · !carta · !serie
!fav · !liberar · !rarezas

[cbu]🛠ᩧㅤ⿻  ׁ   ꒰    Tools
[CI]!ask <question> · !trasl <es|en|ru> <text>
!tts <text> · !horoscopo <sign> · !ping

[cbu]👋ᩧㅤ⿻  ׁ   ꒰    Welcome
[CI]!setwelcome <text> · !setwelcome off|on|reset
Staff only.

[cbu]🌐ᩧㅤ⿻  ׁ   ꒰    Language
[CI]!langset es|en|ru to change my language.

[ci]Type !help when you want to see this list.

[c]ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚ྀི̣︶˚̣  ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚̣"""


def greeting(lang=None) -> str:
    return TEXT.replace("{bot}", BOT_NAME)


@client.command(["/start", "/help", "/ayuda"])
@commands_enable_required()
async def cmd_start(event: respObject.Event):
    await reply(event, greeting())
