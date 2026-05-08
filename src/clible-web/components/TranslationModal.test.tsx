import { afterEach } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import type { AvailableTranslation, InstalledTranslation } from '../types/bible';
import { TranslationModal } from './TranslationModal';

function renderModal(override?: Partial<React.ComponentProps<typeof TranslationModal>>) {
  const installedTranslations: InstalledTranslation[] = [
    { id: 'web', name: 'WEB', language: 'en', format: 'usfx' },
  ];
  const availableTranslations: AvailableTranslation[] = [
    { id: 'web', name: 'World English Bible', language: 'en', format: 'USFX', size_mb: 5.9 },
    { id: 'kjv', name: 'King James Version', language: 'en', format: 'OSIS', size_mb: 9.6 },
    { id: 'fin-1992', name: 'Finnish 1992', language: 'fi', format: 'BEBLIA', size_mb: 4.9 },
    { id: 'greeksblgnt', name: 'SBLGNT', language: 'grc', format: 'BEBLIA', size_mb: 1.8 },
    { id: 'hebrewaleppocodex', name: 'Hebrew Aleppo Codex', language: 'he', format: 'BEBLIA', size_mb: 3.5 },
    { id: 'zzz-extra', name: 'Extra', language: 'en', format: 'USFX', size_mb: 1.0 },
  ];

  const props: React.ComponentProps<typeof TranslationModal> = {
    installedTranslations,
    availableTranslations,
    loadingAvailableTranslations: false,
    translationsLoadError: null,
    installError: null,
    installSuccess: null,
    installingTranslationId: null,
    activeTranslation: null,
    uiLanguage: 'en',
    query: '',
    onQueryChange: vi.fn(),
    onSelect: vi.fn(),
    onInstall: vi.fn(),
    onClose: vi.fn(),
    ...override,
  };

  return render(<TranslationModal {...props} />);
}

describe('TranslationModal', () => {
  afterEach(() => cleanup());

  it('does not close when installing; close button is disabled', () => {
    const onClose = vi.fn();
    renderModal({ installingTranslationId: 'hebrewaleppocodex', onClose });

    const closeBtn = screen.getByRole('button', { name: 'Close' });
    expect(closeBtn).toBeDisabled();
    fireEvent.click(closeBtn);
    expect(onClose).not.toHaveBeenCalled();
  });

  it('calls onQueryChange when typing into search input', () => {
    const onQueryChange = vi.fn();
    renderModal({ onQueryChange });

    const inputs = screen.getAllByPlaceholderText(/Search translations/i);
    const input = inputs[inputs.length - 1];
    fireEvent.input(input, {
      target: { value: 'hebrew' },
    });
    expect(onQueryChange).toHaveBeenCalledWith('hebrew');
  });

  it('renders featured section before browse', () => {
    renderModal();
    const headings = screen.getAllByRole('heading', { level: 4 }).map((h) => h.textContent);
    expect(headings[0]).toBe('Featured');
    expect(headings).toContain('Browse');
  });
});

