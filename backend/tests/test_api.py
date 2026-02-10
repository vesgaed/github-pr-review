from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from github_pull_request_status_cli.api import app
from github_pull_request_status_cli.github_api_client import OpenPullRequestsResult, PullRequestSummary
from datetime import datetime, timezone

client = TestClient(app)

def test_read_main_docs():
    response = client.get("/docs")
    assert response.status_code == 200

def test_list_user_repos_no_token():
    response = client.get("/api/user/repos")
    # Should fail because token is required
    assert response.status_code == 401
    assert response.json() == {"detail": "GitHub Token is required to list user repositories."}

@patch("github_pull_request_status_cli.api.GitHubApiClient")
def test_list_pull_requests_success(MockClient):
    # Mock the client instance
    mock_instance = MockClient.return_value
    
    # Mock return data
    mock_pr = PullRequestSummary(
        pull_request_number=1,
        title="Test PR",
        author_login="user",
        html_url="http://github.com/owner/repo/pull/1",
        label_names={"bug"},
        is_draft=False,
        state="open",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    mock_result = OpenPullRequestsResult(
        pull_requests=[mock_pr],
        pages_fetched=1,
        response_was_from_cache=False
    )
    
    # Setup async mock
    async def async_return():
        return mock_result
    
    mock_instance.list_open_pull_requests.side_effect = lambda **kwargs: async_return()

    response = client.get("/api/pull-requests?repository=owner/repo&token=dummy")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Test PR"
    assert data["items"][0]["labels"] == ["bug"]

@patch("github_pull_request_status_cli.api.GitHubApiClient")
def test_list_user_repos_success(MockClient):
    mock_instance = MockClient.return_value
    
    # Mock return data
    mock_repos = [
        {
            "full_name": "owner/repo1",
            "private": False,
            "html_url": "http://github.com/owner/repo1",
            "description": "Desc",
            "updated_at": "2023-01-01T00:00:00Z"
        }
    ]
    
    async def async_return():
        return mock_repos
    
    mock_instance.list_user_repositories.side_effect = lambda **kwargs: async_return()

    response = client.get("/api/user/repos?token=valid_token")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["full_name"] == "owner/repo1"
