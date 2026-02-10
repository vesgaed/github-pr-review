# Compliance Matrix - Senior Full-Stack Engineer Exercise

This document maps the project features against the requirements provided in the take-home exercise prompt.

## Core Requirements

| Requirement | Implementation Status | Location / Notes |
| :--- | :---: | :--- |
| **Authenticate with GitHub API** | ✅ **Done** | `backend/src/.../github_api_client.py` (Handling Bearer Token) |
| **Fetch Open Pull Requests** | ✅ **Done** | `backend/src/.../github_api_client.py` (`list_open_pull_requests`) |
| **Display Meaningful Information** | ✅ **Done** | Frontend displays Status, ID, Title, Author, Labels, Age. |
| **Handle Pagination** | ✅ **Done** | Backend handles `Link` header; Frontend allows `Max Pages` config. |
| **Basic Caching** | ✅ **Done** | File-based TTL Cache in `backend/src/.../local_cache.py`. |
| **README Instructions** | ✅ **Done** | Root `README.md` covers Installation, Running, and Design Decisions. |
| **Security (No Token Committed)** | ✅ **Done** | Token via `env` or UI input. `.env` is gitignored. |

## Optional Enhancements (Implemented)

| Enhancement | Implementation Status | Notes |
| :--- | :---: | :--- |
| **Agent / MCP Layer** | ✅ **Done** | Endpoint `/api/agent/tools` exposes tools for AI agents. |
| **LLM Summary** | ✅ **Done** | Implemented using Google Gemini. |
| **Automated Tests** | ✅ **Done** | Added `backend/tests/` with `pytest` for API logic. |
| **UI Polish** | ✅ **Done** | Modern React + Tailwind CSS, Dark Mode, Responsive, Glassmorphism. |
| **Docker Orchestration** | ✅ **Bonus** | Full `docker-compose` setup for easy "one-command" start. |
| **Swagger Documentation** | ✅ **Bonus** | Professional OpenAPI docs at `/docs`. |
| **"My Repositories" Feature**| ✅ **Bonus** | Auto-lists user's repos if token is provided. |

## Self-Evaluation Rubric

- **Functionality**: End-to-end working application with Docker.
- **Code Quality**: Structured Monorepo, Typed Python (FastAPI), Typed TypeScript (React), Separation of Concerns.
- **Bugs**: Handled edge cases like 401/403/404 errors and network failures.
- **Design Decisions**: Documented in `README.md`.
