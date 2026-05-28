# Microservice-Analytics-Service

Analytics microservice for SEMS (FastAPI + MongoDB + Kafka) with DDD architecture.

## Local integration targets

- Config Service: `http://localhost:8090`
- API Gateway: `http://localhost:8081`
- This service base URL: `http://localhost:8004`
- Route prefix: `/api/v1/analytics`

## Minimal local env

Use `.env.example` as base:

```env
PORT=8004
CONFIG_SERVICE_URL=http://localhost:8090
CONFIG_SERVICE_TIMEOUT_SECONDS=3.0
SERVICE_NAME=analytics-service
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]

MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>/<database>?retryWrites=true&w=majority
MONGODB_DATABASE=sems_analytics_db

# Optional only if Kafka auth is required
KAFKA_SASL_USERNAME=<kafka-username>
KAFKA_SASL_PASSWORD=<kafka-password>
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
uvicorn main:app --host 0.0.0.0 --port 8004 --reload
```

## Local dependencies

- MongoDB Atlas or local MongoDB reachable from `MONGODB_URI`
- Kafka broker on `localhost:9092` if Kafka is enabled

## Notes about auth

This microservice does not enforce JWT by itself. Auth is expected to be handled by API Gateway.

