def bump_version(version_str: str) -> str:
    """Bump patch version by 1.

    Args:
        version_str: Version string in format "major.minor.patch"

    Returns:
        Bumped version with incremented patch number
    """
    major, minor, patch = map(int, version_str.split("."))
    patch += 1
    return f"{major}.{minor}.{patch}"
