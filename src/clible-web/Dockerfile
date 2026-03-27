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

# 3. WEB APP DIRECTORY
# Luodaan hakemisto ja varmistetaan, että clible-käyttäjä omistaa sen.
WORKDIR /app/web
RUN chown -R clible:clible /app/web

# 4. SWITCH TO NON-ROOT USER
# Kaikki loput vaiheet suoritetaan rajoitetulla käyttäjällä.
USER clible

# 5. DEPENDENCIES
COPY --chown=clible:clible package*.json ./
RUN --mount=type=cache,target=/home/clible/.npm,uid=10001,gid=10001 \
    npm ci

# 6. BUILD WEB APP
COPY --chown=clible:clible . .
ENV NODE_ENV=production
RUN npm run build

# 7. VERIFY CLI IS AVAILABLE
RUN clible --help >/dev/null

# 8. EXPOSE & START
EXPOSE 3000
CMD ["npm", "start"]