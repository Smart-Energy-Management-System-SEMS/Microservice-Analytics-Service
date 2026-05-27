from typing import Any


class AnalyticsAcl:
    def normalize_external_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        return dict(payload)
