// src/gifs.js
// Mapea cada "reacción" del bot a un archivo .gif local, en res/gifs/.
// No depende de AltAmino: solo lee bytes del disco.

const fs = require("fs");
const path = require("path");

const GIFS_DIR = path.join(__dirname, "..", "res", "gifs");

// key -> nombre de archivo dentro de res/gifs/
// Agregá más líneas acá a medida que consigas gifs para otras reacciones.
const GIF_MAP = {
  horoscopo: "horoscopo.gif",
  roll: "roll.gif",
  dice: "roll.gif",
  flip: "flip.gif",
  eightball: "8ball.gif",
  ship: "ship.gif",
  rps: "rps.gif",
  marry: "marry.gif",
  divorce: "divorce.gif",
};

/**
 * @param {string} key  una de las claves de GIF_MAP
 * @returns {{ok:true, buffer:Buffer, filename:string} | {ok:false, message:string}}
 */
function getGif(key) {
  const filename = GIF_MAP[key];
  if (!filename) {
    return { ok: false, message: `No hay gif configurado para "${key}".` };
  }
  const filePath = path.join(GIFS_DIR, filename);
  try {
    const buffer = fs.readFileSync(filePath);
    return { ok: true, buffer, filename };
  } catch {
    return { ok: false, message: `Falta el archivo res/gifs/${filename}.` };
  }
}

module.exports = { getGif, GIF_MAP };
