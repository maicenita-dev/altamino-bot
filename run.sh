#!/data/data/com.termux/files/usr/bin/bash
# Mantiene el bot corriendo: si se cierra solo (por ejemplo, socket caído), lo reinicia.
cd "$HOME/altamino-bot" || exit 1
trap 'echo; echo "Bot detenido."; exit 0' INT
while true; do
  ./backup.sh
  python main.py
  code=$?
  if [ "$code" -eq 4 ]; then
    echo "Ya hay otra copia del bot corriendo. No se reinicia."
    exit 4
  fi
  echo "El bot se cerró (código $code). Reiniciando en 15 s... (CTRL+C para cancelar)"
  sleep 15
done
