# GitHub Pull Request Explorer

A full-stack application to visualize and explore open Pull Requests from any GitHub repository.

![License](https://img.shields.io/badge/license-MIT-blue)
![Status](https://img.shields.io/badge/status-stable-green)

## 🚀 Overview

This project is a submission for the Senior Full-Stack Engineer Take-Home Exercise. It transforms a CLI tool into a modern web application with a **FastAPI** backend and a **React + Tailwind CSS** frontend, orchestrated via **Docker**.

### Key Features

-   **Live PR Fetching**: Real-time data from GitHub API.
-   **Smart Caching**: Local file-based cache to prevent rate-limiting (TTL: 90s).
-   **User Repositories**: Authenticated users can see their own repositories instantly.
-   **Modern UI**: Dark mode, glassmorphism, and responsive design.
-   **Dockerized**: One command to run everything.
-   **Swagger API Docs**: Fully documented API at `/docs`.

## 🛠️ Tech Stack

-   **Backend**: Python 3.12, FastAPI, Pydantic, Httpx.
-   **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons.
-   **DevOps**: Docker, Docker Compose.

## 🏁 Quick Start

### Prerequisites
-   Docker & Docker Compose installed.
-   (Optional) GitHub Personal Access Token.

### Running the App

1.  **Clone the repository**:
    ```bash
    git clone <your-repo-url>
    cd github-pull-request-status-cli
    ```

2.  **Start Services**:
    ```bash
    docker-compose up --build
    ```

3.  **Access the Application**:
    *   **Frontend**: [http://localhost:3002](http://localhost:3002)
    *   **Backend API Docs**: [http://localhost:8001/docs](http://localhost:8001/docs)

## 🧪 Running Tests

Unit tests are included for the backend logic.

1.  **Enter the Backend Container**:
    ```bash
    docker-compose exec backend bash
    ```
2.  **Run Pytest**:
    ```bash
    pytest
    ```

## 📂 Project Structure

```
├── backend/                # Python FastAPI Application
│   ├── src/                # Source code
│   ├── tests/              # Unit tests
│   └── Dockerfile          # Backend container config
├── frontend/               # React Application
│   ├── src/                # Components and Logic
│   └── Dockerfile          # Frontend container config
├── docs/                   # Documentation
│   ├── GITHUB_TOKEN.md     # Token generation guide
│   └── SCOPE.md            # Scope and limitations
├── docker-compose.yml      # Orchestration
└── COMPLIANCE.md           # Requirement Compliance Matrix
```

## 🔒 Security & Tokens

For public repositories, you can use the app without a token (subject to strict rate limits). For private repos or higher limits:

1.  Generate a token (see [docs/GITHUB_TOKEN.md](docs/GITHUB_TOKEN.md)).
2.  Paste it in the UI "GitHub Token" field.
3.  Or set it in `backend/.env` (renaming `.env.example`).

## ✍️ Design Decisions

1.  **Monorepo**: Kept both services in one repo for simplicity and shared context.
2.  **FastAPI**: Chosen for its speed, type safety, and automatic Swagger docs.
3.  **Client-Side Fetching**: The frontend proxies requests through the backend to avoid CORS issues with GitHub API directly and to utilize the backend's caching layer.
4.  **No Database**: Used file-based caching to keep the architecture lightweight and portable without needing Redis/Postgres.

## 📈 Future Improvements

-   [ ] Add comprehensive E2E testing (Cypress/Playwright).
-   [ ] Implement persistent storage (SQLite/Postgres) for user preferences.
-   [ ] Add CI/CD GitHub Actions workflow.

## ✅ Feature Verification Guide

To make it easy for the team to verify the requirements, here is a step-by-step guide:

### Core Requirements
1.  **Authenticate with GitHub API**:
    *   *Verify*: Check `backend/.env` for `GITHUB_TOKEN` or enter a token in the Frontend UI.
    *   *Action*: Search for a private repository (if your token has access) to confirm authentication works.
2.  **Fetch Open Pull Requests**:
    *   *Action*: Enter `vercel/next.js` in the search bar and click "Fetch PRs".
    *   *Verify*: A list of open PR cards appears.
3.  **Display Meaningful Information**:
    *   *Verify*: Each card shows Title, Number, Author Avatar, Created Date, Labels, and Draft status.
4.  **Handle Pagination**:
    *   *Action*: Search for a large repo (e.g., `facebook/react`) and scroll to the bottom of the list.
    *   *Verify*: Use the "Previous" and "Next" buttons to navigate through pages (10 items per page).
5.  **Basic Caching**:
    *   *Action*: Click "Fetch PRs" for `vercel/next.js`. Wait 5 seconds. Click "Fetch PRs" again.
    *   *Verify*: The second fetch is instant, and a yellow "CACHED" badge appears next to the item count.
6.  **Security**:
    *   *Verify*: The `.env` file is in `.gitignore`, so no secrets are committed.

### Optional Enhancements (Bonus)
7.  **Agentic Layer (MCP)**:
    *   *Action*: Navigate to [http://localhost:8001/api/agent/tools](http://localhost:8001/api/agent/tools).
    *   *Verify*: A JSON response listing `list_open_pull_requests` and `summarize_pull_request` tools.
8.  **AI Summary**:
    *   *Action*: Click the "✨ Summarize" button on any PR card.
    *   *Verify*: A formatted Markdown summary appears (requires `GEMINI_API_KEY` in `.env`).
9.  **Automated Tests**:
    *   *Action*: Run `pytest` inside the backend container.
    *   *Verify*: All tests pass.

