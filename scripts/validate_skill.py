#!/usr/bin/env python3
"""Validate the repository's Airlock skill folder without external dependencies."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata"}


def _frontmatter(skill_md: Path) -> str:
    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        raise ValueError("No YAML frontmatter found.")

    end_marker = "\n---\n"
    end = content.find(end_marker, 4)
    if end == -1:
        raise ValueError("Invalid frontmatter format.")
    return content[4:end]


def _top_level_values(frontmatter: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if not line or line.startswith((" ", "-")):
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$", line)
        if not match:
            raise ValueError(f"Invalid frontmatter line: {line}")
        key, value = match.groups()
        values[key] = (value or "").strip().strip("'\"")
    return values


def validate_skill(skill_dir: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise ValueError(f"SKILL.md not found: {skill_md}")

    values = _top_level_values(_frontmatter(skill_md))
    unexpected = set(values) - ALLOWED_FRONTMATTER_KEYS
    if unexpected:
        allowed = ", ".join(sorted(ALLOWED_FRONTMATTER_KEYS))
        found = ", ".join(sorted(unexpected))
        raise ValueError(f"Unexpected frontmatter key(s): {found}. Allowed keys: {allowed}")

    for required in ("name", "description"):
        if required not in values or not values[required]:
            raise ValueError(f"Missing required frontmatter value: {required}")

    name = values["name"]
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError("Skill name must be hyphen-case with lowercase letters, digits, and hyphens.")
    if len(name) > MAX_SKILL_NAME_LENGTH:
        raise ValueError(f"Skill name is too long: {len(name)} characters.")
    if skill_dir.name != name:
        raise ValueError(f"Skill folder must match frontmatter name: expected {name}, got {skill_dir.name}")

    description = values["description"]
    if "<" in description or ">" in description:
        raise ValueError("Description cannot contain angle brackets.")
    if len(description) > MAX_DESCRIPTION_LENGTH:
        raise ValueError(f"Description is too long: {len(description)} characters.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Airlock skill folder.")
    parser.add_argument("skill_dir", type=Path)
    args = parser.parse_args()

    try:
        validate_skill(args.skill_dir)
    except ValueError as exc:
        print(f"Skill is invalid: {exc}")
        return 1

    print("Skill is valid!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
