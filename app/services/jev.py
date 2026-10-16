
from typing import Any

import httpx

from app.core.config import settings


JEV_BASE_URL = "https://api.typesafe.ai"


class JevServiceError(Exception):
    """Raised when the JEV API request fails."""


class JevService:
    def __init__(self) -> None:
        if not settings.jev_api_key:
            raise JevServiceError("JEV_API_KEY is not configured")

        self.headers = {
            "Authorization": f"Bearer {settings.jev_api_key}",
            "Content-Type": "application/json",
        }

    async def list_models(self) -> dict[str, Any]:
        return await self._request("GET", "/v1/models")

    async def decide(
        self,
        state: str | dict[str, Any],
        questions: dict[str, Any],
        model: str = "jev-latest",
    ) -> dict[str, Any]:
        payload = {
            "model": model,
            "state": state,
            "questions": questions,
        }

        return await self._request(
            "POST",
            "/v1/systemone",
            json=payload,
        )

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(
                base_url=JEV_BASE_URL,
                headers=self.headers,
                timeout=20.0,
            ) as client:
                response = await client.request(
                    method,
                    path,
                    **kwargs,
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as exc:
            raise JevServiceError(
                f"JEV API returned HTTP {exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:
            raise JevServiceError(
                "Could not connect to JEV API"
            ) from exc
