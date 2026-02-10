from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from rich import box
from rich.console import Console
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parent
SOURCE_DIRECTORY = PROJECT_ROOT / "src"
sys.path.insert(0, str(SOURCE_DIRECTORY))

from github_pull_request_status_cli.configuration import load_application_settings
from github_pull_request_status_cli.local_cache import LocalTimeToLiveCache
from github_pull_request_status_cli.github_api_client import GitHubApiClient


console = Console()


def _format_result_cell(success: bool) -> str:
    return "✅ PASS" if success else "❌ FAIL"


def main() -> None:
    environment_file_path = PROJECT_ROOT / ".env"
    load_dotenv(environment_file_path if environment_file_path.exists() else None)

    checks: list[tuple[str, bool, str]] = []

    checks.append((".env file exists", environment_file_path.exists(), f"Expected at: {environment_file_path}"))

    github_token_is_present = bool(os.getenv("GITHUB_TOKEN", "").strip())
    checks.append(("GITHUB_TOKEN is set", github_token_is_present, "Set via environment variable or .env"))

    api_call_succeeds = False
    authentication_is_likely_active = False
    rate_limit_payload: dict[str, Any] = {}

    try:
        application_settings = load_application_settings(require_token=False)
        cache_backend = LocalTimeToLiveCache(default_time_to_live_seconds=application_settings.cache_time_to_live_seconds)

        github_api_client = GitHubApiClient(
            github_token=application_settings.github_personal_access_token,
            api_base_url=application_settings.github_api_base_url,
            request_timeout_seconds=application_settings.http_request_timeout_seconds,
            cache_backend=cache_backend,
        )

        import anyio

        async def _execute_rate_limit() -> None:
            nonlocal api_call_succeeds, authentication_is_likely_active, rate_limit_payload
            rate_limit_payload = await github_api_client.fetch_rate_limit_status()
            core_limits = (rate_limit_payload.get("resources") or {}).get("core") or {}
            core_limit_value = int(core_limits.get("limit") or 0)
            api_call_succeeds = core_limit_value > 0
            authentication_is_likely_active = core_limit_value >= 1000

        anyio.run(_execute_rate_limit)

    except Exception:
        api_call_succeeds = False
        authentication_is_likely_active = False

    checks.append(("GitHub API call works (/rate_limit)", api_call_succeeds, "Network + GitHub API reachable"))
    checks.append(("Authentication likely active (high rate limit)", authentication_is_likely_active, "With token, core.limit is usually 5000"))

    pagination_is_confirmed = False
    cache_is_confirmed = False

    try:
        application_settings = load_application_settings(require_token=True)
        cache_backend = LocalTimeToLiveCache(default_time_to_live_seconds=application_settings.cache_time_to_live_seconds)

        github_api_client = GitHubApiClient(
            github_token=application_settings.github_personal_access_token,
            api_base_url=application_settings.github_api_base_url,
            request_timeout_seconds=application_settings.http_request_timeout_seconds,
            cache_backend=cache_backend,
        )

        import anyio

        async def _execute_pagination_and_cache_checks() -> None:
            nonlocal pagination_is_confirmed, cache_is_confirmed
            repository_identifier = application_settings.default_repository

            first_fetch = await github_api_client.list_open_pull_requests(
                repository_identifier=repository_identifier,
                items_per_page=1,
                maximum_pages_to_fetch=2,
                bypass_cache=True,
            )
            pagination_is_confirmed = first_fetch.pages_fetched >= 2

            second_fetch = await github_api_client.list_open_pull_requests(
                repository_identifier=repository_identifier,
                items_per_page=1,
                maximum_pages_to_fetch=2,
                bypass_cache=False,
            )
            cache_is_confirmed = second_fetch.response_was_from_cache is True

        anyio.run(_execute_pagination_and_cache_checks)

    except Exception:
        pagination_is_confirmed = False
        cache_is_confirmed = False

    checks.append(("Pagination exercised (>=2 pages)", pagination_is_confirmed, "Uses Link header + follows rel=next"))
    checks.append(("Cache exercised (2nd call served from cache)", cache_is_confirmed, "TTL cache prevents repeated API calls"))

    table = Table(title="Audit Criteria Checklist", box=box.SIMPLE_HEAVY)
    table.add_column("Check", style="bold")
    table.add_column("Result", width=10)
    table.add_column("Notes", overflow="fold")

    for check_name, success, notes in checks:
        table.add_row(check_name, _format_result_cell(success), notes)

    console.print(table)

    critical_failures = any(
        check_name in (".env file exists", "GITHUB_TOKEN is set", "GitHub API call works (/rate_limit)") and not success
        for check_name, success, _ in checks
    )
    raise SystemExit(1 if critical_failures else 0)


if __name__ == "__main__":
    main()
