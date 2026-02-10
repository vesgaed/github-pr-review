from typing import List, Dict, Any
from pydantic import BaseModel, Field

class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]

def get_mcp_tools() -> List[ToolDefinition]:
    """
    Returns a list of tools available for AI agents in MCP format.
    """
    return [
        ToolDefinition(
            name="list_open_pull_requests",
            description="Fetches a list of open pull requests for a given repository. Useful for understanding current work in progress.",
            input_schema={
                "type": "object",
                "properties": {
                    "repository": {
                        "type": "string",
                        "description": "The repository in 'owner/name' format (e.g., 'vercel/next.js')"
                    },
                    "max_pages": {
                        "type": "integer",
                        "description": "Maximum number of pages to fetch (default: 3)",
                        "default": 3
                    }
                },
                "required": ["repository"]
            }
        ),
        ToolDefinition(
            name="summarize_pull_request",
            description="Generates a natural language summary of a specific Pull Request using LLM.",
            input_schema={
                "type": "object",
                "properties": {
                    "number": {
                        "type": "integer",
                        "description": "The pull request number"
                    },
                    "repository": {
                        "type": "string",
                        "description": "The repository identifier"
                    }
                },
                "required": ["number", "repository"]
            }
        ),
        ToolDefinition(
            name="list_user_repositories",
            description="Lists repositories that the authenticated user has access to.",
            input_schema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]
