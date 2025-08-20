#!/usr/bin/env python3
"""
determine_tag.py

Extracts the base image tag from a Dockerfile and optionally writes it to $GITHUB_ENV.

Usage:
    python determine_tag.py <path-to-dockerfile>
"""

import os
import re
import sys
from typing import Optional


def read_dockerfile(path: str) -> list[str]:
    """Read the Dockerfile and return a list of lines."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()


def find_first_from_line(lines: list[str]) -> str:
    """Return the first FROM line in the Dockerfile."""
    for line in lines:
        if line.strip().upper().startswith("FROM"):
            return line.strip()
    raise ValueError("No FROM line found in Dockerfile")


def strip_build_alias(from_line: str) -> str:
    """Remove any trailing 'AS ...' alias from a FROM line."""
    return re.sub(r"\s+AS\s+.*", "", from_line, flags=re.IGNORECASE)


def extract_tag_from_from_line(from_line: str) -> str:
    """Extract the tag (after the last colon) from a FROM line."""
    if ":" not in from_line:
        raise ValueError(f"No tag found in FROM line: {from_line}")
    return from_line.split(":")[-1]


def write_to_github_env(tag: str, github_env: Optional[str] = None) -> None:
    """Write the TAG to $GITHUB_ENV if provided (used in GitHub Actions)."""
    if github_env:
        with open(github_env, "a", encoding="utf-8") as f:
            f.write(f"TAG={tag}\n")


def extract_tag(dockerfile_path: str) -> str:
    """High-level function to extract a tag from a Dockerfile."""
    lines = read_dockerfile(dockerfile_path)
    from_line = find_first_from_line(lines)
    cleaned = strip_build_alias(from_line)
    return extract_tag_from_from_line(cleaned)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python determine_tag.py <path-to-dockerfile>", file=sys.stderr)
        sys.exit(1)

    dockerfile_path = sys.argv[1]

    try:
        tag = extract_tag(dockerfile_path)
        print(f"TAG={tag}")
        write_to_github_env(tag, os.getenv("GITHUB_ENV"))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
