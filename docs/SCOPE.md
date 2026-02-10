# Project Scope & Limitations

## Repository Access

This tool adheres to strict security principles regarding repository access:

1.  **Public Repositories**:
    *   Can be accessed **without a token** (subject to strict GitHub Rate Limits, approx 60/hour).
    *   Can be accessed **with a token** (Standard Rate Limits, approx 5000/hour).

2.  **Private Repositories**:
    *   **Require a valid GitHub Token** with the `repo` scope.
    *   If no token is provided, the API will return a `404 Not Found` to protect the existence of private resources, mimicking GitHub's security model.

## Data Fetching Strategy

*   The application fetches **Open** Pull Requests only.
*   It automatically handles pagination, fetching up to the configured `Max Pages` limit (default: 3 pages of 30 items).
*   Data is cached locally for **90 seconds** to prevent hitting rate limits during frequent refreshes.
