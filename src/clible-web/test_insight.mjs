import { GoogleGenAI } from "@google/genai";
import fs from "fs";

const apiKey = fs.readFileSync("../../.env", "utf8")
    .split("\n")
    .find(line => line.startsWith("GEMINI_API_KEY="))
    ?.split("=")[1]?.replace(/['"]/g, "");

const ai = new GoogleGenAI({ apiKey });

const insightSystemInstruction =
  "You are a scholarly Bible study assistant. Write the full answer—including every `##` and `###` heading—in the same language as the Bible passage the user pasted. " +
  "If the passage is clearly in one language (e.g. Finnish, Swedish, German), use that language for headings and body. " +
  "Only use English if the passage is English or the language is genuinely ambiguous. " +
  "Stay balanced and historically grounded. Follow the requested Markdown shape exactly (real `##` / `###` headings, not bold-only titles).";

function buildInsightUserPrompt(passageText) {
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

async function run() {
    try {
        const response = await ai.models.generateContent({
            model: "gemini-3-flash-preview",
            contents: buildInsightUserPrompt("Jesus walks on water"),
            config: {
                systemInstruction: insightSystemInstruction,
            },
        });
        console.log("Success with gemini-3-flash-preview:", !!response.text);
    } catch (e) {
        console.error("SDK Error:", e);
    }
}
run();
