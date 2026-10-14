"""Minijuegos: lógica pura, devuelve DATOS (el texto lo arma i18n)."""
import random
import re

from .i18n import EIGHTBALL_ANSWERS

EIGHTBALL_COUNT = len(EIGHTBALL_ANSWERS["es"])


def roll() -> dict:
    a, b = random.randint(1, 6), random.randint(1, 6)
    return {"a": a, "b": b, "total": a + b}


def dice(sides) -> dict:
    s = sides if isinstance(sides, int) and 2 <= sides <= 1000 else 6
    return {"sides": s, "result": random.randint(1, s)}


def coin() -> dict:
    return {"result": random.choice(["heads", "tails"])}


def eightball(question: str) -> dict:
    if not question or not question.strip():
        return {"ok": False}
    return {"ok": True, "answerIndex": random.randrange(EIGHTBALL_COUNT)}


def percent(what: str) -> dict:
    if not what or not what.strip():
        return {"ok": False}
    return {"ok": True, "what": what.strip(), "value": random.randint(0, 100)}


def ship(members: list) -> dict:
    """members: lista de {"userId", "nickname"}"""
    if not members or len(members) < 2:
        return {"ok": False}
    a, b = random.sample(members, 2)
    return {"ok": True, "a": a["nickname"], "b": b["nickname"], "value": random.randint(0, 100)}


def choose(raw: str) -> dict:
    parts = re.split(r",|\s+(?:o|or|или)\s+", raw or "", flags=re.IGNORECASE)
    options = [p.strip() for p in parts if p and p.strip()]
    if len(options) < 2:
        return {"ok": False}
    return {"ok": True, "choice": random.choice(options)}


# acepta piedra/papel/tijera en los 3 idiomas
RPS_INPUT = {
    "piedra": 0, "rock": 0, "камень": 0, "🪨": 0,
    "tijera": 1, "tijeras": 1, "scissors": 1, "ножницы": 1, "✂️": 1,
    "papel": 2, "paper": 2, "бумага": 2, "📄": 2,
}


def rps(choice_raw: str) -> dict:
    user = RPS_INPUT.get((choice_raw or "").lower().strip())
    if user is None:
        return {"ok": False}
    bot = random.randint(0, 2)
    if user == bot:
        result = "tie"
    elif (user + 1) % 3 == bot:
        result = "lose"
    else:
        result = "win"
    return {"ok": True, "userChoice": user, "botChoice": bot, "result": result}
