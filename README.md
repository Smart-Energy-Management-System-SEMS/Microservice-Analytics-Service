# Microservice-Analytics-Service

Analytics microservice for SEMS (FastAPI + MongoDB + Kafka) with DDD architecture.

## Required environment variables

Base template in `.env.example`:

```env
PORT=8080
CONFIG_SERVICE_URL=http://config-service:8090
KAFKA_BROKERS=kafka:9092
KAFKA_SECURITY_PROTOCOL=
KAFKA_SASL_MECHANISM=
KAFKA_USERNAME=
KAFKA_PASSWORD=
KAFKA_TOPIC_ENERGY_EVENTS=energy.events
KAFKA_TOPIC_ANALYTICS_EVENTS=analytics.events
KAFKA_CONSUMED_TOPICS=["energy.events"]
KAFKA_CONSUMED_EVENT_TYPES=["energy.consumption.recorded"]
DATABASE_URL=
MONGODB_URI=
ENVIRONMENT=production
```

Notes:
- Default container setup: if this API and Kafka run in Docker on the same network, use `KAFKA_BROKERS=kafka:9092`.
- If you run this API outside Docker, point `KAFKA_BROKERS` to a reachable broker hostname, not `localhost`.
- For Azure Event Hubs over Kafka, use your external namespace host and `SASL_SSL`.

## Kafka/Event Hubs contract

- Analytics consumes only from `energy.events`.
- Analytics filters by `eventType` and processes only:
  - `energy.consumption.recorded`
- Analytics routes by `eventType`; the physical topic is only the grouped transport channel.
- Analytics publishes only `analytics.*` events to `analytics.events`.
- `billing.events` remains the only valid physical topic for future `billing.*` events, but this service does not emit any `billing.*` event today.
- Published messages use the standard envelope:

```json
{
  "eventId": "7df2fb42-b7bc-4f55-8fc0-5f75539c8948",
  "eventType": "analytics.anomaly.detected",
  "occurredAt": "2026-06-12T22:30:00+00:00",
  "data": {}
}
```

## Config resolved from Config Service

This service consumes:

- `GET /api/v1/config/services`
- `GET /api/v1/config/services/{serviceName}`
- `GET /api/v1/config/kafka`

If Config Service is unavailable, local defaults are used as fallback.

## Health check

Public and no-auth:

- `GET /api/v1/analytics/health`
- `GET /api/v1/health`

## Main endpoints

- `GET /api/v1/analytics/device-identifications/user/{user_id}`
- `POST /api/v1/analytics/device-identifications`
- `GET /api/v1/analytics/bill-predictions/user/{user_id}`
- `POST /api/v1/analytics/bill-predictions`
- `GET /api/v1/analytics/recommendations/user/{user_id}`
- `POST /api/v1/analytics/recommendations`
- `PATCH /api/v1/analytics/recommendations/{recommendation_id}/apply`
- `GET /api/v1/analytics/anomalies/user/{user_id}`
- `POST /api/v1/analytics/anomalies`
- `PATCH /api/v1/analytics/anomalies/{anomaly_id}/resolve`
- `GET /api/v1/analytics/consumption-rankings/user/{user_id}`
- `POST /api/v1/analytics/consumption-rankings`

## Run local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Adjust .env for local dependencies (Config Service, MongoDB, Kafka).
# Important: this template defaults to container mode with kafka:9092.
# For Event Hubs/Kafka, replace it with your namespace hostname and SASL settings.
uvicorn main:app --host 0.0.0.0 --port $env:PORT --reload
```

## Build Docker image

```powershell
docker build -t sems-analytics-service:latest .
```

## Run Docker container

```powershell
docker run --rm -p 8080:8080 `
  --env-file .env `
  -e PORT=8080 `
  sems-analytics-service:latest
```

## Azure Container Apps deployment guide

```powershell
# 1) Variables base
$RG="sems-rg"
$LOC="eastus"
$ENV="sems-aca-env"
$ACR="semsacr"
$APP="analytics-service"
$IMAGE="$ACR.azurecr.io/analytics-service:latest"

# 2) Resource group + ACR + ACA environment
az group create --name $RG --location $LOC
az acr create --name $ACR --resource-group $RG --sku Basic
az containerapp env create --name $ENV --resource-group $RG --location $LOC

# 3) Build and push image
az acr build --registry $ACR --image analytics-service:latest .

# 4) Deploy Container App
az containerapp create `
  --name $APP `
  --resource-group $RG `
  --environment $ENV `
  --image $IMAGE `
  --target-port 8080 `
  --ingress external `
  --env-vars `
    PORT=8080 `
    CONFIG_SERVICE_URL=<https://config-service-url> `
    KAFKA_BROKERS=<namespace>.servicebus.windows.net:9093 `
    KAFKA_SECURITY_PROTOCOL=SASL_SSL `
    KAFKA_SASL_MECHANISM=PLAIN `
    KAFKA_USERNAME=\$ConnectionString `
    KAFKA_PASSWORD=<event-hubs-connection-string> `
    KAFKA_TOPIC_ENERGY_EVENTS=energy.events `
    KAFKA_TOPIC_ANALYTICS_EVENTS=analytics.events `
    KAFKA_CONSUMED_TOPICS='["energy.events"]' `
    KAFKA_CONSUMED_EVENT_TYPES='["energy.consumption.recorded"]' `
    MONGODB_URI=<mongodb-connection-string> `
    ENVIRONMENT=production
```

Validation:
- `GET /api/v1/health`
- Existing APIs under `/api/v1/analytics/*`

## Notes about auth

This microservice does not enforce JWT by itself. Auth is expected to be handled by API Gateway.
