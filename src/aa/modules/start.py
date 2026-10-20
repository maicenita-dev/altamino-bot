"""!start, !help, !ayuda: el bot se presenta y muestra sus comandos (en inglés)."""
from altamino import respObject

from src.aa import client
from src.utils import reply
from src.utils.wrappers.chat_settings import commands_enable_required
from src.core.config import BOT_NAME
from src.core.ctx import lang_of

TEXTS = {
    "en": """[c]ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚ྀི̣︶˚̣  ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚̣
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
!fav · !liberar (!release) · !rarezas (!rarity)

[cbu]🛠ᩧㅤ⿻  ׁ   ꒰    Tools
[CI]!ask <question> · !trasl <es|en|ru> <text>
!tts <text> · !voz · !horoscopo <sign> · !ping

[cbu]👋ᩧㅤ⿻  ׁ   ꒰    Welcome
[CI]!setwelcome <text> · !setwelcome off|on|reset
Staff only.

[cbu]🌐ᩧㅤ⿻  ׁ   ꒰    Language
[CI]!langset es|en|ru changes the bot's language (staff only).

[ci]Type !help when you want to see this list.

[c]ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚ྀི̣︶˚̣  ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚̣""",
    "es": """[c]ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚ྀི̣︶˚̣  ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚̣
[C]💜ᩧㅤ⿻  ׁ   ꒰    ¡Hola! Soy {bot}

[C]💜ᩧㅤ⿻  ׁ   ꒰    Ya estoy en el chat. Esto es lo que puedo hacer:

[cbu]🎮ᩧㅤ⿻  ׁ   ꒰    Juegos
[CI]!roll !dice !flip !8ball !percent !ship !choose !rps

[cbu]💍ᩧㅤ⿻  ׁ   ꒰    Parejas
[CI]!marry @user · !divorce · !marriage

[cbu]🌸ᩧㅤ⿻  ׁ   ꒰    Anime
[CI]!waifu · !husbando · !claim
!harem · !top · !cooldown
!buscar · !carta · !serie
!fav · !liberar · !rarezas

[cbu]🛠ᩧㅤ⿻  ׁ   ꒰    Herramientas
[CI]!ask <pregunta> · !trasl <es|en|ru> <texto>
!tts <texto> · !voz · !horoscopo <signo> · !ping

[cbu]👋ᩧㅤ⿻  ׁ   ꒰    Bienvenida
[CI]!setwelcome <texto> · !setwelcome off|on|reset
Solo staff.

[cbu]🌐ᩧㅤ⿻  ׁ   ꒰    Idioma
[CI]!langset es|en|ru cambia el idioma del bot (solo staff).

[ci]Escribí !help cuando quieras ver esta lista.

[c]ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚ྀི̣︶˚̣  ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚̣""",
    "ru": """[c]ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚ྀི̣︶˚̣  ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚̣
[C]💜ᩧㅤ⿻  ׁ   ꒰    Привет! Я {bot}

[C]💜ᩧㅤ⿻  ׁ   ꒰    Я уже в чате. Вот что я умею:

[cbu]🎮ᩧㅤ⿻  ׁ   ꒰    Игры
[CI]!roll !dice !flip !8ball !percent !ship !choose !rps

[cbu]💍ᩧㅤ⿻  ׁ   ꒰    Пары
[CI]!marry @user · !divorce · !marriage

[cbu]🌸ᩧㅤ⿻  ׁ   ꒰    Аниме
[CI]!waifu · !husbando · !claim
!harem · !top · !cooldown
!buscar · !carta · !serie
!fav · !liberar (!release) · !rarezas (!rarity)

[cbu]🛠ᩧㅤ⿻  ׁ   ꒰    Инструменты
[CI]!ask <вопрос> · !trasl <es|en|ru> <текст>
!tts <текст> · !voz · !horoscopo <знак> · !ping

[cbu]👋ᩧㅤ⿻  ׁ   ꒰    Приветствие
[CI]!setwelcome <текст> · !setwelcome off|on|reset
Только персонал.

[cbu]🌐ᩧㅤ⿻  ׁ   ꒰    Язык
[CI]!langset es|en|ru меняет язык бота (только персонал).

[ci]Напиши !help, когда захочешь увидеть этот список.

[c]ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚ྀི̣︶˚̣  ྀི︶˚̣  ྀི︶˚̣  ྀི︶˚̣""",
}


def greeting(lang=None) -> str:
    text = TEXTS.get(lang) or TEXTS["en"]
    return text.replace("{bot}", BOT_NAME)


@client.command(["/start", "/help", "/ayuda"])
@commands_enable_required()
async def cmd_start(event: respObject.Event):
    await reply(event, greeting(lang_of(event)))


# ---- Português (pt-BR) y mención de pt en los otros idiomas ----
for _k in list(TEXTS):
    TEXTS[_k] = (TEXTS[_k].replace("!langset es|en|ru", "!langset es|en|ru|pt")
                 .replace("<es|en|ru>", "<es|en|ru|pt>"))
_pt = TEXTS["es"]
for _a, _b in [
    ("¡Hola! Soy {bot}", "Olá! Eu sou {bot}"),
    ("Ya estoy en el chat. Esto es lo que puedo hacer:", "Já estou no chat. Veja o que eu posso fazer:"),
    ("Juegos", "Jogos"),
    ("Parejas", "Casais"),
    ("Herramientas", "Ferramentas"),
    ("Bienvenida", "Boas-vindas"),
    ("<pregunta>", "<pergunta>"),
    ("Solo staff.", "Somente equipe."),
    ("cambia el idioma del bot (solo staff)", "altera o idioma do bot (somente equipe)"),
    ("Escribí !help cuando quieras ver esta lista.", "Digite !help quando quiser ver esta lista."),
]:
    _pt = _pt.replace(_a, _b)
TEXTS["pt"] = _pt
