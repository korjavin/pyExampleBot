# Telegram Bot Project Plan

This document outlines the plan to create a Python Telegram bot that interacts with an OpenAI-compatible LLM, runs in Docker, and has CI/CD via GitHub Actions.

## Requirements Summary

*   **Functionality:** Respond to messages mentioning the bot by name/login, forward the message text to an LLM via an OpenAI-compatible API, and reply with the LLM's response.
*   **Mention Handling:** Dynamically fetch bot name/username from Telegram API to detect mentions.
*   **Empty Messages:** Reply with "i don't see text" if the message has no text content.
*   **Configuration:** Use environment variables for `TELEGRAM_BOT_TOKEN`, `OPENAI_BASEURL`, `OPENAI_TOKEN`, `SYSTEM_MSG`.
*   **LLM Interaction:** Include `SYSTEM_MSG` in the prompt sent to the LLM.
*   **Deployment:** Run the bot inside a Docker container.
*   **CI/CD:** Use GitHub Actions to build the Docker image and push it to GitHub Container Registry (ghcr.io) for the `github.com/korjavin/pyExampleBot` repository.
*   **Documentation:** Create a `README.md` with architecture diagrams, setup instructions, and usage details.

## Proposed Libraries

*   **Telegram:** `python-telegram-bot`
*   **OpenAI API:** `openai`
*   **Environment Variables:** `python-dotenv`

## Development Plan

**Phase 1: Project Setup & Core Logic**

1.  **Initialize Project Structure:**
    *   `bot.py`: Main application script.
    *   `requirements.txt`: Python dependencies.
    *   `.env.example`: Template for environment variables.
    *   `.gitignore`: Specifies intentionally untracked files that Git should ignore.
2.  **Implement Bot Core (`bot.py`):**
    *   Load environment variables.
    *   Set up `python-telegram-bot` application.
    *   Define message handler:
        *   Fetch bot details (`bot.get_me()`).
        *   Check for mentions using fetched name/username.
        *   Handle empty messages ("i don't see text").
        *   If mentioned and text exists:
            *   Initialize `openai` client.
            *   Construct LLM prompt (System Message + User Message).
            *   Call LLM API.
            *   Reply to the original Telegram message.
        *   Include error handling.
    *   Register message handler.
    *   Start bot polling.
3.  **Define Dependencies (`requirements.txt`):**
    *   `python-telegram-bot[job-queue]`
    *   `openai`
    *   `python-dotenv`

**Phase 2: Containerization & CI/CD**

4.  **Create Dockerfile:**
    *   Use `python:3.10-slim` base image.
    *   Install dependencies from `requirements.txt`.
    *   Copy application code.
    *   Set `CMD ["python", "bot.py"]`.
5.  **Set up GitHub Actions Workflow (`.github/workflows/docker-publish.yml`):**
    *   Trigger on push to `main` branch.
    *   Job: `build_and_push`
        *   Checkout code.
        *   Login to `ghcr.io`.
        *   Setup Docker Buildx.
        *   Build and tag image (`ghcr.io/korjavin/pyExampleBot:latest`, `ghcr.io/korjavin/pyExampleBot:<sha>`).
        *   Push image to `ghcr.io`.

**Phase 3: Documentation**

6.  **Write README.md:**
    *   Project Title & Description.
    *   Architecture (including diagrams below).
    *   Environment Variables (`.env.example`).
    *   Setup & Running (Local & Docker).
    *   GitHub Actions CI/CD explanation.

## Architecture Diagrams

### Component Diagram

```mermaid
graph TD
    User -- Interacts via Telegram --> TelegramAPI[Telegram API]
    TelegramAPI -- Sends Update --> BotApp[Python Bot App (in Docker)]
    BotApp -- Fetches Bot Info --> TelegramAPI
    BotApp -- Reads Env Vars --> HostOS[Host OS/Docker Env]
    BotApp -- Uses OpenAI Client --> OpenAI_API[OpenAI Compatible API]
    BotApp -- Sends Reply --> TelegramAPI

    subgraph Docker Container
        BotApp
    end

    subgraph CI/CD
        GitHubRepo[GitHub Repo: korjavin/pyExampleBot] -- Triggers --> GitHubActions[GitHub Actions]
        GitHubActions -- Builds & Pushes --> GHCR[GitHub Container Registry (ghcr.io)]
        GitHubActions -- Uses Secrets --> GitHubRepo
    end

    GHCR -- Image Pulled By --> DockerHost[Docker Host for Deployment]
    DockerHost -- Runs --> DockerContainer
```

### Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Telegram
    participant BotApp
    participant OpenAI_API

    User->>Telegram: Sends message mentioning @BotLogin
    Telegram->>BotApp: Forwards message update
    BotApp->>BotApp: Get self.first_name, self.username
    BotApp->>BotApp: Check if message text exists & mentions bot
    alt Message is valid and mentions bot
        BotApp->>BotApp: Load SYSTEM_MSG from Env
        BotApp->>OpenAI_API: Request chat completion (SYSTEM_MSG + User Text)
        OpenAI_API-->>BotApp: LLM Response
        BotApp->>Telegram: Send reply to original message
        Telegram-->>User: Shows bot's reply
    else Message has no text
         BotApp->>Telegram: Send reply "i don't see text"
         Telegram-->>User: Shows "i don't see text"
    else Message does not mention bot
        BotApp->>BotApp: Ignore message
    end