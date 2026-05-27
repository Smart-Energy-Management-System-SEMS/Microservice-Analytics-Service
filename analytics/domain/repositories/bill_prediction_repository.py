from abc import ABC, abstractmethod

from analytics.domain.model.entities.bill_prediction import BillPrediction


class BillPredictionRepository(ABC):
    @abstractmethod
    async def save(self, prediction: BillPrediction) -> BillPrediction:
        raise NotImplementedError

    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> list[BillPrediction]:
        raise NotImplementedError
