from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = (
    BASE_DIR / "adaptive_rl.db"
).resolve()


class Settings(BaseSettings):
    app_name: str = "AdaptiveRL Tic-Tac-Toe"
    app_version: str = "0.5.1"
    debug: bool = True
    frontend_origin: str = "http://localhost:5173"
    frontend_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    database_url: str = (
        f"sqlite:///{DATABASE_PATH.as_posix()}"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
