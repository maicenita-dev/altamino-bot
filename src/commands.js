// src/commands.js
// Conecta comandos de texto con la lógica pura. No sabe nada de cómo
// se manda el mensaje: eso lo hace el "ctx" que le pasa el adapter.
//
// ctx esperado (lo arma el adapter, según lo que devuelva la lib de Alx0rr):
//   ctx.args        -> string, todo lo que sigue al comando
//   ctx.author       -> { userId, nickname }
//   ctx.members       -> array de { userId, nickname } del chat (para /ship)
//   ctx.mentioned      -> array de { userId, nickname } mencionados (para /marry)
//   ctx.reply(text)     -> async, manda texto
//   ctx.replyAudio(buffer) -> async, manda el buffer como mensaje de voz
//   ctx.replyMedia(buffer, filename) -> async, OPCIONAL, manda un archivo (ej. gif)

const { getHoroscope } = require("./horoscope");
const games = require("./games");
const { textToSpeech } = require("./tts");
const marriage = require("./marriage");
const { getGif } = require("./gifs");
const { askAI } = require("./ask");
const { BOT_NAME } = require("./config");
const { t, SIGN_NAMES, HOROSCOPE_PHRASES, EIGHTBALL_ANSWERS, RPS_NAMES } = require("./i18n");
const { getLang, setLang, SUPPORTED: LANGS } = require("./lang");
const { translateText } = require("./translate");

// Intenta mandar el gif de una reacción. Si no existe el archivo o el
// adapter no soporta replyMedia todavía, no hace nada (silencioso).
async function sendGif(ctx, key) {
  if (typeof ctx.replyMedia !== "function") return;
  const gif = getGif(key);
  if (gif.ok) await ctx.replyMedia(gif.buffer, gif.filename);
}

const commands = {
  "/ping": async (ctx) => {
    const lang = getLang(ctx.author.userId);
    return ctx.reply(t(lang, "ping_result"));
  },

  "/horoscopo": async (ctx) => {
    const lang = getLang(ctx.author.userId);
    const result = getHoroscope(ctx.args);
    if (!result.ok) {
      const options = result.signKeys.map((k) => SIGN_NAMES[lang][k]).join(", ");
      return ctx.reply(t(lang, "horoscope_notRecognized", { options }));
    }
    const signName = SIGN_NAMES[lang][result.signKey];
    const phrase = HOROSCOPE_PHRASES[lang][result.phraseIndex];
    const header = t(lang, "horoscope_header", { sign: signName, date: result.dateISO });
    await ctx.reply(`${header}\n\n${phrase}`);
    return sendGif(ctx, "horoscopo");
  },

  "/roll": async (ctx) => {
    const lang = getLang(ctx.author.userId);
    const { a, b, total } = games.roll();
    await ctx.reply(t(lang, "roll_result", { a, b, total }));
    return sendGif(ctx, "roll");
  },

  "/dice": async (ctx) => {
    const lang = getLang(ctx.author.userId);
    const { sides, result } = games.dice(parseInt(ctx.args, 10));
    await ctx.reply(t(lang, "dice_result", { sides, result }));
    return sendGif(ctx, "dice");
  },

  "/flip": async (ctx) => {
    const lang = getLang(ctx.author.userId);
    const { result } = games.coin();
    await ctx.reply(t(lang, result === "heads" ? "coin_heads" : "coin_tails"));
    return sendGif(ctx, "flip");
  },

  "/8ball": async (ctx) => {
    const lang = getLang(ctx.author.userId);
    const result = games.eightball(ctx.args);
    if (!result.ok) return ctx.reply(t(lang, "eightball_noQuestion"));
    await ctx.reply(`🎱 ${EIGHTBALL_ANSWERS[lang][result.answerIndex]}`);
    return sendGif(ctx, "eightball");
  },

  "/percent": async (ctx) => {
    const lang = getLang(ctx.author.userId);
    const result = games.percent(ctx.args);
    if (!result.ok) return ctx.reply(t(lang, "percent_prompt"));
    return ctx.reply(t(lang, "percent_result", { what: result.what, value: result.value }));
  },

  "/ship": async (ctx) => {
    const lang = getLang(ctx.author.userId);
    const result = games.ship(ctx.members);
    if (!result.ok) return ctx.reply(t(lang, "ship_needMore"));
    await ctx.reply(t(lang, "ship_result", { a: result.a, b: result.b, value: result.value }));
    return sendGif(ctx, "ship");
  },

  "/choose": async (ctx) => {
    const lang = getLang(ctx.author.userId);
    const result = games.choose(ctx.args);
    if (!result.ok) return ctx.reply(t(lang, "choose_needMore"));
    return ctx.reply(t(lang, "choose_result", { choice: result.choice }));
  },

  "/rps": async (ctx) => {
    const lang = getLang(ctx.author.userId);
    const result = games.rps(ctx.args);
    if (!result.ok) return ctx.reply(t(lang, "rps_invalid"));
    const names = RPS_NAMES[lang];
    await ctx.reply(
      t(lang, "rps_result", {
        user: names[result.userChoice],
        bot: names[result.botChoice],
        result: t(lang, `rps_${result.result}`),
      })
    );
    return sendGif(ctx, "rps");
  },

  "/marry": async (ctx) => {
    const lang = getLang(ctx.author.userId);
    const target = ctx.mentioned && ctx.mentioned[0];
    const result = marriage.propose(ctx.author, target);

    const byStatus = {
      noTarget: () => t(lang, "marry_noTarget"),
      self: () => t(lang, "marry_self"),
      alreadyMarried: () => t(lang, "marry_alreadyMarried"),
      targetMarried: () => t(lang, "marry_targetMarried", { target: result.target }),
      married: () => t(lang, "marry_married", { proposer: result.proposer, target: result.target }),
      proposed: () => t(lang, "marry_proposed", { proposer: result.proposer, target: result.target }),
    };

    await ctx.reply(byStatus[result.status]());
    if (result.status === "married") return sendGif(ctx, "marry");
  },

  "/divorce": async (ctx) => {
    const lang = getLang(ctx.author.userId);
    const result = marriage.divorce(ctx.author);
    if (result.status === "notMarried") return ctx.reply(t(lang, "divorce_notMarried"));
    await ctx.reply(t(lang, "divorce_done", { user: result.user }));
    return sendGif(ctx, "divorce");
  },

  "/marriage": async (ctx) => {
    const lang = getLang(ctx.author.userId);
    const result = marriage.status(ctx.author, ctx.members);
    if (!result.married) return ctx.reply(t(lang, "marriage_single"));
    return ctx.reply(t(lang, "marriage_married", { partner: result.partner || "?" }));
  },

  "/tts": async (ctx) => {
    const lang = getLang(ctx.author.userId);
    if (!ctx.args || !ctx.args.trim()) return ctx.reply(t(lang, "tts_needText"));
    try {
      const audio = await textToSpeech(ctx.args);
      return ctx.replyAudio(audio);
    } catch (err) {
      return ctx.reply(t(lang, "tts_error", { error: err.message }));
    }
  },

  "/ask": async (ctx) => {
    const lang = getLang(ctx.author.userId);
    if (!ctx.args || !ctx.args.trim()) return ctx.reply(t(lang, "ask_needQuestion"));
    try {
      const result = await askAI(ctx.args);
      if (!result.ok) return ctx.reply(t(lang, "ask_needQuestion"));
      return ctx.reply(result.text);
    } catch {
      return ctx.reply(t(lang, "ask_error"));
    }
  },

  "/langset": async (ctx) => {
    const requested = (ctx.args || "").trim().toLowerCase();
    if (!LANGS.includes(requested)) {
      const lang = getLang(ctx.author.userId);
      return ctx.reply(t(lang, "langset_usage"));
    }
    setLang(ctx.author.userId, requested);
    return ctx.reply(t(requested, "langset_done", { lang: requested }));
  },

  "/trasl": async (ctx) => {
    const lang = getLang(ctx.author.userId);
    const [target, ...rest] = (ctx.args || "").trim().split(/\s+/);
    const text = rest.join(" ");
    if (!LANGS.includes(target) || !text) {
      return ctx.reply(t(lang, "trasl_usage"));
    }
    try {
      const translated = await translateText(text, target);
      return ctx.reply(translated);
    } catch {
      return ctx.reply(t(lang, "trasl_error"));
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

/**
 * Mensaje de presentación de Emma. Pensado para llamarse cuando el
 * adapter detecte que el bot se unió a un chat/comunidad nueva —
 * eso depende de un evento que todavía no tenemos de la librería
 * de AltAmino, así que por ahora queda lista para conectar.
 *
 * @param {string} lang
 */
function getIntroMessage(lang) {
  return t(lang, "intro_message", { name: BOT_NAME });
}

module.exports = { commands, handleMessage, getIntroMessage };
