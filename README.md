# GitHub Pull Request Status CLI/Dashboard

## Overview

This application is a **Pull Request Status Explorer** designed to help developers quickly understand the state of a GitHub repository. It fetches open pull requests, displays them with rich context (author avatars, body snippets, labels), and provides advanced features like **AI-powered Summaries** and **Statistical Visualization**.

It was built as a response to the "Senior Full-Stack Engineer Take-Home Exercise".

## ✨ Key Features

### Core Requirements
*   **Authentication**: Secure integration with GitHub API using Personal Access Tokens (PAT).
*   **Data Fetching**: Retrives open PRs with key metadata (title, author, labels, draft status, timestamps).
*   **Pagination**: Efficiently handles large repositories by fetching multiple pages.
*   **Caching**: In-memory caching layer (TTL: 90s) to perform smoothly and respect GitHub API rate limits.
*   **Search**: Filter by any public repository (e.g., `vercel/next.js`, `facebook/react`).

### Optional Enhancements (Implemented)
*   **🤖 AI Summaries**: Integrates with **Google Gemini** (via `google-generativeai`) to provide natural language summaries of pull requests. Configurable model selection.
*   **📊 Stats Dashboard**: Interactive visualizations using `recharts` to show PR label distribution and top contributors.
*   **🕵️ Agentic API**: Exposes an MCP (Model Context Protocol) compatible endpoint at `/api/agent/tools`, allowing AI agents to discover and use the backend tools programmatically.
*   **🎨 UI Polish**: A modern, responsive "Glassmorphism" design using Tailwind CSS v4, with dark mode, skeletons, and smooth transitions.

## 🏗 Architecture & Design Decisions

### Backend: Python (FastAPI)
*   **Framework**: FastAPI was chosen for its speed, automatic Swagger/OpenAPI documentation, and native async support (critical for handling multiple upstream API calls).
*   **Structure**:
    *   `api.py`: Entry point and route definitions.
    *   `github_api_client.py`: Encapsulates all GitHub interaction logic.
    *   `cache.py`: Implements a reusable `TimeToLiveCache` protocol, allowing for easy swapping of cache backends (e.g., to Redis) in the future without changing business logic.
    *   `llm_client.py`: dedicated client for Gemini AI interaction, isolating third-party AI dependencies.
    *   `mcp_tools.py`: Definitions for the Agentic layer.
*   **Data Validation**: Pydantic models ensure type safety and automatic validation of external API responses.

### Frontend: React (Vite)
*   **Build Tool**: Vite for lightning-fast HMR and building.
*   **Styling**: **Tailwind CSS v4** for utility-first styling. I chose this to iterate rapidly on the UI without context-switching to CSS files.
*   **Component Library**: Built from scratch using raw Tailwind for maximum control and "spectacular" visuals, rather than relying on a heavy UI kit. `lucide-react` provides consistent iconography.
*   **Markdown Rendering**: `react-markdown` is used to safely render the rich text returned by the AI.

### Infrastructure: Docker
*   **Containerization**: Both services are Dockerized to ensure consistent execution across environments.
*   **Orchestration**: `docker-compose` manages the multi-container setup (Backend + Frontend) and networking.

## 🚀 Installation & Usage

### Prerequisites
*   Docker & Docker Compose installed.
*   A GitHub Personal Access Token (Read-only for public repos is sufficient).
*   (Optional) A Google Gemini API Key for AI summaries.

### Quick Start

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd github-pull-request-status-cli
    ```

2.  **Configure Environment**:
    
    The backend requires environment variables. Create a `.env` file in the `backend/` directory based on `.env.example`.

    ```bash
    cp backend/.env.example backend/.env
    ```

    Edit `backend/.env` with your credentials:

    ```env
    # Required for higher rate limits
    GITHUB_TOKEN=ghp_your_github_token_here

    # Required for AI Summaries
    GEMINI_API_KEY=AIzaSy_your_gemini_key_here
    
    # Optional: Select your model (default: gemini-1.5-flash)
    GEMINI_MODEL=gemini-1.5-pro
    ```

3.  **Run with Docker**:
    ```bash
    docker-compose up --build
    ```

4.  **Access the Application**:
    *   **Frontend**: [http://localhost:3001](http://localhost:3001)
    *   **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🧪 Testing

To run the backend test suite:

```bash
cd backend
pip install -r requirements.txt
pytest
```

## 📝 Self-Evaluation (Rubric)

*   **Core Functionality**: ✅ Works end-to-end. Fetches PRs, handles pagination, caches results.
*   **Code Quality**: ✅ Structured, typed (Python type hints + TypeScript), and modular.
*   **Communication**: ✅ Clear README, documented API, and helpful error messages.
*   **Enhancements**: ✅ AI Summaries, Stats Dashboard, and Agent API are fully implemented and working.

## 🔮 Future Improvements

With more time, I would:
*   Implement a **Redis** cache backend for persistence across restarts.
*   Add **Server-Side Pagination** for the frontend to handle repositories with thousands of PRs (currently fetches 'Max Pages' and paginates in memory/UI).
*   Add E2E tests using **Playwright**.
*   Implement a proper CI/CD pipeline (GitHub Actions).

---
*Built by [Edves] for the Senior Full-Stack Engineer Take-Home Exercise.*
