# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./
COPY main.py ./
COPY src ./src
COPY tests ./tests

RUN uv sync --all-groups --frozen
RUN uv run ruff check .
RUN uv run ruff format --check .
RUN uv run pytest -v
RUN uv build

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /app/dist/*.whl /tmp/clible.whl
RUN pip install --no-cache-dir /tmp/clible.whl && rm /tmp/clible.whl

ENTRYPOINT ["clible"]
CMD ["--help"]
