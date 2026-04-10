from sys import version


print(f"Current version: {VERSION}") nump:version

def bump_version(version):
    major, minor, patch = map(int, version.split("."))
    patch += 1
    return f"{major}.{minor}.{patch}"
