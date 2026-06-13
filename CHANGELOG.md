# Changelog

This project follows SemVer-style GitHub releases. Tags should use the
`vMAJOR.MINOR.PATCH` form, such as `v0.1.0`.

## Unreleased

## 0.4.1 - 2026-06-13

- Improved the CoCo Airlock skill for `CREATE_SPEC_FAILED` troubleshooting:
  `VALIDATION.invalid_tabs` is described as failed validation sections, not
  unknown JSON keys.
- Documented validator-correct spec creation shapes for CoCo, including
  canonical CSV `file_rules`, guest-access public folder requirements, and
  strftime date/datetime formats such as `%Y-%m-%d` instead of invalid display
  masks such as `YYYY-MM-DD`.
- Updated bundled CoCo spec templates to use the canonical `airlock/` package
  folder, validator-shaped column configs, canonical CSV file-rule keys, and a
  copyable date column with a strftime format.
- Kept the root skill lean by moving duplicated detailed examples into bundled
  references while preserving the CoCo-critical blocker guidance in `SKILL.md`.

## 0.4.0 - 2026-06-12

- Renamed the canonical skill directory from `airlock_skills/` to `airlock/`
  so the repository, release asset, CoCo install path, and skill frontmatter
  all use the same skill folder name.

## 0.3.3 - 2026-06-12

- Added CoCo packaging guidance and a `scripts/package_coco_skill.py` helper
  that produces an install-time skill folder named `airlock`.

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
  upstream delegation/tooling sync notes, and canonical `airlock/`
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
