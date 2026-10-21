# tasks.md

Task list for the "Python Project". Requirements: `requirements.md`.
Agent rules: `AGENTS.md`.

How to use:
- Work on one task at a time, in order
- A task is done only when its "Done when" is met
- Mark finished tasks with `[x]`, one Conventional Commit per task
- Every commit references its task ID at the end of the subject,
  e.g. `feat: add game model (T1.3)`
- **[You]** = done by the developer, **[Agent]** = done by the AI agent,
  reviewed by the developer before committing

---

## Phase 0: Preparation [You]

- [x] **T0.1 Register team**
  Email to the lecturer: name(s), student ID number, link to the Git repository.
  Done when: email sent.

- [x] **T0.2 Create Git repository**
  Create an empty GitHub repository and clone it locally.
  Done when: empty repo is cloned.

- [x] **T0.3 Add project documents**
  Add `requirements.md`, `AGENTS.md` and `tasks.md` to the repo
  (plus `CLAUDE.md` containing `@AGENTS.md` if using Claude Code).
  Done when: committed as `docs: add project requirements and agent instructions`.

- [x] **T0.4 Install Python 3.15**
  `uv python install 3.15`
  Done when: `uv run --python 3.15 python --version` prints 3.15.x.

- [x] **T0.5 Check Python 3.15 compatibility**
  In a throwaway folder, create a project with Python 3.15 and add all planned
  dependencies: fastapi, uvicorn, pydantic, sqlalchemy, a PostgreSQL driver
  (e.g. psycopg), pytest, httpx, ruff, pyright.
  Check that `uv sync` succeeds and that every package can be imported.
  Done when: all packages install and import on 3.15, or problems are noted
  in `AGENTS.md` (package, error, workaround or fallback decision).

- [x] **T0.6 Start PostgreSQL container**
  PostgreSQL 18 or 19 as a Docker container, with a persistent volume.
  Done when: container runs and accepts connections.

- [x] **T0.7 Create database schema**
  Tables as described in `AGENTS.md`:
  - `game` incl. `version` column for optimistic locking
  - `game_details` with unique FK to `game` (1:1)
  - `review` with FK to `game` (1:N)
  Insert a few test records in every table.
  Done when: schema and test data exist; SQL script is committed to the repo.

- [x] **T0.8 Connect DB browser**
  Connect a DB browser (e.g. DBeaver or pgAdmin) to the container.
  Done when: tables and test data are visible in the browser.

---

## Phase 1: Project Setup [Agent]

- [ ] **T1.1 Create pyproject.toml**
  Initialize the project with uv for Python 3.15. `pyproject.toml` replaces
  `requirements.txt` and contains the configuration for uv, ruff and pyright.
  Done when: `uv sync`, `uv run ruff check .` and `uv run pyright` run
  without errors.

- [ ] **T1.2 Add .editorconfig**
  Universal IDE configuration (indentation, line endings, charset),
  consistent with the ruff settings.
  Done when: file is committed.

- [ ] **T1.3 Add GitHub Actions workflow**
  Workflow triggered on push that runs `ruff check`, `ruff format --check`,
  `pyright` and `pytest`.
  Done when: the workflow passes on GitHub.

---

## Phase 2: Database Access [Agent]

- [ ] **T2.1 Database configuration**
  Connection settings from environment variables, SQLAlchemy engine and
  session provided via FastAPI dependency injection.
  Done when: the app starts and can open a DB session.

- [ ] **T2.2 SQLAlchemy models**
  Map the existing tables (`game`, `game_details`, `review`) incl. the 1:1
  and 1:N relationships. Do not change the schema.
  Done when: models load the test data correctly, incl. related objects.

---

## Phase 3: REST API [Agent]

- [ ] **T3.1 Pydantic response models**
  Response models for Game incl. GameDetails and Reviews.
  Done when: models are used as `response_model` in the endpoints.

- [ ] **T3.2 GET with path parameter**
  Fetch a single game by ID, 404 if not found.
  Done when: works for existing and missing IDs.

- [ ] **T3.3 GET with query parameters**
  Search/filter games via query parameters (e.g. title, genre).
  Done when: filters return the expected results.

- [ ] **T3.4 Conditional GET**
  Single-game GET supports conditional requests (e.g. ETag based on `version`
  plus `If-None-Match`, responding with 304 Not Modified).
  Done when: a repeated request with a matching header returns 304.

- [ ] **T3.5 POST with validation**
  Create a game; request body validated with Pydantic.
  Done when: valid data creates a record, invalid data is rejected with 422.

- [ ] **T3.6 PUT with validation and lost-update protection**
  Update a game; request body validated with Pydantic; concurrent updates
  are detected via `version` (e.g. `If-Match` header, 412 on mismatch).
  Done when: an update with an outdated version is rejected and does not
  overwrite data.

---

## Phase 4: Docker [Agent]

- [ ] **T4.1 Dockerfile for the app**
  Done when: the image builds and the app runs in a container.

- [ ] **T4.2 docker-bake.hcl**
  Bake file to differentiate images (which variants is still open,
  e.g. dev/prod; clarify with the lecturer).
  Done when: `docker buildx bake` builds all defined variants.

---

## Phase 5: Testing [Agent + You]

- [ ] **T5.1 pytest integration tests**
  Integration tests for GET and POST against the real database.
  Done when: `uv run pytest` passes locally and in CI.

- [ ] **T5.2 Bruno collection** [You]
  Requests for GET and POST, committed to the repo.
  Done when: all requests run successfully against the local server.

---

## Phase 6: Final Check [You]

- [ ] **T6.1 Check against requirements**
  Go through the checklist in `requirements.md` and tick every item.
  Done when: every requirement is met and all CI checks pass.

---

## Out of Scope (optional, not required)
- Keycloak and security via dependency injection
