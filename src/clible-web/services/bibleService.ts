/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { GoogleGenAI } from "@google/genai";
import { BibleResponse, TextStats, WordFrequency } from '../types/bible';

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

export class BibleService {
  async getAiInsight(result: BibleResponse): Promise<string> {
    const response = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: `Analyze this Bible passage: "${result.text}". 
      Provide a brief summary, historical context, and 3 key takeaways. 
      Format the response in a clean, readable way with headings.`,
      config: {
        systemInstruction: "You are a scholarly Bible study assistant. Provide insightful, balanced, and historically accurate commentary.",
      }
    });
    return response.text;
  }

  async getAiTone(text: string): Promise<string> {
    const response = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: `Analyze the tone, mood, and linguistic style of this passage: "${text}". Be concise.`,
      config: {
        systemInstruction: "Analyze the tone and mood of the text provided.",
      }
    });
    return response.text;
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
      args = `compare "${value}" --left ${translation} --right ${compareTranslation || 'web'}`;
      // Note: compare does not use --top according to user instructions
    }

    const response = await fetch(`/api/clible?cmd=analytics&args=${encodeURIComponent(args)}`);
    if (!response.ok) throw new Error('Failed to fetch native analytics');
    const data = await response.json();
    
    // Assuming Clible returns a structured JSON for analytics
    return {
      stats: {
        wordCount: data.word_count || 0,
        charCount: data.char_count || 0,
        avgWordLength: data.avg_word_length?.toFixed(1) || "0.0",
        uniqueWords: data.unique_words || 0
      },
      frequency: data.top_words?.map((w: any) => ({ name: w.word, value: w.count })) || []
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
