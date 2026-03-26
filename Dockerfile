# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy uv binary from official uv image.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Dependencies first. Keep this layer stable for better cache reuse.
# README.md is required by hatchling (`readme = "README.md"`).
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --group dev --frozen

# Copy source separately so dependency cache remains valid across code changes.
COPY .gitignore main.py ./
COPY src ./src
COPY tests ./tests

# Keep checks as separate layers for better incremental build behavior.
RUN uv run ruff check .
RUN uv run ruff format --check .
RUN uv run pytest -v
RUN uv build

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG APP_USER=clible
ARG APP_UID=10001
ARG APP_GID=10001

# Use explicit UID/GID so file ownership remains predictable across
# local Docker runs, CI, and Kubernetes/container runtimes.
RUN groupadd --gid "${APP_GID}" "${APP_USER}" \
    && useradd --uid "${APP_UID}" --gid "${APP_GID}" \
       --create-home --home-dir "/home/${APP_USER}" \
       --shell /usr/sbin/nologin "${APP_USER}" \
    && mkdir -p /app \
    && chown "${APP_USER}:${APP_USER}" /app

WORKDIR /app

# Copy only the built wheel from builder stage to keep runtime image minimal
# and avoid shipping source/tests/tooling.
COPY --from=builder --chown=${APP_USER}:${APP_USER} /app/dist/*.whl /tmp/

USER ${APP_USER}:${APP_USER}
# Install into a user-owned virtual environment instead of system site-packages,
# so runtime does not require root privileges.
RUN python -m venv "/home/${APP_USER}/.venv" \
    && "/home/${APP_USER}/.venv/bin/pip" install --no-cache-dir /tmp/*.whl \
    && rm /tmp/*.whl

# Expose the venv binaries (`clible`, `python`) as default executables.
ENV PATH="/home/${APP_USER}/.venv/bin:${PATH}"

ENTRYPOINT ["clible"]
CMD ["--help"]