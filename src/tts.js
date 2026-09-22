// src/tts.js
// Convierte texto en un Buffer de audio (mp3). No depende de AltAmino,
// solo devuelve bytes — el adapter se encarga de mandarlos como media.
//
// La voz usada depende del idioma pedido: si el texto es en ruso pero
// se pide voz "es", va a sonar mal (pronunciación incorrecta). Por eso
// textToSpeech recibe el idioma como parámetro.

const gttsFactory = require("node-gtts");

const MAX_CHARS = 300;
const engines = {};

function getEngine(lang) {
  if (!engines[lang]) engines[lang] = gttsFactory(lang);
  return engines[lang];
}

/**
 * @param {string} text
 * @param {"es"|"en"|"ru"} [lang]  idioma/voz a usar (default "es")
 * @returns {Promise<Buffer>} audio en mp3
 */
function textToSpeech(text, lang = "es") {
  return new Promise((resolve, reject) => {
    const clean = (text || "").trim();
    if (!clean) return reject(new Error("Texto vacío"));
    if (clean.length > MAX_CHARS) return reject(new Error(`Máximo ${MAX_CHARS} caracteres`));

    const chunks = [];
    const stream = getEngine(lang).stream(clean);
    stream.on("data", (chunk) => chunks.push(chunk));
    stream.on("end", () => resolve(Buffer.concat(chunks)));
    stream.on("error", reject);
  });
}

module.exports = { textToSpeech, MAX_CHARS };
