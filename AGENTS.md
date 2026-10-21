# AGENTS.md

Instructions for AI coding agents working in this repository.

## Project
A small REST server prototype in Python for the university course
"AI-Assisted Server Development". The full requirements are in
`requirements.md`; read it before starting any task.

Tasks are tracked in `tasks.md`. Only work on the task you are asked to do,
and mark it as done (`[x]`) once its "Done when" condition is met.

The developer is responsible for every line of code. Keep changes small,
understandable and easy to review.

## Stack (fixed, do not substitute)
- Python 3.15
- uv as package manager, `pyproject.toml` as the only dependency and tool
  configuration (no `requirements.txt`)
- FastAPI with dependency injection, Pydantic for request/response models
- SQLAlchemy for database access
- PostgreSQL (Docker container, already set up)
- ruff for linting and formatting
- pyright as type checker
- pytest for integration tests, Bruno as API client
- Docker with `docker-bake.hcl` for image variants
- GitHub Actions for CI

## Data Model
The database schema already exists. Map it, do not redesign it.

- **Game**: id, title, genre, release_date, version
- **GameDetails** (1:1 with Game): id, game_id (unique FK), description,
  developer, publisher
- **Review** (1:N, one Game has many Reviews): id, game_id (FK), rating,
  comment, created_at

`Game.version` is used for optimistic locking (lost-update protection on PUT).

## API Requirements
- GET with path or query parameters, including conditional GET
- POST with Pydantic validation
- PUT with validation and lost-update protection

## Workflow
- Work in small, incremental steps: one task per prompt, one commit per task
- Use Conventional Commits (`feat:`, `fix:`, `chore:`, `test:`, `docs:`, ...)
- Before each commit, all of these must pass:
  - `uv run ruff check .`
  - `uv run ruff format --check .`
  - `uv run pyright`
  - `uv run pytest`
- Do not add dependencies without saying why
- If a requirement is unclear, ask instead of guessing

## Out of Scope
- Keycloak, authentication and authorization are not required.
  Do not add them unless explicitly asked.
