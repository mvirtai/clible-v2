"""Translation catalog sync.

Fetches available Bible translation XML files from upstream GitHub repos
(USFX/OSIS/ZEFANIA from `seven1m/open-bibles`, BEBLIA from `Beblia/Holy-Bible-XML-Format`),
then merges them into the local `src/clible/data/translations.json` catalog.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

_OPEN_BIBLES_OWNER = "seven1m"
_OPEN_BIBLES_REPO = "open-bibles"
_BEBLIA_OWNER = "Beblia"
_BEBLIA_REPO = "Holy-Bible-XML-Format"

_OPEN_BIBLES_REF = "master"
_BEBLIA_REF = "master"


class TranslationCatalogSyncError(RuntimeError):
    pass


@dataclass(frozen=True)
class DiscoveredTranslation:
    id: str | None
    name: str
    language: str
    format: str
    filename: str
    url: str
    size_mb: float
    base: str


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify_id(text: str) -> str:
    """Convert arbitrary filename-like text into a stable lowercase slug."""
    normalized = text.strip().lower()
    normalized = _SLUG_RE.sub("-", normalized)
    normalized = normalized.strip("-")
    return normalized or "translation"


def _titleize_from_base(base: str) -> str:
    # Keep it simple and deterministic; existing entries preserve more curated names.
    cleaned = base.replace("-", " ").replace("_", " ").replace(".", " ")
    parts = [p for p in cleaned.split() if p]
    return " ".join(p[:1].upper() + p[1:].lower() for p in parts) if parts else "Bible Translation"


_OPEN_BIBLES_LANG_3_TO_2 = {
    "eng": "en",
    "fin": "fi",
    "fra": "fr",
    "deu": "de",
    "ger": "de",
    "spa": "es",
    "ita": "it",
    "por": "pt",
    "rus": "ru",
    "nld": "nl",
    "swe": "sv",
    "dan": "da",
    "nor": "no",
    "pol": "pl",
    "cze": "cs",
    "ces": "cs",
    "tur": "tr",
    "hun": "hu",
    "ara": "ar",
    "heb": "he",
    "ell": "el",
    "elln": "el",
    "gre": "el",
}


def guess_language_from_openbibles_base(base: str) -> str:
    token = re.split(r"[-_.\s]+", base.lower(), maxsplit=1)[0] if base else ""
    return _OPEN_BIBLES_LANG_3_TO_2.get(token, token[:2] if token else "en")


def guess_language_from_beblia_base(base: str) -> str:
    lower = base.lower()
    if "finnish" in lower:
        return "fi"
    if "english" in lower:
        return "en"
    if "swedish" in lower:
        return "sv"
    if "norwegian" in lower:
        return "no"
    return "en"


def _raw_github_url(owner: str, repo: str, ref: str, path: str) -> str:
    # Raw URLs work for seeding and for `CLIBLE_SEED_BASE_URL` overrides (which use `filename`).
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"


def infer_openbibles_format_and_base(filename: str) -> tuple[str, str] | None:
    lower = filename.lower()
    if lower.endswith(".usfx.xml"):
        return "USFX", filename[: -len(".usfx.xml")]
    if lower.endswith(".osis.xml"):
        return "OSIS", filename[: -len(".osis.xml")]
    if lower.endswith(".zefania.xml"):
        return "ZEFANIA", filename[: -len(".zefania.xml")]
    return None


def infer_beblia_format_and_base(filename: str) -> tuple[str, str] | None:
    lower = filename.lower()
    if lower.endswith("bible.xml"):
        # Example: `Finnish1992Bible.xml` -> `Finnish1992`
        return "BEBLIA", filename[: -len("Bible.xml")]
    if lower.endswith(".xml"):
        return "BEBLIA", filename[: -len(".xml")]
    return None


def merge_translations_catalog(
    existing_catalog: dict[str, dict[str, Any]],
    discovered: Iterable[DiscoveredTranslation],
) -> dict[str, dict[str, Any]]:
    """Merge discovered items into the existing catalog.

    - Keeps existing `id` values when filenames match.
    - Otherwise generates stable IDs from the derived `base`.
    """
    out: dict[str, dict[str, Any]] = dict(existing_catalog)

    existing_by_filename: dict[str, str] = {}
    for tid, entry in out.items():
        filename = entry.get("filename")
        if isinstance(filename, str) and filename:
            existing_by_filename[filename] = tid

    used_ids = set(out.keys())

    for item in discovered:
        existing_id = existing_by_filename.get(item.filename)
        if existing_id:
            tid = existing_id
        else:
            tid = slugify_id(item.base)
            if tid in out and out[tid].get("filename") != item.filename:
                # Avoid collisions across generated entries.
                suffix = item.format.lower()
                candidate = f"{tid}-{suffix}"
                i = 2
                while candidate in out and out[candidate].get("filename") != item.filename:
                    candidate = f"{tid}-{suffix}-{i}"
                    i += 1
                tid = candidate

        existing_entry = out.get(tid, {})
        out[tid] = {
            "name": existing_entry.get("name") or item.name,
            "language": existing_entry.get("language") or item.language,
            "format": item.format,
            "filename": item.filename,
            "url": item.url,
            "size_mb": item.size_mb,
        }
        used_ids.add(tid)

    return out


def _fetch_github_tree(
    *,
    owner: str,
    repo: str,
    ref: str,
    github_token: str | None,
    timeout_seconds: int,
) -> list[dict[str, Any]]:
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{ref}?recursive=1"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "clible/translation-catalog-sync",
    }
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    resp = requests.get(url, headers=headers, timeout=timeout_seconds)
    resp.raise_for_status()
    payload = resp.json()
    if not isinstance(payload, dict) or not isinstance(payload.get("tree"), list):
        raise TranslationCatalogSyncError(
            f"Unexpected GitHub API response shape for {owner}/{repo}"
        )
    return payload["tree"]


def discover_openbibles_translations(
    *,
    github_token: str | None,
    timeout_seconds: int = 60,
) -> list[DiscoveredTranslation]:
    tree = _fetch_github_tree(
        owner=_OPEN_BIBLES_OWNER,
        repo=_OPEN_BIBLES_REPO,
        ref=_OPEN_BIBLES_REF,
        github_token=github_token,
        timeout_seconds=timeout_seconds,
    )

    discovered: list[DiscoveredTranslation] = []
    for entry in tree:
        if entry.get("type") != "blob":
            continue
        path = str(entry.get("path", ""))
        if not path:
            continue
        inferred = infer_openbibles_format_and_base(path)
        if not inferred:
            continue
        fmt, base = inferred
        filename = path
        language = guess_language_from_openbibles_base(base)
        name = _titleize_from_base(base)
        discovered.append(
            DiscoveredTranslation(
                id=None,
                name=name,
                language=language,
                format=fmt,
                filename=filename,
                url=_raw_github_url(
                    _OPEN_BIBLES_OWNER,
                    _OPEN_BIBLES_REPO,
                    _OPEN_BIBLES_REF,
                    filename,
                ),
                size_mb=0.0,  # Size is optional; keep numeric for schema stability.
                base=base,
            )
        )

    return discovered


def discover_beblia_translations(
    *,
    github_token: str | None,
    timeout_seconds: int = 60,
) -> list[DiscoveredTranslation]:
    tree = _fetch_github_tree(
        owner=_BEBLIA_OWNER,
        repo=_BEBLIA_REPO,
        ref=_BEBLIA_REF,
        github_token=github_token,
        timeout_seconds=timeout_seconds,
    )

    discovered: list[DiscoveredTranslation] = []
    for entry in tree:
        if entry.get("type") != "blob":
            continue
        path = str(entry.get("path", ""))
        if not path:
            continue

        # Heuristic: prioritize files that look like Bible translations.
        if not path.lower().endswith("bible.xml"):
            continue

        inferred = infer_beblia_format_and_base(path)
        if not inferred:
            continue
        fmt, base = inferred
        filename = path
        language = guess_language_from_beblia_base(base)
        name = _titleize_from_base(base)
        discovered.append(
            DiscoveredTranslation(
                id=None,
                name=name,
                language=language,
                format=fmt,
                filename=filename,
                url=_raw_github_url(
                    _BEBLIA_OWNER,
                    _BEBLIA_REPO,
                    _BEBLIA_REF,
                    filename,
                ),
                size_mb=0.0,
                base=base,
            )
        )

    return discovered


def sync_translations_catalog(
    *,
    catalog_path: Path | None = None,
    github_token: str | None = None,
    timeout_seconds: int = 60,
) -> dict[str, int]:
    """Synchronize the local translations catalog with upstream sources.

    Writes `catalog_path` in-place.
    """
    if catalog_path is None:
        catalog_path = Path(__file__).resolve().parent.parent / "data" / "translations.json"

    if not catalog_path.exists():
        raise TranslationCatalogSyncError(f"Catalog file not found: {catalog_path}")

    existing_catalog: dict[str, dict[str, Any]] = json.loads(
        catalog_path.read_text(encoding="utf-8")
    )

    token = github_token or None

    openbibles_items = discover_openbibles_translations(
        github_token=token, timeout_seconds=timeout_seconds
    )
    beblia_items = discover_beblia_translations(
        github_token=token, timeout_seconds=timeout_seconds
    )

    discovered = [*openbibles_items, *beblia_items]

    merged = merge_translations_catalog(existing_catalog, discovered)

    catalog_path.write_text(
        json.dumps(merged, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    return {
        "existing_count": len(existing_catalog),
        "discovered_count": len(discovered),
        "merged_count": len(merged),
    }

