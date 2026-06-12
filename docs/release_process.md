# Release Process

This repository should use GitHub Releases with SemVer-style tags.

## Version Policy

- Use tags in the form `vMAJOR.MINOR.PATCH`.
- Keep `pyproject.toml`, `src/airlock_mcp/__init__.py`, and
  `CHANGELOG.md` aligned.
- During `0.x`, minor releases may add or change supported tool behavior. Patch
  releases should be bugfixes, docs corrections, and compatibility fixes.
- If a release requires a new Airlock stored procedure signature or return
  contract, name the minimum Airlock API version or installed documentation hash
  in the release notes.

## Before Tagging

1. Confirm the working tree contains only intended changes.
2. Run:
   ```bash
   uv run --extra dev ruff check .
   uv run --extra dev python -m pytest
   git diff --check
   python3 scripts/validate_skill.py airlock
   python3 scripts/package_coco_skill.py
   uv build
   ```
3. Update `CHANGELOG.md`.
4. Update versions in `pyproject.toml` and `src/airlock_mcp/__init__.py`.
5. Confirm the public repo has the intended license, repository URL, package
   name, and release target.
6. Commit the release.
7. Create an annotated tag:
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   ```
8. Push the commit and tag, then create a GitHub Release from the tag.

## Distribution

Publish in this order:

1. GitHub Release from the tag.
2. Python package named `airlock-skills`, when package publishing is ready.
3. Canonical `airlock/` directory from the released Git tag.

## Release Notes

Release notes should say:

- where to install the MCP server package or Git release
- how to import or copy the `airlock/` directory
- how CoCo users should install the `airlock/` skill folder under
  `.snowflake/cortex/skills/airlock/`
- what changed for MCP users
- what changed for the Airlock skill
- whether installed Airlock procedure contracts changed
- whether any safety defaults changed
- which tests were run
