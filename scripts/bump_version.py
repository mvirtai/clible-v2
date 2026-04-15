import argparse
import re
import sys
from pathlib import Path

VERSION_COMMENT_PREFIX = "# Version "
PYPROJECT_VERSION_RE = re.compile(r'^(version\s*=\s*)"([^"]+)"', re.MULTILINE)
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)([-+].*)?$")


def bump_version(version_str: str) -> str:
    """Bump patch version by 1.

    Args:
        version_str: Version string in format "major.minor.patch" or
            "major.minor.patch-suffix".

    Returns:
        Bumped version with incremented patch number.
    """
    match = SEMVER_RE.match(version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")

    major, minor, patch, suffix = match.groups()
    return f"{major}.{minor}.{int(patch) + 1}.{suffix or ''}".rstrip(".")


def normalize_version(version_str: str) -> str:
    version = version_str.strip()
    if not version:
        raise ValueError("Version must not be empty")
    if not SEMVER_RE.match(version):
        raise ValueError(f"Version must follow semver-like format: {version}")
    return version


def read_version_file(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    first_line = text.splitlines()[0] if text else ""
    if first_line.startswith(VERSION_COMMENT_PREFIX):
        return first_line[len(VERSION_COMMENT_PREFIX) :].strip()
    raise ValueError(f"Could not read version from {path}")


def write_version_file(path: Path, version: str) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and lines[0].startswith(VERSION_COMMENT_PREFIX):
        lines[0] = f"{VERSION_COMMENT_PREFIX}{version}"
    else:
        lines.insert(0, f"{VERSION_COMMENT_PREFIX}{version}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_pyproject_version(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = PYPROJECT_VERSION_RE.search(text)
    if not match:
        raise ValueError(f"Could not find version in {path}")
    return match.group(2)


def write_pyproject_version(path: Path, version: str) -> None:
    text = path.read_text(encoding="utf-8")
    replacement, count = PYPROJECT_VERSION_RE.subn(rf"\1\"{version}\"", text, count=1)
    if count != 1:
        raise ValueError(f"Could not replace version in {path}")
    path.write_text(replacement, encoding="utf-8")


def validate_matching_versions(version_file: Path, pyproject_file: Path) -> str:
    version_file_version = read_version_file(version_file)
    pyproject_version = read_pyproject_version(pyproject_file)
    if version_file_version != pyproject_version:
        raise ValueError(
            f"Version mismatch between {version_file} ({version_file_version}) "
            f"and {pyproject_file} ({pyproject_version}). "
            "Specify a single version to align both files."
        )
    return version_file_version


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Set or bump project version in VERSION and pyproject.toml."
    )
    parser.add_argument(
        "version",
        nargs="?",
        help="Version string to set, e.g. 2.0.0-beta. If omitted, reads current version interactively.",  # noqa: E501
    )
    parser.add_argument(
        "--bump",
        action="store_true",
        help="Bump the patch version from the current project version.",
    )
    parser.add_argument(
        "--version-file",
        default="VERSION",
        help="Path to VERSION file.",
    )
    parser.add_argument(
        "--pyproject",
        default="pyproject.toml",
        help="Path to pyproject.toml.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the proposed changes without writing files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    version_file = Path(args.version_file)
    pyproject_file = Path(args.pyproject)

    if args.bump and args.version:
        raise ValueError("Cannot use --bump and a version string at the same time.")

    if args.bump:
        current_version = validate_matching_versions(version_file, pyproject_file)
        version = bump_version(current_version)
    elif args.version:
        version = normalize_version(args.version)
    else:
        if sys.stdin.isatty():
            version = normalize_version(input("Enter version to set (e.g. 2.0.0-beta): ").strip())
        else:
            raise ValueError("Version is required when not running interactively.")

    print(f"Setting version to: {version}")
    print(f"  - {version_file}")
    print(f"  - {pyproject_file}")

    if not args.dry_run:
        write_version_file(version_file, version)
        write_pyproject_version(pyproject_file, version)
        print("Updated versions successfully.")
    else:
        print("Dry run enabled; no files changed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
