import { describe, expect, it } from 'vitest';

import { getExportAiNotesParts } from './exportNotes';

describe('getExportAiNotesParts', () => {
  it('returns standard ai notes heading for regular markdown export', () => {
    const out = getExportAiNotesParts('md', false);
    expect(out.separator).toContain('## AI Study Notes');
    expect(out.closingTag).toBe('');
  });

  it('returns original study heading for markdown export', () => {
    const out = getExportAiNotesParts('md', true);
    expect(out.separator).toContain('## Original Language Study Notes');
    expect(out.closingTag).toBe('');
  });

  it('returns xml opening and matching closing tags for original study', () => {
    const out = getExportAiNotesParts('xml', true);
    expect(out.separator).toContain('<original_language_study_notes>');
    expect(out.closingTag).toBe('\n</original_language_study_notes>');
  });

  it('returns empty parts for unsupported format', () => {
    const out = getExportAiNotesParts('json', true);
    expect(out.separator).toBe('');
    expect(out.closingTag).toBe('');
  });
});

