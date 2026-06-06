# Changelog

This project follows SemVer-style GitHub releases. Tags should use the
`vMAJOR.MINOR.PATCH` form, such as `v0.1.0`.

## Unreleased

- Documentation cleanup after `v0.2.0`: refreshed release-process wording,
  upstream delegation/tooling sync notes, and canonical `airlock_skills/`
  packaging.

## 0.2.0 - 2026-05-19

Delegation compatibility update for the current Airlock user API:

- Added delegated context passthrough for `airlock_validate_data`,
  `airlock_replace_attachment`, and `airlock_edit_file_workflow`.
- Refreshed MCP, Airlock skill, and design guidance for current Airlock
  delegation behavior.
- Synced Airlock delegation and tooling docs from upstream Airlock source docs.
- Added tests for delegated validation, attachment replacement, and workflow
  procedure-call construction.

## 0.1.0 - 2026-05-18

Initial public scaffold for Airlock Skills:

- User-safe Airlock MCP server for documented `airlock.user.*` procedures.
- User-safe delegation tools and delegated load/attachment context.
- Canonical Airlock skill for safe Airlock usage through SQL or MCP tools.
- Snowflake CLI guidance for installed documentation discovery.
- Design docs for MCP usage, Airlock skills, delegation, install/security,
  version/source-of-truth boundaries, and agent-oriented Airlock architecture.
