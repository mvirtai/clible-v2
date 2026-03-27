/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { BibleResponse } from '../types/bible';

export class BibleRepository {
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
    
    return await response.json();
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
