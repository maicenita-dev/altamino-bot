// src/translate.js
// Traduce texto libre para /trasl. Usa "translate-google", un paquete NO
// OFICIAL que pega contra Google Translate sin necesitar API key.
// Como no es oficial, puede eventualmente dejar de funcionar si Google
// cambia algo — igual riesgo que node-gtts (que ya usás en tts.js).

const translate = require("translate-google");

const SUPPORTED = ["es", "en", "ru"];

/**
 * @param {string} text
 * @param {"es"|"en"|"ru"} targetLang
 * @returns {Promise<string>}
 */
async function translateText(text, targetLang) {
  if (!SUPPORTED.includes(targetLang)) {
    throw new Error(`Idioma no soportado: ${targetLang}`);
  }
  return translate(text, { to: targetLang });
}

module.exports = { translateText, SUPPORTED };
