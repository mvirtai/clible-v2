/**
 * Escapes Markdown ordered-list markers at the start of lines (e.g. "1. Foo"),
 * so that plain text like "1. ..." doesn't get rendered as a list with indentation.
 */
export function escapeOrderedListStarts(text: string): string {
  if (!text) return text;
  // ReactMarkdown treats `^\d+\.` as an ordered list marker.
  // Escape the dot to force literal text rendering.
  return text.replace(/^(\s*)(\d{1,3})\.\s+/gm, (_m, ws: string, n: string) => `${ws}${n}\\. `);
}

