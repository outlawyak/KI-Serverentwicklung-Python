# Games API

A small REST server prototype for the university course "AI-Assisted Server
Development". It manages games, their details (1:1) and reviews (1:N) in
PostgreSQL.

- Requirements: [requirements.md](requirements.md)
- Task list: [tasks.md](tasks.md)
- Instructions for AI agents: [AGENTS.md](AGENTS.md)

Built with Claude Code (Opus 5.5, reasoning effort medium). The developer
reviewed every change before committing it.

## Stack

| Area        | Tool                                                    |
| ----------- | ------------------------------------------------------- |
| Language    | Python 3.15, uv                                         |
| Web         | FastAPI, Pydantic                                       |
| Database    | PostgreSQL 18, SQLAlchemy 2, psycopg 3                  |
| Quality     | ruff, pyright, pytest                                   |
| Images / CI | Docker (`docker-bake.hcl`), [GitHub Actions](.github/workflows/ci.yml) |

## Development Setup

Requires [uv](https://docs.astral.sh/uv/) 0.13+ and Docker with Compose and
Buildx. uv installs Python 3.15 itself.

```sh
git clone https://github.com/outlawyak/KI-Serverentwicklung-Python.git
cd KI-Serverentwicklung-Python
uv sync
docker compose up --wait
uv run uvicorn app.main:app --reload
```

The server runs on <http://localhost:8000>, with Swagger UI at `/docs` and a
health check at `/health`.

On its first start, the database is created from `db/schema.sql` (schema and
test data). `docker compose down` stops it and keeps the data;
`docker compose down -v` deletes the data, so the next `up` starts fresh.

### Configuration

The app reads the database connection from these environment variables.
The defaults match `compose.yaml`, which reads the same variables (except
`POSTGRES_HOST`).

| Variable            | Default     |
| ------------------- | ----------- |
| `POSTGRES_HOST`     | `localhost` |
| `POSTGRES_PORT`     | `5432`      |
| `POSTGRES_USER`     | `app`       |
| `POSTGRES_PASSWORD` | `app`       |
| `POSTGRES_DB`       | `games`     |

### Checks

All of these must pass before every commit, and CI runs them on every push.
The tests need the running database; each test is rolled back afterwards.

```sh
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

## Docker Images

`docker-bake.hcl` builds two images from the multi-stage `Dockerfile`. Both
contain only the runtime dependencies and run as a non-root user.

| Image            | Base image                              | Shell |
| ---------------- | --------------------------------------- | ----- |
| `ai-server:dev`  | `debian:trixie-slim`                    | yes   |
| `ai-server:prod` | `gcr.io/distroless/cc-debian13:nonroot` | no    |

To build an image and run it against the Compose database:

```sh
docker compose up --wait   # database and its network ai-server_default
docker buildx bake         # builds ai-server:dev and ai-server:prod
docker run --rm --name ai-server -p 8000:8000 \
  --network ai-server_default -e POSTGRES_HOST=db ai-server:prod
```

For the dev image, use `ai-server:dev` in the last command;
`docker exec -it ai-server bash` then opens a shell in it. The prod image has
no shell, so use `docker logs` and `/health` instead.
In production, set all `POSTGRES_*` variables with a real password. The
database needs the schema from `db/schema.sql`; the app does not create
tables.

## API

| Method | Path                   | Description                                                |
| ------ | ---------------------- | ---------------------------------------------------------- |
| GET    | `/health`              | Checks the DB connection                                   |
| GET    | `/games?title=&genre=` | Lists games, optionally filtered                           |
| POST   | `/games`               | Creates a game (422 for invalid data)                      |
| GET    | `/games/{id}`          | Returns one game with an ETag (304 with `If-None-Match`)   |
| PUT    | `/games/{id}`          | Updates a game (`If-Match` required: 428, 412 on conflict) |
| GET    | `/games/{id}/details`  | Returns the game's details                                 |
| POST   | `/games/{id}/details`  | Creates the details (409 if they already exist)            |
| GET    | `/games/{id}/reviews`  | Lists the game's reviews                                   |
| POST   | `/games/{id}/reviews`  | Adds a review                                              |

### Conditional GET and lost-update protection

The ETag of a game is its `version` column, which increases with every
update.

```sh
# Read a game and note its ETag, e.g. "0"
curl -i http://localhost:8000/games/1

# Same ETag: 304 Not Modified, no body
curl -i -H 'If-None-Match: "0"' http://localhost:8000/games/1

# Update with the ETag you last saw; an outdated ETag returns 412
curl -i -X PUT http://localhost:8000/games/1 \
  -H 'Content-Type: application/json' \
  -H 'If-Match: "0"' \
  -d '{"title": "New Title", "genre": "RPG", "release_date": "2024-01-01"}'
```
