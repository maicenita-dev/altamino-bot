// src/ask.js
// Genera respuestas de IA para /ask usando una API gratuita, sin
// necesidad de cuenta ni API key. Al no ser un servicio pago, puede
// tener límites de uso o caerse en algún momento.

async function askAI(prompt) {
  const clean = (prompt || "").trim();
  if (!clean) return { ok: false };

  const url = `https://text.pollinations.ai/${encodeURIComponent(clean)}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`status ${res.status}`);
  }
  const text = (await res.text()).trim();
  return { ok: true, text };
}

module.exports = { askAI };
