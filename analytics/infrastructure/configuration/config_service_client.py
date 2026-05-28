import json
import logging
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)


class ConfigServiceClient:
    def __init__(self, base_url: str, timeout_seconds: float = 3.0):
        self._base_url = base_url.rstrip("/") + "/"
        self._timeout_seconds = timeout_seconds

    def get_service_config(self, service_name: str) -> dict[str, Any]:
        service_path = f"api/v1/config/services/{quote(service_name)}"
        service_config = self._get_json(service_path)
        if not service_config:
            # Backward compatibility with older Config Service route shape.
            service_config = self._get_json(f"api/v1/config/{quote(service_name)}")
        kafka_config = self._get_json("api/v1/config/kafka")
        services_config = self._get_json("api/v1/config/services")

        merged: dict[str, Any] = {}
        merged.update(_ensure_dict(services_config.get("shared")))
        merged.update(_ensure_dict(kafka_config))
        merged.update(_find_service_entry(services_config, service_name))
        merged.update(_ensure_dict(service_config))
        return merged

    def _get_json(self, path: str) -> dict[str, Any]:
        url = urljoin(self._base_url, path)
        request = Request(url, headers={"Accept": "application/json"})
        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                payload = response.read().decode("utf-8")
                decoded = json.loads(payload)
                return decoded if isinstance(decoded, dict) else {}
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            logger.warning("Config service request failed for %s: %s", url, exc)
            return {}


def _find_service_entry(services_payload: dict[str, Any], service_name: str) -> dict[str, Any]:
    services = services_payload.get("services")
    if not isinstance(services, list):
        return {}

    for entry in services:
        if not isinstance(entry, dict):
            continue
        candidate = entry.get("serviceName") or entry.get("name")
        if isinstance(candidate, str) and candidate.strip().lower() == service_name.lower():
            return entry
    return {}


def _ensure_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}
