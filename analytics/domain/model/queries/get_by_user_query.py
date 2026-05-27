from dataclasses import dataclass


@dataclass(slots=True)
class GetByUserQuery:
    user_id: str
