from fastapi import APIRouter, Depends

from analytics.application.commandservices.bill_prediction_command_service import BillPredictionCommandService
from analytics.application.queryservices.bill_prediction_query_service import BillPredictionQueryService
from analytics.domain.model.queries.get_by_user_query import GetByUserQuery
from analytics.interfaces.rest.controllers.dependencies import (
    get_bill_prediction_command_service,
    get_bill_prediction_query_service,
)
from analytics.interfaces.rest.resources.bill_prediction_resource import CreateBillPredictionRequest, BillPredictionResponse
from analytics.interfaces.rest.transform import bill_prediction_transform as transform

router = APIRouter(prefix="/bill-predictions", tags=["Bill Predictions"])


@router.get("/user/{user_id}", response_model=list[BillPredictionResponse])
async def get_bill_predictions_by_user(
    user_id: str,
    query_service: BillPredictionQueryService = Depends(get_bill_prediction_query_service),
) -> list[BillPredictionResponse]:
    predictions = await query_service.get_by_user(GetByUserQuery(user_id=user_id))
    return [transform.entity_to_response(prediction) for prediction in predictions]


@router.post("", response_model=BillPredictionResponse, status_code=201)
async def create_bill_prediction(
    request: CreateBillPredictionRequest,
    command_service: BillPredictionCommandService = Depends(get_bill_prediction_command_service),
) -> BillPredictionResponse:
    prediction = await command_service.create(transform.request_to_command(request))
    return transform.entity_to_response(prediction)
