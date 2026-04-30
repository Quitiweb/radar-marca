# RadarMarca SaaS MVP

## Objetivo

Pasar de landing + demo técnica a un SaaS mínimo que permita:

1. login con Google
2. crear cuenta de usuario
3. dar de alta una marca
4. activar una prueba inicial
5. convertir después a un plan de 200 €/mes

## Stack recomendado

### Frontend público
- GitHub Pages para landing y demo pública

### App autenticada
- frontend ligero servido aparte o en el mismo dominio con ruta dedicada
- primera opción razonable: HTML/JS sencillo o app pequeña posterior

### Auth
- Supabase Auth con Google OAuth

### Base de datos
- Supabase Postgres

### Pagos
- Stripe

### Backend
- primera fase: Supabase + edge/server functions mínimas
- si crece la lógica de escaneo o billing, mover piezas a FastAPI/Flask

## Flujo de usuario deseado

### 1. Registro
- el usuario entra en RadarMarca
- hace login con Google
- se crea perfil interno

### 2. Onboarding
- introduce nombre de la marca
- introduce dominio principal
- opcionalmente lista blanca inicial
- selecciona objetivo principal: fraude, suplantación, visibilidad

### 3. Prueba inicial
- se crea una cuenta en estado `trialing`
- se permite al menos una marca y un número limitado de scans
- el usuario ve una primera demo real con su marca

### 4. Conversión
- si le encaja, activa suscripción
- pasa a `active`
- pago recurrente de 200 €/mes

## Modelo mínimo de datos

### profiles
Usuario autenticado.

### workspaces
Cuenta o cliente. Al principio puede coincidir con un usuario.

### brands
Marcas dadas de alta.

### brand_domains
Dominios legítimos de cada marca.

### scans
Ejecuciones de escaneo.

### findings
Hallazgos por scan.

### subscriptions
Estado comercial: trialing, active, past_due, canceled.

## Decisiones prácticas

- Empezar simple: un usuario puede crear su propio workspace.
- Más adelante: varios usuarios por workspace.
- Stripe no se necesita para la primera demo autenticada si primero validamos login + alta de marca.
- El backend de scans puede seguir corriendo fuera del frontend y escribir resultados en DB.

## Fases recomendadas

### Fase 1
- login con Google
- perfil
- alta de una marca
- panel placeholder con estado de trial

### Fase 2
- crear scans desde la app
- guardar resultados en base de datos
- mostrar histórico simple

### Fase 3
- Stripe
- límites de plan
- multiusuario

## Riesgos a evitar

- meter Stripe antes de validar onboarding
- construir backend complejo antes de tener flujo de alta claro
- mezclar landing pública con app interna sin separación conceptual

## Recomendación actual

Siguiente paso real: montar

1. esquema Supabase
2. auth con Google
3. app mínima con onboarding de marca

Eso ya nos deja en una posición muy buena para probar RadarMarca con una cuenta real del master.
