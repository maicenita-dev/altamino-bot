"""Economía de las cartas: !daily, !coins, !shop, !buy (por comunidad)."""
import time

from altamino import respObject

from src.aa import client
from src.aa.modules.cards import _fmt, _load, _lock, _refresh, _save, _user
from src.core import deco
from src.core.ctx import lang_of, scope_of, args
from src.utils import reply
from src.utils.wrappers.chat_settings import commands_enable_required

DAILY_AMOUNT = 100
DAILY_COOLDOWN = 20 * 3600
REWARD = [10, 30, 80, 200]                      # monedas por liberar, según la rareza
PRICES = {"fav": 100, "rolls": 200, "claim": 300}
FAV_COOLDOWN = 24 * 3600

MSG = {
    "es": {
        "daily_ok": "🎁 Cobraste tu recompensa diaria: +{n} monedas. Total: {total} 🪙",
        "daily_wait": "Ya cobraste tu recompensa diaria. Volvé en {t}.",
        "coins": "🪙 {nick}: {n} monedas",
        "coins_daily_ready": "Recompensa diaria: disponible ✅ (!daily)",
        "coins_daily_wait": "Recompensa diaria: en {t}",
        "shop_title": "🛒 Tienda",
        "shop_fav": "fav — Cambiar tu favorito sin esperar 24 h ({price} 🪙)",
        "shop_rolls": "rolls — Reiniciar tus tiradas ({price} 🪙)",
        "shop_claim": "claim — Reiniciar el tiempo de reclamo ({price} 🪙)",
        "shop_footer": "Comprá con !buy <item>. Tus monedas: {n} 🪙",
        "buy_usage": "Elegí qué comprar. Ej: !buy fav (mirá las opciones en !shop)",
        "buy_unknown": "Ese objeto no existe. Mirá las opciones en !shop.",
        "buy_poor": "No te alcanzan las monedas: necesitás {price} 🪙 y tenés {n} 🪙.",
        "buy_not_needed": "No lo necesitás ahora, así que no te cobré.",
        "buy_fav": "✅ Ya podés cambiar tu favorito con !fav. Pagaste {price} 🪙.",
        "buy_rolls": "✅ Tus tiradas se reiniciaron. Pagaste {price} 🪙.",
        "buy_claim": "✅ Ya podés reclamar de nuevo. Pagaste {price} 🪙.",
        "reward": "+{n} monedas 🪙",
    },
    "en": {
        "daily_ok": "🎁 You collected your daily reward: +{n} coins. Total: {total} 🪙",
        "daily_wait": "You already collected your daily reward. Come back in {t}.",
        "coins": "🪙 {nick}: {n} coins",
        "coins_daily_ready": "Daily reward: available ✅ (!daily)",
        "coins_daily_wait": "Daily reward: in {t}",
        "shop_title": "🛒 Shop",
        "shop_fav": "fav — Change your favorite without waiting 24 h ({price} 🪙)",
        "shop_rolls": "rolls — Reset your rolls ({price} 🪙)",
        "shop_claim": "claim — Reset the claim timer ({price} 🪙)",
        "shop_footer": "Buy with !buy <item>. Your coins: {n} 🪙",
        "buy_usage": "Pick what to buy. Ex: !buy fav (see the options in !shop)",
        "buy_unknown": "That item doesn't exist. See the options in !shop.",
        "buy_poor": "Not enough coins: you need {price} 🪙 and have {n} 🪙.",
        "buy_not_needed": "You don't need it right now, so you weren't charged.",
        "buy_fav": "✅ You can change your favorite with !fav now. You paid {price} 🪙.",
        "buy_rolls": "✅ Your rolls were reset. You paid {price} 🪙.",
        "buy_claim": "✅ You can claim again now. You paid {price} 🪙.",
        "reward": "+{n} coins 🪙",
    },
    "ru": {
        "daily_ok": "🎁 Ты получил(а) ежедневную награду: +{n} монет. Всего: {total} 🪙",
        "daily_wait": "Ты уже получил(а) ежедневную награду. Возвращайся через {t}.",
        "coins": "🪙 {nick}: {n} монет",
        "coins_daily_ready": "Ежедневная награда: доступна ✅ (!daily)",
        "coins_daily_wait": "Ежедневная награда: через {t}",
        "shop_title": "🛒 Магазин",
        "shop_fav": "fav — Сменить любимого без ожидания 24 ч ({price} 🪙)",
        "shop_rolls": "rolls — Сбросить броски ({price} 🪙)",
        "shop_claim": "claim — Сбросить таймер получения ({price} 🪙)",
        "shop_footer": "Покупай командой !buy <предмет>. Твои монеты: {n} 🪙",
        "buy_usage": "Выбери, что купить. Пример: !buy fav (варианты в !shop)",
        "buy_unknown": "Такого предмета нет. Варианты смотри в !shop.",
        "buy_poor": "Не хватает монет: нужно {price} 🪙, у тебя {n} 🪙.",
        "buy_not_needed": "Сейчас это не нужно, поэтому монеты не списаны.",
        "buy_fav": "✅ Теперь можно сменить любимого командой !fav. Оплачено {price} 🪙.",
        "buy_rolls": "✅ Броски сброшены. Оплачено {price} 🪙.",
        "buy_claim": "✅ Теперь можно снова забирать. Оплачено {price} 🪙.",
        "reward": "+{n} монет 🪙",
    },
    "pt": {
        "daily_ok": "🎁 Você coletou sua recompensa diária: +{n} moedas. Total: {total} 🪙",
        "daily_wait": "Você já coletou sua recompensa diária. Volte em {t}.",
        "coins": "🪙 {nick}: {n} moedas",
        "coins_daily_ready": "Recompensa diária: disponível ✅ (!daily)",
        "coins_daily_wait": "Recompensa diária: em {t}",
        "shop_title": "🛒 Loja",
        "shop_fav": "fav — Trocar seu favorito sem esperar 24 h ({price} 🪙)",
        "shop_rolls": "rolls — Reiniciar suas rolagens ({price} 🪙)",
        "shop_claim": "claim — Reiniciar o tempo de reivindicação ({price} 🪙)",
        "shop_footer": "Compre com !buy <item>. Suas moedas: {n} 🪙",
        "buy_usage": "Escolha o que comprar. Ex: !buy fav (veja as opções em !shop)",
        "buy_unknown": "Esse item não existe. Veja as opções em !shop.",
        "buy_poor": "Moedas insuficientes: você precisa de {price} 🪙 e tem {n} 🪙.",
        "buy_not_needed": "Você não precisa disso agora, então não cobrei.",
        "buy_fav": "✅ Agora você pode trocar seu favorito com !fav. Você pagou {price} 🪙.",
        "buy_rolls": "✅ Suas rolagens foram reiniciadas. Você pagou {price} 🪙.",
        "buy_claim": "✅ Agora você pode reivindicar de novo. Você pagou {price} 🪙.",
        "reward": "+{n} moedas 🪙",
    },
}


def _m(lang, key, **kw):
    return (MSG.get(lang) or MSG["es"])[key].format(**kw)


def reward_text(lang, n):
    return _m(lang, "reward", n=n)


@client.command(["!daily"])
@commands_enable_required()
async def cmd_daily(event: respObject.Event):
    lang, scope = lang_of(event), scope_of(event)
    async with _lock:
        db = _load(scope)
        uid, u = _user(db, event)
        now = time.time()
        wait = u.get("daily_at", 0) + DAILY_COOLDOWN - now
        if wait > 0:
            _save(scope, db)
            return await reply(event, deco.daily("wait", _m(lang, "daily_wait", t=_fmt(wait))))
        u["coins"] = u.get("coins", 0) + DAILY_AMOUNT
        u["daily_at"] = now
        total = u["coins"]
        _save(scope, db)
    await reply(event, deco.daily("ok", _m(lang, "daily_ok", n=DAILY_AMOUNT, total=total)))


@client.command(["!coins"])
@commands_enable_required()
async def cmd_coins(event: respObject.Event):
    lang, scope = lang_of(event), scope_of(event)
    async with _lock:
        db = _load(scope)
        uid, u = _user(db, event)
        _save(scope, db)
        n, nick = u.get("coins", 0), u["nick"]
        wait = u.get("daily_at", 0) + DAILY_COOLDOWN - time.time()
    daily = _m(lang, "coins_daily_wait", t=_fmt(wait)) if wait > 0 else _m(lang, "coins_daily_ready")
    await reply(event, deco.coins(_m(lang, "coins", nick=nick, n=n), daily))


@client.command(["!shop"])
@commands_enable_required()
async def cmd_shop(event: respObject.Event):
    lang, scope = lang_of(event), scope_of(event)
    async with _lock:
        db = _load(scope)
        uid, u = _user(db, event)
        _save(scope, db)
        n = u.get("coins", 0)
    items = [_m(lang, f"shop_{k}", price=p) for k, p in PRICES.items()]
    await reply(event, deco.shop(_m(lang, "shop_title"), items, _m(lang, "shop_footer", n=n)))


@client.command(["!buy"])
@commands_enable_required()
async def cmd_buy(event: respObject.Event):
    lang, scope = lang_of(event), scope_of(event)
    item = args(event).strip().lower()
    if not item:
        return await reply(event, deco.buy("usage", _m(lang, "buy_usage")))
    if item not in PRICES:
        return await reply(event, deco.buy("unknown", _m(lang, "buy_unknown")))
    price = PRICES[item]
    async with _lock:
        db = _load(scope)
        uid, u = _user(db, event)
        now = time.time()
        if item == "fav":
            needed = u.get("fav_at", 0) + FAV_COOLDOWN - now > 0
        elif item == "rolls":
            _refresh(u, now)
            needed = u["rolls"] > 0
        else:
            needed = u.get("claim_at", 0) > now
        if not needed:
            _save(scope, db)
            return await reply(event, deco.buy("not_needed", _m(lang, "buy_not_needed")))
        coins = u.get("coins", 0)
        if coins < price:
            _save(scope, db)
            return await reply(event, deco.buy("poor", _m(lang, "buy_poor", price=price, n=coins)))
        u["coins"] = coins - price
        if item == "fav":
            u["fav_at"] = 0
        elif item == "rolls":
            u["rolls"], u["roll_start"] = 0, now
        else:
            u["claim_at"] = 0
        _save(scope, db)
    await reply(event, deco.buy(item, _m(lang, f"buy_{item}", price=price)))
