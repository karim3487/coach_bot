import logging
from http.client import HTTPException

import httpx

from coach_bot.data import config
from coach_bot.models.schemas import (
    ClientProfileCreate,
    ClientProfileShort,
    Goal,
)

profiles_route = config.BACKEND_URL + "/profiles/"
goals_route = config.BACKEND_URL + "/goals/"
backup_codes_route = config.BACKEND_URL + "/backup-codes/"

logger = logging.getLogger(__name__)


async def create_or_update_user(user: ClientProfileCreate) -> ClientProfileShort | None:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{profiles_route}upsert/", json=user.model_dump(mode="json"),
        )
        response.raise_for_status()
        data = response.json()
        data["goal"] = data["goal_display"]
        return ClientProfileShort(**data)


async def get_goals() -> list[str]:
    async with httpx.AsyncClient() as client:
        response = await client.get(goals_route)
        response.raise_for_status()
        return [goal["name"] for goal in response.json()]


async def get_goal_by_slug(slug: str) -> Goal | None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{goals_route}by-name/{slug}/")
        if response.status_code == 404:  # noqa: PLR2004
            return None
        response.raise_for_status()
        return Goal(**response.json())


async def get_user(telegram_id: int) -> ClientProfileShort | None:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{profiles_route}by-telegram/{telegram_id}/")
            if response.status_code == 404:  # noqa: PLR2004
                return None
            response.raise_for_status()
            return ClientProfileShort(**response.json())
        except httpx.RequestError as e:
            logger.exception("Error when request to server", exc_info=e)
            raise HTTPException(status_code=503, detail="Server unavailable") from e
        except httpx.HTTPStatusError as e:
            logger.exception("Error HTTP-status", exc_info=e)
            raise HTTPException(
                status_code=e.response.status_code, detail="Error from server",
            ) from e


async def get_backup_codes(telegram_id: str) -> list[str]:
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{backup_codes_route}generate/", json={"telegram_id": telegram_id})
        response.raise_for_status()
        return response.json()


async def auth_with_backup_code(
    code: str, telegram_id: int,
) -> ClientProfileShort | None:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{backup_codes_route}use", json={"code": code, "telegram_id": telegram_id},
        )
        if response.status_code == 401:  # noqa: PLR2004
            raise HTTPException(401)
        response.raise_for_status()
        return ClientProfileShort(**response.json())
