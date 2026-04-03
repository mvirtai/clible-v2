/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { BibleResponse, InstalledTranslation, SearchResultRow } from '../types/bible';

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

  async search(
    word: string,
    translation: string,
    scope?: string,
    scopeRef?: string,
    limit?: number
  ): Promise<SearchResultRow[]> {
    // Format args as: "<WORD>" -t <TRANSLATION> [--scope <scope>] [-r <scope_ref>] [-n <limit>]
    let args = `"${word}" -t ${translation}`;
    if (scope) args += ` --scope ${scope}`;
    if (scopeRef) args += ` -r "${scopeRef}"`;
    if (limit) args += ` -n ${limit}`;

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
    const rows = this.mapSearchJsonToRows(data);
    logSearch('mapped rows count', rows.length);
    return rows;
  }
}

export const bibleRepository = new BibleRepository();
