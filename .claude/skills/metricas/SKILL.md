---
name: metricas
description: Usa esta skill cuando el usuario pida sus números, estadísticas o métricas de Instagram (@estacionline), de la web estacionline.com o de su comunidad — "cómo venimos", "pasame los números", "métricas", "seguidores", "cuánto rindió". Jala los datos reales, actualiza vault/outputs/metricas.md (lo que lee el HUD) y resume en 3 líneas con el número que más cambió primero.
---

# metricas — jala tus números y los resume

Una skill, un propósito: **traer las métricas reales y dejarlas en el vault**.
Nunca inventar números: si una fuente falla, se dice y se marca `s/d`.

## Fuentes de datos

1. **Instagram (@estacionline)** — API Graph con las credenciales ya
   configuradas en `jarvis-haz-lo-tuyo/instagram.json`
   (`{username, ig_user_id, page_id, access_token}`). Con `urllib` (stdlib,
   como los demás scripts del repo):
   - Seguidores: `GET https://graph.facebook.com/v21.0/{ig_user_id}?fields=followers_count,media_count&access_token=…`
   - Interacciones 7 días: `GET /{ig_user_id}/media?fields=like_count,comments_count,timestamp&limit=25`
     y sumar likes+comentarios de los posts de los últimos 7 días.
   - Vistas/alcance 7 días: `GET /{ig_user_id}/insights?metric=views&period=day&since=…&until=…`
     (si la API rechaza `views`, probar `reach`; si tampoco, marcar `s/d`).
2. **Web estacionline.com** (opcional, si el usuario lo pide): posts
   publicados en la semana vía la REST API de WordPress con
   `jarvis-haz-lo-tuyo/wordpress.json`.
3. Si no hay credenciales a mano o la API falla, preguntar los números al
   usuario **o** marcar `s/d` — jamás rellenar con datos de ejemplo.

## Salida obligatoria: `vault/outputs/metricas.md`

Formato EXACTO (el HUD lo parsea — números planos, sin puntos de miles;
`serie7` = hasta 7 valores de más viejo a más nuevo, el de hoy al final):

```
# Métricas Estacionline
actualizado: 2026-08-19 17:00

## Seguidores IG
actual: 12480
serie7: 12100 12180 12220 12300 12350 12420 12480

## Vistas 7d
actual: 45200
serie7: 39800 41200 40100 42700 43900 44800 45200

## Interacciones 7d
actual: 1830
serie7: 1500 1540 1610 1650 1700 1780 1830
```

Cómo mantener `serie7`: leer el `metricas.md` anterior, correr la serie una
posición y agregar el valor de hoy al final (máximo 7). Si es la primera
corrida, la serie arranca con un solo valor. Si una métrica vino `s/d`,
conservar el último valor conocido y agregar debajo `nota: <qué falló>`.

Además, **registrar el histórico completo**: agregar una línea
`2026-08-19 17:00 | seguidores 12480 | vistas 45200 | interacciones 1830`
al final de `vault/raw/metricas-historial.md` (crearlo si no existe).

## Al correr (protocolo HUD)

En `vault/outputs/estado-skills.md`: al empezar, poner la línea de
`metricas` en `corriendo`; al terminar, volver a `inactiva`, sumar 1 a
`hoy:`, poner `ultima: HH:MM` y actualizar la línea `actualizado:`.
Si `actualizado:` era de otro día, resetear antes todos los `hoy:` a 0.

## Respuesta al usuario

Resumir en **3 líneas**, el número que más cambió primero. Ejemplo de tono:
"Interacciones +18% esta semana (1830), el carrusel de obras empujó todo.
Seguidores 12480 (+60 en 7 días). Vistas estables en 45200."
