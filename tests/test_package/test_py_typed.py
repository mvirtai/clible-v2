"""Packaging markers (PEP 561)."""

from importlib.resources import files


def test_py_typed_marker_present_in_package():
    """Installed/distribution layout exposes py.typed for type checkers."""
    marker = files("clible") / "py.typed"
    assert marker.is_file()
