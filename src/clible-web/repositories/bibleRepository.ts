/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { BibleResponse, InstalledTranslation } from '../types/bible';

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

  async search(word: string, translation: string, scope?: string, scopeRef?: string, limit?: number): Promise<any> {
    // Format args as: "<WORD>" -t <TRANSLATION> [--scope <scope>] [-r <scope_ref>] [-n <limit>]
    let args = `"${word}" -t ${translation}`;
    if (scope) args += ` --scope ${scope}`;
    if (scopeRef) args += ` -r "${scopeRef}"`;
    if (limit) args += ` -n ${limit}`;

    const response = await fetch(`/api/clible?cmd=search&args=${encodeURIComponent(args)}`);
    if (!response.ok) throw new Error('Search failed');
    return await response.json();
  }
}

export const bibleRepository = new BibleRepository();
