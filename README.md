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
-   **Stats Dashboard**: Visualizations for PR labels and top contributors.
-   **Agent API**: MCP-compatible endpoint at `/api/agent/tools` for AI integration.
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
    *   **Frontend**: [http://localhost:3001](http://localhost:3001)
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
