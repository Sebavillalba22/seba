#!/bin/bash
# Inter NO viene en el contenedor. Sin esto, Playwright renderiza con otra
# tipografía y todas las medidas de renglones quedan mal.
set -e
mkdir -p /home/claude/fonts && cd /home/claude/fonts
curl -sL -o inter.zip "https://github.com/rsms/inter/releases/download/v4.0/Inter-4.0.zip"
unzip -o -q inter.zip -d inter
mkdir -p ~/.fonts
for w in Regular Medium SemiBold Bold ExtraBold Black; do
  cp "inter/extras/ttf/Inter-$w.ttf" ~/.fonts/
done
fc-cache -f > /dev/null 2>&1
fc-list | grep -i inter && echo "Inter instalada"
