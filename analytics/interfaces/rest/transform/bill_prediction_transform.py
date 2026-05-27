from dataclasses import asdict

from analytics.domain.model.commands.create_bill_prediction_command import CreateBillPredictionCommand
from analytics.domain.model.entities.bill_prediction import BillPrediction
from analytics.interfaces.rest.resources.bill_prediction_resource import CreateBillPredictionRequest, BillPredictionResponse


def request_to_command(request: CreateBillPredictionRequest) -> CreateBillPredictionCommand:
    return CreateBillPredictionCommand(**request.model_dump())


def entity_to_response(entity: BillPrediction) -> BillPredictionResponse:
    return BillPredictionResponse(**asdict(entity))
