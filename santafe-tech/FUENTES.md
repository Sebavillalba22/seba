# Fuentes para el Radar — Santafe.tech

Sí: hay **muchísimas** fuentes para generar contenido. Santa Fe tiene un ecosistema
científico-tecnológico enorme y casi ningún medio lo cubre en serio. Acá están,
organizadas por tipo, con **cómo se automatiza cada una** para el Radar.

**Leyenda de automatización:**
`RSS` = tiene feed, fácil de leer automático · `SCRAPE` = hay que scrapear la web ·
`API` = tiene API/datos abiertos · `SOCIAL` = se sigue por redes · `MAIL` = suscripción a newsletter

> ⚠️ Los dominios son los oficiales; el endpoint exacto del feed (ej. `/feed`, `/rss`)
> hay que verificarlo al conectar cada fuente.

---

## 🔬 Ciencia (CONICET + institutos)

| Fuente | Dónde | Automatización |
|---|---|---|
| CONICET Nacional | conicet.gov.ar (sección noticias) | RSS / SCRAPE |
| CCT CONICET Rosario | santafe-conicet / cctrosario | SCRAPE |
| CCT CONICET Santa Fe | santafe.conicet.gov.ar | SCRAPE |
| IBR (Biología Molecular Rosario) | ibr-conicet.gov.ar | SCRAPE |
| INTEC (Tecnología Química) | intec.gov.ar | SCRAPE |
| CIFASIS (sistemas/señales) | cifasis-conicet.gov.ar | SCRAPE |
| INALI (limnología) | inali.conicet.gov.ar | SCRAPE |
| CONICET Digital (papers) | ri.conicet.gov.ar | API / SCRAPE |

**Papers santafesinos:** SciELO, Google Scholar (alertas por autor/institución), CONICET Digital → `API/MAIL`.

---

## 🎓 Universidades

| Fuente | Dónde | Automatización |
|---|---|---|
| UNL (Litoral) | unl.edu.ar · El Paraninfo | RSS / SCRAPE |
| UNR (Rosario) | unr.edu.ar | RSS / SCRAPE |
| UTN Santa Fe | frsf.utn.edu.ar | SCRAPE |
| UTN Rosario | frro.utn.edu.ar | SCRAPE |
| UCSF (Católica SF) | ucsf.edu.ar | SCRAPE |
| Austral Rosario | austral.edu.ar | SCRAPE |

Casi todas publican investigaciones, premios, convenios y eventos → oro puro para el medio.

---

## 🏛️ Gobierno y datos abiertos

| Fuente | Dónde | Automatización |
|---|---|---|
| Provincia de Santa Fe | santafe.gob.ar (prensa) | RSS / SCRAPE |
| Agencia de Ciencia, Tecnología e Innovación | (dependencia provincial) | SCRAPE |
| Datos abiertos provincia | datos.santafe.gob.ar | API |
| Municipalidad de Rosario | rosario.gob.ar | RSS / SCRAPE |
| Municipalidad de Santa Fe | santafeciudad.gov.ar | SCRAPE |
| Municipalidad de Rafaela | rafaela.gob.ar | SCRAPE |

---

## 📰 Medios locales (para captar la actualidad)

| Fuente | Dónde | Automatización |
|---|---|---|
| La Capital (Rosario) | lacapital.com.ar | RSS |
| El Litoral (Santa Fe) | ellitoral.com | RSS |
| Rosario3 | rosario3.com | RSS |
| Aire de Santa Fe | airedesantafe.com.ar | RSS |
| Diario UNO Santa Fe | unosantafe.com.ar | RSS |

Se usan para detectar temas y **hacer la versión con profundidad/contexto** que ellos no hacen.

---

## 🚀 Polos, clusters e incubadoras

| Fuente | Dónde | Automatización |
|---|---|---|
| Polo Tecnológico Rosario | polotecnologico.net | SCRAPE / SOCIAL |
| Parque Tecnológico Litoral Centro (PTLC) | ptlc.org.ar | SCRAPE |
| Cluster TIC Santa Fe | (web + LinkedIn) | SOCIAL |
| Parque Tecnológico Rafaela | rafaela.gob.ar / web propia | SCRAPE |
| UNL Emprende / UNR Emprende | dentro de las universidades | SCRAPE |

---

## 💼 Empresas del ecosistema

| Fuente | Dónde | Automatización |
|---|---|---|
| Bioceres | bioceres.com.ar (prensa/IR) | RSS / SCRAPE |
| Agrofy / Agrofy News | agrofynews.com | RSS |
| Globant (Rosario) | globant.com (press) | RSS |
| NeuralSoft | neuralsoft.com | SCRAPE / SOCIAL |
| Wiagro, Inventu, Endeev, startups | web + LinkedIn | SOCIAL |

Para empresas, **LinkedIn** suele ser la mejor fuente (anuncios, rondas, contrataciones).

---

## 📅 Eventos y comunidad

| Fuente | Dónde | Automatización |
|---|---|---|
| Eventbrite / Meetup (Santa Fe/Rosario) | eventbrite.com.ar, meetup.com | API / SCRAPE |
| Agendas universitarias | web de cada facultad | SCRAPE |
| Comunidades dev / game / IA | Discord, Instagram, X | SOCIAL |

---

## 🌐 Internacionales (para contexto)

TechCrunch · Wired · The Verge · Ars Technica · MIT Technology Review · IEEE Spectrum
→ todas con **RSS**. Se usan para comparar tendencias globales con lo santafesino.

---

## 🎯 Por dónde arrancar (Radar MVP)

No conectes 100 fuentes de una — es una trampa (mucho ruido). Arrancá con **10-15 de alto valor y fáciles** (las que tienen RSS):

1. La Capital · El Litoral · Rosario3 · Aire (medios, `RSS`)
2. UNL · UNR (universidades)
3. CONICET nacional + CCT Rosario/Santa Fe (ciencia)
4. Provincia de Santa Fe + Rosario (gobierno)
5. Agrofy News + Bioceres (empresas/agtech)
6. TechCrunch/Wired (contexto internacional)

Con eso ya tenés **decenas de señales por día** para que la IA clasifique y el editor elija.

---

## 🔁 Cómo encaja con el Radar

```
FUENTES (esta lista)  →  RECOLECTOR (RSS/scrape/API)  →  IA CLASIFICA
(categoría, ciudad, organización, impacto, prioridad)  →  TABLERO EDITORIAL  →  vos decidís
```

La ventaja competitiva no es tener las fuentes (están ahí para todos): es **procesarlas
con IA y sumarles contexto y profundidad**. Eso es lo que ningún medio santafesino hace hoy.
