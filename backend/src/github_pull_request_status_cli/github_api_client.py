from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Optional
from urllib.parse import urlparse, parse_qs

import httpx

from .local_cache import LocalTimeToLiveCache
from .pull_request_models import PullRequestSummary, parse_pull_requests_from_github_payload


class GitHubApiError(RuntimeError):
    pass


class GitHubAuthenticationError(GitHubApiError):
    pass


class GitHubRepositoryNotFoundError(GitHubApiError):
    pass


class GitHubRateLimitExceededError(GitHubApiError):
    def __init__(self, message: str, *, reset_unix_epoch_seconds: Optional[int] = None) -> None:
        super().__init__(message)
        self.reset_unix_epoch_seconds = reset_unix_epoch_seconds


@dataclass(frozen=True)
class OpenPullRequestsResult:
    pull_requests: list[PullRequestSummary]
    pages_fetched: int
    response_was_from_cache: bool


def parse_github_link_header(link_header_value: str) -> dict[str, str]:
    parsed_links: dict[str, str] = {}
    if not link_header_value:
        return parsed_links

    link_segments = [segment.strip() for segment in link_header_value.split(",") if segment.strip()]
    for link_segment in link_segments:
        if ";" not in link_segment:
            continue

        url_part, *parameter_parts = [part.strip() for part in link_segment.split(";")]
        if not (url_part.startswith("<") and url_part.endswith(">")):
            continue

        url_value = url_part[1:-1].strip()
        relation_type: Optional[str] = None

        for parameter_part in parameter_parts:
            if parameter_part.startswith("rel="):
                relation_type = parameter_part.split("=", 1)[1].strip().strip('"')
                break

        if relation_type:
            parsed_links[relation_type] = url_value

    return parsed_links


def _read_integer_header(response_headers: httpx.Headers, header_name: str) -> Optional[int]:
    header_value = response_headers.get(header_name)
    if not header_value:
        return None
    try:
        return int(header_value)
    except ValueError:
        return None


class GitHubApiClient:
    def __init__(
        self,
        *,
        github_token: str,
        api_base_url: str = "https://api.github.com",
        request_timeout_seconds: float = 15.0,
        cache_backend: Optional[LocalTimeToLiveCache] = None,
        user_agent_value: str = "github-pull-request-status-cli/1.0",
    ) -> None:
        self.github_token = github_token.strip()
        self.api_base_url = api_base_url.rstrip("/")
        self.request_timeout = httpx.Timeout(request_timeout_seconds)
        self.cache_backend = cache_backend or LocalTimeToLiveCache(default_time_to_live_seconds=90)
        self.user_agent_value = user_agent_value

    def _build_default_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": self.user_agent_value,
        }
        if self.github_token:
            headers["Authorization"] = f"Bearer {self.github_token}"
        return headers

    async def _perform_request(self, method: str, url_path: str, *, query_parameters: Optional[dict[str, Any]] = None) -> httpx.Response:
        async with httpx.AsyncClient(base_url=self.api_base_url, headers=self._build_default_headers(), timeout=self.request_timeout) as http_client:
            response = await http_client.request(method, url_path, params=query_parameters)

            if response.status_code == 401:
                raise GitHubAuthenticationError("Unauthorized (401). Check your GITHUB_TOKEN.")

            if response.status_code == 404:
                raise GitHubRepositoryNotFoundError("Not found (404). Check repository owner/name.")

            if response.status_code == 403:
                remaining_requests = _read_integer_header(response.headers, "X-RateLimit-Remaining")
                reset_epoch = _read_integer_header(response.headers, "X-RateLimit-Reset")
                error_message = ""
                try:
                    error_message = str((response.json() or {}).get("message", ""))
                except Exception:
                    error_message = ""

                if remaining_requests == 0 or "rate limit" in error_message.lower():
                    raise GitHubRateLimitExceededError(
                        f"Rate limit exceeded (403). Remaining={remaining_requests}.",
                        reset_unix_epoch_seconds=reset_epoch,
                    )

            if response.status_code >= 400:
                try:
                    response_payload = response.json()
                    message = response_payload.get("message", f"HTTP {response.status_code}")
                except Exception:
                    message = f"HTTP {response.status_code}"
                raise GitHubApiError(message)

            return response

    @staticmethod
    def parse_repository_identifier(repository_identifier: str) -> tuple[str, str]:
        normalized_repository_identifier = repository_identifier.strip()
        if normalized_repository_identifier.count("/") != 1:
            raise ValueError("Repository must be in the form 'owner/name'.")
        repository_owner, repository_name = normalized_repository_identifier.split("/", 1)
        repository_owner = repository_owner.strip()
        repository_name = repository_name.strip()
        if not repository_owner or not repository_name:
            raise ValueError("Repository must be in the form 'owner/name'.")
        return repository_owner, repository_name

    async def fetch_rate_limit_status(self) -> dict[str, Any]:
        response = await self._perform_request("GET", "/rate_limit")
        return response.json()

    async def list_open_pull_requests(
        self,
        *,
        repository_identifier: str,
        items_per_page: int = 50,
        maximum_pages_to_fetch: Optional[int] = None,
        bypass_cache: bool = False,
        sort_field: str = "updated",
        sort_direction: str = "desc",
    ) -> OpenPullRequestsResult:
        repository_owner, repository_name = self.parse_repository_identifier(repository_identifier)
        items_per_page = max(1, min(int(items_per_page), 100))
        maximum_pages = None if maximum_pages_to_fetch is None else max(1, int(maximum_pages_to_fetch))

        cache_key = (
            f"pull_requests:open:{repository_owner}/{repository_name}:"
            f"items_per_page={items_per_page}:max_pages={maximum_pages}:sort={sort_field}:direction={sort_direction}"
        )

        if not bypass_cache:
            cached_payload = self.cache_backend.get_cached_value(cache_key)
            if isinstance(cached_payload, dict) and isinstance(cached_payload.get("items"), list):
                pull_requests = parse_pull_requests_from_github_payload(cached_payload["items"])
                pages_fetched = int(cached_payload.get("pages_fetched") or 0)
                return OpenPullRequestsResult(
                    pull_requests=pull_requests,
                    pages_fetched=pages_fetched,
                    response_was_from_cache=True,
                )

        request_path = f"/repos/{repository_owner}/{repository_name}/pulls"
        initial_parameters: dict[str, Any] = {
            "state": "open",
            "per_page": items_per_page,
            "page": 1,
            "sort": sort_field,
            "direction": sort_direction,
        }

        pages_fetched = 0
        aggregated_items: list[dict[str, Any]] = []

        next_request_path: Optional[str] = request_path
        next_query_parameters: Optional[dict[str, Any]] = initial_parameters

        while next_request_path:
            response = await self._perform_request("GET", next_request_path, query_parameters=next_query_parameters)
            response_items = response.json()

            if not isinstance(response_items, list):
                break

            aggregated_items.extend([item for item in response_items if isinstance(item, dict)])
            pages_fetched += 1

            if maximum_pages is not None and pages_fetched >= maximum_pages:
                break

            parsed_links = parse_github_link_header(response.headers.get("Link", ""))
            next_page_url = parsed_links.get("next")
            if not next_page_url:
                break

            parsed_next_url = urlparse(next_page_url)
            if parsed_next_url.scheme and parsed_next_url.netloc:
                next_request_path = parsed_next_url.path
                parsed_query = parse_qs(parsed_next_url.query)
                next_query_parameters = {key: values[0] for key, values in parsed_query.items() if values}
            else:
                next_request_path = next_page_url
                next_query_parameters = None

            await asyncio.sleep(0)

        self.cache_backend.set_cached_value(cache_key, {"items": aggregated_items, "pages_fetched": pages_fetched})
        pull_requests = parse_pull_requests_from_github_payload(aggregated_items)
        return OpenPullRequestsResult(
            pull_requests=pull_requests,
            pages_fetched=pages_fetched,
            response_was_from_cache=False,
        )

    async def list_user_repositories(
        self,
        *,
        maximum_items: int = 10,
        connection_type: str = "owner",
        sort_field: str = "updated",
        sort_direction: str = "desc",
    ) -> list[dict[str, Any]]:
        """
        List repositories that the authenticated user has access to.
        This requires a valid GitHub Token.
        """
        if not self.github_token:
            return []

        # We don't cache this aggressively as it might change, but a short TTL is fine.
        cache_key = f"user:repos:type={connection_type}:sort={sort_field}:limit={maximum_items}"
        cached_data = self.cache_backend.get_cached_value(cache_key)
        if cached_data:
            return cached_data

        response = await self._perform_request(
            "GET", 
            "/user/repos", 
            query_parameters={
                "type": connection_type,
                "sort": sort_field,
                "direction": sort_direction,
                "per_page": maximum_items,
            }
        )
        
        repos = response.json()
        if not isinstance(repos, list):
            return []

        # Simplify payload for frontend
        simplified_repos = [
            {
                "full_name": repo.get("full_name"),
                "private": repo.get("private"),
                "updated_at": repo.get("updated_at"),
                "description": repo.get("description"),
                "html_url": repo.get("html_url"),
            }
            for repo in repos
            if isinstance(repo, dict) and repo.get("full_name")
        ]

        self.cache_backend.set_cached_value(cache_key, simplified_repos, time_to_live_seconds=60)
        return simplified_repos
