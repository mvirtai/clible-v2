import { describe, expect, it } from "vitest";

import { extractNextFocus } from "./nextFocus";

describe("extractNextFocus", () => {
  it("returns empty list when no json footer exists", () => {
    const out = extractNextFocus("hello\n\n## Title\nbody");
    expect(out.nextFocus).toEqual([]);
    expect(out.cleanedText).toContain("## Title");
  });

  it("extracts next_focus from final json block and strips it", () => {
    const input =
      "## A\n\nText.\n\n```json\n{\n  \"next_focus\": [\n    {\"label\":\"agápē\",\"kind\":\"word\",\"reason\":\"key noun\"},\n    {\"label\":\"covenant\",\"kind\":\"theme\",\"reason\":\"core motif\"}\n  ]\n}\n```\n";
    const out = extractNextFocus(input);
    expect(out.cleanedText).toBe("## A\n\nText.");
    expect(out.nextFocus).toHaveLength(2);
    expect(out.nextFocus[0].label).toBe("agápē");
  });

  it("ignores json block if content appears after it", () => {
    const input =
      "Text\n\n```json\n{\"next_focus\": [{\"label\":\"x\",\"kind\":\"word\",\"reason\":\"r\"}]}\n```\n\nTrailing";
    const out = extractNextFocus(input);
    expect(out.nextFocus).toEqual([]);
    expect(out.cleanedText).toContain("Trailing");
  });

  it("filters invalid items and limits to 3", () => {
    const input =
      "Text\n\n```json\n{\n  \"next_focus\": [\n    {\"label\":\" \",\"kind\":\"word\",\"reason\":\"x\"},\n    {\"label\":\"a\",\"kind\":\"nope\",\"reason\":\"x\"},\n    {\"label\":\"b\",\"kind\":\"word\",\"reason\":\"ok\"},\n    {\"label\":\"c\",\"kind\":\"theme\",\"reason\":\"ok\"},\n    {\"label\":\"d\",\"kind\":\"question\",\"reason\":\"ok\"},\n    {\"label\":\"e\",\"kind\":\"phrase\",\"reason\":\"ok\"}\n  ]\n}\n```\n";
    const out = extractNextFocus(input);
    expect(out.nextFocus.map((x) => x.label)).toEqual(["b", "c", "d"]);
  });
});

