"""Read package version in pyproject.toml."""

import argparse
import re


def get_version():
    """Read package version from pyproject.toml."""
    with open("./pyproject.toml") as file:
        content = file.read()
    version_match = re.search(r'^version\s*=\s*"([\d.]*)"', content, re.MULTILINE)
    if version_match:
        return version_match.group(1)
    msg = "Package version not found in pyproject.toml"
    raise Exception(msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--only_package_version",
        type=bool,
        default=False,
        help="Only display current package version",
    )
    args = parser.parse_args()
    version = get_version()
    print(version)  # noqa: T201
