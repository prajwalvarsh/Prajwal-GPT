"""Centralised configuration management for PrajwalGPT services."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

_DEFAULTS_PATH = Path(__file__).with_name("constants.json")


def _load_defaults() -> Dict[str, Any]:
    with _DEFAULTS_PATH.open("r", encoding="utf-8") as fp:
        return json.load(fp)


_DEFAULTS = _load_defaults()

# Load environment variables from a local .env file if present.
load_dotenv()


@dataclass(frozen=True, slots=True)
class Settings:
    """Shared configuration values consumed by every service."""

    ollama_host: str = os.getenv("OLLAMA_HOST", _DEFAULTS["OLLAMA_HOST"])
    ollama_model: str = os.getenv("OLLAMA_MODEL", _DEFAULTS["OLLAMA_MODEL"])
    embedding_model: str = os.getenv("EMBEDDING_MODEL", _DEFAULTS["EMBEDDING_MODEL"])
    vector_store_path: str = os.getenv("VECTOR_STORE_PATH", _DEFAULTS["VECTOR_STORE_PATH"])
    api_base_url: str = os.getenv("API_BASE_URL", _DEFAULTS["API_BASE_URL"])
    api_port: int = int(os.getenv("API_PORT", _DEFAULTS["API_PORT"]))
    frontend_base_url: str = os.getenv("FRONTEND_BASE_URL", _DEFAULTS["FRONTEND_BASE_URL"])

    def to_dict(self) -> Dict[str, Any]:
        """Return a serialisable representation of the settings."""

        return asdict(self)


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return a cached instance of :class:`Settings`."""

    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


settings = get_settings()
