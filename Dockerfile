# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Kopioi uv valmiista imagesta — ei pip install -vaihetta
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

# Jokainen tarkistus omalla layerillaan
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

RUN groupadd --gid "${APP_GID}" "${APP_USER}" \
    && useradd --uid "${APP_UID}" --gid "${APP_GID}" \
       --create-home --home-dir "/home/${APP_USER}" \
       --shell /usr/sbin/nologin "${APP_USER}" \
    && mkdir -p /app \
    && chown "${APP_USER}:${APP_USER}" /app

WORKDIR /app

COPY --from=builder --chown=${APP_USER}:${APP_USER} /app/dist/*.whl /tmp/

USER ${APP_USER}:${APP_USER}
RUN python -m venv "/home/${APP_USER}/.venv" \
    && "/home/${APP_USER}/.venv/bin/pip" install --no-cache-dir --upgrade "pip>=25.3" \
    && "/home/${APP_USER}/.venv/bin/pip" install --no-cache-dir /tmp/*.whl \
    && rm /tmp/*.whl

ENV PATH="/home/${APP_USER}/.venv/bin:${PATH}"

ENTRYPOINT ["clible"]
CMD ["--help"]