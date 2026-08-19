---
name: metricas
description: Usa esta skill cuando el usuario pida sus números, estadísticas o métricas de Instagram (@estacionline), de la web estacionline.com o de su comunidad — "cómo venimos", "pasame los números", "métricas", "seguidores", "cuánto rindió". Jala los datos reales, actualiza vault/outputs/metricas.md (lo que lee el HUD) y resume en 3 líneas con el número que más cambió primero.
---

# metricas — jala tus números y los resume

Una skill, un propósito: **traer las métricas reales y dejarlas en el vault**.
Nunca inventar números: si una fuente falla, se dice y queda marcado.

## Cómo correrla

```bash
python3 scripts/metricas.py
```

El script hace todo: lee las credenciales, pega a la API Graph, actualiza
`vault/outputs/metricas.md` manteniendo la serie de 7 días, agrega la línea al
histórico en `vault/raw/metricas-historial.md`, mueve el estado en
`vault/outputs/estado-skills.md` y devuelve el resumen ya ordenado por el
número que más cambió.

| Situación | Qué correr |
|---|---|
| Duda de si el token sirve | `python3 scripts/metricas.py --check` |
| Sin credenciales / API caída | `python3 scripts/metricas.py --manual seguidores=12480 vistas=45200 interacciones=1830` |

**No reescribir el `.md` a mano**: el script mantiene la serie (si ya corrió
hoy reemplaza el valor del día, no lo duplica) y el formato que el HUD parsea.

## De dónde salen los números

Credenciales: `jarvis-haz-lo-tuyo/instagram.json`
(`{username, ig_user_id, page_id, access_token}`) o las variables de entorno
`IG_USER_ID` / `IG_ACCESS_TOKEN`.

- **Seguidores**: `followers_count` del perfil.
- **Interacciones 7d**: likes + comentarios de los posts de los últimos 7 días.
- **Vistas 7d**: insights diarios (`views`; si la cuenta no lo habilita, cae a
  `reach` y lo aclara en el archivo).

Si una métrica falla, el script **conserva el último valor conocido** y escribe
`nota:` con el error — el HUD lo muestra. Cuando eso pase, decírselo al usuario
en vez de pasar el número viejo como si fuera de hoy.

Para sumar la web (posts publicados en la semana): REST API de WordPress con
`jarvis-haz-lo-tuyo/wordpress.json`. Solo si el usuario lo pide.

## Formato de `vault/outputs/metricas.md`

Lo genera el script; queda documentado por si hay que leerlo o repararlo:

```
# Métricas Estacionline
actualizado: 2026-08-19 17:00

## Seguidores IG
actual: 12480
serie7: 12100 12180 12220 12300 12350 12420 12480
```

`serie7` = hasta 7 valores, del más viejo al más nuevo. Una sección `##` por
métrica, `nota:` opcional debajo.

## Respuesta al usuario

Las **3 líneas** que devuelve el script, tal cual salen (ya vienen ordenadas
por variación). Si querés, agregá una línea de lectura editorial: qué post o
qué día explica el movimiento.
