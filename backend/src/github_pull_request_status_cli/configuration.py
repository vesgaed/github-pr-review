from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class ApplicationSettings:
    github_personal_access_token: str
    github_api_base_url: str
    default_repository: str
    cache_time_to_live_seconds: int
    http_request_timeout_seconds: float
    gemini_api_key: str


def _read_environment_int(variable_name: str, default_value: int) -> int:
    raw_value = os.getenv(variable_name, "").strip()
    if not raw_value:
        return default_value
    try:
        return int(raw_value)
    except ValueError:
        return default_value


def _read_environment_float(variable_name: str, default_value: float) -> float:
    raw_value = os.getenv(variable_name, "").strip()
    if not raw_value:
        return default_value
    try:
        return float(raw_value)
    except ValueError:
        return default_value


def load_application_settings(*, require_token: bool = True) -> ApplicationSettings:
    github_token = os.getenv("GITHUB_TOKEN", "").strip()
    if require_token and not github_token:
        raise RuntimeError(
            "Missing GITHUB_TOKEN. Export it as an environment variable or set it in .env.\n"
            "PowerShell:\n"
            '  $env:GITHUB_TOKEN="ghp_..."\n'
            "Or create .env from .env.example."
        )

    return ApplicationSettings(
        github_personal_access_token=github_token,
        github_api_base_url=os.getenv("GITHUB_API_BASE_URL", "https://api.github.com").strip(),
        default_repository=os.getenv("GITHUB_DEFAULT_REPOSITORY", "vercel/next.js").strip(),
        cache_time_to_live_seconds=_read_environment_int("CACHE_TIME_TO_LIVE_SECONDS", 90),
        http_request_timeout_seconds=_read_environment_float("HTTP_REQUEST_TIMEOUT_SECONDS", 15.0),
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
    )
