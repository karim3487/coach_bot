import logging
from http.client import HTTPException

import httpx

from coach_bot.data import config
from coach_bot.models.schemas import UserCreate, UserRead

users_route = config.BACKEND_URL + "/users"
backup_codes_route = config.BACKEND_URL + "/backup_codes"

logger = logging.getLogger(__name__)


async def create_or_update_user(user: UserCreate) -> UserRead | None:
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{users_route}/{user.telegram_id}", json=user.model_dump(mode="json")
        )
        response.raise_for_status()
        return UserRead(**response.json())


async def get_user(telegram_id: int) -> UserRead | None:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{users_route}/telegram/{telegram_id}")
            if response.status_code == 404:  # noqa: PLR2004
                return None
            response.raise_for_status()
            return UserRead(**response.json())
        except httpx.RequestError as e:
            logger.exception("Error when request to server", exc_info=e)
            raise HTTPException(status_code=503, detail="Server unavailable") from e
        except httpx.HTTPStatusError as e:
            logger.exception("Error HTTP-status", exc_info=e)
            raise HTTPException(
                status_code=e.response.status_code, detail="Error from server"
            ) from e


async def get_backup_codes(telegram_id: str) -> list[str]:
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{backup_codes_route}/generate_tg/{telegram_id}")
        response.raise_for_status()
        return response.json()["codes"]


async def auth_with_backup_code(code: str, telegram_id: int) -> UserRead | None:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{backup_codes_route}/use", json={"code": code, "telegram_id": telegram_id}
        )
        if response.status_code == 401:  # noqa: PLR2004
            raise HTTPException(401)
        response.raise_for_status()
        return UserRead(**response.json())
