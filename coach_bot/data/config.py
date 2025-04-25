from environs import Env

env = Env()
env.read_env()

BOT_TOKEN: str = env.str("BOT_TOKEN")
BOT_ID: str = BOT_TOKEN.split(":")[0]

LOGGING_LEVEL: int = env.int("LOGGING_LEVEL", 10)

USE_PG_LINK: bool = env.bool("USE_PG_LINK", False)

BACKEND_URL: str = env.str("BACKEND_URL", "http://localhost:8000/api/v1")

print(
    f"Using backend URL: {BACKEND_URL}",
)

DROP_PREVIOUS_UPDATES: bool = env.bool("DROP_PREVIOUS_UPDATES", False)
