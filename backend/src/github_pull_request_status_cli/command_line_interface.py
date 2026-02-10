from __future__ import annotations

import json
from typing import Optional

import anyio
import typer
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty

from .configuration import load_application_settings
from .local_cache import LocalTimeToLiveCache
from .github_api_client import (
    GitHubApiClient,
    GitHubApiError,
    GitHubAuthenticationError,
    GitHubRateLimitExceededError,
    GitHubRepositoryNotFoundError,
)
from .terminal_rendering import build_pull_requests_table

command_line_application = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="GitHub Pull Request Status CLI — fetch and display open pull requests with pagination + cache.",
)

pull_requests_command_group = typer.Typer(no_args_is_help=True, help="Commands for pull requests.")

command_line_application.add_typer(pull_requests_command_group, name="pull-requests")
command_line_application.add_typer(pull_requests_command_group, name="prs")

console = Console()


def create_github_api_client(*, require_token: bool = True) -> GitHubApiClient:
    application_settings = load_application_settings(require_token=require_token)
    cache_backend = LocalTimeToLiveCache(default_time_to_live_seconds=application_settings.cache_time_to_live_seconds)
    return GitHubApiClient(
        github_token=application_settings.github_personal_access_token,
        api_base_url=application_settings.github_api_base_url,
        request_timeout_seconds=application_settings.http_request_timeout_seconds,
        cache_backend=cache_backend,
    )


def _render_exception_and_exit(exception: Exception) -> None:
    if isinstance(exception, GitHubRateLimitExceededError):
        message = str(exception)
        if exception.reset_unix_epoch_seconds:
            message = f"{message} reset_unix_epoch_seconds={exception.reset_unix_epoch_seconds}"
        console.print(Panel(message, title="Rate Limit", style="red"))
        raise typer.Exit(code=2)

    if isinstance(exception, GitHubAuthenticationError):
        console.print(Panel(str(exception), title="Authentication Error", style="red"))
        raise typer.Exit(code=2)

    if isinstance(exception, GitHubRepositoryNotFoundError):
        console.print(Panel(str(exception), title="Repository Not Found", style="red"))
        raise typer.Exit(code=2)

    if isinstance(exception, GitHubApiError):
        console.print(Panel(str(exception), title="GitHub API Error", style="red"))
        raise typer.Exit(code=2)

    console.print(Panel(repr(exception), title="Unexpected Error", style="red"))
    raise typer.Exit(code=1)


@pull_requests_command_group.command("list")
def list_open_pull_requests(
    repository: Optional[str] = typer.Option(None, "--repository", "-r", help="Repository in owner/name format."),
    items_per_page: int = typer.Option(50, "--items-per-page", help="Items per page (1..100)."),
    maximum_pages_to_fetch: Optional[int] = typer.Option(None, "--maximum-pages-to-fetch", help="Max pages to fetch (default: all)."),
    maximum_rows_to_display: Optional[int] = typer.Option(None, "--maximum-rows-to-display", help="Limit displayed rows after fetching."),
    bypass_cache: bool = typer.Option(False, "--bypass-cache", help="Ignore cache and fetch live."),
    output_json: bool = typer.Option(False, "--output-json", help="Print JSON instead of a table."),
) -> None:
    """
    Fetch open pull requests (with pagination) and display them in a readable table.
    """
    try:
        application_settings = load_application_settings(require_token=True)
        repository_identifier = (repository or application_settings.default_repository).strip()

        async def _execute() -> None:
            github_api_client = create_github_api_client(require_token=True)
            open_pull_requests_result = await github_api_client.list_open_pull_requests(
                repository_identifier=repository_identifier,
                items_per_page=items_per_page,
                maximum_pages_to_fetch=maximum_pages_to_fetch,
                bypass_cache=bypass_cache,
            )

            pull_requests = open_pull_requests_result.pull_requests
            if maximum_rows_to_display is not None:
                pull_requests = pull_requests[: max(0, int(maximum_rows_to_display))]

            if output_json:
                output_payload = {
                    "repository": repository_identifier,
                    "pages_fetched": open_pull_requests_result.pages_fetched,
                    "response_was_from_cache": open_pull_requests_result.response_was_from_cache,
                    "count": len(pull_requests),
                    "items": [
                        {
                            "pull_request_number": pull_request.pull_request_number,
                            "title": pull_request.title,
                            "author_login": pull_request.author_login,
                            "html_url": pull_request.html_url,
                            "label_names": list(pull_request.label_names),
                            "is_draft": pull_request.is_draft,
                            "state": pull_request.state,
                            "created_at": pull_request.created_at.isoformat(),
                            "updated_at": pull_request.updated_at.isoformat(),
                        }
                        for pull_request in pull_requests
                    ],
                }
                console.print_json(json.dumps(output_payload, ensure_ascii=False))
                return

            table = build_pull_requests_table(
                pull_requests,
                repository_identifier=repository_identifier,
                pages_fetched=open_pull_requests_result.pages_fetched,
                response_was_from_cache=open_pull_requests_result.response_was_from_cache,
            )
            console.print(table)

        anyio.run(_execute)

    except Exception as exception:
        _render_exception_and_exit(exception)


@command_line_application.command("rate-limit")
def show_rate_limit_status() -> None:
    """
    Show your current GitHub rate-limit status.
    """
    try:
        async def _execute() -> None:
            github_api_client = create_github_api_client(require_token=False)
            rate_limit_payload = await github_api_client.fetch_rate_limit_status()
            console.print(Panel(Pretty(rate_limit_payload), title="GitHub Rate Limit", style="cyan"))

        anyio.run(_execute)

    except Exception as exception:
        _render_exception_and_exit(exception)


@command_line_application.command("cache-clear")
def clear_local_cache() -> None:
    """
    Clear local time-to-live cache.
    """
    try:
        application_settings = load_application_settings(require_token=False)
        cache_backend = LocalTimeToLiveCache(default_time_to_live_seconds=application_settings.cache_time_to_live_seconds)
        cache_backend.clear_all_cached_values()
        console.print(Panel("Cache cleared.", title="OK", style="green"))
    except Exception as exception:
        _render_exception_and_exit(exception)
