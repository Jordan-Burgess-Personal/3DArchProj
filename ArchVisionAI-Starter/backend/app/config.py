from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


# backend/app/config.py -> backend/app -> backend -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


def _get_required_environment_variable(name: str) -> str:
    """Return a required environment variable or raise a clear error."""

    value = os.getenv(name)

    if value is None or not value.strip():
        raise RuntimeError(
            f"Required environment variable {name!r} is missing. "
            f"Create {ENV_FILE} using .env.example as a guide."
        )

    return value.strip()


def _get_boolean_environment_variable(
    name: str,
    default: bool = False,
) -> bool:
    """Convert a common environment-variable boolean value to bool."""

    raw_value = os.getenv(name)

    if raw_value is None:
        return default

    normalized_value = raw_value.strip().lower()

    if normalized_value in {"1", "true", "yes", "on"}:
        return True

    if normalized_value in {"0", "false", "no", "off"}:
        return False

    raise RuntimeError(
        f"Environment variable {name!r} must be a boolean value."
    )


def _get_integer_environment_variable(
    name: str,
    default: int,
) -> int:
    """Convert an environment variable to an integer."""

    raw_value = os.getenv(name)

    if raw_value is None:
        return default

    try:
        return int(raw_value)
    except ValueError as error:
        raise RuntimeError(
            f"Environment variable {name!r} must be an integer."
        ) from error


def _get_list_environment_variable(
    name: str,
    default: str = "",
) -> list[str]:
    """Convert a comma-separated environment variable into a list."""

    raw_value = os.getenv(name, default)

    return [
        value.strip()
        for value in raw_value.split(",")
        if value.strip()
    ]


@dataclass(frozen=True)
class Settings:
    """Centralized application configuration."""

    app_name: str
    app_version: str
    app_environment: str
    debug: bool

    backend_host: str
    backend_port: int
    cors_origins: list[str]

    database_url: str

    openai_api_key: str | None
    openai_model: str | None


@lru_cache
def get_settings() -> Settings:
    """Load and cache application settings."""

    return Settings(
        app_name=os.getenv("APP_NAME", "ArchVision AI API"),
        app_version=os.getenv("APP_VERSION", "0.1.0"),
        app_environment=os.getenv("APP_ENV", "development"),
        debug=_get_boolean_environment_variable(
            "DEBUG",
            default=False,
        ),
        backend_host=os.getenv("BACKEND_HOST", "127.0.0.1"),
        backend_port=_get_integer_environment_variable(
            "BACKEND_PORT",
            default=8000,
        ),
        cors_origins=_get_list_environment_variable(
            "CORS_ORIGINS",
            default="http://localhost:5173",
        ),
        database_url=_get_required_environment_variable("DATABASE_URL"),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL") or None,
    )


settings = get_settings()