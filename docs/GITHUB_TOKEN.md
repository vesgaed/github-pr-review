# How to Generate a GitHub Token

To fully utilize this application, especially for accessing private repositories or avoiding rate limits, you need a Personal Access Token (Classic).

## Steps

1.  Log in to your GitHub account.
2.  Navigate to **Settings** > **Developer settings** > **Personal access tokens** > **Tokens (classic)**.
3.  Click **Generate new token (classic)**.
4.  **Note**: Give it a descriptive name (e.g., "PR Explorer").
5.  **Scopes**:
    *   **Public Repos Only**: You do NOT need to check any scopes. Just generate the token.
    *   **Private Repos**: Check the `repo` box (Full control of private repositories).
6.  Click **Generate token**.
7.  **Copy the token** immediately (starts with `ghp_...`). You won't be able to see it again.

## Usage in App

You can use the token in two ways:

1.  **Environment Variable**: Create a `.env` file in `backend/`:
    ```env
    GITHUB_TOKEN=ghp_your_token_here
    ```
2.  **UI Input**: Paste it directly into the "GitHub Token" field in the web interface.
