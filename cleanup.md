# Airlock Skills Cleanup

## Variables

- `last_improve_dependency_sync_at`: `2026-05-26`
- `last_improve_cleanup_pass_at`: `2026-06-06`
- `last_improve_coverage_pass_at`: `null`

## Follow-up backlog

| Date | Source | Target | Issue | Suggested next action |
| --- | --- | --- | --- | --- |
| 2026-05-18 | Upstream Airlock `docs/airlock-skills.md` | `README.md`, `docs/*.md`, `airlock_skills/SKILL.md` | The upstream combined guide is broader than this repo's focused docs. | Decide whether to make `docs/airlock-skills.md` the primary guide in this repo or keep it as an upstream sync reference. |

## Done log

- 2026-06-06: Implemented the skill packaging improvement plan: kept
  `airlock_skills/` canonical as the only committed user skill, kept optional
  provider-copy generation, added business-leader starting guidance, and
  documented skill upgrade steps.
- 2026-05-26: Re-ran dependent-repo sync; confirmed shared
  `agent_delegation`, `airlock-skills`, and `airlock_spec_design` docs match
  upstream, kept the distributable `airlock_skills/` package aligned with
  current agent guidance, and verified the tool repo checks.
- 2026-05-19: Re-ran dependent-repo sync after `v0.2.0`; confirmed
  `docs/agent_delegation.md` and `docs/airlock-skills.md` match upstream,
  verified delegated `validate_data`, `replace_attachment`, and
  `edit_file_workflow` signatures against Airlock wrappers, and refreshed
  post-release docs wording.
- 2026-05-22: Added a top-level `airlock_skills/` skill package with `SKILL.md`,
  examples, templates, and references so agents can load Airlock guidance
  without pointing at `docs/` or provider-specific skill paths.
- 2026-05-18: Bootstrapped dependent-repo maintenance docs, synced upstream
  `docs/agent_delegation.md` and `docs/airlock-skills.md`, added user-safe
  delegation MCP tools/parameters, and refreshed delegation guidance.
- 2026-05-18: Ran inbound dependency sync after v0.1.0 release; verified
  delegation, license, work-item, and expectation procedure names against
  upstream Airlock wrappers, kept upstream app-object-name guidance, and added
  the same caveat to the skill docs.
- 2026-05-19: Synced current upstream delegation docs and moved-guide redirects,
  verified delegated `validate_data`, `replace_attachment`, and
  `edit_file_workflow` signatures against Airlock procedure wrappers, and
  updated MCP tools/tests to pass delegated context for those procedures.
