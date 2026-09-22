// src/i18n.js
// Diccionario de strings del bot en es/en/ru + helper de interpolación.
// Los otros módulos (games, horoscope, marriage) devuelven DATOS, no texto;
// commands.js usa t() y estas tablas para armar el mensaje final en el
// idioma que corresponda.

const SUPPORTED = ["es", "en", "ru"];

const SIGN_NAMES = {
  es: {
    aries: "♈ Aries", tauro: "♉ Tauro", geminis: "♊ Géminis", cancer: "♋ Cáncer",
    leo: "♌ Leo", virgo: "♍ Virgo", libra: "♎ Libra", escorpio: "♏ Escorpio",
    sagitario: "♐ Sagitario", capricornio: "♑ Capricornio", acuario: "♒ Acuario", piscis: "♓ Piscis",
  },
  en: {
    aries: "♈ Aries", tauro: "♉ Taurus", geminis: "♊ Gemini", cancer: "♋ Cancer",
    leo: "♌ Leo", virgo: "♍ Virgo", libra: "♎ Libra", escorpio: "♏ Scorpio",
    sagitario: "♐ Sagittarius", capricornio: "♑ Capricorn", acuario: "♒ Aquarius", piscis: "♓ Pisces",
  },
  ru: {
    aries: "♈ Овен", tauro: "♉ Телец", geminis: "♊ Близнецы", cancer: "♋ Рак",
    leo: "♌ Лев", virgo: "♍ Дева", libra: "♎ Весы", escorpio: "♏ Скорпион",
    sagitario: "♐ Стрелец", capricornio: "♑ Козерог", acuario: "♒ Водолей", piscis: "♓ Рыбы",
  },
};

// Mismo orden en los 3 idiomas: el índice es lo que importa, no el texto.
const HOROSCOPE_PHRASES = {
  es: [
    "Hoy es un buen día para tomar una decisión que venías postergando.",
    "Cuidado con los gastos impulsivos, tu billetera te lo va a agradecer.",
    "Alguien de tu pasado puede reaparecer. Vos decidís si abrís la puerta.",
    "Tu energía está alta hoy: aprovechala para algo creativo.",
    "Momento de escuchar más y hablar menos, sobre todo en discusiones.",
    "Una sorpresa agradable se acerca, mantené los ojos abiertos.",
    "Es un buen día para reconectar con amigos que tenés abandonados.",
    "Tu paciencia va a ser puesta a prueba, respirá antes de responder.",
  ],
  en: [
    "Today is a good day to make a decision you've been putting off.",
    "Watch out for impulsive spending, your wallet will thank you.",
    "Someone from your past might reappear. You decide whether to open the door.",
    "Your energy is high today: use it for something creative.",
    "Time to listen more and talk less, especially in arguments.",
    "A pleasant surprise is coming, keep your eyes open.",
    "It's a good day to reconnect with friends you've been neglecting.",
    "Your patience will be tested, take a breath before responding.",
  ],
  ru: [
    "Сегодня хороший день, чтобы принять решение, которое ты откладывал(а).",
    "Осторожно с импульсивными тратами — твой кошелёк будет благодарен.",
    "Кто-то из твоего прошлого может появиться снова. Ты решаешь, открывать ли дверь.",
    "Сегодня у тебя много энергии — используй её для чего-то творческого.",
    "Время больше слушать и меньше говорить, особенно в спорах.",
    "Приятный сюрприз уже близко, будь внимателен(на).",
    "Хороший день, чтобы снова связаться с друзьями, которых ты забросил(а).",
    "Твоё терпение будет испытано — сделай вдох перед тем, как ответить.",
  ],
};

// Mismo orden en los 3 idiomas.
const EIGHTBALL_ANSWERS = {
  es: [
    "Sí, sin dudas.", "No cuentes con eso.", "Puede ser.", "Mejor no te lo digo ahora.",
    "Definitivamente sí.", "Muy dudoso.", "Pregúntame de nuevo más tarde.", "Absolutamente no.",
  ],
  en: [
    "Yes, definitely.", "Don't count on it.", "Maybe.", "Better not tell you now.",
    "Definitely yes.", "Very doubtful.", "Ask me again later.", "Absolutely not.",
  ],
  ru: [
    "Да, без сомнений.", "Даже не думай.", "Может быть.", "Лучше не скажу сейчас.",
    "Определённо да.", "Очень сомнительно.", "Спроси меня позже.", "Абсолютно нет.",
  ],
};

// índice 0=piedra/rock, 1=tijera/scissors, 2=papel/paper
const RPS_NAMES = {
  es: ["piedra", "tijera", "papel"],
  en: ["rock", "scissors", "paper"],
  ru: ["камень", "ножницы", "бумага"],
};

const STRINGS = {
  es: {
    horoscope_notRecognized: "Signo no reconocido. Opciones: {options}",
    horoscope_header: "{sign} — {date}",
    roll_result: "🎲 Sacaste {a} y {b} (total: {total})",
    dice_result: "🎲 Dado de {sides} caras: {result}",
    coin_heads: "🪙 Cara",
    coin_tails: "🪙 Ceca",
    eightball_noQuestion: "Hacé una pregunta primero.",
    percent_prompt: "Decime qué querés medir. Ej: /percent amor",
    percent_result: "📊 {what}: {value}%",
    ship_needMore: "Necesito al menos 2 personas en el chat.",
    ship_result: "💘 {a} + {b} = {value}% de compatibilidad",
    choose_needMore: "Dame al menos dos opciones separadas por coma.",
    choose_result: "👉 {choice}",
    rps_invalid: "Elegí: piedra, papel o tijera.",
    rps_result: "✊✋✌️ Vos: {user} | Bot: {bot} → {result}",
    rps_win: "ganaste", rps_lose: "perdiste", rps_tie: "empate",
    marry_noTarget: "Mencioná a alguien. Ej: /marry @usuario",
    marry_self: "No podés casarte con vos mismo jaja.",
    marry_alreadyMarried: "Ya estás casado/a. Divorciate primero con /divorce.",
    marry_targetMarried: "{target} ya está casado/a con alguien.",
    marry_married: "💍 {proposer} y {target} se casaron!",
    marry_proposed: "💌 {proposer} le propuso matrimonio a {target}. Para aceptar, {target} escribe /marry mencionando a {proposer}.",
    divorce_notMarried: "No estás casado/a con nadie.",
    divorce_done: "💔 {user} se divorció.",
    marriage_single: "No estás casado/a con nadie.",
    marriage_married: "💍 Estás casado/a con {partner}.",
    tts_needText: "Escribí el texto después del comando. Ej: /tts hola",
    tts_error: "No pude generar el audio: {error}",
    langset_usage: "Usá /langset es, /langset en o /langset ru",
    langset_done: "Idioma cambiado a {lang}.",
    trasl_usage: "Usá /trasl es, en o ru seguido del texto. Ej: /trasl en hola que tal",
    trasl_error: "No pude traducir el texto, intentá de nuevo.",
  },
  en: {
    horoscope_notRecognized: "Sign not recognized. Options: {options}",
    horoscope_header: "{sign} — {date}",
    roll_result: "🎲 You got {a} and {b} (total: {total})",
    dice_result: "🎲 {sides}-sided die: {result}",
    coin_heads: "🪙 Heads",
    coin_tails: "🪙 Tails",
    eightball_noQuestion: "Ask a question first.",
    percent_prompt: "Tell me what to measure. Ex: /percent love",
    percent_result: "📊 {what}: {value}%",
    ship_needMore: "I need at least 2 people in the chat.",
    ship_result: "💘 {a} + {b} = {value}% compatibility",
    choose_needMore: "Give me at least two options separated by commas.",
    choose_result: "👉 {choice}",
    rps_invalid: "Choose: rock, paper or scissors.",
    rps_result: "✊✋✌️ You: {user} | Bot: {bot} → {result}",
    rps_win: "you won", rps_lose: "you lost", rps_tie: "tie",
    marry_noTarget: "Mention someone. Ex: /marry @user",
    marry_self: "You can't marry yourself, haha.",
    marry_alreadyMarried: "You're already married. Divorce first with /divorce.",
    marry_targetMarried: "{target} is already married to someone.",
    marry_married: "💍 {proposer} and {target} got married!",
    marry_proposed: "💌 {proposer} proposed to {target}. To accept, {target} types /marry mentioning {proposer}.",
    divorce_notMarried: "You're not married to anyone.",
    divorce_done: "💔 {user} got divorced.",
    marriage_single: "You're not married to anyone.",
    marriage_married: "💍 You're married to {partner}.",
    tts_needText: "Write the text after the command. Ex: /tts hello",
    tts_error: "Couldn't generate the audio: {error}",
    langset_usage: "Use /langset es, /langset en or /langset ru",
    langset_done: "Language changed to {lang}.",
    trasl_usage: "Use /trasl es, en or ru followed by the text. Ex: /trasl en hola que tal",
    trasl_error: "Couldn't translate the text, try again.",
  },
  ru: {
    horoscope_notRecognized: "Знак не распознан. Варианты: {options}",
    horoscope_header: "{sign} — {date}",
    roll_result: "🎲 Выпало {a} и {b} (всего: {total})",
    dice_result: "🎲 Кубик на {sides} граней: {result}",
    coin_heads: "🪙 Орёл",
    coin_tails: "🪙 Решка",
    eightball_noQuestion: "Сначала задай вопрос.",
    percent_prompt: "Скажи, что измерить. Пример: /percent любовь",
    percent_result: "📊 {what}: {value}%",
    ship_needMore: "Нужно хотя бы 2 человека в чате.",
    ship_result: "💘 {a} + {b} = {value}% совместимости",
    choose_needMore: "Дай хотя бы два варианта, разделённых запятой.",
    choose_result: "👉 {choice}",
    rps_invalid: "Выбери: камень, ножницы или бумага.",
    rps_result: "✊✋✌️ Ты: {user} | Бот: {bot} → {result}",
    rps_win: "ты выиграл(а)", rps_lose: "ты проиграл(а)", rps_tie: "ничья",
    marry_noTarget: "Упомяни кого-то. Пример: /marry @пользователь",
    marry_self: "Нельзя жениться на самом себе, ха-ха.",
    marry_alreadyMarried: "Ты уже в браке. Сначала разведись с помощью /divorce.",
    marry_targetMarried: "{target} уже состоит в браке с кем-то.",
    marry_married: "💍 {proposer} и {target} поженились!",
    marry_proposed: "💌 {proposer} сделал(а) предложение {target}. Чтобы принять, {target} пишет /marry, упоминая {proposer}.",
    divorce_notMarried: "Ты не в браке ни с кем.",
    divorce_done: "💔 {user} развелся(лась).",
    marriage_single: "Ты не в браке ни с кем.",
    marriage_married: "💍 Ты в браке с {partner}.",
    tts_needText: "Напиши текст после команды. Пример: /tts привет",
    tts_error: "Не удалось создать аудио: {error}",
    langset_usage: "Используй /langset es, /langset en или /langset ru",
    langset_done: "Язык изменён на {lang}.",
    trasl_usage: "Используй /trasl es, en или ru, а затем текст. Пример: /trasl en hola que tal",
    trasl_error: "Не удалось перевести текст, попробуй снова.",
  },
};

/**
 * @param {string} lang  "es" | "en" | "ru"
 * @param {string} key
 * @param {object} [vars]  valores para reemplazar {placeholders}
 */
function t(lang, key, vars) {
  const dict = STRINGS[lang] || STRINGS.es;
  let template = dict[key] || STRINGS.es[key] || key;
  if (vars) {
    for (const [k, v] of Object.entries(vars)) {
      template = template.split(`{${k}}`).join(v);
    }
  }
  return template;
}

module.exports = { t, SUPPORTED, SIGN_NAMES, HOROSCOPE_PHRASES, EIGHTBALL_ANSWERS, RPS_NAMES };
