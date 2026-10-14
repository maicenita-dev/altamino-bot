# Cómo instalar (Termux)

1. Copiá `src/core/` entero a la carpeta `src/` de tu bot.
2. Copiá los 5 archivos de `src/aa/modules/` a `src/aa/modules/`
   (horoscope.py y tts.py REEMPLAZAN a los que ya tenías).
3. Creá las carpetas `data/`, `res/gifs/`, `res/images/` en la raíz del bot.
4. `pip install -r requirements-extra.txt`
5. Gifs opcionales en `res/gifs/`: horoscopo, roll, flip, 8ball, ship, rps,
   marry, divorce (.gif). Si falta alguno, simplemente no se manda.

Lo único adivinado está en `src/core/ctx.py` (marcado con `# ???`):
nickname del autor, listar miembros del chat y menciones.
Probá /ship y /marry; si alguno falla, mandame el error.
