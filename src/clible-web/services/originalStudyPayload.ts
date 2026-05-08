import type { InstalledTranslation } from '../types/bible';
import type { OriginalStudyTranslation, OriginalStudyVerse, StudyScope } from '../types/originalStudy';

export interface OriginalStudyPayloadTranslation {
  id: string;
  name: string;
  text: string;
}

export interface OriginalStudyPayload {
  reference: string;
  scope: StudyScope;
  sourceText: string;
  sourceLanguage: 'grc' | 'he';
  translations: OriginalStudyPayloadTranslation[];
  focus?: string;
}

export function inferOriginalSourceLanguage(
  originalId: string,
  installed: InstalledTranslation[],
): 'grc' | 'he' {
  const origMeta = installed.find((t) => t.id === originalId);
  const langRaw = (origMeta?.language ?? '').toLowerCase().trim();
  if (langRaw === 'he' || langRaw.startsWith('heb') || langRaw === 'hbo') return 'he';

  // Fallback: some catalogs mislabel Hebrew packs as "en".
  const id = originalId.toLowerCase().trim();
  if (id.startsWith('hebrew') || id.includes('leningrad')) return 'he';

  return 'grc';
}

export function buildOriginalStudyPayload(params: {
  reference: string;
  scope: StudyScope;
  sourceLanguage: 'grc' | 'he';
  originalVerses: OriginalStudyVerse[];
  uniqueTargets: string[];
  lookups: Array<Record<string, unknown>>;
  installed: InstalledTranslation[];
  mapLookupToVerses: (data: Record<string, unknown>) => OriginalStudyVerse[];
  focus?: string;
}): {
  payload: OriginalStudyPayload;
  translations: OriginalStudyTranslation[];
} {
  const sourceText = params.originalVerses.map((v) => v.text).join(' ').trim();
  if (!sourceText) {
    throw new Error('No original-language text found for this reference.');
  }

  const payloadTranslations: OriginalStudyPayloadTranslation[] = [];
  const translations: OriginalStudyTranslation[] = [];

  for (let i = 0; i < params.uniqueTargets.length; i++) {
    const tid = params.uniqueTargets[i];
    const verses = params.mapLookupToVerses(params.lookups[i + 1]);
    const text = verses.map((v) => v.text).join(' ').trim();
    const meta = params.installed.find((t) => t.id === tid);
    const name = meta?.name ?? tid;

    payloadTranslations.push({
      id: tid,
      name,
      text: text.trim() ? text : '—',
    });
    translations.push({ id: tid, name, verses });
  }

  return {
    payload: {
      reference: params.reference,
      scope: params.scope,
      sourceText,
      sourceLanguage: params.sourceLanguage,
      translations: payloadTranslations,
      ...(params.focus?.trim() ? { focus: params.focus.trim() } : {}),
    },
    translations,
  };
}

