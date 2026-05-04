"""Structured search request: phrase, boolean (FTS5), or wildcard (REGEXP)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

SearchMode = Literal["phrase", "boolean", "wildcard"]
SearchOperator = Literal["AND", "OR", "NOT"]


@dataclass
class SearchQuery:
    """User search intent separate from FTS5/regex details."""

    terms: list[str]
    operator: SearchOperator = "AND"
    mode: SearchMode = "phrase"
    translation_id: str | None = None
    scope: str = "bible"
    scope_ref: str | None = None

    def to_fts5_match(self) -> str:
        """Build the FTS5 MATCH string for phrase or boolean mode."""
        if self.mode == "wildcard":
            raise ValueError("Wildcard mode does not use FTS5 MATCH.")
        if self.mode == "phrase":
            term = " ".join(self.terms).strip()
            return f'"{term}"'
        if len(self.terms) == 1:
            return self.terms[0]
        joined = f" {self.operator} ".join(self.terms)
        return joined

    def to_regex_pattern(self) -> str:
        """Translate wildcard syntax to a Python regex for REGEXP search."""
        if self.mode != "wildcard":
            raise ValueError("to_regex_pattern() is only valid in wildcard mode.")
        raw = self.terms[0] if self.terms else ""
        escaped = re.escape(raw)
        return escaped.replace(r"\*", r"\w*").replace(r"\?", ".")
