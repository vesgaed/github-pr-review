from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from rich import box
from rich.table import Table
from rich.text import Text

from .pull_request_models import PullRequestSummary


def format_datetime_as_relative_age(target_datetime: datetime) -> str:
    current_time = datetime.now(timezone.utc)
    if target_datetime.tzinfo is None:
        target_datetime = target_datetime.replace(tzinfo=timezone.utc)

    elapsed_time = current_time - target_datetime
    elapsed_seconds = int(elapsed_time.total_seconds())

    if elapsed_seconds < 60:
        return f"{elapsed_seconds}s"

    elapsed_minutes = elapsed_seconds // 60
    if elapsed_minutes < 60:
        return f"{elapsed_minutes}m"

    elapsed_hours = elapsed_minutes // 60
    if elapsed_hours < 48:
        return f"{elapsed_hours}h"

    elapsed_days = elapsed_hours // 24
    return f"{elapsed_days}d"


def build_pull_requests_table(
    pull_requests: Iterable[PullRequestSummary],
    *,
    repository_identifier: str,
    pages_fetched: int,
    response_was_from_cache: bool,
) -> Table:
    metadata_title = f"{repository_identifier} • pages={pages_fetched} • {'cache' if response_was_from_cache else 'live'}"

    table = Table(
        title=f"Open Pull Requests ({metadata_title})",
        box=box.SIMPLE_HEAVY,
        show_lines=False,
        header_style="bold",
    )

    table.add_column("PR #", style="bold", width=8, no_wrap=True)
    table.add_column("Title", overflow="fold")
    table.add_column("Author", width=18)
    table.add_column("Labels", overflow="fold")
    table.add_column("Readiness", width=12, no_wrap=True)
    table.add_column("Updated", width=10, no_wrap=True)
    table.add_column("URL", overflow="fold")

    for pull_request in pull_requests:
        labels_text = ", ".join(pull_request.label_names) if pull_request.label_names else "-"
        readiness_label = "DRAFT" if pull_request.is_draft else "READY"
        readiness_text = Text(readiness_label)
        updated_age = format_datetime_as_relative_age(pull_request.updated_at)

        table.add_row(
            str(pull_request.pull_request_number),
            pull_request.title or "-",
            pull_request.author_login or "-",
            labels_text,
            readiness_text,
            updated_age,
            pull_request.html_url or "-",
        )

    return table
