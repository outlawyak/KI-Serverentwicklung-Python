# syntax=docker/dockerfile:1

# App image with two targets, both on Debian 13 "trixie" (see tasks.md, Phase 4):
#   dev:  debian:trixie-slim, with shell and package manager (apt)
#   prod: distroless cc-debian13, without shell and package manager
# Build one target: docker build --target prod -t ai-server:prod .

# uv binary, same version as used locally.
FROM ghcr.io/astral-sh/uv:0.13.0 AS uv

# Build stage: install Python 3.15 and the runtime dependencies with uv.
# Python and the virtual environment live under /opt, so both runtime stages
# can copy them to the same paths and the venv's interpreter link stays valid.
FROM debian:trixie-slim AS build
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_PYTHON_INSTALL_DIR=/opt/python \
    UV_PYTHON_PREFERENCE=only-managed \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
WORKDIR /app
# Dependencies first, so this layer is cached as long as the lock file is unchanged.
COPY pyproject.toml uv.lock .python-version ./
RUN uv python install && uv sync --locked --no-dev
COPY app ./app

# Dev: shell and apt are available for debugging inside the container.
FROM debian:trixie-slim AS dev
RUN useradd --system --no-create-home app
COPY --from=build /opt/python /opt/python
COPY --from=build /opt/venv /opt/venv
COPY --from=build /app/app /app/app
WORKDIR /app
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Prod: only glibc and the C/C++ runtime libraries, no shell, no apt.
# The nonroot tag runs as user 65532.
FROM gcr.io/distroless/cc-debian13:nonroot AS prod
COPY --from=build /opt/python /opt/python
COPY --from=build /opt/venv /opt/venv
COPY --from=build /app/app /app/app
WORKDIR /app
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
# Exec form with absolute path, since there is no shell to resolve commands.
ENTRYPOINT ["/opt/venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
