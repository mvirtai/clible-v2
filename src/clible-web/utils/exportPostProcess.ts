import { ExportFormat } from '@/components/ExportModal';
import { getExportAiNotesParts } from './exportNotes';

/**
 * Appends AI notes to the export content.
 */
export function appendExportNotes(params: {
  content: string;
  format: ExportFormat;
  cmd: 'verse' | 'search' | 'analytics';
  args: string;
  title: string;
  exportAiText: string | null;
  toneAnalysis: string | null;
}): string {
  let out = params.content;

  if (params.cmd === 'verse' && params.exportAiText) {
    const isOriginalStudyExport = params.title.startsWith('Original Study:');
    const { separator, closingTag } = getExportAiNotesParts(
      params.format,
      isOriginalStudyExport,
    );
    if (separator) {
      out += separator + params.exportAiText;
      if (closingTag) out += closingTag;
    }
  }

  if (
    params.cmd === 'analytics' &&
    params.toneAnalysis &&
    !params.args.trimStart().startsWith('compare ')
  ) {
    let separator = '';
    if (params.format === 'md') separator = '\n\n---\n\n## AI Tone & Style Analysis\n\n';
    else if (params.format === 'txt')
      separator = '\n\n---\n\nAI TONE & STYLE ANALYSIS:\n\n';
    else if (params.format === 'html')
      separator = '\n\n---\n\n<h2>AI Tone & Style Analysis</h2>\n\n';

    if (separator) out += separator + params.toneAnalysis;
  }

  return out;
}

