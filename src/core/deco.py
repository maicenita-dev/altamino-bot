"""Decoración de los mensajes de los minijuegos (formato Amino)."""


def _top(emoji: str) -> str:
    return f"[c]°    ‿      ‿   ‿     ‿   {emoji}   ‿     ‿     ‿     ‿   °"


def _wrap(top: str, lines: list, gap: bool = True) -> str:
    mid = ["", *lines, ""] if gap else list(lines)
    return "\n".join([top, *mid, top])


BOX = "⏝ׅ  ⿻  "
SHIP_TOP = "[c]⠳⣄⣀⣠⠞˖*✿⢷ ⠳⣄⣀⣠⠞˖*✿⢷"
RPS_TOP = "[c]◟ ͜ ◞  ྀི◟ ͜ ׁ🪷 𑄹 ◟ ͜ ◞  ྀི◟ ͜ ׁ🪷 𑄹◟ ͜ ◞  ྀི◟ ͜ ׁ🪷"


def roll(text: str) -> str:
    return _wrap(_top("🎲"), ["[c]" + text])


def dice(text: str) -> str:
    return _wrap(_top("🎲"), ["[ci]" + text])


def flip(text: str) -> str:
    return "𖹭🪙ㅤᢄ︧ ꢶᝳ  ֟፝ ᳕   ̨ꢶ︨ᢃㅤ" + text


def ball(text: str) -> str:
    return _wrap(_top("🎱"), ["[c]" + BOX + text])


def percent(text: str) -> str:
    return _wrap(_top("📊"), ["[c]" + BOX + text])


def ship(text: str) -> str:
    return _wrap(SHIP_TOP, ["[c]⿻ 🌸⠴ㅤ֪ㅤ—ㅤ" + text.rstrip(".") + "ㅤׄㅤ  🍡⠴"], gap=False)


def rps(text: str) -> str:
    return _wrap(RPS_TOP, ["[c]⿻ ✊✋✌️⠴ㅤ֪ㅤ—ㅤ" + text])


def choose(text: str) -> str:
    return _wrap(_top("🙀"), ["[c]𑇡  〬  " + text], gap=False)


JOIN_TOP = "[c]∵∴∵∴ ୨୧ ∴∵∴∵ ୨୧ ∴∵∴∵ ୨୧ ∴∵∴∵"
WEL_TOP = "[c]𐙚𓏵𓏵𓏵𓏵𓏵𓏵𓏵𓏵𓏵𓏵𓏵𐙚"

JOIN_FACES = {
    "chat": "ꉂꉂ◟(˃ꇴ˂ ૂ๑)ㅤ",
    "com": "૮꒰｡ര ᎑ ര｡૮ ꒱ㅤ",
    "bad": "૮𐙚⁔⌯･.･⁔ა𐙚ㅤ",
    "err": "૮ ྀི ◞ ◟ აㅤ",
}
WEL_FACES = {
    "staff": "໒꒰݂𓂂ིྀᴗ . ᴗ𓂂݂ᐢ꒱ིྀ𐰉 ~❤︎゛ ",
    "ok": "･ﾟ･(｡>ω<｡)･ﾟ･ ",
    "reset": "ꕤᴗ ᴗ)⁾⁾♡ ",
    "default": "◍´മ⩊മ`◍ ٛ𐙚 ",
    "help": "꒪꒳꒪🍤 ",
}


def _lines(top: str, lines: list) -> str:
    return "\n".join([top, *lines, top])


def join_msg(kind: str, text: str) -> str:
    return _lines(JOIN_TOP, ["[c]" + JOIN_FACES[kind] + text])


def welcome_msg(kind: str, *texts: str) -> str:
    return _lines(WEL_TOP, ["[c]" + WEL_FACES[kind] + t for t in texts])


# ---- ping, cooldown, parejas, herramientas, idioma ----
COOL_TOP = "[c]੭୧‿⏔⏔⏔ ⑅ ꒰ 𓏵 ꒱⑅ ⏔⏔⏔‿ϑ𐑞"
COOL_FACE = "૮( ⁄ฅ⁄⁄ฅ⁄⁄)აㅤ"
MARRY_TOP = "[c]𐙚𓏵𓏵𓏵𓏵𓏵𓏵𓏵𓏵𓏵𓏵𓏵𓏵𐙚"
MARRY_FACE = "♡ ૮꒰◌  .๑. ꒱ა  𓂃 ♪ㅤ"
DIV_TOP = "[c]︶˚̣̣̣  ྀི︶˚̣̣̣  ྀི︶˚̣̣̣  ྀི︶˚̣̣̣  ྀི︶˚̣̣̣  ྀི︶˚̣̣̣  ྀི︶˚̣̣̣  ྀི︶˚̣̣̣  ྀི︶"
DIV_FACES = {"single": "꒰ᐡ⩌⤙⩌ᐡ꒱ㅤ", "done": "૮ ྀི ◞ ◟ აㅤ"}
MARRIAGE_FACE = "໒꒰݂𓂂ིྀᴗ . ᴗ𓂂݂ᐢ꒱ིྀ𐰉 ~❤︎゛ㅤ"
TOOL_TOP = "[c]◟ ͜ ◞ ೀ ◟ ͜ ◞ ◟ ͜ ◞ ೀ ◟ ͜ ◞◟ ͜ ◞ ೀ ◟ ͜ ◞ ◟ ͜ ◞"
ASK_FACE = "(๑´▿｀๑)♫•*¨*•.¸¸♪✧ㅤ"
TRASL_FACE = "꒰♡ˊ͈ ु꒳ ू`͈꒱.⑅*♡ㅤ"
TTS_TOP = "[c]੭୧‿⏔⏔⏔⏔⏔⏔ ⑅ ꒰ 𓏵 ꒱⑅ ⏔⏔⏔⏔⏔⏔‿ϑ𐑞"
TTS_FACE = "♡̶₊⁺ ໒꒰ྀི ˶> ༝ <˶꒱ྀㅤ"
HORO_FACE = "໒꒰ྀི◍•⩊•◍𐙚꒱აㅤ"
LANG_TOP = "[c]∵∴∵∴ ୨୧ ∴∵∴∵∴ ୨୧ ∴∵∴ ୨୧ ∴∵∴∵"
LANG_FACES = {"usage": "◍´മ⩊മ`◍ ٛ𐙚ㅤ", "done": "◍´മ⩊മ`◍ ٛ𐙚ㅤ", "staff": "ꉂꉂ◟(˃ꇴ˂ ૂ๑)ㅤ"}


def ping(title: str, version: str, delay: str, now: str) -> str:
    d = "𐔌՞꜆.  ̫.꜀՞𐦯♡ㅤ"
    return _lines(_top("🏓"), ["[cbu]🏓ฅ(´ര ̫ ര`)ㅤ" + title, d + version, d + delay, d + now])


def cooldown(rolls: str, claim: str) -> str:
    return _lines(COOL_TOP, ["[c]" + COOL_FACE + rolls, "[c]" + COOL_FACE + claim])


def cards_error(text: str) -> str:
    return _lines(COOL_TOP, ["[c]" + COOL_FACE + text])


def marry(text: str) -> str:
    return _lines(MARRY_TOP, ["[c]" + MARRY_FACE + text])


def divorce(kind: str, text: str) -> str:
    return _lines(DIV_TOP, ["[c]" + DIV_FACES[kind] + text])


def marriage(text: str) -> str:
    return _lines(MARRY_TOP, ["[c]" + MARRIAGE_FACE + text])


def ask(text: str) -> str:
    return _lines(TOOL_TOP, ["[c]" + ASK_FACE + text])


def trasl(text: str) -> str:
    return _lines(TOOL_TOP, ["[c]" + TRASL_FACE + text])


def tts(text: str) -> str:
    return _lines(TTS_TOP, ["[c]" + TTS_FACE + text])


def horo(text: str) -> str:
    return _lines(TTS_TOP, ["[c]" + HORO_FACE + text])


def horo_result(header: str, phrase: str) -> str:
    return _lines(TTS_TOP, ["[c]" + HORO_FACE + header, "", "[c]" + phrase])


def lang(kind: str, text: str) -> str:
    return _lines(LANG_TOP, ["[c]" + LANG_FACES[kind] + text])


# ---- cartas: búsqueda, favorito, liberar, rarezas ----
S1_TOP = "[c]◟ ͜ ◞ ೀ ◟ ͜ ◞ ◟ ͜ ◞ ೀ ◟ ͜ ◞ ೀ ◟ ͜ ◞ ೀ ◟ ͜ ◞"


def _s(top: str, face: str, text: str) -> str:
    return _lines(top, ["[c]" + face + text])


def search_usage(text: str) -> str:
    return _s(S1_TOP, "꒰◍ ´꒳` ◍꒱ㅤ", text)


def search_results(title: str, rows: list) -> str:
    return _lines(S1_TOP, ["[c]･ﾟ･(｡>ω<｡)･ﾟ･ㅤ" + title, ""]
                  + ["(,,ᴗ  ̫ᴗ,,)ꕤ*.ﾟㅤ" + r for r in rows])


def card_usage(text: str) -> str:
    return _s(S1_TOP, "ꕤᴗ ᴗ)⁾⁾♡ㅤ", text)


def card(head: str, series: str, extra: str, status: str, more=None) -> str:
    p = "(｡>ㅅ<｡)ㅤ"
    lines = ["[cu]໒꒰՞ ܸ. .ܸ՞꒱აㅤ" + head, p + series, p + extra, p + status]
    if more:
        lines += ["", "[c]꒪꒳꒪🍤ㅤ" + more]
    return _lines(S1_TOP, lines)


def series_usage(text: str) -> str:
    return _s(MARRY_TOP, HORO_FACE, text)


def series_none(text: str) -> str:
    return _s(MARRY_TOP, JOIN_FACES["bad"], text)


def series_list(title: str, rows: list, more=None) -> str:
    p = "(✿◠‿◠)ㅤ"
    lines = ["[cu]ꉂꉂ◟(˃ꇴ˂ ૂ๑)ㅤ" + title, ""] + [p + r for r in rows]
    if more:
        lines.append(p + more)
    return _lines(MARRY_TOP, lines)


def fav_none(text: str) -> str:
    return _s(MARRY_TOP, COOL_FACE, text)


def fav_current(text: str, wait=None) -> str:
    lines = ["[c]𐔌՞꜆.  ̫.꜀՞𐦯♡ㅤ" + text]
    if wait:
        lines += ["", "[c]꒰ྀི ∩ ◡ ∩ ꒱ㅤ" + wait]
    return _lines(MARRY_TOP, lines)


def fav_wait(text: str) -> str:
    return _s(DIV_TOP, ASK_FACE, text)


def fav_taken(text: str) -> str:
    return _s(DIV_TOP, TRASL_FACE, text)


def fav_set(text: str) -> str:
    return _s(DIV_TOP, "꒰◍ ´꒳` ◍꒱ㅤ", text)


def fav_owned(text: str) -> str:
    return _s(DIV_TOP, "(,,ᴗ  ̫ᴗ,,)ꕤ*.ﾟㅤ", text)


def fav_off(text: str) -> str:
    return _s(DIV_TOP, DIV_FACES["done"], text)


def lib(kind: str, text: str) -> str:
    if kind == "confirm":
        return _s(TTS_TOP, MARRY_FACE, text)
    face = "⿻ 💔⠴ㅤ֪ㅤ—ㅤ" if kind == "done" else "⿻ 🌸⠴ㅤ֪ㅤ—ㅤ"
    return _s(SHIP_TOP, face, text)


def rarities(title: str, rows: list, note: str, fav_note: str) -> str:
    lines = ["[cbu]･ﾟ･(｡>ω<｡)･ﾟ･ㅤ" + title + "ㅤ꒰◍ ´꒳` ◍꒱", ""]
    lines += ["ꕤᴗ ᴗ)⁾⁾♡ㅤ" + r for r in rows]
    lines += ["", "[c](｡>ㅅ<｡)ㅤ" + note, "", "[c]ꉂꉂ◟(˃ꇴ˂ ૂ๑)ㅤ" + fav_note]
    return _lines(TTS_TOP, lines)


def notfound(text: str) -> str:
    return _s(TTS_TOP, "ฅ(´ര ̫ ര`)ㅤ", text)
