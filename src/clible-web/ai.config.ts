/**
 * Central Gemini prompts and model IDs for the Clible web server.
 * Restart the process (or rebuild the Docker image) after editing.
 *
 * Optional environment overrides:
 * - GEMINI_MODEL_INSIGHT — model for POST /api/ai/insight
 * - GEMINI_MODEL_TONE    — model for POST /api/ai/tone
 * - GEMINI_MODEL_STUDY   — model for POST /api/ai/study
 */

export const geminiModels = {
  insight: process.env.GEMINI_MODEL_INSIGHT?.trim() || "gemini-flash-latest",
  tone: process.env.GEMINI_MODEL_TONE?.trim() || "gemini-flash-latest",
  study: process.env.GEMINI_MODEL_STUDY?.trim() || "gemini-flash-latest",
  /**
   * Original-language study: deeper scholarly analysis with transliteration.
   * Defaults to gemini-2.5-pro; override with GEMINI_MODEL_ORIGINAL_STUDY.
   * Note: verify the exact model name in Google AI Studio before deploying.
   */
  originalStudy: process.env.GEMINI_MODEL_ORIGINAL_STUDY?.trim() || "gemini-3-flash-preview",
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

/** Original-language bridging: scholarly comparison of source wording and a translation. */
export const studySystemInstruction =
  "You help readers compare Hebrew or Greek source wording with their translation: lexicon-level glosses where useful, morphology only when pedagogical, parallelism, theological nuance, and translation debates when relevant. " +
  "Stay balanced and historically grounded. If scholarly views diverge, say so briefly—do not assert certainty where the sources do not justify it. " +
  "Use the same written language as the translation excerpt whenever it is clearly in one modern language (e.g. Finnish, English); mirror that language for all Markdown headings. " +
  "Use real Markdown `##` / `###` headings, not bold-only section titles.";

/**
 * Original-language study: multi-translation comparison with phonetic transliteration.
 * The user does not know Greek or Hebrew — phonetics come first, always.
 */
export const originalStudySystemInstruction =
  "You are a biblical scholar serving simultaneously as interpreter, comparative linguist, Bible translator, and theologian. " +
  "Your primary audience is a reader who has NO knowledge of Greek or Hebrew script. " +
  "RULE 1 — Transliteration is mandatory: every time you quote a Greek or Hebrew word, you MUST immediately follow it with its phonetic rendering in Latin characters using standard academic transliteration (e.g. ἠγάπησεν → ēgápēsen; בְּרֵאשִׁית → bereshít). Never quote the original script without the phonetic form alongside it. " +
  "RULE 2 — Key word glosses: for words that materially affect meaning or where translations diverge, provide: original script + phonetic + literal gloss (e.g. ἀγάπη / agápē / 'self-giving love'). " +
  "RULE 3 — Multi-translation evaluation: when multiple modern translations are provided, compare them against the original and identify which best captures the original wording, tone, and theological nuance — and explain why. " +
  "RULE 4 — Language: write all headings and body text in the same language as the provided translations (if Finnish, respond in Finnish; if English, respond in English). " +
  "RULE 5 — Markdown: use real ## and ### headings; never use bold-only text as a substitute for section headings. " +
  "Stay historically grounded. Acknowledge scholarly debate where relevant. Do not assert certainty where the sources do not justify it.";

export function buildOriginalStudyPrompt(params: {
  reference: string;
  sourceLanguage: "grc" | "he";
  sourceText: string;
  translations: Array<{ id: string; name: string; text: string }>;
}): string {
  const langLabel =
    params.sourceLanguage === "grc"
      ? "Koine Greek (primary text)"
      : "Biblical Hebrew (primary text)";

  const translationBlock = params.translations
    .map((tr, i) => `**Translation ${i + 1}: ${tr.name} (${tr.id})**\n\n${tr.text}`)
    .join("\n\n---\n\n");

  return `You are analyzing **${params.reference}** — ${langLabel} compared against ${params.translations.length} modern translation${params.translations.length > 1 ? "s" : ""}.

## Required structure (use real Markdown headings in the translation's language)

**Section A — Phonetic passage** (\`##\` heading)
Write the full passage word by word: for each word give ① original script ② phonetic in Latin ③ literal gloss.
Format example: ἐν / en / "in" — ἀρχῇ / archḗ / "beginning"
Keep one line or short paragraph per verse/clause so the reader can follow along.

**Section B — Context & literary setting** (\`##\` heading)
One concise paragraph: where this passage sits historically, literarily, and theologically.

**Section C — Key words & translation decisions** (\`##\` heading)
Focus on 3–6 words/phrases where the translations differ or where the original nuance is theologically important.
For each: original + phonetic + literal gloss + why it matters + how each translation handles it.

**Section D — Translation comparison** (\`##\` heading)
Evaluate each provided translation against the original. Be specific: what does each capture well, what does it soften or sharpen, where does it diverge from possible readings?

**Section E — Best match verdict** (\`##\` heading)
State clearly which translation best captures the original wording and theological nuance, and why. If they are close, say so and note what the runner-up does better.

**Section F — Study cautions** (\`##\` heading)
What a careful reader should verify beyond this snapshot: textual variants, manuscript traditions, contested readings.

---

**Reference:** ${params.reference}

**Primary text (${langLabel})**

${params.sourceText}

---

${translationBlock}`;
}

export function buildStudyUserPrompt(params: {
  reference: string;
  sourceLanguage: "grc" | "he";
  sourceText: string;
  translationText: string;
}): string {
  const langLabel =
    params.sourceLanguage === "grc"
      ? "Koine Greek (primary text excerpt)"
      : "Hebrew (primary text excerpt)";

  return `The user compares a ${langLabel} with a companion translation.

## Task (keep this structure with real headings)

Pick natural section titles **in the same language as the translation excerpt**.

1. Opening \`##\` section — one paragraph situating the clause or verse historically and literarily.
2. Second \`##\` section — lexical and grammatical observations that materially affect meaning (prioritize phenomena visible in the provided strings).
3. Third \`##\` section — how the quoted translation aligns with, softens, or sharpens possible readings (note ambiguities the original allows).
4. Close with a short \`##\` section listing **study cautions**: what trained scholars would double-check beyond this snapshot.

---

**Reference**

${params.reference}

**Primary (${langLabel})**

${params.sourceText}

**Translation excerpt**

${params.translationText}`;
}
