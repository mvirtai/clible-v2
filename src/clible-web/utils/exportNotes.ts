export interface ExportAiNotesParts {
  separator: string;
  closingTag: string;
}

export function getExportAiNotesParts(
  format: string,
  isOriginalStudyExport: boolean,
): ExportAiNotesParts {
  if (format === 'md') {
    return {
      separator: isOriginalStudyExport
        ? '\n\n---\n\n## Original Language Study Notes\n\n'
        : '\n\n---\n\n## AI Study Notes\n\n',
      closingTag: '',
    };
  }
  if (format === 'txt') {
    return {
      separator: isOriginalStudyExport
        ? '\n\n---\n\nORIGINAL LANGUAGE STUDY NOTES:\n\n'
        : '\n\n---\n\nAI STUDY NOTES:\n\n',
      closingTag: '',
    };
  }
  if (format === 'html') {
    return {
      separator: isOriginalStudyExport
        ? '\n\n---\n\n<h2>Original Language Study Notes</h2>\n\n'
        : '\n\n---\n\n<h2>AI Study Notes</h2>\n\n',
      closingTag: '',
    };
  }
  if (format === 'xml') {
    return {
      separator: isOriginalStudyExport
        ? '\n\n---\n\n<original_language_study_notes>\n'
        : '\n\n---\n\n<ai_study_notes>\n',
      closingTag: isOriginalStudyExport
        ? '\n</original_language_study_notes>'
        : '\n</ai_study_notes>',
    };
  }
  return { separator: '', closingTag: '' };
}

