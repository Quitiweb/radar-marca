# RadarMarca

Detección de presencia digital, dominios sospechosos y posibles suplantaciones de marca.

> **HuellaMarca** será el módulo de contexto: el mapa de huella digital de la marca.

## Bio corta para GitHub

**RadarMarca detecta dominios sospechosos, presencias digitales y posibles suplantaciones relacionadas con una marca.**

## Tagline

**Vigila tu marca en internet. Detecta presencia, imitaciones y fraude potencial.**

## Qué es RadarMarca

RadarMarca es una herramienta para ayudar a marcas, agencias y equipos de seguridad a encontrar señales de riesgo alrededor de una marca en internet.

El objetivo no es prometer una plataforma gigante desde el día uno, sino resolver un problema real de forma simple:

- descubrir dominios parecidos a una marca
- identificar candidatos sospechosos
- priorizar lo que merece revisión humana
- ofrecer una vista clara y repetible cada vez que se consulta

## Problema que resuelve

Muchas marcas no saben:

- qué dominios parecidos existen
- si alguien está intentando suplantarlas
- si hay typosquatting o phishing potencial
- qué huella digital no controlada tienen en la web

RadarMarca nace para reducir esa búsqueda manual.

## MVP v1

El MVP inicial se centra en lo más directo y vendible:

### Incluye

- entrada por nombre de marca
- entrada por fichero JSON de marcas
- generación de variantes de dominio sospechosas
- scoring básico por similitud
- comprobación DNS básica
- comprobación HTTP básica
- whitelist de dominios conocidos
- snapshots JSON por marca
- informe Markdown por marca
- exportación de resultados en JSON
- CLI local para ejecutar búsquedas rápidas

### No incluye todavía

- crawling profundo
- OCR o análisis visual de logos
- monitorización continua programada
- panel web
- integraciones con email/Slack/Telegram
- IA para clasificación avanzada
- análisis de menciones en redes/plataformas

## Enfoque funcional

### RadarMarca
Motor principal de detección.

Busca y prioriza:
- typosquatting
- dominios con tokens similares
- dominios activos
- señales básicas de riesgo

### HuellaMarca
Módulo futuro de contexto.

Servirá para:
- mapear presencia digital conocida
- comparar presencia legítima vs. sospechosa
- guardar snapshots
- construir informes por marca

## Estructura del proyecto

```text
radar-marca/
├─ README.md
├─ pyproject.toml
├─ .gitignore
├─ src/
│  └─ radar_marca/
│     ├─ __init__.py
│     ├─ cli.py
│     ├─ models.py
│     ├─ scorer.py
│     ├─ scan.py
│     ├─ storage.py
│     ├─ domain_generator.py
│     ├─ resolvers.py
│     └─ report.py
├─ tests/
│  ├─ test_domain_generator.py
│  ├─ test_scan.py
│  ├─ test_scorer.py
│  └─ test_storage.py
└─ examples/
   └─ brands.json
```

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e . pytest
```

## Uso rápido

```bash
radar-marca scan --brand "Acme" --domain acme.com --whitelist acme.es --json
```

Ejemplo con límite de candidatos y guardado de snapshot/informe:

```bash
radar-marca scan --brand "Acme" --domain acme.com --limit 25 --save-snapshot --save-report
```

Ejemplo por fichero:

```bash
radar-marca scan-file --input examples/brands.json --limit 15 --skip-http --save-snapshot --save-report
```

## Salida esperada

El comando devuelve candidatos con campos como:

- `domain`
- `similarity_score`
- `dns_resolves`
- `http_reachable`
- `risk_score`
- `notes`

## Roadmap corto

### v1
- CLI funcional
- scoring inicial
- chequeo DNS/HTTP
- JSON de resultados

### v2
- comparación histórica entre snapshots
- lista blanca persistente por marca
- primeras reglas de clasificación
- salida CSV

### v3
- HuellaMarca
- panel web
- alertas
- análisis de contenido

## Idea comercial inicial

Propuesta simple:

- **200 €/mes**
- revisiones periódicas o bajo demanda
- informe claro con hallazgos priorizados

Eso encaja mejor si el foco principal es:

- detección de suplantaciones
- dominios sospechosos
- fraude potencial

Y como valor secundario:

- visibilidad de presencia digital

## Estado

En construcción. Este repo arranca con la base del MVP técnico.
