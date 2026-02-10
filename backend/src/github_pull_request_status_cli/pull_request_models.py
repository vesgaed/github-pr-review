from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable


@dataclass(frozen=True)
class PullRequestSummary:
    pull_request_number: int
    title: str
    author_login: str
    author_avatar_url: str
    html_url: str
    label_names: tuple[str, ...]
    is_draft: bool
    state: str
    created_at: datetime
    updated_at: datetime
    body: str

    @staticmethod
    def _parse_github_datetime(iso_datetime_string: str) -> datetime:
        normalized_value = iso_datetime_string.strip()
        if normalized_value.endswith("Z"):
            normalized_value = normalized_value[:-1] + "+00:00"
        return datetime.fromisoformat(normalized_value)

    @classmethod
    def from_github_api_response(cls, pull_request_payload: dict[str, Any]) -> "PullRequestSummary":
        labels_payload = pull_request_payload.get("labels") or []
        label_names = tuple(
            str(label_object.get("name", "")).strip()
            for label_object in labels_payload
            if isinstance(label_object, dict) and str(label_object.get("name", "")).strip()
        )

        user_payload = pull_request_payload.get("user") or {}
        author_login = str(user_payload.get("login", "")).strip() or "unknown"
        author_avatar_url = str(user_payload.get("avatar_url", "")).strip()

        return cls(
            pull_request_number=int(pull_request_payload["number"]),
            title=str(pull_request_payload.get("title", "")).strip(),
            author_login=author_login,
            author_avatar_url=author_avatar_url,
            html_url=str(pull_request_payload.get("html_url", "")).strip(),
            label_names=label_names,
            is_draft=bool(pull_request_payload.get("draft", False)),
            state=str(pull_request_payload.get("state", "")).strip() or "unknown",
            created_at=cls._parse_github_datetime(str(pull_request_payload.get("created_at", "")).strip()),
            updated_at=cls._parse_github_datetime(str(pull_request_payload.get("updated_at", "")).strip()),
            body=str(pull_request_payload.get("body", "") or ""),
        )


def parse_pull_requests_from_github_payload(items: Iterable[dict[str, Any]]) -> list[PullRequestSummary]:
    pull_requests: list[PullRequestSummary] = []
    for item_payload in items:
        try:
            pull_requests.append(PullRequestSummary.from_github_api_response(item_payload))
        except Exception:
            continue
    return pull_requests
