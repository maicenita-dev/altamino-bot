// src/commands.js
// Conecta comandos de texto con la lógica pura. No sabe nada de cómo
// se manda el mensaje: eso lo hace el "ctx" que le pasa el adapter.
//
// ctx esperado (lo arma el adapter, según lo que devuelva la lib de Alx0rr):
//   ctx.args        -> string, todo lo que sigue al comando
//   ctx.author       -> { userId, nickname }
//   ctx.members       -> array de { userId, nickname } del chat (para /ship)
//   ctx.reply(text)     -> async, manda texto
//   ctx.replyAudio(buffer) -> async, manda el buffer como mensaje de voz

const { getHoroscope } = require("./horoscope");
const games = require("./games");
const { textToSpeech } = require("./tts");

const commands = {
  "/horoscopo": async (ctx) => {
    const result = getHoroscope(ctx.args);
    if (!result.ok) return ctx.reply(result.message);
    return ctx.reply(`${result.sign} — ${result.date}\n\n${result.text}`);
  },

  "/roll": async (ctx) => ctx.reply(games.roll()),
  "/dice": async (ctx) => ctx.reply(games.dice(parseInt(ctx.args, 10))),
  "/flip": async (ctx) => ctx.reply(games.coin()),
  "/8ball": async (ctx) => ctx.reply(games.eightball(ctx.args)),
  "/percent": async (ctx) => ctx.reply(games.percent(ctx.args)),
  "/ship": async (ctx) => ctx.reply(games.ship(ctx.members)),
  "/choose": async (ctx) => ctx.reply(games.choose(ctx.args)),
  "/rps": async (ctx) => ctx.reply(games.rps(ctx.args)),

  "/tts": async (ctx) => {
    if (!ctx.args || !ctx.args.trim()) {
      return ctx.reply("Escribí el texto después del comando. Ej: /tts hola");
    }
    try {
      const audio = await textToSpeech(ctx.args);
      return ctx.replyAudio(audio);
    } catch (err) {
      return ctx.reply(`No pude generar el audio: ${err.message}`);
    }
  },
};

/**
 * @param {string} rawText  contenido completo del mensaje entrante
 * @param {object} ctx      contexto armado por el adapter (sin .args todavía)
 */
async function handleMessage(rawText, ctx) {
  const trimmed = (rawText || "").trim();
  if (!trimmed.startsWith("/")) return false;

  const [cmd, ...rest] = trimmed.split(/\s+/);
  const handler = commands[cmd.toLowerCase()];
  if (!handler) return false;

  await handler({ ...ctx, args: rest.join(" ") });
  return true;
}

module.exports = { commands, handleMessage };
