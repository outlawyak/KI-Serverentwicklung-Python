# Checklist: "Python Project"
(Course: AI-Assisted Server Development)

## Versions
- Python 3.15.0
- PostgreSQL 18 or 19 (19 currently in beta, release in October)

## Prerequisites
- Relational DB with PostgreSQL as a Docker container
  - 1:1 and 1:N relationship
  - DB browser
- Empty Git repository:
  "Commit early, commit often" -> incremental development through prompts
  - Conventional commits

## Tooling
- `pyproject.toml` as replacement for `requirements.txt` and as the central
  configuration, including settings for:
  - **uv**: Python package manager
  - **ruff**: linting and formatting
  - **Type checker**: one of ty, pyrefly or pyright
- `.editorconfig` for universal IDE configuration
- Docker: `docker-bake.hcl` to differentiate images
- GitHub Actions workflow (CI), triggered on push

## App Server
- REST via FastAPI, including dependency injection and Pydantic for responses
  - GET requests: path or query parameters, also conditional GET requests
  - POST request with validation via Pydantic
  - PUT request with validation and avoidance of lost updates
- DB access via SQLAlchemy

## "Testing": GET and POST
- Recommended: an API client such as Bruno, Postman or Thunder Client
- Alternative: pytest (integration tests are sufficient)

## Optional (crossed out by the lecturer, not mandatory)
- Keycloak (caution with 26.8.0 as a hardened image) as a Docker container:
  1 realm with 1 client and at least 1 user and 1 role
- Security via dependency injection

## Checklist
- [x] Team registered by email
- [x] Python 3.15.0 set up
- [x] PostgreSQL container with 1:1 and 1:N relationships
- [x] DB browser connected
- [x] Git repo created, incremental conventional commits
- [x] pyproject.toml with uv, ruff, type checker configured
- [x] .editorconfig added
- [x] docker-bake.hcl for image variants
- [x] GitHub Actions workflow running on push
- [x] FastAPI with dependency injection and Pydantic responses
- [x] GET (path/query params, conditional GET)
- [x] POST with validation
- [x] PUT with validation and lost-update protection
- [x] SQLAlchemy for DB access
- [x] Tests for GET and POST
