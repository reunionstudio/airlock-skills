# Changelog

This project follows SemVer-style GitHub releases. Tags should use the
`vMAJOR.MINOR.PATCH` form, such as `v0.1.0`.

## Unreleased

- No unreleased changes yet.

## 0.2.0 - 2026-05-19

Delegation compatibility update for the current Airlock user API:

- Added delegated context passthrough for `airlock_validate_data`,
  `airlock_replace_attachment`, and `airlock_edit_file_workflow`.
- Refreshed MCP, Cortex Code skill, and design guidance for current Airlock
  delegation behavior.
- Synced Airlock delegation and tooling docs from upstream Airlock source docs.
- Added tests for delegated validation, attachment replacement, and workflow
  procedure-call construction.

## 0.1.0 - 2026-05-18

Initial public scaffold for Airlock Tools:

- User-safe Airlock MCP server for documented `airlock.user.*` procedures.
- User-safe delegation tools and delegated load/attachment context.
- Cortex Code skill for safe Airlock usage through SQL or MCP tools.
- Tooling-maintenance skill for Airlock API drift checks.
- Snowflake CLI guidance for installed documentation discovery.
- Design docs for MCP usage, Cortex Code skills, delegation, install/security,
  version/source-of-truth boundaries, and agent-oriented Airlock architecture.
