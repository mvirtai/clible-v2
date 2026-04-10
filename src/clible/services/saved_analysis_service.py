import json
from typing import Any

from clible.db.repositories.saved_analysis_repo import SavedAnalysisRepo, SavedAnalysisRow
from clible.services.analytic_service import AnalyticService
from clible.services.scope_service import ScopeService


class SavedAnalysisService:
    """Service to save and re-execute Bible text analysis."""

    def __init__(
        self,
        saved_analysis_repo: SavedAnalysisRepo,
        scope_service: ScopeService,
        analytic_service: AnalyticService,
    ):
        """Initialize with repos and analytics engine."""
        self._repo = saved_analysis_repo
        self._scope_service = scope_service
        self._analytic_service = analytic_service

    def save_analysis(
        self,
        name: str,
        reference: str,
        analysis_type: str,
        translation_id: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Save analysis parameters to the current scope."""
        scope_id = self._scope_service.get_current_scope_id()
        params_json = json.dumps(params) if params else None
        return self._repo.create(
            scope_id, name, reference, analysis_type, translation_id, params_json
        )

    def list_saved_analyses(self) -> list[SavedAnalysisRow]:
        """List all saved analyses in the current scope."""
        scope_id = self._scope_service.get_current_scope_id()
        return self._repo.list_by_scope(scope_id)

    def get_and_run(self, identifier: str) -> tuple[SavedAnalysisRow, Any]:
        """Fetch a saved analysis by ID or name and re-execute it.

        Args:
            identifier: UUID or name of the saved analysis.

        Returns:
            Tuple of (SavedAnalysisRow, analysis results).

        Raises:
            ValueError: If the analysis is not found or type is unknown.
        """
        scope_id = self._scope_service.get_current_scope_id()

        # Try ID, then Name
        saved = self._repo.get(identifier)
        if not saved or saved["scope_id"] != scope_id:
            saved = self._repo.get_by_name(identifier, scope_id)

        if not saved:
            raise ValueError(f"Saved analysis '{identifier}' not found in current scope.")

        params = json.loads(saved["params_json"]) if saved["params_json"] else {}
        atype = saved["analysis_type"]
        ref = saved["reference"]
        tid = saved["translation_id"]

        if atype == "reference":
            result = self._analytic_service.analyze_reference(ref, tid, **params)
        elif atype == "chapter":
            # For chapter analysis, we can just use analyze_reference since it handles strings
            # and chapter subcommands in CLI already produce valid chapter references.
            result = self._analytic_service.analyze_reference(ref, tid, **params)
        elif atype == "book":
            # Same for book
            result = self._analytic_service.analyze_reference(ref, tid, **params)
        elif atype == "compare":
            trans_b = params.get("translation_b")
            if not trans_b:
                raise ValueError("Comparison analysis missing 'translation_b' parameter.")
            result = self._analytic_service.compare_translations(ref, tid, trans_b)
        else:
            raise ValueError(f"Unsupported analysis type: {atype}")

        return saved, result

    def delete_saved_analysis(self, identifier: str) -> bool:
        """Delete a saved analysis by ID from the current scope."""
        scope_id = self._scope_service.get_current_scope_id()
        # Try as ID primary
        deleted = self._repo.delete(identifier, scope_id)
        if not deleted:
            # Try as name
            saved = self._repo.get_by_name(identifier, scope_id)
            if saved:
                deleted = self._repo.delete(saved["id"], scope_id)
        return deleted
