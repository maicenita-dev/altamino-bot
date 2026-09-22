// src/lang.js
// Guarda el idioma preferido de cada usuario (persistente, JSON local).

const fs = require("fs");
const path = require("path");

const DB_PATH = path.join(__dirname, "..", "data", "lang.json");
const DEFAULT_LANG = "es";
const SUPPORTED = ["es", "en", "ru"];

function loadDB() {
  try {
    return JSON.parse(fs.readFileSync(DB_PATH, "utf8"));
  } catch {
    return {};
  }
}

function saveDB(db) {
  fs.mkdirSync(path.dirname(DB_PATH), { recursive: true });
  fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2));
}

function getLang(userId) {
  const db = loadDB();
  return db[userId] || DEFAULT_LANG;
}

function setLang(userId, lang) {
  if (!SUPPORTED.includes(lang)) return { ok: false };
  const db = loadDB();
  db[userId] = lang;
  saveDB(db);
  return { ok: true };
}

module.exports = { getLang, setLang, SUPPORTED, DEFAULT_LANG };
