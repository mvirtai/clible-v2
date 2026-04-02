# syntax=docker/dockerfile:1.7

# 1. BUILD ARGUMENTS
# Sallitaan imagen polun antaminen rakennusvaiheessa. Oletuksena nykyinen image.
ARG BASE_IMAGE=europe-north1-docker.pkg.dev/clible-v2dev/clible/clible-v2dev@sha256:f0cfb65b18e5a8ff2eca9edea7ce316c569758db330793a059bb4c1679bf44b5
FROM ${BASE_IMAGE}

# Base image sets ENTRYPOINT to `clible`; override so npm scripts run normally.
ENTRYPOINT []

# Ensure the clible CLI bundled in the base image is on PATH at runtime.
ENV PATH="/home/clible/.venv/bin:${PATH}"

# 2. SYSTEM SETUP (ROOT)
# Vaihdetaan rootiksi vain asennusten ajaksi.
USER root

# Asennetaan Node.js v20.x
ARG DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Replace the CLI from the base image with this repository checkout (same deps as pyproject.toml).
# Build context must be the repo root: docker build -f src/clible-web/Dockerfile .
COPY pyproject.toml README.md /opt/clible-pkg/
COPY src/clible /opt/clible-pkg/src/clible
RUN /home/clible/.venv/bin/pip install --no-cache-dir --upgrade "/opt/clible-pkg" \
    && rm -rf /opt/clible-pkg

# Default package data dir lives under site-packages and is not writable; SQLite WAL needs a writable dir.
RUN mkdir -p /home/clible/.clible-data && chown clible:clible /home/clible/.clible-data
ENV CLIBLE_DATA_DIR=/home/clible/.clible-data

# 3. WEB APP DIRECTORY
# Luodaan hakemisto ja varmistetaan, että clible-käyttäjä omistaa sen.
WORKDIR /app/web
RUN chown -R clible:clible /app/web

# 4. SWITCH TO NON-ROOT USER
# Kaikki loput vaiheet suoritetaan rajoitetulla käyttäjällä.
USER clible

# 5. DEPENDENCIES
COPY --chown=clible:clible src/clible-web/package*.json ./
RUN --mount=type=cache,target=/home/clible/.npm,uid=10001,gid=10001 \
    npm ci

# 6. BUILD WEB APP
COPY --chown=clible:clible src/clible-web/ .
ENV NODE_ENV=production
RUN npm run build

# 7. VERIFY CLI IS AVAILABLE
RUN clible --help >/dev/null

# 8. EXPOSE & START
EXPOSE 3000
# npm does not always preserve Dockerfile ENV for child processes; force production so we never await Vite in the container.
CMD ["sh", "-c", "export NODE_ENV=production && exec npm start"]