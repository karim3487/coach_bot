import logging

import httpx

from coach_bot.data import config
from coach_bot.exceptions.api import (
    CoachApiClientError,
    BackupCodeInvalidOrUsed,
    TelegramIDAlreadyLinked,
)
from coach_bot.models.schemas import (
    ClientProfileCreate,
    ClientProfileShort,
    Goal,
    Plan,
    PaginatedProgramList,
)

logger = logging.getLogger(__name__)


class CoachApiClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=10)
        self._profiles_url = f"{config.BACKEND_URL}/profiles/"
        self._goals_url = f"{config.BACKEND_URL}/goals/"
        self._backup_codes_url = f"{config.BACKEND_URL}/backup-codes/"
        self._programs_url = f"{config.BACKEND_URL}/programs/"
        self._plans_url = f"{config.BACKEND_URL}/plans/"

    async def close(self) -> None:
        await self._client.aclose()

    async def _safe_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        try:
            response = await self._client.request(method, url, **kwargs)
            if response.status_code == 404:
                return response  # Вернуть чтобы обработать в вызывающем методе
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            error_text = e.response.text if e.response else "No response body"
            logger.error(
                "HTTP status error during %s %s: %s",
                method.upper(),
                url,
                error_text,
                exc_info=True,
            )
            raise CoachApiClientError(f"Server error: {error_text}") from e
        except httpx.RequestError as e:
            logger.error(
                "Request error during %s %s", method.upper(), url, exc_info=True,
            )
            raise CoachApiClientError("Network request failed") from e

    async def create_or_update_user(
        self, user: ClientProfileCreate,
    ) -> ClientProfileShort | None:
        response = await self._safe_request(
            "POST",
            f"{self._profiles_url}upsert/",
            json=user.model_dump(mode="json"),
        )

        if response.status_code == 400:
            logger.error("Bad request when creating/updating user: %s", response.text)
            return None

        data = response.json()
        if "goal_display" not in data:
            logger.error("Missing 'goal_display' in create_or_update_user response")
            raise CoachApiClientError("Invalid server response: missing goal_display")

        data["goal"] = data["goal_display"]
        return ClientProfileShort(**data)

    async def get_goals(self) -> list[Goal]:
        response = await self._safe_request("GET", self._goals_url)
        data = response.json()
        if "results" not in data:
            logger.error("Invalid response format: missing 'results' key")
            raise CoachApiClientError("Invalid server response: missing results key")
        return [Goal(**goal) for goal in data["results"]]

    async def get_goal(self, goal_id: int) -> Goal | None:
        response = await self._safe_request("GET", f"{self._goals_url}{goal_id}/")
        if response.status_code == 404:
            return None
        return Goal(**response.json())

    async def get_goal_by_slug(self, slug: str) -> Goal | None:
        response = await self._safe_request("GET", f"{self._goals_url}by-name/{slug}/")
        if response.status_code == 404:
            return None
        return Goal(**response.json())

    async def get_profile(self, telegram_id: int) -> ClientProfileShort | None:
        response = await self._safe_request(
            "GET", f"{self._profiles_url}by-telegram/{telegram_id}/",
        )
        if response.status_code == 404:
            return None
        return ClientProfileShort(**response.json())

    async def get_backup_codes(self, telegram_id: int) -> list[str]:
        response = await self._safe_request(
            "POST",
            f"{self._backup_codes_url}generate/",
            json={"telegram_id": telegram_id},
        )
        data = response.json()
        return data

    async def auth_with_backup_code(self, code: str, telegram_id: int) -> None:
        response = await self._safe_request(
            "POST",
            f"{self._backup_codes_url}use/",
            json={"code": code, "telegram_id": telegram_id},
        )

        if response.status_code == 400:
            try:
                error_detail = response.json().get("detail", "")
            except Exception:
                logger.warning("Failed to parse error response")
                raise CoachApiClientError("Failed to authenticate with backup code")

            if "invalid or already used" in error_detail.lower():
                logger.warning("Invalid or used backup code")
                raise BackupCodeInvalidOrUsed()
            if "telegram id is already linked" in error_detail.lower():
                logger.warning("Telegram ID already linked to another profile")
                raise TelegramIDAlreadyLinked()

            logger.warning(
                "Unknown 400 error during backup code auth: %s", error_detail,
            )
            raise CoachApiClientError(f"Authentication failed: {error_detail}")

        if response.status_code == 401:
            logger.warning("Unauthorized backup code")
            raise BackupCodeInvalidOrUsed()

    async def get_programs(self, goal_id: int, location: str) -> PaginatedProgramList:
        response = await self._safe_request(
            "GET", f"{self._programs_url}?goal={goal_id}&location={location}",
        )
        return PaginatedProgramList(**response.json())

    async def create_plan_from_program(self, telegram_id: int, program_id: int) -> Plan:
        response = await self._safe_request(
            "POST",
            f"{self._plans_url}create/from-program/by-telegram/",
            json={"telegram_id": telegram_id, "program_id": program_id},
        )
        if response.status_code == 400:
            raise CoachApiClientError("Failed to create plan")
        return Plan(**response.json())

    async def create_plan_auto(self, telegram_id: int) -> Plan:
        response = await self._safe_request(
            "POST",
            f"{self._plans_url}create/ai/by-telegram/",
            json={"telegram_id": telegram_id},
        )
        if response.status_code == 400:
            raise CoachApiClientError("Failed to create plan")
        return Plan(**response.json())

    async def get_current_plan(self, telegram_id: int) -> Plan | None:
        response = await self._safe_request(
            "GET", f"{self._plans_url}current/by-telegram/{telegram_id}/",
        )
        if response.status_code == 404:
            return None
        return Plan(**response.json())


api_client = CoachApiClient()
