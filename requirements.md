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
- [ ] Team registered by email
- [ ] Python 3.15.0 set up
- [ ] PostgreSQL container with 1:1 and 1:N relationships
- [ ] DB browser connected
- [ ] Git repo created, incremental conventional commits
- [ ] pyproject.toml with uv, ruff, type checker configured
- [ ] .editorconfig added
- [ ] docker-bake.hcl for image variants
- [ ] GitHub Actions workflow running on push
- [ ] FastAPI with dependency injection and Pydantic responses
- [ ] GET (path/query params, conditional GET)
- [ ] POST with validation
- [ ] PUT with validation and lost-update protection
- [ ] SQLAlchemy for DB access
- [ ] Tests for GET and POST
