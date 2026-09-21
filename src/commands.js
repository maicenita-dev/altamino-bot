// src/commands.js
// Conecta comandos de texto con la lógica pura.

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
