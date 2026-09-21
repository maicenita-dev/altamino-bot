// src/games.js
// Lógica pura de entretenimiento. Cada función devuelve texto listo para mandar.

function randInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function roll() {
  const a = randInt(1, 6);
  const b = randInt(1, 6);
  return `🎲 Sacaste ${a} y ${b} (total: ${a + b})`;
}

function dice(sides = 6) {
  const s = Number.isInteger(sides) && sides >= 2 && sides <= 1000 ? sides : 6;
  return `🎲 Dado de ${s} caras: ${randInt(1, s)}`;
}

function coin() {
  return Math.random() < 0.5 ? "🪙 Cara" : "🪙 Ceca";
}

function eightball(question) {
  const answers = [
    "Sí, sin dudas.", "No cuentes con eso.", "Puede ser.",
    "Mejor no te lo digo ahora.", "Definitivamente sí.",
    "Muy dudoso.", "Pregúntame de nuevo más tarde.", "Absolutamente no.",
  ];
  if (!question || !question.trim()) return "Hacé una pregunta primero.";
  return `🎱 ${answers[randInt(0, answers.length - 1)]}`;
}

function percent(what) {
  if (!what || !what.trim()) return "Decime qué querés medir. Ej: /percent amor";
  return `📊 ${what.trim()}: ${randInt(0, 100)}%`;
}

function ship(members) {
  if (!members || members.length < 2) return "Necesito al menos 2 personas en el chat.";
  const shuffled = [...members].sort(() => Math.random() - 0.5);
  const [a, b] = shuffled;
  return `💘 ${a.nickname} + ${b.nickname} = ${randInt(0, 100)}% de compatibilidad`;
}

function choose(raw) {
  const options = raw
    .split(/,|\s+(?:o|or)\s+/i)
    .map((s) => s.trim())
    .filter(Boolean);
  if (options.length < 2) return "Dame al menos dos opciones separadas por coma.";
  return `👉 ${options[randInt(0, options.length - 1)]}`;
}

const RPS = { piedra: 0, rock: 0, "🪨": 0, tijera: 1, scissors: 1, "✂️": 1, papel: 2, paper: 2, "📄": 2 };

function rps(choiceRaw) {
  const user = RPS[choiceRaw.toLowerCase().trim()];
  if (user === undefined) return "Elegí: piedra, papel o tijera.";
  const bot = randInt(0, 2);
  const names = ["piedra", "papel", "tijera"];
  let result;
  if (user === bot) result = "empate";
  else if ((user + 1) % 3 === bot) result = "perdiste";
  else result = "ganaste";
  return `✊✋✌️ Vos: ${names[user]} | Bot: ${names[bot]} → ${result}`;
}

module.exports = { roll, dice, coin, eightball, percent, ship, choose, rps };
