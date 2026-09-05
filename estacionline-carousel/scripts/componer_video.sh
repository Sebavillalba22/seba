#!/bin/bash
# Compone un video dentro del marco de una placa ya renderizada.
# Uso: ./componer_video.sh slide4.png video.mp4 X Y ANCHO ALTO salida.mp4
# X/Y/ANCHO/ALTO salen de medir_marco.py
set -e
PLACA=$1; VIDEO=$2; X=$3; Y=$4; W=$5; H=$6; OUT=$7
ffmpeg -y -loglevel error -loop 1 -i "$PLACA" -i "$VIDEO" \
  -filter_complex "[0:v]scale=1080:1350,setsar=1[bg];[1:v]scale=${W}:${H},setsar=1[v];[bg][v]overlay=${X}:${Y}[out]" \
  -map "[out]" -map 1:a? -c:v libx264 -pix_fmt yuv420p -crf 20 -preset medium \
  -c:a aac -b:a 128k -shortest -movflags +faststart "$OUT"
echo "listo: $OUT"
