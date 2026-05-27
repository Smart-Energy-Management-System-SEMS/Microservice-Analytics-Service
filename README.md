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
