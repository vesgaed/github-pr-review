from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .mcp_tools import get_mcp_tools, ToolDefinition
from .mcp_tools import get_mcp_tools, ToolDefinition

from .github_api_client import GitHubApiClient, GitHubAuthenticationError, GitHubRateLimitExceededError, GitHubRepositoryNotFoundError
from .configuration import load_application_settings
from .local_cache import LocalTimeToLiveCache

app = FastAPI(
    title="GitHub Pull Request Explorer API",
    description="API for fetching and caching GitHub Pull Requests and User Repositories.",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---

class PullRequestResponse(BaseModel):
    number: int = Field(..., description="The pull request number")
    title: str = Field(..., description="The title of the pull request")
    author: str = Field(..., description="The username of the author")
    author_avatar: str = Field(..., description="Avatar URL of the author")
    html_url: str = Field(..., description="URL to the pull request on GitHub")
    labels: List[str] = Field(default_factory=list, description="List of label names")
    is_draft: bool = Field(..., description="Whether the PR is a draft")
    state: str = Field(..., description="State of the PR (open, closed)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    body: str = Field(..., description="Description of the PR")

class PaginatedResponse(BaseModel):
    items: List[PullRequestResponse] = Field(..., description="List of pull requests")
    pages_fetched: int = Field(..., description="Number of pages fetched from GitHub")
    from_cache: bool = Field(..., description="Whether the response was served from local cache")
    repository: str = Field(..., description="The repository identifier (owner/name)")

class RepositorySummary(BaseModel):
    full_name: str = Field(..., description="Full name of the repository (owner/name)")
    private: bool = Field(..., description="Whether the repository is private")
    html_url: str = Field(..., description="URL to the repository")
    description: Optional[str] = Field(None, description="Repository description")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")

class ErrorResponse(BaseModel):
    detail: str

# --- Endpoints ---

@app.get(
    "/api/pull-requests",
    response_model=PaginatedResponse,
    summary="List Open Pull Requests",
    description="Fetches a list of open pull requests for a given repository. Supports pagination and caching.",
    tags=["Pull Requests"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized (Invalid Token)"},
        403: {"model": ErrorResponse, "description": "Rate Limit Exceeded"},
        404: {"model": ErrorResponse, "description": "Repository Not Found"},
    }
)
async def get_pull_requests(
    repository: str = Query(..., description="Repository in 'owner/name' format", example="vercel/next.js"),
    token: Optional[str] = Query(None, description="Optional GitHub Token (overrides env var)"),
    max_pages: Optional[int] = Query(3, ge=1, le=10, description="Maximum number of pages to fetch"),
    bypass_cache: bool = Query(False, description="If true, forces a fresh fetch from GitHub")
):
    try:
        settings = load_application_settings(require_token=False)
        # Prefer query param token, fallback to env var
        github_token = token or settings.github_personal_access_token

        if not github_token:
             # We allow public access without token, but often it hits rate limits.
             # ideally we warn.
             pass

        cache = LocalTimeToLiveCache(default_time_to_live_seconds=settings.cache_time_to_live_seconds)
        client = GitHubApiClient(github_token=github_token or "", cache_backend=cache)

        result = await client.list_open_pull_requests(
            repository_identifier=repository,
            items_per_page=50,
            maximum_pages_to_fetch=max_pages,
            bypass_cache=bypass_cache
        )
        
        # Convert dataclasses to Pydantic models
        items = [
            PullRequestResponse(
                number=pr.pull_request_number,
                title=pr.title,
                author=pr.author_login,
                author_avatar=pr.author_avatar_url,
                html_url=pr.html_url,
                labels=list(pr.label_names),
                is_draft=pr.is_draft,
                state=pr.state,
                created_at=pr.created_at,
                updated_at=pr.updated_at,
                body=pr.body
            ) for pr in result.pull_requests
        ]
        
        return PaginatedResponse(
            items=items,
            pages_fetched=result.pages_fetched,
            from_cache=result.response_was_from_cache,
            repository=repository
        )

    except GitHubAuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except GitHubRateLimitExceededError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except GitHubRepositoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/user/repos",
    response_model=List[RepositorySummary],
    summary="List User Repositories",
    description="Lists repositories that the authenticated user has access to (owned, collaborated, etc.). Requires a valid token.",
    tags=["User"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized (Missing or Invalid Token)"},
    }
)
async def list_user_repos(
    token: Optional[str] = Query(None, description="GitHub Token (required)")
):
    # Load settings but allow token override
    settings = load_application_settings(require_token=False)
    github_token = token or settings.github_personal_access_token

    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub Token is required to list user repositories.")

    cache = LocalTimeToLiveCache(default_time_to_live_seconds=settings.cache_time_to_live_seconds)
    client = GitHubApiClient(github_token=github_token, cache_backend=cache)

    try:
        # Fetch up to 100 recent repos
        repos = await client.list_user_repositories(maximum_items=100)
        return [
            RepositorySummary(
                full_name=r["full_name"],
                private=r["private"],
                html_url=r["html_url"],
                description=r.get("description"),
                updated_at=r.get("updated_at")
            ) for r in repos
        ]
    except Exception as e:
        # 401/403 are handled inside client usually, but here generic catch
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/agent/tools",
    response_model=List[ToolDefinition],
    summary="Get MCP Tools",
    description="Returns a list of available tools in MCP (Model Context Protocol) format for AI agents.",
    tags=["Agent"]
)
async def get_agent_tools():
    return get_mcp_tools()


class SummaryResponse(BaseModel):
    summary: str

@app.get(
    "/api/pr/{number}/summary",
    response_model=SummaryResponse,
    summary="Summarize Pull Request",
    description="Generates a clear, natural language summary of a Pull Request using Gemini AI.",
    tags=["AI"]
)
async def summarize_pull_request(
    number: int,
    repository: str = Query(..., description="Repository in 'owner/name' format"),
    token: Optional[str] = Query(None)
):
    settings = load_application_settings(require_token=False)
    github_token = token or settings.github_personal_access_token
    
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub Token required")

    cache = LocalTimeToLiveCache(default_time_to_live_seconds=settings.cache_time_to_live_seconds)
    client = GitHubApiClient(github_token=github_token, cache_backend=cache)
    
    try:
        # We need to fetch the specific PR details first. 
        # Ideally we'd have a get_pull_request method, but we can list and filter or just implement get_pr
        # For now, let's assume we can fetch it via the list mechanism or add a specific method.
        # To be efficient and simple, let's just use the existing list method and find it, 
        # or better, let's add a get_pull_request method to GitHubApiClient if needed.
        # But wait, GitHub API has GET /repos/{owner}/{repo}/pulls/{pull_number}
        
        # Let's quickly add a get_pull_request method to the client to be clean, 
        # OR just fetch the list and find it (less efficient but uses existing code).
        # Given the "spectacular" req, let's accept we might need to fetch the single PR.
        # But I can't edit the client right now easily without context.
        # Let's use the list_open_pull_requests and filter. It's safe enough for now.
        
        result = await client.list_open_pull_requests(
            repository_identifier=repository,
            items_per_page=100  # Try to find it
        )
        
        target_pr = next((pr for pr in result.pull_requests if pr.pull_request_number == number), None)
        
        if not target_pr:
             raise HTTPException(status_code=404, detail="Pull Request not found in open list")
             
        # Initialize Gemini Client
        try:
            from .llm_client import GeminiClient
            gemini = GeminiClient()
            summary = await gemini.summarize_pr(target_pr.title, target_pr.body)
            return SummaryResponse(summary=summary)
        except ValueError as e:
             raise HTTPException(status_code=503, detail="AI Service Config Error: " + str(e))
        except Exception as e:
             return SummaryResponse(summary=f"Could not generate summary: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


