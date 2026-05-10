import type { UILanguage } from './bookNames';

export type { UILanguage };

export const strings = {
  en: {
    // App / shell
    chooseTranslation: 'Choose translation',
    settingsTitle: 'Settings',
    signOutTitle: 'Sign out',
    historyToggleAria: 'Search history',
    translationPickerAria: 'Bible translation',
    adminTitle: 'Admin',
    tabReader: 'Reader',
    tabAnalytics: 'Analytics',
    footerCopyright: ({year}: {year: number}) => `© ${year} clible`,
    footerDocumentation: 'Documentation',
    footerApi: 'API',
    footerGithub: 'GitHub',
    errFailedLoadTranslations: 'Failed to load translations.',
    errSelectTranslationFirst:
      'Select a translation first (globe menu). Install one with: clible seed install <id>',
    errSearchFailed: 'Search failed.',
    errUnexpected: 'An unexpected error occurred.',
    errInsightsFailed: 'Failed to generate insights.',
    errAiToneUnavailable: 'AI tone analysis unavailable.',
    errExportFailed: 'Export failed.',
    errDeleteFailed: 'Delete failed.',
    appBootLoading: 'Loading...',
    errSaveSettings: 'Failed to save settings.',
    errInstallTranslation: 'Failed to install translation.',

    // ReaderView
    readerEmptyTitle: 'Ready for study',
    readerEmptyHint: 'Enter a verse to begin.',
    readerShare: 'Share',
    readerExport: 'Export',
    readerAiInsights: 'AI Insights',
    readerGenerateInsights: 'Generate Insights',
    readerAiLoading: 'Consulting the archives...',
    readerAiPlaceholder: 'Click above for AI-powered context and study notes.',

    // SearchPanel (scope / search area)
    searchFindInScripture: 'Find in Scripture',
    searchVerseLookup: 'Verse Lookup',
    searchEntryCompare: 'Compare',
    searchCompareLandingHint:
      'Pick two translations and a reference below — align verses side by side with similarity.',
    searchPlaceholderVerse: 'Enter verse (e.g. John 3:16, Psalms 23)...',
    searchPlaceholderWildcard: 'Enter a pattern (e.g. lov*, faith?)...',
    searchPlaceholderGeneral: 'Find a word, theme, or phrase...',
    searchAriaVerse: 'Enter Bible reference',
    searchAriaSearch: 'Search Bible text',
    searchRecentHeader: 'Recent searches',
    searchClear: 'Clear',
    searchHistoryMeta: ({ count, scopeLabel }: { count: number; scopeLabel: string }) =>
      `${scopeLabel} · ${count} verses`,
    searchOperatorAnd: 'and also contains',
    searchOperatorOr: 'or contains',
    searchOperatorNot: 'but not',
    searchSecondWordPlaceholder: 'second word...',
    searchWildcardHint:
      'Use * for any ending (lov* finds love, loves, loving). Use ? for one letter (wom?n).',
    searchHideOptions: 'Hide options',
    searchRefine: 'Refine your search',
    searchTypeHeading: 'Search type',
    searchModePhrase: 'Any word in verse',
    searchModePhraseDesc: 'Finds verses containing the word or phrase',
    searchModeWords: 'Combine words',
    searchModeWordsDesc: 'Find verses with multiple words (AND / OR / NOT)',
    searchModeWildcard: 'Word pattern',
    searchModeWildcardDesc: 'lov* finds love, loves, loving',
    searchMatchHeading: 'Match',
    searchMatchAll: 'All words',
    searchMatchAny: 'Any word',
    searchMatchExclude: 'Exclude second',
    searchScopePrefix: 'Search in:',
    searchAllBible: 'All Bible',
    searchOldTestament: 'Old Testament',
    searchNewTestament: 'New Testament',
    searchPickBook: 'A specific book...',

    // SearchView
    searchResultsTitle: 'Search Results',
    searchUniqueVerses: (n: number) =>
      `${n} unique verse${n === 1 ? '' : 's'}`,
    searchExportTitle: 'Export results',
    searchNoResults: 'No verses found for this search.',

    // SearchStatsPanel
    statsOccurrences: 'Occurrences',
    statsUniqueVerses: 'Unique verses',
    statsBooks: 'Books',
    statsTopBooks: 'Top books',
    statsOccurrencesCol: 'Occurrences',
    statsTruncated: (shown: number, total: number) =>
      `Showing first ${shown} of ${total} matching verses (limit).`,

    // AnalyticsView
    analyticsModeReference: 'Reference',
    analyticsModeChapter: 'Chapter',
    analyticsModeBook: 'Book',
    analyticsExport: 'Export Analytics',
    compareExport: 'Export compare',
    statsWords: 'Words',
    statsUnique: 'Unique',
    statsAvgLength: 'Avg Length',
    statsChars: 'Chars',
    analyticsWordFrequency: 'Word Frequency',
    analyticsFreqViewBarTitle: 'Bar chart',
    analyticsFreqViewCloudTitle: 'Word cloud',
    analyticsAiTone: 'AI Tone Analysis',
    analyticsAiLoading: 'Analyzing linguistic patterns...',
    analyticsTonePlaceholder: 'Select a passage to analyze its tone.',

    compareTitle: 'Translation compare',
    compareReferenceLabel: 'Reference',
    compareReferencePlaceholder: 'e.g. John 3:16 or John 3:16-18',
    compareLeftLabel: 'Left translation',
    compareRightLabel: 'Right translation',
    compareRunButton: 'Compare',
    compareLoading: 'Comparing translations…',
    compareNoResult: 'Run a comparison to see aligned verses and similarity.',
    compareVerseColumn: 'Verse',
    compareSimilarityColumn: 'Similarity',
    compareAvgSimilarity: 'Average similarity',
    compareExactMatches: 'Exact text matches',
    compareAlignedVerses: 'Verses aligned on both sides',
    compareTotalVerses: 'Compared rows',
    compareMostSimilar: 'Most similar verse',
    compareSharedWords: 'Top shared tokens',
    compareAiStudy: 'AI original-language study',
    compareAiStudyHint: 'Connecting a scholarly model to Hebrew/Greek + your translation is planned next.',
    compareNeedTwoTranslations:
      'Install at least two translations to compare.',

    tabOriginalStudy: 'Original Languages',
    originalStudyTitle: 'Original Language Study',
    originalStudyLandingHint:
      'Pair an original-language text (Greek or Hebrew) with up to three modern translations. AI provides phonetic transliteration and a comparative reading.',
    originalSetupTitle: 'Original language packs required',
    originalSetupHint:
      'To study the original languages, install Greek (NT) or Hebrew (OT). Both are small, public-domain editions.',
    originalInstallGreek: 'Install Greek NT (greeksblgnt)',
    originalInstallHebrew: 'Install Hebrew OT (heb-leningrad)',
    originalSelectOriginal: 'Original-language source',
    originalSelectTranslations: 'Compare against (1–3 translations)',
    originalRunButton: 'Analyse',
    originalLoading: 'Consulting the sources…',
    originalAnalysisHeading: 'Scholarly analysis',
    originalNoResult: 'Run an analysis to see the original-language study.',
    originalNeedTargets: 'Select at least one translation to compare against.',
    originalReferenceLabel: 'Reference',
    originalReferencePlaceholder: 'e.g. John 3:16 or Genesis 1:1',
    originalVersesHeading: 'Verses side by side',
    originalAlreadyInstalled: 'Installed',

    errAnalyticsNeedVerse:
      'Look up a verse first to use Reference, Chapter, or Book analytics.',

    // SettingsPanel
    settingsCloseBackdrop: 'Close settings',
    settingsClose: 'Close',
    settingsDialogLabel: 'Settings',
    settingsHeading: 'Settings',
    settingsSubtitle: 'User preferences are saved to your account.',
    settingsProfile: 'Profile',
    settingsUsername: 'Username',
    settingsUserId: 'User id',
    settingsTheme: 'Theme',
    themeLight: 'Light',
    themeDark: 'Dark',
    themeSystem: 'System',
    settingsLoading: 'Loading settings…',
    settingsInterfaceLang: 'Interface language',
    settingsInterfaceLangHint:
      'Book names and picker labels. Does not change Bible text (use Translation).',
    langEnglish: 'English',
    langFinnish: 'Suomi',
    settingsTranslation: 'Translation',
    settingsDefaultTranslation: 'Default translation',
    settingsNotSelected: 'Not selected',
    settingsChoose: 'Choose…',
    settingsTranslationFootnote:
      'Installed translations are environment-wide. Your selection is saved per user.',

    // TranslationModal
    translationModalTitle: 'Select Translation',
    translationSearchPlaceholder: 'Search translations (id, name, language)…',
    translationSearchHint: 'Tip: try “fin”, “greek”, “hebrew”, or a translation id like “web”.',
    translationFeaturedLabel: 'Featured',
    translationInstalledSectionLabel: 'Installed',
    translationBrowseLabel: 'Browse',
    translationBrowseLimitedHint: 'Showing a limited list. Use search to find more.',
    translationNoneInstalled:
      'No translations are installed on this server yet. Use Install to fetch one from the catalog.',
    translationCatalogLoading: 'Loading translation catalog...',
    translationCatalogEmpty: 'No translations found in the catalog.',
    translationFooter:
      'Installable translations come from the shared catalog. Installed translations are specific to this server environment.',
    translationSelected: 'Selected',
    translationUse: 'Use',
    translationInstalled: 'Installed',
    translationInstalling: 'Installing...',
    translationInstall: 'Install',

    // ExportModal
    exportModalTitle: 'Export Study',
    exportPreparing: 'Preparing your archives...',
    formatMdName: 'Markdown',
    formatMdDesc: 'Best for study notes and Obsidian.',
    formatHtmlName: 'HTML',
    formatHtmlDesc: 'Rich formatting, printable.',
    formatJsonName: 'JSON',
    formatJsonDesc: 'Structured data for developers.',
    formatTxtName: 'Plain Text',
    formatTxtDesc: 'Simple, universal format.',
    formatCsvName: 'CSV',
    formatCsvDesc: 'Spreadsheet compatible.',
    formatXmlName: 'XML',
    formatXmlDesc: 'Tag-based structure.',

    // Saved search
    saveSearchSaved: 'Saved',
    saveSearchPlaceholder: 'Name this search...',
    saveSearchSave: 'Save',
    saveSearchCancel: 'Cancel',
    saveSearchPrompt: 'Save this search',
    savedSearchesLabel: 'Saved searches',
    savedSearchRemove: 'Remove',
    savedSearchScopeTitle: (scope: string) => `Scope: ${scope}`,

    // Scope label in history (raw codes from API — optional localization later)
    historyScopeOT: 'OT',
    historyScopeNT: 'NT',
    historyScopeWholeBible: 'Whole Bible',

    // BookPickerModal
    bookPickerTitle: 'Choose a Book',
    bookPickerClose: 'Close',

    // ReadingPlanView / StreakBadge
    tabReading: 'Reading',
    readingTitle: 'Reading',
    readingSubtitle: 'Build a habit with a daily plan and streak.',
    readingLoading: 'Loading reading plan…',
    readingDays: (n: number) => `${n} day${n === 1 ? '' : 's'}`,
    readingDaysCompleted: (done: number, total: number) => `${done}/${total} days completed`,
    readingActivePlan: 'Active plan',
    readingStart: 'Start',
    readingAbandon: 'Abandon',
    readingToday: 'Today',
    readingDay: (n: number) => `Day ${n}`,
    readingMarkComplete: 'Mark complete',
    readingCompleted: 'Completed',
    readingNoPassages: 'No passages for today.',
    readingStreakAriaLabel: (n: number) => `Reading streak: ${n} day${n === 1 ? '' : 's'}`,

    readingPlanPsalms30Title: 'Psalms in 30 Days',
    readingPlanPsalms30Desc:
      'Read the Book of Psalms in 30 days (5 psalms per day).',
    readingPlanNt90Title: 'New Testament in 90 Days',
    readingPlanNt90Desc:
      'Read the New Testament in 90 days (mostly 3 chapters per day).',
    readingPlanAnnualTitle: 'Bible in a Year',
    readingPlanAnnualDesc:
      'Read the full Bible in 365 days (auto-generated: 3–4 chapters per day).',
  },
  fi: {
    chooseTranslation: 'Valitse käännös',
    settingsTitle: 'Asetukset',
    signOutTitle: 'Kirjaudu ulos',
    historyToggleAria: 'Hakuhistoria',
    translationPickerAria: 'Raamatunkäännös',
    adminTitle: 'Ylläpito',
    tabReader: 'Lukija',
    tabAnalytics: 'Analyysi',
    footerCopyright: ({year}: {year: number}) => `© ${year} clible`,
    footerDocumentation: 'Dokumentaatio',
    footerApi: 'API',
    footerGithub: 'GitHub',
    errFailedLoadTranslations: 'Käännösten lataus epäonnistui.',
    errSelectTranslationFirst:
      'Valitse ensin käännös (maapallo-valikko). Asenna: clible seed install <id>',
    errSearchFailed: 'Haku epäonnistui.',
    errUnexpected: 'Odottamaton virhe.',
    errInsightsFailed: 'Oivallusten luonti epäonnistui.',
    errAiToneUnavailable: 'Sävyanalyysi ei ole käytettävissä.',
    errExportFailed: 'Vienti epäonnistui.',
    errDeleteFailed: 'Poisto epäonnistui.',
    appBootLoading: 'Ladataan…',
    errSaveSettings: 'Asetusten tallennus epäonnistui.',
    errInstallTranslation: 'Käännöksen asennus epäonnistui.',

    readerEmptyTitle: 'Aloita lukeminen',
    readerEmptyHint: 'Syötä jae tai viite aloittaaksesi.',
    readerShare: 'Jaa',
    readerExport: 'Vie',
    readerAiInsights: 'Tekoäly-oivallukset',
    readerGenerateInsights: 'Luo oivalluksia',
    readerAiLoading: 'Haetaan tietoja…',
    readerAiPlaceholder: 'Valitse yllä oivalluksia ja opastusta lukemiseen.',

    searchFindInScripture: 'Etsi tekstistä',
    searchVerseLookup: 'Jaehaku',
    searchEntryCompare: 'Vertaa',
    searchCompareLandingHint:
      'Valitse kaksi käännöstä ja viite alla — jakeet kohdakkain ja samankaltaisuus.',
    searchPlaceholderVerse: 'Syötä jae (esim. Joh. 3:16 tai Psalmit 23)...',
    searchPlaceholderWildcard: 'Syötä hahmo (esim. rak*, usko?)...',
    searchPlaceholderGeneral: 'Etsi sanaa, aihetta tai ilmausta...',
    searchAriaVerse: 'Syötä raamatun viite',
    searchAriaSearch: 'Hae raamatun tekstistä',
    searchRecentHeader: 'Viimeisimmät haut',
    searchClear: 'Tyhjennä',
    searchHistoryMeta: ({ count, scopeLabel }: { count: number; scopeLabel: string }) =>
      `${scopeLabel} · ${count} jaetta`,
    searchOperatorAnd: 'ja sisältää myös',
    searchOperatorOr: 'tai sisältää',
    searchOperatorNot: 'mutta ei',
    searchSecondWordPlaceholder: 'toinen sana...',
    searchWildcardHint:
      '* = mikä tahansa loppu (rak* → rakastaa, rakkaus). ? = yksi merkki (nainen).',
    searchHideOptions: 'Piilota valinnat',
    searchRefine: 'Tarkenna hakua',
    searchTypeHeading: 'Haun tyyppi',
    searchModePhrase: 'Sana tai lause jaeessa',
    searchModePhraseDesc: 'Etsii jakeet, joissa esiintyy annettu sana tai lause',
    searchModeWords: 'Useampi sana',
    searchModeWordsDesc: 'Jakeet, joissa on useampi sana (JA / TAI / EI)',
    searchModeWildcard: 'Sanan hahmo',
    searchModeWildcardDesc: 'esim. rak* löytää rakastaa, rakkauden',
    searchMatchHeading: 'Yhdistäminen',
    searchMatchAll: 'Kaikki sanat',
    searchMatchAny: 'Mikä tahansa sana',
    searchMatchExclude: 'Jätä toinen pois',
    searchScopePrefix: 'Rajaa:',
    searchAllBible: 'Koko Raamattu',
    searchOldTestament: 'Vanha testamentti',
    searchNewTestament: 'Uusi testamentti',
    searchPickBook: 'Valitse kirja…',

    searchResultsTitle: 'Hakutulokset',
    searchUniqueVerses: (n: number) =>
      n === 1 ? `${n} ainutlaatuinen jae` : `${n} ainutlaatuista jaetta`,
    searchExportTitle: 'Vie tulokset',
    searchNoResults: 'Tällä haulla ei löytynyt jakeita.',

    statsOccurrences: 'Osumat',
    statsUniqueVerses: 'Eri jakeita',
    statsBooks: 'Kirjoja',
    statsTopBooks: 'Kärkikirjat',
    statsOccurrencesCol: 'Osumat',
    statsTruncated: (shown: number, total: number) =>
      `Näytetään ensimmäiset ${shown} / ${total} osumasta (rajoitus).`,

    analyticsModeReference: 'Viite',
    analyticsModeChapter: 'Luku',
    analyticsModeBook: 'Kirja',
    analyticsExport: 'Vie analyysi',
    compareExport: 'Vie vertailu',
    statsWords: 'Sanat',
    statsUnique: 'Eri sanoja',
    statsAvgLength: 'Kesk. pituus',
    statsChars: 'Merkkejä',
    analyticsWordFrequency: 'Sanojen frekvenssi',
    analyticsFreqViewBarTitle: 'Pylväsdiagrammi',
    analyticsFreqViewCloudTitle: 'Sanapilvi',
    analyticsAiTone: 'Tekoälyn sävyanalyysi',
    analyticsAiLoading: 'Analysoidaan kielenpiirteitä…',
    analyticsTonePlaceholder: 'Valitse jakeisto, jonka sävyä analysoidaan.',

    compareTitle: 'Käännösten vertailu',
    compareReferenceLabel: 'Viite',
    compareReferencePlaceholder: 'esim. Joh. 3:16 tai Joh. 3:16-18',
    compareLeftLabel: 'Vasen käännös',
    compareRightLabel: 'Oikea käännös',
    compareRunButton: 'Vertaa',
    compareLoading: 'Vertaillaan käännöksiä…',
    compareNoResult: 'Aloita vertailu nähdäksesi kohdistetut jakeet ja samankaltaisuuden.',
    compareVerseColumn: 'Jae',
    compareSimilarityColumn: 'Samankaltaisuus',
    compareAvgSimilarity: 'Keskimääräinen samankaltaisuus',
    compareExactMatches: 'Täsmälleen sama teksti',
    compareAlignedVerses: 'Molemmilla puolin kohdistettuja jakoja',
    compareTotalVerses: 'Vertailurivejä',
    compareMostSimilar: 'Eniten samankaltainen jae',
    compareSharedWords: 'Yleisimmät yhteiset sanat',
    compareAiStudy: 'Tekoälyavusteinen alkukielitutkimus',
    compareAiStudyHint:
      'Heprea/kreikka + oma käännös -pohjaisen mallin kytkeminen toteutetaan seuraavassa vaiheessa.',
    compareNeedTwoTranslations:
      'Asenna ainakin kaksi käännöstä vertailua varten.',

    tabOriginalStudy: 'Alkukieli',
    originalStudyTitle: 'Alkukielitutkimus',
    originalStudyLandingHint:
      'Yhdistä alkukielinen teksti (kreikka tai heprea) ja enintään kolme nykykäännöstä. Tekoäly tuottaa foneettisen translitteroinnin ja vertailevan tulkinnan.',
    originalSetupTitle: 'Alkukielipaketti puuttuu',
    originalSetupHint:
      'Alkukielitutkimusta varten asenna kreikka (UT) tai heprea (VT). Molemmat ovat kompakteja, vapaasti saatavilla olevia laitoksia.',
    originalInstallGreek: 'Asenna kreikka (UT) — greeksblgnt',
    originalInstallHebrew: 'Asenna heprea (VT) — heb-leningrad',
    originalSelectOriginal: 'Alkukielen lähde',
    originalSelectTranslations: 'Vertaa käännöksiin (1–3)',
    originalRunButton: 'Analysoi',
    originalLoading: 'Tutkitaan alkutekstiä…',
    originalAnalysisHeading: 'Tieteellinen analyysi',
    originalNoResult: 'Aloita analyysi nähdäksesi alkukielitutkimuksen.',
    originalNeedTargets: 'Valitse vähintään yksi käännös vertailtavaksi.',
    originalReferenceLabel: 'Viite',
    originalReferencePlaceholder: 'esim. Joh. 3:16 tai 1. Moos. 1:1',
    originalVersesHeading: 'Jakeet rinnakkain',
    originalAlreadyInstalled: 'Asennettu',

    errAnalyticsNeedVerse:
      'Viite-, luku- ja kirja-analyysi vaatii ensin jaehaun.',

    settingsCloseBackdrop: 'Sulje asetukset',
    settingsClose: 'Sulje',
    settingsDialogLabel: 'Asetukset',
    settingsHeading: 'Asetukset',
    settingsSubtitle: 'Käyttäjäasetukset tallennetaan tilillesi.',
    settingsProfile: 'Profiili',
    settingsUsername: 'Käyttäjänimi',
    settingsUserId: 'Käyttäjätunnus',
    settingsTheme: 'Teema',
    themeLight: 'Vaalea',
    themeDark: 'Tumma',
    themeSystem: 'Järjestelmä',
    settingsLoading: 'Ladataan asetuksia…',
    settingsInterfaceLang: 'Käyttöliittymän kieli',
    settingsInterfaceLangHint:
      'Kirjojen nimet ja valikot. Ei vaihda raamatun tekstiä (käännös erikseen).',
    langEnglish: 'English',
    langFinnish: 'Suomi',
    settingsTranslation: 'Käännös',
    settingsDefaultTranslation: 'Oletuskäännös',
    settingsNotSelected: 'Ei valittu',
    settingsChoose: 'Valitse…',
    settingsTranslationFootnote:
      'Asennetut käännökset ovat palvelimen laajuisia. Valintasi tallennetaan käyttäjää kohti.',

    translationModalTitle: 'Valitse käännös',
    translationSearchPlaceholder: 'Hae käännöksiä (id, nimi, kieli)…',
    translationSearchHint: 'Vinkki: kokeile “fin”, “greek”, “hebrew” tai käännös-id:tä kuten “web”.',
    translationFeaturedLabel: 'Tärkeimmät',
    translationInstalledSectionLabel: 'Asennetut',
    translationBrowseLabel: 'Selaa',
    translationBrowseLimitedHint: 'Lista on rajattu. Haku löytää lisää.',
    translationNoneInstalled:
      'Tällä palvelimella ei ole vielä asennettuja käännöksiä. Asenna jokin luettelosta.',
    translationCatalogLoading: 'Ladataan käännösluetteloa...',
    translationCatalogEmpty: 'Luettelosta ei löytynyt käännöksiä.',
    translationFooter:
      'Asennettavat käännökset tulevat jaetusta luettelosta. Asennetut käännökset ovat tämän palvelimen kohtaisia.',
    translationSelected: 'Valittu',
    translationUse: 'Käytä',
    translationInstalled: 'Asennettu',
    translationInstalling: 'Asennetaan...',
    translationInstall: 'Asenna',

    exportModalTitle: 'Vie materiaali',
    exportPreparing: 'Valmistellaan vientiä…',
    formatMdName: 'Markdown',
    formatMdDesc: 'Muistikirjat ja Obsidian.',
    formatHtmlName: 'HTML',
    formatHtmlDesc: 'Muotoiltu, tulostettava.',
    formatJsonName: 'JSON',
    formatJsonDesc: 'Rakennettu data kehittäjille.',
    formatTxtName: 'Pelkkä teksti',
    formatTxtDesc: 'Yksinkertainen, yleinen.',
    formatCsvName: 'CSV',
    formatCsvDesc: 'Taulukko-ohjelmiin.',
    formatXmlName: 'XML',
    formatXmlDesc: 'Tagipohjainen rakenne.',

    saveSearchSaved: 'Tallennettu',
    saveSearchPlaceholder: 'Anna haulle nimi…',
    saveSearchSave: 'Tallenna',
    saveSearchCancel: 'Peruuta',
    saveSearchPrompt: 'Tallenna tämä haku',
    savedSearchesLabel: 'Tallennetut haut',
    savedSearchRemove: 'Poista',
    savedSearchScopeTitle: (scope: string) => `Rajaus: ${scope}`,

    historyScopeOT: 'VT',
    historyScopeNT: 'UT',
    historyScopeWholeBible: 'Koko Raamattu',

    bookPickerTitle: 'Valitse kirja',
    bookPickerClose: 'Sulje',

    tabReading: 'Lukeminen',
    readingTitle: 'Lukeminen',
    readingSubtitle: 'Rakenna tapa päivittäisellä lukusuunnitelmalla.',
    readingLoading: 'Ladataan lukusuunnitelmaa…',
    readingDays: (n: number) => `${n} päivää`,
    readingDaysCompleted: (done: number, total: number) => `${done}/${total} päivää suoritettu`,
    readingActivePlan: 'Aktiivinen suunnitelma',
    readingStart: 'Aloita',
    readingAbandon: 'Hylkää',
    readingToday: 'Tänään',
    readingDay: (n: number) => `Päivä ${n}`,
    readingMarkComplete: 'Merkitse tehdyksi',
    readingCompleted: 'Suoritettu',
    readingNoPassages: 'Ei luettavaa tänään.',
    readingStreakAriaLabel: (n: number) => `Lukuputki: ${n} päivää`,

    readingPlanPsalms30Title: 'Psalmit 30 päivässä',
    readingPlanPsalms30Desc:
      'Lue psalmit 30 päivässä (viisi psalmia päivässä).',
    readingPlanNt90Title: 'Uusi testamentti 90 päivässä',
    readingPlanNt90Desc:
      'Lue Uusi testamentti 90 päivässä (pääosin kolme lukua päivässä).',
    readingPlanAnnualTitle: 'Raamattu vuodessa',
    readingPlanAnnualDesc:
      'Lue koko Raamattu 365 päivässä (automaattinen jako: 3–4 lukua päivässä).',
  },
} as const;

export type Messages = typeof strings.en;

export function t(lang: UILanguage): Messages {
  return strings[lang] as unknown as Messages;
}

/** UI copy for catalog reading plans (seed data is English; translate by stable id). */
export function localizedReadingPlanCopy(
  lang: UILanguage,
  plan: { id: string; name: string; description: string | null },
): { name: string; description: string | null } {
  const m = t(lang);
  switch (plan.id) {
    case '30day-psalms':
      return {
        name: m.readingPlanPsalms30Title,
        description: m.readingPlanPsalms30Desc,
      };
    case '90day-nt':
      return {
        name: m.readingPlanNt90Title,
        description: m.readingPlanNt90Desc,
      };
    case 'annual':
      return {
        name: m.readingPlanAnnualTitle,
        description: m.readingPlanAnnualDesc,
      };
    default:
      return { name: plan.name, description: plan.description };
  }
}

export function verseAriaLabel(verse: number, lang: UILanguage): string {
  return lang === 'fi' ? `Jae ${verse}` : `Verse ${verse}`;
}
