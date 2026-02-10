from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]

def get_mcp_tools() -> List[ToolDefinition]:
    return [
        ToolDefinition(
            name="list_pull_requests",
            description="Fetch open pull requests for a specific GitHub repository. Use this to get the status of PRs.",
            input_schema={
                "type": "object",
                "properties": {
                    "repository": {
                        "type": "string",
                        "description": "The repository name in 'owner/name' format (e.g., 'vercel/next.js')."
                    },
                    "max_pages": {
                        "type": "integer",
                        "description": "Maximum number of pages to fetch (default: 3).",
                        "default": 3
                    },
                    "bypass_cache": {
                        "type": "boolean",
                        "description": "Set to true to force a fresh fetch from GitHub.",
                        "default": False
                    }
                },
                "required": ["repository"]
            }
        ),
        ToolDefinition(
            name="list_user_repositories",
            description="List repositories that the authenticated user has access to. Requires a token.",
            input_schema={
                "type": "object",
                "properties": {}
            }
        )
    ]
