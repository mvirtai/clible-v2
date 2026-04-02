/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { BibleResponse, TextStats, WordFrequency } from '../types/bible';

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
      const message = details?.hint || details?.error || "Failed to generate insights.";
      throw new Error(message);
    }

    const data = await response.json();
    return typeof data?.text === "string" ? data.text : "";
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
      const message = details?.hint || details?.error || "Failed to analyze tone.";
      throw new Error(message);
    }

    const data = await response.json();
    return typeof data?.text === "string" ? data.text : "";
  }

  /**
   * Calls the local CLI bridge for native Clible analytics
   */
  async getNativeAnalytics(
    type: 'reference' | 'chapter' | 'book' | 'compare',
    value: string,
    translation: string,
    top: number = 10,
    compareTranslation?: string
  ): Promise<{ stats: TextStats, frequency: WordFrequency[] }> {
    let args = '';
    
    if (type === 'reference') {
      args = `reference "${value}" --translation ${translation} --top ${top}`;
    } else if (type === 'chapter') {
      // Assuming value is "Book Chapter" (e.g., "John 3")
      const parts = value.split(' ');
      const book = parts.slice(0, -1).join(' ');
      const chapter = parts[parts.length - 1];
      args = `chapter "${book}" ${chapter} --translation ${translation} --top ${top}`;
    } else if (type === 'book') {
      args = `book "${value}" --translation ${translation} --top ${top}`;
    } else if (type === 'compare') {
      if (!compareTranslation?.trim()) {
        throw new Error(
          "Analytics compare requires a second translation id (compareTranslation)."
        );
      }
      args = `compare "${value}" --left ${translation} --right ${compareTranslation}`;
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
