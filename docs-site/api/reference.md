---
title: Web API reference
aside: false
outline: false
---

# Web API reference

The clible web app exposes a small REST API on top of the Express bridge. This page renders the live OpenAPI 3.1 specification from [`docs/api/openapi.yml`](https://github.com/mvirtai/clible-v2/blob/main/docs/api/openapi.yml).

The spec is the single source of truth. Edit it in `docs/api/openapi.yml`, push to `main`, and this page updates on the next docs build.

<ClientOnly>
  <RedocReference spec="/api/openapi.yml" />
</ClientOnly>
