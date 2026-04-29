"""Tests for analytics_export compatibility re-export module."""

from clible.ui import analytics_export
from clible.ui.export import export_compare as export_compare_from_export


def test_analytics_export_re_exports_expected_symbols():
    assert "export_compare" in analytics_export.__all__
    assert "validate_export_format" in analytics_export.__all__
    assert analytics_export.export_compare is export_compare_from_export
