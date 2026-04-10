/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * Triggers a browser download for a blob/string content.
 */
export function downloadFile(content: string | Blob, filename: string, contentType: string) {
  const blob = typeof content === 'string' ? new Blob([content], { type: contentType }) : content;
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
