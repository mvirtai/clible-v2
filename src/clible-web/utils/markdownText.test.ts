import { describe, expect, it } from 'vitest';

import { escapeOrderedListStarts } from './markdownText';

describe('escapeOrderedListStarts', () => {
  it('escapes ordered list markers at line start', () => {
    const input = ['B — Heading', '1. First item', '  2. Second item', '', '10. Tenth'].join('\n');
    const out = escapeOrderedListStarts(input);
    expect(out).toContain('1\\. First item');
    expect(out).toContain('  2\\. Second item');
    expect(out).toContain('10\\. Tenth');
  });

  it('leaves non-list lines unchanged', () => {
    const input = 'Version 1.2.3 is fine.\nA. Not an ordered list.';
    expect(escapeOrderedListStarts(input)).toBe(input);
  });
});

