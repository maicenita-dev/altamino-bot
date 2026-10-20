#!/data/data/com.termux/files/usr/bin/bash
# Copia de seguridad de data/  (colecciones, catálogos, idiomas...)
# Uso: ./backup.sh           solo si pasaron más de 6 h desde la última
#      ./backup.sh --force   siempre
cd "$HOME/altamino-bot" || exit 1
DEST="$HOME/storage/shared/Download/altamino-backups"
[ -d "$HOME/storage/shared" ] || DEST="$HOME/altamino-backups"
mkdir -p "$DEST"
last=$(ls -t "$DEST"/data-*.tar.gz 2>/dev/null | head -1)
if [ "$1" != "--force" ] && [ -n "$last" ] && [ -z "$(find "$last" -mmin +360)" ]; then
  exit 0
fi
file="$DEST/data-$(date +%Y%m%d-%H%M).tar.gz"
tar -czf "$file" --exclude='data/bot.lock' data && echo "Copia guardada: $file"
ls -t "$DEST"/data-*.tar.gz | tail -n +8 | xargs -r rm --
