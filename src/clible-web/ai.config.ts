/**
 * Central Gemini prompts and model IDs for the Clible web server.
 * Restart the process (or rebuild the Docker image) after editing.
 *
 * Optional environment overrides:
 * - GEMINI_MODEL_INSIGHT — model for POST /api/ai/insight
 * - GEMINI_MODEL_TONE    — model for POST /api/ai/tone
 */

export const geminiModels = {
  insight: process.env.GEMINI_MODEL_INSIGHT?.trim() || "gemini-flash-latest",
  tone: process.env.GEMINI_MODEL_TONE?.trim() || "gemini-flash-latest",
} as const;

/**
 * Insight commentary: structure is fixed (Markdown levels), but wording of every
 * heading must follow the passage language (not English by default).
 */
export const insightSystemInstruction =
  "You are a scholarly Bible study assistant. Write the full answer—including every `##` and `###` heading—in the same language as the Bible passage the user pasted. " +
  "If the passage is clearly in one language (e.g. Finnish, Swedish, German), use that language for headings and body. " +
  "Only use English if the passage is English or the language is genuinely ambiguous. " +
  "Stay balanced and historically grounded. Follow the requested Markdown shape exactly (real `##` / `###` headings, not bold-only titles).";

/**
 * User message: passage text and semantic section order (no fixed English titles).
 */
export function buildInsightUserPrompt(passageText: string): string {
  return `Analyze the Bible passage at the end of this message.

## Structure (use real Markdown headings—word the titles yourself)

Use **three** \`##\` sections **in this order**. Choose natural titles in **the same language as the passage** (do not keep English labels if the passage is not English).

**Section A — short opening overview**  
One concise paragraph.  
_Finnish example titles:_ \`## Johdanto\` or \`## Yhteenveto\`  
_English examples:_ \`## Summary\` or \`## Overview\`

**Section B — historical and cultural background**  
One to several paragraphs; scale length to how much relevant context exists and to passage length.  
_Finnish example:_ \`## Historiallinen konteksti\`  
_English example:_ \`## Historical context\`

**Section C — exactly three takeaways**  
A \`##\` title, then three subsections. Each takeaway: one \`###\` line (number + short title) and one paragraph.  
_Finnish example section title:_ \`## Kolme keskeistä pointtia\` or \`## Kolme pointtia\`  
_Finnish takeaway lines:_ \`### 1. …\`, \`### 2. …\`, \`### 3. …\` with Finnish titles.

**Formatting rules**
- Every section and takeaway must use \`##\` or \`###\` headings (not \`**bold**\` alone for those titles).
- **All** headings and body text must match the passage language.
- Do not prefix the answer with a separate intro sentence in another language; start directly with the first \`##\` section if possible.

## Passage

${passageText}`;
}

/**
 * Tone / style analysis: structure mirrors AI Insights (real headings, not bold-only titles).
 */
export const toneSystemInstruction =
  "You describe tone, mood, and linguistic style of Bible passages. " +
  "Write the full answer—including every Markdown heading—in the same language as the passage. " +
  "Use real `##` / `###` headings for section titles; reserve `**bold**` for short emphasis inside paragraphs only, never as a substitute for headings. " +
  "Keep sections scannable: tight paragraphs, optional bullet lists for subpoints.";

/**
 * User message: fixed visual hierarchy so UI can style headings larger than inline bold.
 */
export function buildToneUserPrompt(passageText: string): string {
  return `Analyze the **tone**, **mood (atmosphere)**, and **linguistic style** of the passage at the end of this message.

Your reply must follow this Markdown layout (do not copy the instruction labels below into the answer):

**Language:** Write all headings and body text in the **same language as the passage**.

**1. No lead-in sentence**  
Do not start your response with a sentence introducing what you will cover.

**2. Three main sections — each starts with a level-2 Markdown heading (\`##\`)**

Use exactly **three** \`##\` sections in this order. Pick natural titles in the passage language. 
Adjust the length of your response to fit the length of the passage provided and the amount and quality of relevant facts you find.

| Role | Finnish examples | English examples |
|------|------------------|------------------|
| A | \`## Sävy\` | \`## Tone\` |
| B | \`## Tunnelma\` | \`## Atmosphere\` |
| C | \`## Kielellinen tyyli\` | \`## Linguistic style\` |

Under each \`##\`, write one or more paragraphs. Be concise but concrete.

**3. Emphasis vs headings**

- Put section names (**Sävy**, **Tunnelma**, …) **only** on the \`##\` line. Do **not** repeat them as \`**bold**\` at the start of the paragraph.
- Use \`**bold**\` only for short in-sentence emphasis (a few words). Those must stay visually smaller than the \`##\` titles in a rendered UI.

**4. Subpoints (optional)**  
Use \`- **Label:** explanation\` if needed; keep bullets secondary to \`##\` titles.

**5. Do not**  
- Do not use \`###\` for the three pillars unless you need a rare sub-subsection; the three main blocks must be \`##\`.
- Do not use \`**bold**\` alone for the three section titles.

--- Passage ---

${passageText}`;
}
