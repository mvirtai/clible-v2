<script setup lang="ts">
import { onMounted, onUnmounted, ref, useTemplateRef } from "vue";
import { withBase } from "vitepress";

/**
 * Renders an OpenAPI specification using Redoc Standalone.
 *
 * Redoc is loaded from a CDN at runtime instead of bundled, because
 * pinning a heavy SPA framework into VitePress's client bundle for a
 * single page is not worth the extra build complexity.
 */
const props = defineProps<{
  /** Site-relative path (e.g. /api/openapi.yml) or absolute URL. */
  spec: string;
}>();

const resolvedSpec = props.spec.startsWith("http")
  ? props.spec
  : withBase(props.spec);

const REDOC_SRC =
  "https://cdn.jsdelivr.net/npm/redoc@2.5.0/bundles/redoc.standalone.js";

const host = useTemplateRef<HTMLDivElement>("host");
const error = ref<string | null>(null);

let scriptEl: HTMLScriptElement | null = null;

function loadRedoc(): Promise<typeof window & { Redoc?: any }> {
  const w = window as typeof window & { Redoc?: any };
  if (w.Redoc) return Promise.resolve(w);

  return new Promise((resolveLoad, rejectLoad) => {
    const existing = document.querySelector<HTMLScriptElement>(
      `script[src="${REDOC_SRC}"]`,
    );
    if (existing) {
      existing.addEventListener("load", () => resolveLoad(w));
      existing.addEventListener("error", () => rejectLoad(new Error("Redoc failed to load")));
      return;
    }

    scriptEl = document.createElement("script");
    scriptEl.src = REDOC_SRC;
    scriptEl.async = true;
    scriptEl.onload = () => resolveLoad(w);
    scriptEl.onerror = () => rejectLoad(new Error("Redoc failed to load"));
    document.head.appendChild(scriptEl);
  });
}

onMounted(async () => {
  try {
    const w = await loadRedoc();
    if (!host.value || !w.Redoc) return;
    w.Redoc.init(
      resolvedSpec,
      {
        scrollYOffset: 64,
        hideDownloadButton: false,
        expandResponses: "200,201",
        nativeScrollbars: true,
      },
      host.value,
    );
  } catch (err) {
    error.value =
      err instanceof Error ? err.message : "Failed to render API reference.";
  }
});

onUnmounted(() => {
  // Leave the cached <script> in the DOM so SPA route changes don't refetch it,
  // but clear our host element so the next mount renders cleanly.
  if (host.value) host.value.innerHTML = "";
});
</script>

<template>
  <div class="redoc-host">
    <div v-if="error" role="alert">
      Failed to load API reference: {{ error }}
    </div>
    <div ref="host" />
  </div>
</template>
