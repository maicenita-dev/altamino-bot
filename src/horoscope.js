// src/horoscope.js
// Lógica pura: no sabe nada de AltAmino, solo calcula texto.

const SIGNS = {
  aries: "♈ Aries",
  tauro: "♉ Tauro",
  geminis: "♊ Géminis",
  cancer: "♋ Cáncer",
  leo: "♌ Leo",
  virgo: "♍ Virgo",
  libra: "♎ Libra",
  escorpio: "♏ Escorpio",
  sagitario: "♐ Sagitario",
  capricornio: "♑ Capricornio",
  acuario: "♒ Acuario",
  piscis: "♓ Piscis",
};

// Agregá las frases que quieras acá
const PHRASES = [
  "Hoy es un buen día para tomar una decisión que venías postergando.",
  "Cuidado con los gastos impulsivos, tu billetera te lo va a agradecer.",
  "Alguien de tu pasado puede reaparecer. Vos decidís si abrís la puerta.",
  "Tu energía está alta hoy: aprovechala para algo creativo.",
  "Momento de escuchar más y hablar menos, sobre todo en discusiones.",
  "Una sorpresa agradable se acerca, mantené los ojos abiertos.",
  "Es un buen día para reconectar con amigos que tenés abandonados.",
  "Tu paciencia va a ser puesta a prueba, respirá antes de responder.",
];

// Hash simple y determinístico (mismo string -> mismo número siempre)
function hash(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = (h * 31 + str.charCodeAt(i)) >>> 0;
  }
  return h;
}

function normalizeSign(raw) {
  return raw
    .toLowerCase()
    .trim()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, ""); // saca tildes: géminis -> geminis
}

/**
 * Devuelve el horóscopo del día para un signo.
 * La misma fecha + mismo signo siempre da la misma frase.
 */
function getHoroscope(rawSign) {
  const key = normalizeSign(rawSign);
  if (!SIGNS[key]) {
    return {
      ok: false,
      message: `Signo no reconocido. Opciones: ${Object.keys(SIGNS).join(", ")}`,
    };
  }

  const today = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
  const idx = hash(`${today}-${key}`) % PHRASES.length;

  return {
    ok: true,
    sign: SIGNS[key],
    date: today,
    text: PHRASES[idx],
  };
}

module.exports = { getHoroscope, SIGNS };
