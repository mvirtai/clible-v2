STRINGS = {
    "en": {
        "search": "Search",
        "analytics": "Analytics",
        "verse": "Verse",
    },
    "fi": {
        "search": "Haku",
        "analytics": "Analyysi",
        "verse": "Jae",
    },
}


def t(key: str, lang: str) -> str:
    return STRINGS.get(lang, STRINGS["en"]).get(key, key)
