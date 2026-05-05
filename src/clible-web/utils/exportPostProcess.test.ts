import { describe, expect, it } from 'vitest';

import { appendExportNotes } from './exportPostProcess';

describe('appendExportNotes', () => {
  it('appends original-study note heading for verse markdown export', () => {
    const out = appendExportNotes({
      content: 'base',
      format: 'md',
      cmd: 'verse',
      args: '"John 3:16" -t greeksblgnt',
      title: 'Original Study: John 3:16 (greeksblgnt)',
      exportAiText: 'analysis text',
      toneAnalysis: null,
    });

    expect(out).toContain('## Original Language Study Notes');
    expect(out).toContain('analysis text');
  });

  it('appends tone analysis only for analytics non-compare exports', () => {
    const out = appendExportNotes({
      content: 'base',
      format: 'md',
      cmd: 'analytics',
      args: 'reference "John 3:16" -t fin-1992',
      title: 'Analytics: John 3:16',
      exportAiText: null,
      toneAnalysis: 'tone body',
    });

    expect(out).toContain('## AI Tone & Style Analysis');
    expect(out).toContain('tone body');
  });

  it('does not append tone analysis for compare analytics exports', () => {
    const out = appendExportNotes({
      content: 'base',
      format: 'md',
      cmd: 'analytics',
      args: 'compare "John 3:16" --left fin-1992 --right web',
      title: 'Compare: John 3:16',
      exportAiText: null,
      toneAnalysis: 'tone body',
    });

    expect(out).toBe('base');
  });
});

