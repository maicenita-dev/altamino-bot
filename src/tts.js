// src/tts.js
// Convierte texto en un Buffer de audio (mp3).

const gtts = require("node-gtts")("es");

const MAX_CHARS = 300;

function textToSpeech(text) {
  return new Promise((resolve, reject) => {
    const clean = (text || "").trim();
    if (!clean) return reject(new Error("Texto vacío"));
    if (clean.length > MAX_CHARS) return reject(new Error(`Máximo ${MAX_CHARS} caracteres`));

    const chunks = [];
    const stream = gtts.stream(clean);
    stream.on("data", (chunk) => chunks.push(chunk));
    stream.on("end", () => resolve(Buffer.concat(chunks)));
    stream.on("error", reject);
  });
}

module.exports = { textToSpeech, MAX_CHARS };
