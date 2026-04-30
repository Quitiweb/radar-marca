# RadarMarca

Detección de presencia digital, dominios sospechosos y posibles suplantaciones de marca.

> **HuellaMarca** será el módulo de contexto: el mapa de huella digital de la marca.

## Bio corta para GitHub

**RadarMarca detecta dominios sospechosos, presencias digitales y posibles suplantaciones relacionadas con una marca.**

## Tagline

**Vigila tu marca en internet. Detecta presencia, imitaciones y fraude potencial.**

## Qué es RadarMarca

RadarMarca es una herramienta para ayudar a marcas, agencias y equipos de seguridad a encontrar señales de riesgo alrededor de una marca en internet.

## Estado actual

Ahora mismo el proyecto va por una **v0.4** funcional para trabajo local.

## Qué incluye ya

- persistencia por cliente y marca
- config estable por marca
- generación de variantes de dominio sospechosas
- scoring básico por similitud
- comprobación DNS básica
- comprobación HTTP básica
- whitelist de dominios conocidos
- snapshots JSON por marca
- diff entre snapshots
- ranking de hallazgos nuevos vs ya vistos
- comparación de riesgo: sube / baja / se mantiene
- informe Markdown por marca
- exportación JSON y CSV
- mini dashboard HTML
- visor web local con Flask
- enriquecimiento básico con CT logs, NS, MX, título HTTP y fingerprint simple

## Qué no incluye todavía

- crawling profundo
- OCR o análisis visual de logos
- monitorización continua programada
- alertas automáticas
- integraciones con email/Slack/Telegram
- clasificación avanzada con IA
- análisis de menciones en redes/plataformas

## Enfoque funcional

### RadarMarca
Motor principal de detección.

Busca y prioriza:
- typosquatting
- dominios con tokens similares
- dominios activos
- señales básicas de riesgo
- certificados recientes relacionados

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
│     ├─ history.py
│     ├─ sources.py
│     ├─ webapp.py
│     ├─ domain_generator.py
│     ├─ resolvers.py
│     └─ report.py
├─ tests/
│  ├─ test_domain_generator.py
│  ├─ test_history.py
│  ├─ test_report.py
│  ├─ test_scan.py
│  ├─ test_scorer.py
│  ├─ test_sources.py
│  ├─ test_storage.py
│  └─ test_webapp.py
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

Crear config estable por marca:

```bash
radar-marca init-brand --client demo --brand "Acme" --domain acme.com --whitelist acme.es
```

Escaneo usando la config estable:

```bash
radar-marca scan --client demo --brand "Acme" --use-config --json
```

Escaneo con snapshot, informe, CSV y HTML:

```bash
radar-marca scan --client demo --brand "Acme" --use-config --limit 25 --save-snapshot --save-report --save-csv --save-html
```

Escaneo por fichero:

```bash
radar-marca scan-file --input examples/brands.json --limit 15 --skip-http --save-snapshot --save-report --save-csv --save-html
```

Comparar snapshots:

```bash
radar-marca diff --client demo --brand "Acme"
```

Levantar visor web local:

```bash
radar-marca serve --host 127.0.0.1 --port 5000
```

## Salida esperada

Los resultados incluyen campos como:

- `domain`
- `similarity_score`
- `dns_resolves`
- `http_reachable`
- `risk_score`
- `notes`
- `ns_records`
- `mx_records`
- `title`
- `fingerprint`
- `whois_summary`
- `source_tags`
- `status` en CSV (`new`, `seen`, `current`)

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

## Siguientes pasos

### Entrega visible rápida

- publicar una primera versión visible en `https://radar.quitiweb.com`
- usar **GitHub Pages** para la landing y demo inicial
- añadir **GitHub Actions** para despliegue automático, como en `qw-landing`
- enseñar una demo clara con datos de ejemplo o semirreales

### Producto SaaS

- permitir registro de usuario
- permitir alta de marcas por cliente
- login con Google para pruebas rápidas del master y primeros usuarios
- prueba gratuita inicial
- cobro recurrente de **200 €/mes** si el usuario continúa

### Arquitectura recomendada

- **Frontend / landing**: GitHub Pages
- **Auth**: Supabase Auth o Clerk
- **Base de datos**: Supabase
- **Pagos**: Stripe
- **Backend/API**: Flask/FastAPI o funciones serverless según convenga

### Producto y detección

- snapshots programados
- correlación de títulos, logos y templates
- reglas de clasificación más finas
- conectores de alertas
- más fuentes además de dominios

### Ecosistema

- mantener **RadarMarca** como capa de riesgo y protección
- desarrollar **HuellaMarca** como capa de contexto y visibilidad
- decidir más adelante si HuellaMarca vive como producto independiente o como módulo del panel principal

## Change log

Ver `CHANGELOG.md` para el hilo de iteraciones y decisiones del proyecto.

## Estado

En construcción, pero ya usable como base real de producto técnico.
