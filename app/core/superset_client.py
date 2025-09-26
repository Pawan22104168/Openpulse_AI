import requests
from typing import List, Dict, Any
from app.config import settings


class SupersetClient:
    """
    Production-ready client for Superset 5.0.0 REST API.
    Supports fetching dashboards, charts, and datasets.
    """

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _get(self, endpoint: str, params: dict = None) -> dict:
        """
        Helper GET request to Superset API with error handling.
        """
        url = f"{self.base_url}/api/v1/{endpoint.lstrip('/')}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            raise Exception(f"Superset API error [{response.status_code}]: {response.text}") from e
        except requests.RequestException as e:
            raise Exception(f"Superset request failed: {str(e)}") from e

    def fetch_dashboard_metadata(self, dashboard_id: int) -> Dict[str, Any]:
        """
        Fetch dashboard metadata including charts and datasets.
        Compatible with Superset 5.0.0.
        """
        # --- Fetch dashboard
        dashboard_resp = self._get(f"dashboard/{dashboard_id}")
        dashboard_result = dashboard_resp.get("result")
        if not dashboard_result:
            raise Exception(f"No dashboard found with id {dashboard_id}")

        dashboard_data = dashboard_result

        # --- Extract charts
        charts: List[Dict[str, Any]] = []
        for chart in dashboard_data.get("charts", []):
            chart_id = chart.get("id")
            if chart_id:
                chart_resp = self._get(f"chart/{chart_id}")
                chart_result = chart_resp.get("result")
                if chart_result:
                    charts.append(chart_result)

        # --- Extract datasets
        dataset_ids = list({c.get("dataset_id") for c in charts if c.get("dataset_id")})
        datasets: List[Dict[str, Any]] = []
        for dataset_id in dataset_ids:
            dataset_resp = self._get(f"dataset/{dataset_id}")
            dataset_result = dataset_resp.get("result")
            if dataset_result:
                datasets.append(dataset_result)

        return {
            "dashboard": dashboard_data,
            "charts": charts,
            "datasets": datasets
        }
