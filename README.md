# Microservice-Analytics-Service

Analytics Service para Smart Energy Management System construido con Python, FastAPI, MongoDB Atlas, Motor async driver, Kafka, Pydantic y arquitectura DDD.

Este microservicio no usa Machine Learning, AWS, SageMaker, OpenAI ni servicios externos de IA. Toda la analitica se calcula con reglas internas, promedios, umbrales y heuristicas.

## Responsabilidades

- Analitica de consumo energetico.
- Prediccion simple de facturacion basada en reglas.
- Generacion de recomendaciones.
- Deteccion simple de anomalias.
- Rankings de consumo.

## Estructura

```text
analytics/
  application/
    commandservices/
    eventhandlers/
    outboundservices/
    queryservices/
  domain/
    model/
      aggregates/
      commands/
      entities/
      queries/
      valueobjects/
    repositories/
    services/
  infrastructure/
    configuration/
    messaging/kafka/
    persistence/mongodb/
      configuration/
      model/
      repositories/
  interfaces/
    acl/
    rest/
      controllers/
      resources/
      transform/
main.py
```

## Variables de entorno

Copia `.env.example` a `.env` y configura:

```env
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>/<database>?retryWrites=true&w=majority
MONGODB_DATABASE=sems_analytics_db
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_CONSUMER_GROUP=analytics-service-group
```

## Ejecutar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8004
```

## Ejecutar con Docker

El contenedor usa MongoDB Atlas mediante `.env` y levanta Kafka local con Docker Compose.

```powershell
docker compose up --build
```

La API queda disponible en:

```text
http://localhost:8004/api/v1/analytics
```

Health check:

```powershell
curl http://localhost:8004/api/v1/analytics/health
```

Para detener:

```powershell
docker compose down
```

Para limpiar tambien el volumen local de Kafka:

```powershell
docker compose down -v
```

Si el API Gateway corre en Docker y esta conectado a la red `sems-network`, puede enrutar hacia:

```text
http://analytics-service:8004/api/v1/analytics/**
```

Si el API Gateway corre fuera de Docker, puede enrutar hacia:

```text
http://localhost:8004/api/v1/analytics/**
```

## Deploy en Render

Render no sube ni usa la carpeta `.venv`; instala dependencias desde `requirements.txt` o construye la imagen con el `Dockerfile`.

Este repositorio incluye `render.yaml` para crear:

- Un Web Service Docker: `sems-analytics-service`.
- Un Cron Job opcional: `sems-analytics-keep-alive`.

Variables que debes configurar en Render:

```env
MONGODB_URI=mongodb+srv://...
MONGODB_DATABASE=sems_analytics_db
```

Si usas Kafka en produccion, configura un broker externo:

```env
KAFKA_ENABLED=true
KAFKA_BOOTSTRAP_SERVERS=<broker-host>:<broker-port>
```

Para un deploy inicial sin broker Kafka externo, deja:

```env
KAFKA_ENABLED=false
```

Render no ejecuta `docker-compose.yml`; ese archivo es para desarrollo local. En Render se usa `Dockerfile` o runtime Python por servicio.

Para el Cron Job de keep-alive configura:

```env
KEEP_ALIVE_URL=https://<tu-servicio>.onrender.com/api/v1/analytics/health
```

El Cron Job esta programado cada 10 minutos:

```text
*/10 * * * *
```

Nota: los Web Services free de Render pueden dormir tras 15 minutos sin trafico. Los Cron Jobs de Render tienen costo minimo mensual segun la documentacion actual de Render. Tambien puedes usar un monitor externo como UptimeRobot o cron-job.org apuntando al endpoint `/health`.

## Endpoints

Base path:

```text
/api/v1/analytics
```

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

## Kafka

Consume:

- `energy.consumption.recorded`
- `device.registered`
- `device.updated`

Publica:

- `analytics.bill_prediction.generated`
- `analytics.recommendation.generated`
- `analytics.anomaly.detected`
- `analytics.device_identified`
- `analytics.consumption_ranking.generated`

## Colecciones MongoDB

- `device_identification_results`
- `bill_predictions`
- `recommendations`
- `anomalies`
- `consumption_rankings`
