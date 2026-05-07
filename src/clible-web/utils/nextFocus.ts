export type NextFocusKind = "word" | "theme" | "question" | "phrase";

export interface NextFocusItem {
  label: string;
  kind: NextFocusKind;
  reason: string;
}

function isValidKind(value: unknown): value is NextFocusKind {
  return value === "word" || value === "theme" || value === "question" || value === "phrase";
}

function normalizeItems(raw: unknown): NextFocusItem[] {
  if (!Array.isArray(raw)) return [];
  const out: NextFocusItem[] = [];
  for (const item of raw) {
    if (!item || typeof item !== "object" || Array.isArray(item)) continue;
    const row = item as Record<string, unknown>;
    const label = typeof row.label === "string" ? row.label.trim() : "";
    const kind = row.kind;
    const reason = typeof row.reason === "string" ? row.reason.trim() : "";
    if (!label || !isValidKind(kind) || !reason) continue;
    out.push({ label, kind, reason });
    if (out.length >= 3) break;
  }
  return out;
}

/**
 * Extracts a final ```json ...``` code block containing { next_focus: [...] }.
 * If parsing fails, returns the original text and an empty list.
 */
export function extractNextFocus(text: string): { cleanedText: string; nextFocus: NextFocusItem[] } {
  const input = String(text ?? "");
  const re = /```json\s*([\s\S]*?)\s*```/g;
  let match: RegExpExecArray | null = null;
  let last: RegExpExecArray | null = null;
  while ((match = re.exec(input)) !== null) {
    last = match;
  }
  if (!last) return { cleanedText: input, nextFocus: [] };

  const jsonRaw = last[1]?.trim();
  const after = input.slice(last.index + last[0].length);
  // Only treat as footer if it is the final thing (allow whitespace).
  if (after.trim().length > 0) return { cleanedText: input, nextFocus: [] };

  if (!jsonRaw) return { cleanedText: input, nextFocus: [] };

  try {
    const parsed = JSON.parse(jsonRaw) as unknown;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return { cleanedText: input, nextFocus: [] };
    }
    const obj = parsed as Record<string, unknown>;
    const nextFocus = normalizeItems(obj.next_focus);
    const cleanedText = input.slice(0, last.index).trimEnd();
    return { cleanedText, nextFocus };
  } catch {
    return { cleanedText: input, nextFocus: [] };
  }
}

