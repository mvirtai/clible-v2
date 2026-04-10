/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { BibleResponse, InstalledTranslation } from '../types/bible';
import {
  SearchResponse,
  SearchResultRow,
  SearchStatistics,
} from '../types/search';

/** Default `-n` for web search: keeps JSON payload small; stats still reflect the full match set. */
export const DEFAULT_WEB_SEARCH_LIMIT = 50;

/** Dev-only: trace search bridge in the browser console (Vite sets import.meta.env.DEV). */
const SEARCH_DEBUG = import.meta.env.DEV;

function logSearch(...args: unknown[]) {
  if (SEARCH_DEBUG) {
    console.log('[clible-web] search:', ...args);
  }
}

export class BibleRepository {
  async listInstalledTranslations(): Promise<InstalledTranslation[]> {
    const response = await fetch(
      `/api/clible?cmd=seed&args=${encodeURIComponent("list")}`
    );
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        (errorData as { error?: string }).error ??
          "Failed to list installed translations."
      );
    }
    const data: unknown = await response.json();
    if (!Array.isArray(data)) {
      throw new Error("Invalid response when listing translations.");
    }
    return data as InstalledTranslation[];
  }

  /**
   * Instead of calling an external API, we call our local Express bridge
   * which executes the 'clible' command on the server.
   */
  async getVerse(reference: string, translation: string): Promise<BibleResponse> {
    // Format args as: "<REFERENCE>" -t <TRANSLATION>
    const args = `"${reference}" -t ${translation}`;
    const response = await fetch(`/api/clible?cmd=verse&args=${encodeURIComponent(args)}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to fetch verse from Clible CLI.');
    }
    
    const data = await response.json();
    return this.mapVerseLookupToBibleResponse(data);
  }

  /** Maps `clible verse --json` export (`verse_lookup`) to the UI shape. */
  private mapVerseLookupToBibleResponse(data: Record<string, unknown>): BibleResponse {
    const rows = (data.verses as Array<Record<string, unknown>> | undefined) ?? [];
    const first = rows[0];
    const refDisplay =
      first != null
        ? `${String(first.book_id ?? "")} ${String(first.chapter ?? "")}:${String(first.verse ?? "")}`.trim()
        : String(data.title ?? "");
    const text = rows.map((v) => String(v.text ?? "")).join(" ");
    const translationName = String(data.translation_id ?? "");

    return {
      reference: refDisplay,
      text,
      translation_name: translationName,
      verses: rows.map((v) => ({
        book_name: String(v.book_id ?? ""),
        chapter: Number(v.chapter ?? 0),
        verse: Number(v.verse ?? 0),
        text: String(v.text ?? ""),
      })),
    };
  }

  /**
   * Maps `clible search --json` payload (`type: "search"`) to UI rows.
   * See docs/SEARCH_FLOW.md (repo root) for the full bridge pipeline.
   */
  private mapSearchJsonToRows(data: Record<string, unknown>): SearchResultRow[] {
    if (data.type !== 'search') {
      throw new Error('Invalid search response from Clible CLI (expected type "search").');
    }
    const verses = data.verses;
    if (!Array.isArray(verses)) {
      throw new Error('Invalid search response: "verses" must be an array.');
    }
    return verses.map((row) => {
      const r = row as Record<string, unknown>;
      const reference = `${String(r.book_id ?? '').trim()} ${String(r.chapter ?? '')}:${String(r.verse ?? '')}`.trim();
      return {
        reference,
        text: String(r.text ?? ''),
      };
    });
  }

  private mapSearchStatistics(raw: unknown): SearchStatistics {
    if (raw == null || typeof raw !== 'object') {
      return {
        totalOccurrences: 0,
        uniqueVerses: 0,
        booksWithMatches: 0,
        topBooks: [],
      };
    }
    const obj = raw as Record<string, unknown>;
    const topBooksRaw = obj.top_books;
    const topBooks: Array<[string, number]> = [];
    if (Array.isArray(topBooksRaw)) {
      for (const item of topBooksRaw) {
        if (Array.isArray(item) && item.length >= 2) {
          topBooks.push([String(item[0]), Number(item[1])]);
        }
      }
    }
    return {
      totalOccurrences: Number(obj.total_occurrences ?? 0),
      uniqueVerses: Number(obj.unique_verses ?? 0),
      booksWithMatches: Number(obj.books_with_matches ?? 0),
      topBooks,
    };
  }

  private mapSearchJsonToResponse(data: Record<string, unknown>): SearchResponse {
    const rows = this.mapSearchJsonToRows(data);
    return {
      rows,
      statistics: this.mapSearchStatistics(data.statistics),
      query: String(data.query ?? ''),
      title: String(data.title ?? ''),
      translationId:
        data.translation_id == null || data.translation_id === ''
          ? null
          : String(data.translation_id),
      scope: data.scope == null ? null : String(data.scope),
      scopeRef: data.scope_ref == null ? null : String(data.scope_ref),
    };
  }

  async search(
    word: string,
    translation: string,
    scope?: string,
    scopeRef?: string,
    limit: number = DEFAULT_WEB_SEARCH_LIMIT
  ): Promise<SearchResponse> {
    // Format args as: "<WORD>" -t <TRANSLATION> [--scope <scope>] [-r <scope_ref>] [-n <limit>]
    let args = `"${word}" -t ${translation}`;
    if (scope) args += ` --scope ${scope}`;
    if (scopeRef) args += ` -r "${scopeRef}"`;
    if (limit > 0) args += ` -n ${limit}`;

    const url = `/api/clible?cmd=search&args=${encodeURIComponent(args)}`;
    logSearch('GET', url);
    const response = await fetch(url);
    logSearch('response status', response.status, response.statusText);

    if (!response.ok) {
      const errorData = (await response.json().catch(() => ({}))) as {
        error?: string;
        rawOutput?: string;
      };
      logSearch('error body', errorData);
      throw new Error(
        errorData.error ?? 'Search failed'
      );
    }

    const data = (await response.json()) as Record<string, unknown>;
    logSearch('parsed JSON top-level keys', Object.keys(data));
    const out = this.mapSearchJsonToResponse(data);
    logSearch('mapped rows count', out.rows.length);
    return out;
  }
  async export(
    cmd: "verse" | "search" | "analytics",
    args: string,
    format: string,
    aiInsight?: string | null
  ): Promise<{ content: string; contentType: string }> {
    const exportArgs = `${args} --stdout-export ${format}`;
    const response = await fetch(
      `/api/clible?cmd=${cmd}&args=${encodeURIComponent(exportArgs)}`
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        (errorData as { error?: string }).error ?? "Export failed."
      );
    }

    let content = await response.text();
    const contentType = response.headers.get("Content-Type") || "text/plain";

    if (aiInsight) {
      content = this._appendAiInsight(content, aiInsight, format);
    }

    return { content, contentType };
  }

  private _escapeXml(text: string): string {
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  private _appendAiInsight(content: string, aiInsight: string, format: string): string {
    switch (format) {
      case "md":
        return content.trimEnd() + "\n\n## AI Insight\n\n" + aiInsight + "\n";

      case "html": {
        const section =
          "<section class='page-card'>" +
          "<div class='section-title'><h2>AI Insight</h2><span>AI-generated context and study notes</span></div>" +
          "<div class='glow' style='white-space:pre-wrap'>" +
          this._escapeXml(aiInsight) +
          "</div></section>";
        const footerMarker = "<p class='footer-note'>";
        if (content.includes(footerMarker)) {
          return content.replace(footerMarker, section + footerMarker);
        }
        return content.replace("</main>", section + "</main>");
      }

      case "txt":
        return (
          content.trimEnd() +
          "\n\nAI INSIGHT\n" +
          "-".repeat(40) +
          "\n" +
          aiInsight +
          "\n"
        );

      case "json": {
        try {
          const parsed = JSON.parse(content) as Record<string, unknown>;
          parsed.ai_insight = aiInsight;
          return JSON.stringify(parsed, null, 2);
        } catch {
          return content;
        }
      }

      case "xml": {
        const escaped = this._escapeXml(aiInsight);
        return content.trimEnd().replace(/<\/[^>]+>$/, (closing) => `  <ai-insight>${escaped}</ai-insight>\n${closing}`);
      }

      case "csv":
      default:
        return content;
    }
  }
}

export const bibleRepository = new BibleRepository();
