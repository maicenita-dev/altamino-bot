"""Casamientos: devuelve status + datos. Persiste en data/marriages.json"""
from .config import DATA_DIR
from .storage import load_json, save_json

DB_PATH = DATA_DIR / "marriages.json"
# marriages: {userId: partnerId}   (espejado en ambos lados)
# proposals: {targetId: proposerId} (propuesta pendiente hacia targetId)


def _load() -> dict:
    db = load_json(DB_PATH, {})
    db.setdefault("marriages", {})
    db.setdefault("proposals", {})
    return db


def propose(proposer: dict, target: dict | None) -> dict:
    """proposer/target: {"userId", "nickname"}"""
    if not target:
        return {"status": "noTarget"}
    pid, tid = str(proposer["userId"]), str(target["userId"])
    if pid == tid:
        return {"status": "self"}

    db = _load()
    if pid in db["marriages"]:
        return {"status": "alreadyMarried"}
    if tid in db["marriages"]:
        return {"status": "targetMarried", "target": target["nickname"]}

    # si el target ya le había propuesto al proposer, se casan directo
    if db["proposals"].get(pid) == tid:
        del db["proposals"][pid]
        db["marriages"][pid] = tid
        db["marriages"][tid] = pid
        save_json(DB_PATH, db)
        return {"status": "married", "proposer": proposer["nickname"], "target": target["nickname"]}

    db["proposals"][tid] = pid
    save_json(DB_PATH, db)
    return {"status": "proposed", "proposer": proposer["nickname"], "target": target["nickname"]}


def divorce(user: dict) -> dict:
    uid = str(user["userId"])
    db = _load()
    partner = db["marriages"].get(uid)
    if not partner:
        return {"status": "notMarried"}
    db["marriages"].pop(uid, None)
    db["marriages"].pop(partner, None)
    save_json(DB_PATH, db)
    return {"status": "divorced", "user": user["nickname"]}


def status(user: dict, members: list | None) -> dict:
    partner_id = _load()["marriages"].get(str(user["userId"]))
    if not partner_id:
        return {"married": False}
    partner = next((m for m in (members or []) if str(m["userId"]) == partner_id), None)
    return {"married": True, "partner": partner["nickname"] if partner else None}
