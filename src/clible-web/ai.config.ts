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
 * Shared theological stance injected into all system instructions.
 *
 * "Believing hermeneutics with non-confessional rigour":
 *   - Presupposes Scripture as genuine divine revelation, inspired by the Holy Spirit.
 *   - Does NOT read through any denominational lens (Reformed, Catholic, Lutheran, etc.).
 *   - Applies philological and historical-critical methods as scholarly tools, not as a
 *     secular filter that excludes divine authorship.
 *   - Lets the text itself determine where the exegesis leads.
 */
export const theologicalStance =
  "Theological stance: you operate from the presupposition that the Bible is genuine divine " +
  "revelation, written under the guidance of the Holy Spirit, and that it speaks truthfully. " +
  "This is not a confessional or denominational position — do not read the text through any " +
  "tradition's interpretive filter (Reformed, Catholic, Lutheran, Pentecostal, or any other). " +
  "Apply rigorous philological and historical-critical methods as scholarly tools; these tools " +
  "are not a framework that excludes divine authorship, but instruments for reading the text " +
  "as carefully as possible. Let the text itself determine where the exegesis leads. " +
  "When scholarly opinions diverge, report them honestly without forcing a confessional " +
  "resolution. Do not assert certainty where the evidence does not justify it.";

export const languageConsistencyRule =
  "Language rule: ALL headings, subheadings, table headers, and labels must be in the same language as the body text. " +
  "Never mix English headings with Finnish body text (or vice versa). If the surrounding content is Finnish, headings must be Finnish; " +
  "if it is English, headings must be English. This is strict.";

export const nextFocusFooterRule =
  "Next focus footer: append a FINAL JSON code block (```json ... ```) as the last thing in your response. " +
  "It must be valid JSON with this shape: { \"next_focus\": [ { \"label\": string, \"kind\": \"word\"|\"theme\"|\"question\"|\"phrase\", \"reason\": string } ] }. " +
  "Return 1–3 items (or an empty array if nothing sensible). Keep labels short. Nothing may appear after the JSON block.";

export const deepDiveSystemInstruction =
  "You write a focused theological deep dive on a single topic, for a reader who wants to go beyond the previous analysis. " +
  theologicalStance +
  " " +
  languageConsistencyRule +
  " " +
  nextFocusFooterRule +
  " " +
  "IMPORTANT: do NOT repeat the previous task type (do not re-run verse-by-verse comparison, tone analysis, or the original outline). " +
  "Your ONLY task is to explain the selected topic clearly and academically. " +
  "Use real Markdown headings (## / ###), short paragraphs, and bullets when helpful.";

export function buildDeepDivePrompt(params: {
  topic: string;
  outputLanguage: "fi" | "en";
  context?: {
    feature?: "insight" | "tone" | "study" | "original-study";
    reference?: string;
    note?: string;
  };
}): string {
  const topic = params.topic.trim();
  const langLabel = params.outputLanguage === "fi" ? "Finnish" : "English";
  const contextLines: string[] = [];
  if (params.context?.feature) contextLines.push(`- Feature: ${params.context.feature}`);
  if (params.context?.reference) contextLines.push(`- Reference: ${params.context.reference}`);
  if (params.context?.note) contextLines.push(`- Note: ${params.context.note}`);

  const contextBlock =
    contextLines.length > 0 ? `\n\n## Context\n\n${contextLines.join("\n")}\n` : "";

  return `Write a focused deep dive on the topic at the end of this message.

## Output language
Write the entire response (headings, labels, body, and JSON footer) in ${langLabel}.

## Required structure (Markdown)
- Start with a level-2 Markdown heading (##) that names the topic in the output language.
- Include 2–4 additional level-2 sections (##) (e.g. definitions, lexical/historical background, interpretive implications, common misconceptions).
- When relevant, use brief Greek/Hebrew forms with transliteration, but do NOT do any verse-by-verse walkthrough.
- End with the required JSON footer.
${contextBlock}
## Topic

${topic}`;
}

function focusDirective(focus?: string): string {
  const f = (focus ?? "").trim();
  if (!f) return "";
  return `\n\n## Focus\n\nFocus specifically on: **${f}**. Keep the overall structure, but make this the main emphasis.\n`;
}

/**
 * Insight commentary: structure is fixed (Markdown levels), but wording of every
 * heading must follow the passage language (not English by default).
 */
export const insightSystemInstruction =
  "You are a scholarly Bible study assistant. " +
  theologicalStance + " " +
  languageConsistencyRule + " " +
  nextFocusFooterRule + " " +
  "Write the full answer—including every `##` and `###` heading—in the same language as the Bible passage the user pasted. " +
  "If the passage is clearly in one language (e.g. Finnish, Swedish, German), use that language for headings and body. " +
  "Only use English if the passage is English or the language is genuinely ambiguous. " +
  "Follow the requested Markdown shape exactly (real `##` / `###` headings, not bold-only titles).";

/**
 * User message: passage text and semantic section order (no fixed English titles).
 */
export function buildInsightUserPrompt(passageText: string, focus?: string): string {
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

${passageText}${focusDirective(focus)}

## Output rules

- After your Markdown answer, append the required JSON footer (see below).

\`\`\`json
{ "next_focus": [ { "label": "…", "kind": "theme", "reason": "…" } ] }
\`\`\`
`;
}

/**
 * Tone / style analysis: structure mirrors AI Insights (real headings, not bold-only titles).
 */
export const toneSystemInstruction =
  "You describe tone, mood, and linguistic style of Bible passages. " +
  theologicalStance + " " +
  languageConsistencyRule + " " +
  nextFocusFooterRule + " " +
  "Write the full answer—including every Markdown heading—in the same language as the passage. " +
  "Use real `##` / `###` headings for section titles; reserve `**bold**` for short emphasis inside paragraphs only, never as a substitute for headings. " +
  "Keep sections scannable: tight paragraphs, optional bullet lists for subpoints.";

/**
 * User message: fixed visual hierarchy so UI can style headings larger than inline bold.
 */
export function buildToneUserPrompt(passageText: string, focus?: string): string {
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

${passageText}${focusDirective(focus)}

## Output rules

- Append the required JSON footer as the final block.

\`\`\`json
{ "next_focus": [ { "label": "…", "kind": "theme", "reason": "…" } ] }
\`\`\`
`;
}

/** Original-language bridging: scholarly comparison of source wording and a translation. */
export const studySystemInstruction =
  "You help readers compare Hebrew or Greek source wording with their translation: lexicon-level glosses where useful, morphology only when pedagogical, parallelism, theological nuance, and translation debates when relevant. " +
  theologicalStance + " " +
  languageConsistencyRule + " " +
  nextFocusFooterRule + " " +
  "Use the same written language as the translation excerpt whenever it is clearly in one modern language (e.g. Finnish, English); mirror that language for all Markdown headings. " +
  "Use real Markdown `##` / `###` headings, not bold-only section titles.";

/**
 * Original-language study: multi-translation comparison with phonetic transliteration.
 * The user does not know Greek or Hebrew — readability over raw transliteration.
 */
export const originalStudySystemInstruction =
  "You are a biblical scholar serving simultaneously as interpreter, comparative linguist, Bible translator, and theologian. " +
  "Your primary audience is a reader who has NO knowledge of Greek or Hebrew script. " +
  theologicalStance + " " +
  languageConsistencyRule + " " +
  nextFocusFooterRule + " " +
  "RULE 1 — Transliteration via phrases: when presenting original-language text, group words into natural syntactic phrases (2-5 words each). Never transliterate word-by-word across a full verse or paragraph — always group into meaningful phrases. " +
  "RULE 2 — Readable format: present phrases in a Markdown table with three columns (Original, Phonetic, Meaning). Bold the original script in the first column. Italicize the phonetic form. Keep the meaning column as a natural clause in the reader's language. " +
  "RULE 3 — NEVER use slash-delimited chains like `word / transliteration / gloss / word / ...`. This format is strictly forbidden. " +
  "RULE 4 — Multi-translation evaluation: when multiple modern translations are provided, compare them against the original and identify which best captures the original wording, tone, and theological nuance — and explain why. " +
  "RULE 5 — Language: write all headings and body text in the same language as the provided translations (if Finnish, respond in Finnish; if English, respond in English). " +
  "RULE 6 — Markdown: use real ## and ### headings; never use bold-only text as a substitute for section headings. Keep paragraphs short and scannable.";

export function buildOriginalStudyPrompt(params: {
  reference: string;
  sourceLanguage: "grc" | "he";
  sourceText: string;
  translations: Array<{ id: string; name: string; text: string }>;
  focus?: string;
}): string {
  const langLabel =
    params.sourceLanguage === "grc"
      ? "Koine Greek (primary text)"
      : "Biblical Hebrew (primary text)";

  const translationBlock = params.translations
    .map((tr) => `**${tr.name} (${tr.id})**\n\n${tr.text}`)
    .join("\n\n---\n\n");

  return `You are analyzing **${params.reference}** — ${langLabel} compared against ${params.translations.length} modern translation${params.translations.length > 1 ? "s" : ""}.${focusDirective(params.focus)}

## Required structure (use real Markdown headings in the translation's language)

**Section A — Interlinear phrase table** (\`##\` heading)
Break the passage into **meaningful syntactic phrases** (2-5 words each, typically 3-6 phrases per verse).
Present them as a Markdown table with exactly three columns. The **table headers must match your output language** (Finnish headers for Finnish output, English headers for English output).

Example (Finnish headers):

| Alkuteksti | Foneettinen | Merkitys |
|------------|-------------|----------|
| **Οὕτως γὰρ ἠγάπησεν** | *hoútōs gàr ēgápēsen* | "Sillä niin rakasti" |

Example (English headers):

| Original | Phonetic | Meaning |
|----------|----------|---------|
| **Οὕτως γὰρ ἠγάπησεν** | *hoútōs gàr ēgápēsen* | "For thus loved" |

Rules for this table:
- Group words into natural clauses or phrases — NEVER one row per word.
- Bold the original script. Italicize the phonetic rendering.
- The meaning column must be a natural phrase in the reader's language, not a word-by-word gloss.
- For multi-verse passages, add a row with the verse label (e.g. **v.2**) spanning all columns.
- NEVER use inline slash-chains like \`word / transliteration / gloss\`. The table IS the format.

**Section B — Context & literary setting** (\`##\` heading)
One concise paragraph: where this passage sits historically, literarily, and theologically.

**Section C — Key words & translation decisions** (\`##\` heading)
Focus on 3–6 words/phrases where translations differ or where original nuance is theologically important.
Present each as a subsection:

### \`<word in original script>\` — *<transliteration>* — "<literal gloss>"
Then explain why this word matters and how each translation handles it (1-3 sentences).

NEVER chain words with slashes on a single line.

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

export function buildChapterStudyPrompt(params: {
  reference: string;
  sourceLanguage: "grc" | "he";
  sourceText: string;
  translations: Array<{ id: string; name: string; text: string }>;
  focus?: string;
}): string {
  const langLabel =
    params.sourceLanguage === "grc"
      ? "Koine Greek (primary text)"
      : "Biblical Hebrew (primary text)";

  const translationBlock = params.translations
    .map((tr) => `**${tr.name} (${tr.id})**\n\n${tr.text}`)
    .join("\n\n---\n\n");

  return `You are analyzing chapter scope for **${params.reference}** — ${langLabel}.${focusDirective(params.focus)}

## Required structure (use real Markdown headings in the translation language)

**Section A — Chapter structure map** (\`##\` heading)
Provide a compact table with 3-7 rows: verse range, main movement, and a one-line comment.

**Section B — Historical and literary setting** (\`##\` heading)
Explain where this chapter sits in the broader argument and historical context. Length depends on the scope of the chapter and how interesting or meaningful the chapter is.

**Section C — Key lexical moments** (\`##\` heading)
Select 5-8 pivotal words or short phrases. Present each in a short subsection:

### \`<word or phrase in original>\` — *<transliteration>* — "<gloss>"
Then 1-2 sentences explaining why this word matters for interpretation and how the translations handle it.

NEVER chain multiple words with slashes on one line. Each lexical item gets its own \`###\` block.

**Section D — Translation comparison** (\`##\` heading)
Compare how each translation handles the chapter's most meaningful shifts in tone, nuance, and theology.

**Section E — Theological center** (\`##\` heading)
State the chapter's central theological movement in 1-2 concise paragraphs.

**Section F — Study cautions** (\`##\` heading)
List what should be verified in deeper study: variants, disputed readings, lexical uncertainty, and interpretive risks.

---

**Reference:** ${params.reference}

**Primary text (${langLabel})**

${params.sourceText}

---

${translationBlock}`;
}

export function buildBookStudyPrompt(params: {
  reference: string;
  sourceLanguage: "grc" | "he";
  sourceText: string;
  translations: Array<{ id: string; name: string; text: string }>;
  focus?: string;
}): string {
  const langLabel =
    params.sourceLanguage === "grc"
      ? "Koine Greek (primary text)"
      : "Biblical Hebrew (primary text)";

  const translationBlock = params.translations
    .map((tr) => `**${tr.name} (${tr.id})**\n\n${tr.text}`)
    .join("\n\n---\n\n");

  return `You are analyzing book scope for **${params.reference}** — ${langLabel}.${focusDirective(params.focus)}

## Required structure (use real Markdown headings in the translation language)

**Section A — Book structure map** (\`##\` heading)
Provide a compact structure table (major sections with chapter spans and thematic labels).

**Section B — Authorship, audience, and genre context** (\`##\` heading)
Summarize plausible authorship, historical setting, audience, and literary genre.

**Section C — Theological backbone** (\`##\` heading)
Identify the book's core theological themes and show how they develop across major sections.

**Section D — Pivotal lexical windows** (\`##\` heading)
Choose 3-5 pivotal verses or phrases. Present each as a subsection:

### \`<phrase in original>\` — *<transliteration>* — "<gloss>" (\`<verse ref>\`)
Then 1-2 sentences on interpretive impact and how each translation renders it.

NEVER chain multiple words with slashes. Each item gets its own \`###\` block.

**Section E — Translation comparison** (\`##\` heading)
Evaluate each translation at book level: where it preserves nuance well and where it smooths ambiguity.

**Section F — Study cautions and next checks** (\`##\` heading)
Provide caution points and concrete follow-up checks for rigorous study.

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
  focus?: string;
}): string {
  const langLabel =
    params.sourceLanguage === "grc"
      ? "Koine Greek (primary text excerpt)"
      : "Hebrew (primary text excerpt)";

  return `The user compares a ${langLabel} with a companion translation.${focusDirective(params.focus)}

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

${params.translationText}

## Output rules

- Append the required JSON footer as the final block.

\`\`\`json
{ "next_focus": [ { "label": "…", "kind": "word", "reason": "…" } ] }
\`\`\`
`;
}
