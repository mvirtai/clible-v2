/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { BibleResponse, TextStats, WordFrequency } from '../types/bible';
import type { CompareResult } from '../types/compare';

export class BibleService {
  async getAiInsight(result: BibleResponse): Promise<string> {
    const response = await fetch("/api/ai/insight", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: result.text }),
    });

    if (!response.ok) {
      let details: any = undefined;
      try {
        details = await response.json();
      } catch {
        // ignore
      }
      const message = details?.hint || details?.details || details?.error || "Failed to generate insights.";
      throw new Error(message);
    }

    const data = await response.json();
    return typeof data?.text === "string" ? data.text : "";
  }

  /**
   * Full translation comparison payload from the CLI analytics compare command.
   */
  async getCompareResult(
    ref: string,
    leftTranslation: string,
    rightTranslation: string
  ): Promise<CompareResult> {
    const trimmed = ref.trim();
    if (!trimmed) {
      throw new Error('Reference is required for comparison.');
    }
    const left = leftTranslation.trim();
    const right = rightTranslation.trim();
    if (!left || !right) {
      throw new Error('Both translations must be selected.');
    }
    if (left === right) {
      throw new Error('Choose two different translations to compare.');
    }

    const args = `compare ${JSON.stringify(trimmed)} --left ${left} --right ${right}`;
    const response = await fetch(
      `/api/clible?cmd=analytics&args=${encodeURIComponent(args)}`
    );

    const raw = await response.text();
    let data: unknown;
    try {
      data = JSON.parse(raw);
    } catch {
      throw new Error(raw || 'Invalid response from compare.');
    }

    if (!response.ok) {
      const errObj = data as Record<string, unknown>;
      const message =
        (typeof errObj.error === 'string' && errObj.error) ||
        (typeof errObj.details === 'string' && errObj.details) ||
        (typeof errObj.hint === 'string' ? errObj.hint : '') ||
        'Translation compare failed.';
      throw new Error(message);
    }

    if (!data || typeof data !== 'object' || Array.isArray(data)) {
      throw new Error('Invalid compare payload.');
    }
    const payload = data as Record<string, unknown>;
    const aligned = payload.aligned_verses;
    const summary = payload.summary;
    if (!Array.isArray(aligned) || !summary || typeof summary !== 'object') {
      throw new Error('Malformed compare JSON from CLI.');
    }
    if (
      typeof payload.reference !== 'string' ||
      aligned.length === 0
    ) {
      throw new Error(
        'No verses found for this reference in the selected translations.'
      );
    }

    return data as CompareResult;
  }

  async getAiTone(text: string): Promise<string> {
    const response = await fetch("/api/ai/tone", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      let details: any = undefined;
      try {
        details = await response.json();
      } catch {
        // ignore
      }
      const message = details?.hint || details?.details || details?.error || "Failed to analyze tone.";
      throw new Error(message);
    }

    const data = await response.json();
    return typeof data?.text === "string" ? data.text : "";
  }

  /**
   * Calls the local CLI bridge for native Clible analytics
   */
  async getNativeAnalytics(
    type: 'reference' | 'chapter' | 'book',
    value: string,
    translation: string,
    top: number = 10
  ): Promise<{ stats: TextStats, frequency: WordFrequency[] }> {
    let args = '';

    if (type === 'reference') {
      args = `reference "${value}" --translation ${translation} --top ${top}`;
    } else if (type === 'chapter') {
      // value is a full reference like "John 3:16" — extract book and chapter number
      const colonIdx = value.lastIndexOf(':');
      const beforeColon = colonIdx !== -1 ? value.slice(0, colonIdx) : value;
      const parts = beforeColon.split(' ');
      const book = parts.slice(0, -1).join(' ');
      const chapter = parts[parts.length - 1];
      args = `chapter "${book}" ${chapter} --translation ${translation} --top ${top}`;
    } else if (type === 'book') {
      // value is a full reference like "John 3:16" — extract only the book name
      const bookName = value.replace(/\s+\d.*$/, '');
      args = `book "${bookName}" --translation ${translation} --top ${top}`;
    }

    const response = await fetch(`/api/clible?cmd=analytics&args=${encodeURIComponent(args)}`);
    if (!response.ok) throw new Error('Failed to fetch native analytics');
    const data = (await response.json()) as Record<string, unknown>;

    const wordCount = Number(data.token_count ?? data.word_count ?? 0);
    const uniqueWords = Number(
      data.unique_token_count ?? data.unique_words ?? 0
    );
    const charCount = Number(
      data.character_count ?? data.char_count ?? 0
    );
    const avgRaw = data.avg_word_length ?? data.avgWordLength;
    const avgWordLength =
      typeof avgRaw === "number"
        ? avgRaw.toFixed(1)
        : typeof avgRaw === "string" && avgRaw.length > 0
          ? avgRaw
          : "0.0";

    return {
      stats: {
        wordCount,
        charCount,
        avgWordLength,
        uniqueWords,
      },
      frequency:
        (data.top_words as Array<{ word: string; count: number }> | undefined)?.map(
          (w) => ({ name: w.word, value: w.count })
        ) ?? [],
    };
  }

  // Legacy JS fallbacks (optional)
  calculateStats(text: string): TextStats {
    const words = text.split(/\s+/).filter(w => w.length > 0);
    return {
      wordCount: words.length,
      charCount: text.length,
      avgWordLength: (text.length / words.length).toFixed(1),
      uniqueWords: new Set(words.map(w => w.toLowerCase())).size
    };
  }

  calculateWordFrequency(text: string): WordFrequency[] {
    const words = text.toLowerCase().replace(/[^\w\s]/g, '').split(/\s+/).filter(w => w.length > 3);
    const counts: Record<string, number> = {};
    words.forEach(w => counts[w] = (counts[w] || 0) + 1);
    return Object.entries(counts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 8);
  }
}

export const bibleService = new BibleService();
