# Chronicler

Overview: A tool to help develop ideas for a fantasy novel; integrates with Obsidian vault; supports AI-assisted idea generation and character chat. Prior issues include data syncing with Obsidian and UI open/read problems.

Tech Stack:
- Backend/AI: Python/Local Ollama and/or OpenRouter
- Storage: Obsidian vault (read/write) via file system
- UI: Web-based (to be designed)

Current State:
- Inconsistent syncing; data being misinterpreted as characters/places

Startup:
- Single-command startup with docker-compose or Makefile (dev)
- Secrets via .env; persistent data as needed

How to Run (starter):
- make dev-meeting  (start Meeting Transcriber only)
- make dev  (start all projects)

Notes:
- Starter README; update as project evolves.

---
## Phase 2 Scaffolding: CI, Tests, and Onboarding

This section details the setup for continuous integration, testing, and essential project documentation.

### Continuous Integration (CI)

**GitHub Actions:** A CI workflow is configured to run automated checks on every push and pull request to the main branch.

*   **Location:** `.github/workflows/ci.yml` in the repository root.
*   **Jobs:**
    *   `backend`: Runs Python tests and linting.
    *   `lint`: Checks Python code style.
*   **Trigger:** Pushes to `main` branch and pull requests targeting `main`.
*   **Onboarding:** This workflow provides a baseline for code quality assurance. You can extend it with more specific checks or deployment steps as the project matures.

### Testing

**Local Testing:** You can run tests locally to ensure code changes adhere to standards before committing.

*   **Backend:** Use pytest.
    ```bash
    cd /home/dmoniz/projects/chronicler/backend
    pytest tests/backend/test_basic.py
    ```
*   **Frontend:** (Placeholder for future frontend tests)
    ```bash
    # Example for if a frontend exists and uses Jest
    # cd /home/dmoniz/projects/chronicler/frontend
    # npm test
    ```
*   **Linting:** Ensure code adheres to style guides.
    *   Python: Black, Ruff, isort (run automated checks via CI or locally).
    *   TypeScript/JavaScript: ESLint, Prettier (if a frontend is added).

### Model Planning

**Centralized Policy:** The primary model strategy and fallbacks are managed in a central `MODEL_PLAN.md` at the workspace root (`/home/dmoniz/.openclaw/workspace-coding/MODEL_PLAN.md`). This file outlines your preferred model settings for development.

### Running Locally

1.  **Start services:** Use `make dev` from the workspace root to start all projects, or `make dev-chronicler` to start only Chronicler.
2.  **Run tests:** Execute `pytest` in the `backend/tests` directory.
3.  **Lint:** `black`, `ruff`, `isort` for the backend.

'team' Phase 2 progress:
- README_CHRONICER.md updated with Phase 2 status, CI/test setup, and model plan reference.
- CI workflow (`.github/workflows/ci.yml`) and test skeleton created for the Chronicler backend.
