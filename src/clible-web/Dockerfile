# syntax=docker/dockerfile:1.7

ARG BASE_IMAGE=europe-north1-docker.pkg.dev/clible-v2dev/clible/clible-v2dev@sha256:f0cfb65b18e5a8ff2eca9edea7ce316c569758db330793a059bb4c1679bf44b5
FROM ${BASE_IMAGE}

LABEL org.opencontainers.image.title="clible-web" \
      org.opencontainers.image.description="Clible Bible study tool – web interface" \
      org.opencontainers.image.source="https://github.com/vivaldev/clible-v2"

# Base image sets ENTRYPOINT to `clible`; override so npm scripts run normally.
ENTRYPOINT []

# Ensure the clible CLI bundled in the base image is on PATH at runtime.
ENV PATH="/home/clible/.venv/bin:${PATH}"

# 1. SYSTEM SETUP (ROOT)
# Switch to root only for installation steps.
USER root

ARG DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Replace the CLI from the base image with this repository checkout.
# Build context must be the repo root: docker build -f src/clible-web/Dockerfile .
COPY pyproject.toml README.md /opt/clible-pkg/
COPY src/clible /opt/clible-pkg/src/clible
RUN /home/clible/.venv/bin/pip install --no-cache-dir --upgrade "/opt/clible-pkg" \
    && rm -rf /opt/clible-pkg

# Create writable data directory for the CLI; SQLite WAL requires a writable location.
RUN mkdir -p /home/clible/.clible-data && chown clible:clible /home/clible/.clible-data
ENV CLIBLE_DATA_DIR=/home/clible/.clible-data
ENV CLIBLE_USER_DATA_DIR=/app/web/data

# 2. WEB APP DIRECTORY
WORKDIR /app/web
RUN mkdir -p data && chown -R clible:clible /app/web

# 3. SWITCH TO NON-ROOT USER
# All subsequent steps run as the restricted clible user.
USER clible

# 4. DEPENDENCIES
COPY --chown=clible:clible src/clible-web/package*.json ./
RUN --mount=type=cache,target=/home/clible/.npm,uid=10001,gid=10001 \
    npm ci

# 5. BUILD WEB APP
COPY --chown=clible:clible src/clible-web/ .
ENV NODE_ENV=production
RUN npm run build

# 6. VERIFY CLI IS AVAILABLE
RUN clible --help >/dev/null

# 7. RUNTIME
# users.db and sessions are written here; mount a named volume to persist across restarts.
VOLUME ["/app/web/data"]

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s \
    CMD curl -f http://localhost:3000/health || exit 1

CMD ["npm", "start"]
