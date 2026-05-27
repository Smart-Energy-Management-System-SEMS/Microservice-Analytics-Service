from dataclasses import asdict

from analytics.domain.model.commands.create_anomaly_command import CreateAnomalyCommand
from analytics.domain.model.entities.anomaly import Anomaly
from analytics.interfaces.rest.resources.anomaly_resource import CreateAnomalyRequest, AnomalyResponse


def request_to_command(request: CreateAnomalyRequest) -> CreateAnomalyCommand:
    return CreateAnomalyCommand(**request.model_dump())


def entity_to_response(entity: Anomaly) -> AnomalyResponse:
    return AnomalyResponse(**asdict(entity))
