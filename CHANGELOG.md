# CHANGELOG

Este archivo sirve para mantener el hilo entre iteraciones de RadarMarca.

## v0.5.0

- arquitectura documentada para SaaS MVP en `docs/saas-mvp.md`
- esquema inicial de Supabase en `supabase/schema.sql`
- notas de arranque para Supabase en `supabase/README.md`
- app preview estática en `site/app.html`
- la landing enlaza ya a la preview de app

## v0.4.2

- demo pública estática en `site/demo.html`
- página simple de solicitud de prueba en `site/interest.html`
- CTA más claro y recorrido comercial mejor resuelto en la landing
- pequeños ajustes visuales para enseñar más sensación de producto

## v0.4.1

- landing estática inicial para `radar.quitiweb.com`
- estilos y copy de primera versión comercial
- workflow de GitHub Actions para desplegar GitHub Pages desde `site/`
- documentación actualizada para Pages y demo pública

## v0.4.0

- persistencia por cliente y marca
- config estable por marca
- snapshots por marca
- diff entre snapshots
- ranking de hallazgos nuevos vs ya vistos
- comparación de riesgo: sube / baja / se mantiene
- exportación JSON / CSV / HTML
- visor web local con Flask
- enriquecimiento básico con CT logs, NS, MX, título HTTP, fingerprint simple y resumen WHOIS
- subida del proyecto a GitHub con historial de commits operativo

## v0.3.0

- comparación histórica entre snapshots
- export CSV
- mini dashboard HTML
- comando `diff`
- primeros informes con hallazgos nuevos y ya vistos

## v0.2.0

- whitelist de dominios conocidos
- snapshots JSON por marca
- informe Markdown por marca
- escaneo por fichero JSON
- entorno virtual `.venv` preparado e instalación local de dependencias

## v0.1.0

- bootstrap del proyecto
- README inicial
- estructura base del repo
- CLI local
- generación de dominios candidatos
- scoring básico
- comprobación DNS/HTTP
- salida JSON

## Próximos hitos

### Hito: radar.quitiweb.com
- landing pública inicial
- demo visible
- despliegue con GitHub Pages
- automatización con GitHub Actions

### Hito: primeras cuentas reales
- login con Google
- alta de usuario y marcas
- prueba gratuita
- pago recurrente de 200 €/mes

### Hito: ecosistema RadarMarca + HuellaMarca
- RadarMarca como capa de protección y riesgo
- HuellaMarca como capa de contexto y visibilidad
- decidir si ambos viven separados o bajo una misma plataforma
