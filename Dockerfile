# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy uv from the official image instead of installing it with pip.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Dependencies first — these layers are cached unless pyproject.toml/uv.lock/README.md change
# README.md is required by hatchling during build (pyproject.toml: readme = "README.md")
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --all-groups --frozen

# Code copied separately — does not invalidate the above cache
COPY .gitignore main.py ./
COPY src ./src
COPY tests ./tests

# Keep each check in its own layer so failures are easy to identify.
RUN uv run ruff check .
RUN uv run ruff format --check .
RUN uv run pytest -v
RUN uv build

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /app/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

ENTRYPOINT ["clible"]
CMD ["--help"]