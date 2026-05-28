# Microservice-Analytics-Service

Microservicio de Analytics para SEMS, construido con Python, FastAPI, MongoDB y Kafka, siguiendo arquitectura DDD.

## Objetivo de esta versión

Este servicio ahora está preparado para consumir configuración centralizada desde un **Config Service** y reducir configuración hardcodeada/repetida.

## Variables de entorno del microservicio

Solo se mantienen variables propias de despliegue o sensibles:

```env
PORT=8004
CONFIG_SERVICE_URL=http://localhost:8000
CONFIG_SERVICE_TIMEOUT_SECONDS=3.0
SERVICE_NAME=analytics-service

MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>/<database>?retryWrites=true&w=majority
MONGODB_DATABASE=sems_analytics_db

# Opcional: solo si Kafka usa autenticacion
KAFKA_SASL_USERNAME=<kafka-username>
KAFKA_SASL_PASSWORD=<kafka-password>
```

## Configuración que ahora viene desde Config Service

El microservicio consulta:

- `GET /api/v1/config/services`
- `GET /api/v1/config/kafka`
- `GET /api/v1/config/{service-name}`

Y usa esa configuración para:

- `api_prefix` (por defecto: `/api/v1/analytics`)
- Kafka:
  - `bootstrap servers`
  - `consumer group`
  - `enabled`
  - `security protocol`
  - `sasl mechanism`
  - tópicos de consumo/producción
- Reglas de negocio compartidas:
  - `default_tariff_per_kwh`
  - `default_currency`
  - `anomaly_threshold_percentage`
- CORS (`allowed_origins`)

Si Config Service no responde, el servicio usa defaults locales seguros (fallback) y sigue operativo.

## Endpoints (sin cambios de contrato)

Base path (configurable): `/api/v1/analytics`

- `GET /health`
- `GET /device-identifications/user/{user_id}`
- `POST /device-identifications`
- `GET /bill-predictions/user/{user_id}`
- `POST /bill-predictions`
- `GET /recommendations/user/{user_id}`
- `POST /recommendations`
- `PATCH /recommendations/{recommendation_id}/apply`
- `GET /anomalies/user/{user_id}`
- `POST /anomalies`
- `PATCH /anomalies/{anomaly_id}/resolve`
- `GET /consumption-rankings/user/{user_id}`
- `POST /consumption-rankings`

## Ejecución local

1. Crear `.env` a partir de `.env.example`.
2. Configurar MongoDB y `CONFIG_SERVICE_URL`.
3. Ejecutar:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8004
```

Health check:

```text
http://localhost:8004/api/v1/analytics/health
```

## Docker local

```powershell
docker compose up --build
```

En Docker Compose, Kafka se levanta localmente para desarrollo y creación de tópicos.

## Azure Container Apps (recomendado)

En ACA, configura:

- Secretos:
  - `MONGODB_URI`
  - `KAFKA_SASL_PASSWORD` (si aplica)
- Variables de entorno:
  - `PORT`
  - `CONFIG_SERVICE_URL` (idealmente URL interna del Config Service en ACA)
  - `SERVICE_NAME=analytics-service`
  - `MONGODB_DATABASE`
  - `KAFKA_SASL_USERNAME` (si aplica)

Recomendaciones:

- Exponer Config Service por red interna del entorno ACA.
- Gestionar secretos con `secretRef`.
- Configurar readiness/liveness apuntando a `/api/v1/analytics/health` (o al `api_prefix` centralizado si cambia).
