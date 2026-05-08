import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import type { InstalledTranslation } from '../types/bible';
import type { OriginalStudyResult } from '../types/originalStudy';
import { OriginalStudyView } from './OriginalStudyView';

const baseProps = {
  activeTranslationId: 'fin-1992',
  uiLanguage: 'en' as const,
  installingTranslationId: null,
  onInstallTranslation: vi.fn(),
  result: null as OriginalStudyResult | null,
  loading: false,
  error: null as string | null,
  defaultReference: null as string | null,
  onStudy: vi.fn(),
};

describe('OriginalStudyView', () => {
  it('shows setup state when no original-language packs are installed', () => {
    const installedTranslations: InstalledTranslation[] = [
      { id: 'fin-1992', name: 'FIN', language: 'fi', format: 'usfx' },
    ];
    const onInstallTranslation = vi.fn();
    render(
      <OriginalStudyView
        {...baseProps}
        installedTranslations={installedTranslations}
        onInstallTranslation={onInstallTranslation}
      />,
    );

    expect(screen.getByText('Original language packs required')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Install Greek NT/i }));
    expect(onInstallTranslation).toHaveBeenCalledWith('greeksblgnt');

    fireEvent.click(screen.getByRole('button', { name: /Install Hebrew OT/i }));
    expect(onInstallTranslation).toHaveBeenCalledWith('hebrewaleppocodex');
  });

  it('submits selected reference/original/targets', () => {
    const installedTranslations: InstalledTranslation[] = [
      { id: 'greeksblgnt', name: 'Greek', language: 'grc', format: 'usfx' },
      { id: 'fin-1992', name: 'FIN', language: 'fi', format: 'usfx' },
      { id: 'web', name: 'WEB', language: 'en', format: 'usfx' },
    ];
    const onStudy = vi.fn();
    render(<OriginalStudyView {...baseProps} installedTranslations={installedTranslations} onStudy={onStudy} />);

    fireEvent.change(screen.getByPlaceholderText('e.g. John 3:16 or Genesis 1:1'), {
      target: { value: 'John 3:16' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Analyse' }));

    expect(onStudy).toHaveBeenCalledWith('John 3:16', 'greeksblgnt', ['fin-1992'], 'verse');
  });

  it('renders result table and export button when result exists', () => {
    const installedTranslations: InstalledTranslation[] = [
      { id: 'greeksblgnt', name: 'Greek', language: 'grc', format: 'usfx' },
      { id: 'fin-1992', name: 'FIN', language: 'fi', format: 'usfx' },
    ];
    const result: OriginalStudyResult = {
      reference: 'John 3:16',
      scope: 'verse',
      originalId: 'greeksblgnt',
      sourceLanguage: 'grc',
      originalVerses: [{ book_name: 'JHN', chapter: 3, verse: 16, text: 'ΟΥΤΩΣ' }],
      translations: [
        {
          id: 'fin-1992',
          name: 'FIN',
          verses: [{ book_name: 'JHN', chapter: 3, verse: 16, text: 'Sillä niin' }],
        },
      ],
      analysis: '## Analysis\n\nText.',
      nextFocus: [{ label: 'agápē', kind: 'word', reason: 'key term' }],
    };
    const onExport = vi.fn();
    render(
      <OriginalStudyView
        {...baseProps}
        installedTranslations={installedTranslations}
        result={result}
        onExport={onExport}
      />,
    );

    expect(screen.getByText('Verses side by side · John 3:16')).toBeInTheDocument();
    const exportBtn = screen.getByRole('button', { name: /Export compare/i });
    fireEvent.click(exportBtn);
    expect(onExport).toHaveBeenCalledTimes(1);
  });
});

