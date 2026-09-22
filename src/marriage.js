// src/marriage.js
// Lógica pura de "casamientos" entre miembros de la comunidad.
// Persiste en un archivo JSON local — no depende de AltAmino para nada.

const fs = require("fs");
const path = require("path");

const DB_PATH = path.join(__dirname, "..", "data", "marriages.json");

function loadDB() {
  try {
    const raw = fs.readFileSync(DB_PATH, "utf8");
    return JSON.parse(raw);
  } catch {
    return { marriages: {}, proposals: {} };
    // marriages: { userId: partnerId }   -> se guarda espejado en ambos lados
    // proposals: { targetId: proposerId } -> propuesta pendiente hacia targetId
  }
}

function saveDB(db) {
  fs.mkdirSync(path.dirname(DB_PATH), { recursive: true });
  fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2));
}

function isMarried(db, userId) {
  return Boolean(db.marriages[userId]);
}

/**
 * @param {{userId:string, nickname:string}} proposer
 * @param {{userId:string, nickname:string}} target
 */
function propose(proposer, target) {
  if (!target) {
    return { ok: false, message: "Mencioná a alguien. Ej: /marry @usuario" };
  }
  if (proposer.userId === target.userId) {
    return { ok: false, message: "No podés casarte con vos mismo jaja." };
  }

  const db = loadDB();

  if (isMarried(db, proposer.userId)) {
    return { ok: false, message: "Ya estás casado/a. Divorciate primero con /divorce." };
  }
  if (isMarried(db, target.userId)) {
    return { ok: false, message: `${target.nickname} ya está casado/a con alguien.` };
  }

  // si el target ya le había propuesto antes al proposer, se casan directo
  if (db.proposals[proposer.userId] === target.userId) {
    delete db.proposals[proposer.userId];
    db.marriages[proposer.userId] = target.userId;
    db.marriages[target.userId] = proposer.userId;
    saveDB(db);
    return { ok: true, married: true, message: `💍 ${proposer.nickname} y ${target.nickname} se casaron!` };
  }

  db.proposals[target.userId] = proposer.userId;
  saveDB(db);
  return {
    ok: true,
    married: false,
    message: `💌 ${proposer.nickname} le propuso matrimonio a ${target.nickname}. Para aceptar, ${target.nickname} escribe /marry mencionando a ${proposer.nickname}.`,
  };
}

function divorce(user) {
  const db = loadDB();
  const partnerId = db.marriages[user.userId];
  if (!partnerId) {
    return { ok: false, message: "No estás casado/a con nadie." };
  }
  delete db.marriages[user.userId];
  delete db.marriages[partnerId];
  saveDB(db);
  return { ok: true, message: `💔 ${user.nickname} se divorció.` };
}

/**
 * @param {{userId:string, nickname:string}} user
 * @param {Array<{userId:string, nickname:string}>} members  para buscar el nombre de la pareja
 */
function status(user, members) {
  const db = loadDB();
  const partnerId = db.marriages[user.userId];
  if (!partnerId) return { ok: true, married: false, message: "No estás casado/a con nadie." };
  const partner = (members || []).find((m) => m.userId === partnerId);
  const name = partner ? partner.nickname : "alguien";
  return { ok: true, married: true, message: `💍 Estás casado/a con ${name}.` };
}

module.exports = { propose, divorce, status };
