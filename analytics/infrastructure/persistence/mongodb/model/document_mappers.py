from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any, Type, TypeVar

from bson import ObjectId

from analytics.domain.model.entities.anomaly import Anomaly
from analytics.domain.model.entities.bill_prediction import BillPrediction
from analytics.domain.model.entities.consumption_ranking import ConsumptionRanking
from analytics.domain.model.entities.device_consumption import DeviceConsumption
from analytics.domain.model.entities.device_identification_result import DeviceIdentificationResult
from analytics.domain.model.entities.recommendation import Recommendation
from analytics.domain.model.valueobjects.ranking_item import RankingItem

T = TypeVar("T")


def _id_to_str(document: dict[str, Any]) -> str | None:
    value = document.get("_id")
    return str(value) if value is not None else None


def _clean_document(data: dict[str, Any]) -> dict[str, Any]:
    document = {key: value for key, value in data.items() if value is not None and key != "id"}
    if data.get("id"):
        document["_id"] = ObjectId(data["id"])
    return document


def dataclass_to_document(entity: Any) -> dict[str, Any]:
    if not is_dataclass(entity):
        raise TypeError("Expected dataclass entity")
    data = asdict(entity)
    return _clean_document(data)


def document_to_device_identification(document: dict[str, Any]) -> DeviceIdentificationResult:
    return DeviceIdentificationResult(
        id=_id_to_str(document),
        user_id=document["user_id"],
        device_id=document["device_id"],
        predicted_device_type=document["predicted_device_type"],
        confidence_score=float(document["confidence_score"]),
        status=document["status"],
        analyzed_at=document["analyzed_at"],
        created_at=document["created_at"],
    )


def document_to_device_consumption(document: dict[str, Any]) -> DeviceConsumption:
    return DeviceConsumption(
        id=_id_to_str(document),
        user_id=document["user_id"],
        device_id=document["device_id"],
        energy_kwh=float(document["energy_kwh"]),
        measured_at=document["measured_at"],
        created_at=document["created_at"],
        meter_id=document.get("meter_id"),
        power_watts=float(document["power_watts"]) if document.get("power_watts") is not None else None,
        estimated_cost=float(document["estimated_cost"]) if document.get("estimated_cost") is not None else None,
        currency=document.get("currency"),
        reading_type=document.get("reading_type"),
    )


def document_to_bill_prediction(document: dict[str, Any]) -> BillPrediction:
    return BillPrediction(
        id=_id_to_str(document),
        user_id=document["user_id"],
        prediction_year=int(document["prediction_year"]),
        prediction_month=int(document["prediction_month"]),
        period_start=document["period_start"],
        period_end=document["period_end"],
        estimated_kwh=float(document["estimated_kwh"]),
        estimated_amount=float(document["estimated_amount"]),
        currency=document["currency"],
        tariff_used=float(document["tariff_used"]),
        error_margin_percentage=float(document["error_margin_percentage"]),
        generated_at=document["generated_at"],
        created_at=document["created_at"],
    )


def document_to_recommendation(document: dict[str, Any]) -> Recommendation:
    return Recommendation(
        id=_id_to_str(document),
        user_id=document["user_id"],
        device_id=document.get("device_id"),
        recommendation_type=document["recommendation_type"],
        title=document["title"],
        description=document["description"],
        estimated_saving_kwh=float(document["estimated_saving_kwh"]),
        estimated_saving_amount=float(document["estimated_saving_amount"]),
        currency=document["currency"],
        status=document["status"],
        generated_at=document["generated_at"],
        applied_at=document.get("applied_at"),
        created_at=document["created_at"],
    )


def document_to_anomaly(document: dict[str, Any]) -> Anomaly:
    return Anomaly(
        id=_id_to_str(document),
        user_id=document["user_id"],
        device_id=document["device_id"],
        anomaly_type=document["anomaly_type"],
        description=document["description"],
        severity=document["severity"],
        status=document["status"],
        actual_kwh=float(document["actual_kwh"]),
        expected_kwh=float(document["expected_kwh"]),
        deviation_percentage=float(document["deviation_percentage"]),
        detected_at=document["detected_at"],
        resolved_at=document.get("resolved_at"),
        created_at=document["created_at"],
    )


def document_to_consumption_ranking(document: dict[str, Any]) -> ConsumptionRanking:
    rankings = [
        RankingItem(
            rank=int(item["rank"]),
            device_id=item["device_id"],
            device_name=item["device_name"],
            total_kwh=float(item["total_kwh"]),
            estimated_amount=float(item["estimated_amount"]),
            percentage_of_total=float(item["percentage_of_total"]),
            currency=item["currency"],
        )
        for item in document.get("rankings", [])
    ]
    return ConsumptionRanking(
        id=_id_to_str(document),
        user_id=document["user_id"],
        period_type=document["period_type"],
        period_start=document["period_start"],
        period_end=document["period_end"],
        rankings=rankings,
        generated_at=document["generated_at"],
        created_at=document["created_at"],
    )


def now_utc() -> datetime:
    return datetime.utcnow()
