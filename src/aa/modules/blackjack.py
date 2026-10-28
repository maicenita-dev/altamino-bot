"""Blackjack con apuestas de monedas (por comunidad). Comandos: !blackjack, !hit, !stand, !double."""
import random
import time

from altamino import respObject

from src.aa import client
from src.aa.modules.cards import _load, _lock, _save, _user
from src.core.ctx import args, lang_of, scope_of
from src.utils import reply
from src.utils.wrappers.chat_settings import commands_enable_required

MIN_BET, MAX_BET = 10, 500
TIMEOUT = 180                      # segundos sin jugar: la partida vence y se pierde la apuesta
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = "♠♥♦♣"

MSG = {
    "es": {
        "usage": "Escribí tu apuesta. Ej: !blackjack 50 (mínimo {min}, máximo {max} 🪙)",
        "range": "La apuesta debe estar entre {min} y {max} 🪙.",
        "poor": "No te alcanzan las monedas: tenés {n} 🪙.",
        "busy": "Ya tenés una partida en curso. Usá !hit, !stand o !double.",
        "none": "No tenés ninguna partida. Empezá con !blackjack <apuesta>.",
        "expired": "Tu partida venció por inactividad y perdiste {bet} 🪙.",
        "title": "🃏 Blackjack — apuesta: {bet} 🪙",
        "you": "Tus cartas: {hand} ({total})",
        "dealer_hidden": "Crupier: {hand} ❓",
        "dealer": "Crupier: {hand} ({total})",
        "actions": "Usá !hit, !stand o !double.",
        "actions_nodouble": "Usá !hit o !stand.",
        "no_double": "Solo podés doblar con tus dos primeras cartas.",
        "poor_double": "No te alcanzan las monedas para doblar: necesitás {n} 🪙 más.",
        "win": "🎉 ¡Ganaste! +{n} 🪙. Total: {coins} 🪙",
        "blackjack": "🃏 ¡Blackjack! +{n} 🪙. Total: {coins} 🪙",
        "push": "🤝 Empate: recuperás tu apuesta. Total: {coins} 🪙",
        "lose": "💸 Perdiste {n} 🪙. Total: {coins} 🪙",
        "bust": "💥 Te pasaste de 21. Perdiste {n} 🪙. Total: {coins} 🪙",
        "dealer_bj": "💸 El crupier tiene blackjack. Perdiste {n} 🪙. Total: {coins} 🪙",
    },
    "en": {
        "usage": "Write your bet. Ex: !blackjack 50 (min {min}, max {max} 🪙)",
        "range": "The bet must be between {min} and {max} 🪙.",
        "poor": "Not enough coins: you have {n} 🪙.",
        "busy": "You already have a game in progress. Use !hit, !stand or !double.",
        "none": "You have no game. Start with !blackjack <bet>.",
        "expired": "Your game expired due to inactivity and you lost {bet} 🪙.",
        "title": "🃏 Blackjack — bet: {bet} 🪙",
        "you": "Your cards: {hand} ({total})",
        "dealer_hidden": "Dealer: {hand} ❓",
        "dealer": "Dealer: {hand} ({total})",
        "actions": "Use !hit, !stand or !double.",
        "actions_nodouble": "Use !hit or !stand.",
        "no_double": "You can only double with your first two cards.",
        "poor_double": "Not enough coins to double: you need {n} 🪙 more.",
        "win": "🎉 You won! +{n} 🪙. Total: {coins} 🪙",
        "blackjack": "🃏 Blackjack! +{n} 🪙. Total: {coins} 🪙",
        "push": "🤝 Push: you get your bet back. Total: {coins} 🪙",
        "lose": "💸 You lost {n} 🪙. Total: {coins} 🪙",
        "bust": "💥 You went over 21. You lost {n} 🪙. Total: {coins} 🪙",
        "dealer_bj": "💸 The dealer has blackjack. You lost {n} 🪙. Total: {coins} 🪙",
    },
    "ru": {
        "usage": "Напиши ставку. Пример: !blackjack 50 (мин. {min}, макс. {max} 🪙)",
        "range": "Ставка должна быть от {min} до {max} 🪙.",
        "poor": "Не хватает монет: у тебя {n} 🪙.",
        "busy": "У тебя уже идёт игра. Используй !hit, !stand или !double.",
        "none": "У тебя нет игры. Начни с !blackjack <ставка>.",
        "expired": "Твоя игра закончилась из-за бездействия, ты потерял(а) {bet} 🪙.",
        "title": "🃏 Блэкджек — ставка: {bet} 🪙",
        "you": "Твои карты: {hand} ({total})",
        "dealer_hidden": "Дилер: {hand} ❓",
        "dealer": "Дилер: {hand} ({total})",
        "actions": "Используй !hit, !stand или !double.",
        "actions_nodouble": "Используй !hit или !stand.",
        "no_double": "Удвоить можно только с первыми двумя картами.",
        "poor_double": "Не хватает монет для удвоения: нужно ещё {n} 🪙.",
        "win": "🎉 Ты выиграл(а)! +{n} 🪙. Всего: {coins} 🪙",
        "blackjack": "🃏 Блэкджек! +{n} 🪙. Всего: {coins} 🪙",
        "push": "🤝 Ничья: ставка возвращена. Всего: {coins} 🪙",
        "lose": "💸 Ты проиграл(а) {n} 🪙. Всего: {coins} 🪙",
        "bust": "💥 Перебор. Ты проиграл(а) {n} 🪙. Всего: {coins} 🪙",
        "dealer_bj": "💸 У дилера блэкджек. Ты проиграл(а) {n} 🪙. Всего: {coins} 🪙",
    },
    "pt": {
        "usage": "Escreva sua aposta. Ex: !blackjack 50 (mín. {min}, máx. {max} 🪙)",
        "range": "A aposta deve estar entre {min} e {max} 🪙.",
        "poor": "Moedas insuficientes: você tem {n} 🪙.",
        "busy": "Você já tem uma partida em andamento. Use !hit, !stand ou !double.",
        "none": "Você não tem nenhuma partida. Comece com !blackjack <aposta>.",
        "expired": "Sua partida expirou por inatividade e você perdeu {bet} 🪙.",
        "title": "🃏 Blackjack — aposta: {bet} 🪙",
        "you": "Suas cartas: {hand} ({total})",
        "dealer_hidden": "Dealer: {hand} ❓",
        "dealer": "Dealer: {hand} ({total})",
        "actions": "Use !hit, !stand ou !double.",
        "actions_nodouble": "Use !hit ou !stand.",
        "no_double": "Você só pode dobrar com as suas duas primeiras cartas.",
        "poor_double": "Moedas insuficientes para dobrar: faltam {n} 🪙.",
        "win": "🎉 Você ganhou! +{n} 🪙. Total: {coins} 🪙",
        "blackjack": "🃏 Blackjack! +{n} 🪙. Total: {coins} 🪙",
        "push": "🤝 Empate: você recupera sua aposta. Total: {coins} 🪙",
        "lose": "💸 Você perdeu {n} 🪙. Total: {coins} 🪙",
        "bust": "💥 Você passou de 21. Perdeu {n} 🪙. Total: {coins} 🪙",
        "dealer_bj": "💸 O dealer tem blackjack. Você perdeu {n} 🪙. Total: {coins} 🪙",
    },
}


def _m(lang, key, **kw):
    return (MSG.get(lang) or MSG["es"])[key].format(**kw)


def _draw() -> str:
    """Baraja infinita: cada carta sale al azar."""
    return random.choice(RANKS) + random.choice(SUITS)


def _total(cards) -> int:
    total, aces = 0, 0
    for c in cards:
        r = c[:-1]
        if r == "A":
            total, aces = total + 11, aces + 1
        elif r in ("J", "Q", "K"):
            total += 10
        else:
            total += int(r)
    while total > 21 and aces:
        total, aces = total - 10, aces - 1
    return total


def _is_bj(cards) -> bool:
    return len(cards) == 2 and _total(cards) == 21


def _board(lang, g, reveal) -> list:
    lines = [_m(lang, "title", bet=g["bet"]),
             _m(lang, "you", hand=" ".join(g["p"]), total=_total(g["p"]))]
    if reveal:
        lines.append(_m(lang, "dealer", hand=" ".join(g["d"]), total=_total(g["d"])))
    else:
        lines.append(_m(lang, "dealer_hidden", hand=g["d"][0]))
    return lines


def _finish(lang, u, g, kind=None) -> str:
    """Cierra la partida: juega el crupier, paga y devuelve el mensaje final."""
    bet, p, d = g["bet"], g["p"], g["d"]
    if kind is None:
        pt = _total(p)
        if pt > 21:
            kind = "bust"
        else:
            while _total(d) < 17:
                d.append(_draw())
            dt = _total(d)
            kind = "win" if (dt > 21 or pt > dt) else ("push" if pt == dt else "lose")
    returned = {"win": 2 * bet, "push": bet, "blackjack": bet + int(bet * 1.5)}.get(kind, 0)
    net = {"win": bet, "push": 0, "blackjack": int(bet * 1.5)}.get(kind, bet)
    u["coins"] = u.get("coins", 0) + returned
    u["bj"] = None
    return "\n".join(_board(lang, g, True) + ["", _m(lang, kind, n=net, coins=u["coins"])])


@client.command(["!blackjack", "!bj"])
@commands_enable_required()
async def cmd_blackjack(event: respObject.Event):
    lang, scope = lang_of(event), scope_of(event)
    raw = args(event).strip()
    async with _lock:
        db = _load(scope)
        uid, u = _user(db, event)
        now, note = time.time(), ""
        g = u.get("bj")
        if g:
            if now - g["t"] > TIMEOUT:
                note = _m(lang, "expired", bet=g["bet"]) + "\n\n"
                u["bj"] = None
            else:
                _save(scope, db)
                return await reply(event, _m(lang, "busy"))
        if not raw.isdigit():
            _save(scope, db)
            return await reply(event, note + _m(lang, "usage", min=MIN_BET, max=MAX_BET))
        bet = int(raw)
        if not MIN_BET <= bet <= MAX_BET:
            _save(scope, db)
            return await reply(event, note + _m(lang, "range", min=MIN_BET, max=MAX_BET))
        coins = u.get("coins", 0)
        if coins < bet:
            _save(scope, db)
            return await reply(event, note + _m(lang, "poor", n=coins))
        u["coins"] = coins - bet
        g = {"bet": bet, "p": [_draw(), _draw()], "d": [_draw(), _draw()], "t": now}
        pbj, dbj = _is_bj(g["p"]), _is_bj(g["d"])
        if pbj or dbj:
            kind = "push" if (pbj and dbj) else ("blackjack" if pbj else "dealer_bj")
            text = _finish(lang, u, g, kind)
        else:
            u["bj"] = g
            text = "\n".join(_board(lang, g, False) + ["", _m(lang, "actions")])
        _save(scope, db)
    await reply(event, note + text)


async def _act(event, action):
    lang, scope = lang_of(event), scope_of(event)
    async with _lock:
        db = _load(scope)
        uid, u = _user(db, event)
        g = u.get("bj")
        if not g:
            _save(scope, db)
            return await reply(event, _m(lang, "none"))
        now = time.time()
        if now - g["t"] > TIMEOUT:
            u["bj"] = None
            _save(scope, db)
            return await reply(event, _m(lang, "expired", bet=g["bet"]))
        g["t"] = now
        if action == "hit":
            g["p"].append(_draw())
            if _total(g["p"]) >= 21:               # se pasó (pierde) o llegó a 21 (planta solo)
                text = _finish(lang, u, g)
            else:
                text = "\n".join(_board(lang, g, False) + ["", _m(lang, "actions_nodouble")])
        elif action == "stand":
            text = _finish(lang, u, g)
        else:
            if len(g["p"]) != 2 or g.get("doubled"):
                _save(scope, db)
                return await reply(event, _m(lang, "no_double"))
            coins = u.get("coins", 0)
            if coins < g["bet"]:
                _save(scope, db)
                return await reply(event, _m(lang, "poor_double", n=g["bet"] - coins))
            u["coins"] = coins - g["bet"]
            g["bet"] *= 2
            g["doubled"] = True
            g["p"].append(_draw())
            text = _finish(lang, u, g)
        _save(scope, db)
    await reply(event, text)


@client.command(["!hit"])
@commands_enable_required()
async def cmd_hit(event: respObject.Event):
    await _act(event, "hit")


@client.command(["!stand"])
@commands_enable_required()
async def cmd_stand(event: respObject.Event):
    await _act(event, "stand")


@client.command(["!double"])
@commands_enable_required()
async def cmd_double(event: respObject.Event):
    await _act(event, "double")
