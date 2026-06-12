# Changelog

This project follows SemVer-style GitHub releases. Tags should use the
`vMAJOR.MINOR.PATCH` form, such as `v0.1.0`.

## Unreleased

## 0.3.2 - 2026-06-12

- Added stronger spec-creation guidance so agents reason through object grain,
  business timestamps, attachments, metadata, variants, and control structures
  before drafting spec JSON.
- Added CoCo-oriented guidance for using the Airlock spec library as a pattern
  source while treating local/uploaded files as more reliable than live web
  access.

## 0.3.1 - 2026-06-11

- Corrected MCP positioning: CoCo and Snowflake-native agents should use the
  Airlock skill plus direct stored procedures first; MCP remains optional for
  external/non-Snowflake agent hosts.

## 0.3.0 - 2026-06-11

- Promoted Snowflake-managed MCP to a first-class path for CoCo, CoWork,
  and Cortex Agents, with a concrete `CREATE MCP SERVER` guide alongside the
  portable MCP quickstart.
- Documentation cleanup after `v0.2.0`: refreshed release-process wording,
  upstream delegation/tooling sync notes, and canonical `airlock_skills/`
  packaging.
- Added governed `posts` / `published_posts` demo guidance so agents discover
  the `agent` Airlock role, use user procedures, submit to
  `public/append_access`, and read back through the reference spec without
  falling back to admin procedures.
- Added records JSON authoring guidance so agents keep business payloads
  separate from role, path, workflow, delegation, attachment, and audit context.
- Added agent-architecture pattern guidance for dedicated human-agent pairing,
  delegation vs impersonation, workflow pushback, watcher polling, published
  reference specs, and chained reviewer/agent handoffs.

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
