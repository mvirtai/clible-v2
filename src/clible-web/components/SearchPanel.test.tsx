import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import type { SearchHistoryEntry } from '../types/searchQuery';
import { SearchPanel } from './SearchPanel';

const history: SearchHistoryEntry[] = [];

const baseProps = {
  activeTranslation: 'fin-1992',
  uiLanguage: 'en' as const,
  onEntryTabChange: vi.fn(),
  onSearch: vi.fn(),
  onVerseSearch: vi.fn(),
  history,
  onHistoryClear: vi.fn(),
  loading: false,
  error: null as string | null,
};

describe('SearchPanel', () => {
  it('renders original tab and sends tab change callback', () => {
    const onEntryTabChange = vi.fn();
    render(<SearchPanel {...baseProps} entryTab="scripture" onEntryTabChange={onEntryTabChange} />);

    fireEvent.click(screen.getByRole('button', { name: 'Original Languages' }));
    expect(onEntryTabChange).toHaveBeenCalledWith('original');
  });

  it('shows original landing hint in original tab', () => {
    render(<SearchPanel {...baseProps} entryTab="original" />);

    expect(
      screen.getByText(/Pair an original-language text \(Greek or Hebrew\) with up to three modern translations/i),
    ).toBeInTheDocument();
  });

  it('still calls verse lookup callback in verse tab', () => {
    const onVerseSearch = vi.fn();
    render(<SearchPanel {...baseProps} entryTab="verse" onVerseSearch={onVerseSearch} />);

    const input = screen.getByLabelText('Enter Bible reference');
    fireEvent.change(input, { target: { value: 'John 3:16' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    expect(onVerseSearch).toHaveBeenCalledWith('John 3:16');
  });
});

