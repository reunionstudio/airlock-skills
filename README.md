# Airlock Skills and MCP Tools

Airlock Skills and MCP Tools helps AI agents use Airlock safely. The repo
publishes one canonical Airlock skill directory plus an optional portable MCP
server for agents that benefit from MCP transport. Airlock's primary API remains
its Snowflake stored procedures.

The core rule is simple: agents should use documented Airlock procedures and
preserve structured results. They should not write directly to Airlock-owned
stages, hybrid tables, secure views, generated views, generated tables, or
replacement apps.

## What Is Here

- `airlock_skills/`: the canonical Airlock skill directory. It contains
  `SKILL.md`, references, examples, and templates.
- `src/airlock_mcp/`: a user-safe portable MCP server for documented
  `airlock.user.*` procedure workflows when an agent host benefits from MCP.
- `docs/`: design, release, MCP, delegation, install/security, and Airlock
  architecture guidance.
- `tests/`: unit tests for procedure call construction, result normalization,
  safety gates, and delegation parameters.

## Quickstart

Use the skill by importing or copying the `airlock_skills/` directory into your
agent's skill system. Each AI tool is responsible for its own skill-import
mechanics; this repo does not maintain provider-specific mirrors.

For CoCo, install the skill with the folder name `airlock`, matching the
`name: airlock` frontmatter. The source directory is named `airlock_skills` for
this repo, but the CoCo workspace destination should be:

```text
.snowflake/cortex/skills/airlock/
```

Create a ready-to-copy folder and zip with:

```bash
python3 scripts/package_coco_skill.py
```

For Snowflake-native agents such as CoCo, start with the skill and direct
Airlock stored-procedure calls. CoCo already runs inside Snowflake, so an MCP
layer is optional rather than required.

For MCP clients outside Snowflake, use the portable MCP server. Start with
[docs/quickstart-mcp.md](docs/quickstart-mcp.md).

Install portable MCP from GitHub Releases today. After package publication, run
the portable MCP server as the Python package named `airlock-skills`.

## Documentation Source Priority

1. Installed Airlock docs from `airlock.user.documentation(...)` for exact
   procedure contracts and the active app version.
2. The public [Airlock documentation site](https://reunionstudio.io/airlock/docs/index.html)
   for product concepts, guides, and operator-facing context.
3. The public [Airlock spec library](https://reunionstudio.io/airlock/docs/spec-library.html)
   for spec modeling examples and reusable business-object patterns.

For the upstream combined agent/tooling guide synced from Airlock, see
[docs/airlock-skills.md](docs/airlock-skills.md).

## Architecture Premise

In an Airlock-oriented agent architecture, Snowflake is the direct system of
record for governed business outputs, not merely a downstream analytics
warehouse where data lands after another app creates the official record.

Airlock is the governance layer between adaptive work and the system of record:
it defines specs, validation, workflow, attachments, references, expectations,
roles, delegation, and governed procedure boundaries.

## Role Boundaries

- Snowflake roles and Snowflake application roles control the session and which
  installed app procedures can be called.
- Airlock roles control business access inside Airlock: specs, paths, workflow,
  attachments, references, and expectations.
- A spec owner is the Airlock role named as a spec's owner role. It can see all
  data for that spec and manage workflows, even when it is not a spec admin.
- Airlock spec admin is a delegated Airlock role capability for editing spec
  configuration or expectations. It is not required for spec ownership and is
  not the same thing as Snowflake `app_admin`.
- Airlock role hierarchy uses `managed_by_role`: a manager role can include
  managed child roles when procedures support managed-role expansion. The child
  does not automatically inherit the manager role's access. Do not set
  `managed_by_role` to `app_admin`; all roles are already manageable by
  `app_admin`.

## Install And Native App Setup

- Airlock Marketplace listing:
  [Reunion Studio Airlock](https://app.snowflake.com/marketplace/listing/GZTSZ1QRFJ6L/reunion-studio-airlock).
- Airlock may request `CREATE DATABASE` so the Native App can create and own
  `AIRLOCK_DATA`, where it stores governed files, manifests, attachments,
  tables, views, and operational data.
- Before uninstalling Airlock, transfer ownership of app-owned objects that
  should be retained. Dropping the app with cascading deletion can delete
  app-owned files and data.
- If `AIRLOCK_DATA` is retained for archival use and Airlock will be reinstalled
  later, rename the retained database first. A fresh install needs to create and
  own a database named exactly `AIRLOCK_DATA`.

## MCP Status

Airlock does not need MCP to work. The Snowflake Native App stored procedures
are the primary AI-facing API, especially for Snowflake-native agents such as
CoCo. The portable MCP server is an optional adapter for MCP-capable agents
outside Snowflake or hosts that strongly prefer MCP tool discovery. Its
user-safe tool surface focuses on:

- Snowflake and Airlock context discovery.
- Installed Airlock documentation and procedure registry discovery.
- Airlock role and license checks.
- Self-service delegation creation and delegation discovery.
- Spec listing and description.
- Inline CSV validation and loading.
- File listing, file selection, and guarded deletion previews.
- Workflow work item listing and validate-first workflow transitions.
- User-visible expectation work/status listing.
- File attachment add, replace, and delete.
- Read-only MCP resources and workflow prompts.

Admin tools are intentionally not exposed in this first cut. The code keeps the
boundary ready for explicit admin mode, but the MVP should be useful for normal
agent submission and review flows first.

Delegated load and attachment calls preserve Airlock's structured actor,
principal, and delegation context. The MCP server does not expose delegated
destructive or governance actions.

## Implementation Choice

The portable MCP server is implemented in Python because Airlock is a
Snowflake-native product and Python has mature Snowflake connector support. MCP
does not require Python. A Node implementation would also be reasonable if
distribution through JavaScript package managers or a TypeScript-first agent
stack becomes more important.

The important contract is not the runtime. It is that tools remain thin wrappers
around documented Airlock stored procedures and preserve structured Airlock
results.

## Versioning

Use GitHub Releases and SemVer tags for this repo:

- Tag releases as `vMAJOR.MINOR.PATCH`, for example `v0.1.0`.
- Keep the Python package version in `pyproject.toml` and
  `src/airlock_mcp/__init__.py` aligned.
- Update [CHANGELOG.md](CHANGELOG.md) before tagging a release.
- During `0.x`, treat minor versions as meaningful feature releases and patch
  versions as bugfix/docs-only releases.
- Call out the minimum supported Airlock stored procedure API version when a
  release depends on a new installed Airlock contract.

## Distribution

- GitHub is the source of truth for docs, the canonical skill, source, tests,
  and releases.
- GitHub Releases and tags provide stable install targets.
- The portable Python package name is `airlock-skills`; the MCP server command
  is `airlock-mcp` with `airlock-skills-mcp` as an alias.
- Agent users install the skill by importing or copying `airlock_skills/` into
  their own agent's skill system. For CoCo, package or rename that source
  directory to `airlock/` under `.snowflake/cortex/skills/`.
- Code, docs, skills, examples, and templates are licensed under Apache-2.0.

## Tool Contract

Every Airlock procedure tool returns a consistent object:

```json
{
  "ok": true,
  "procedure": "airlock.user.load_data",
  "status": "ok",
  "code": null,
  "message": "Loaded file.",
  "payload": {},
  "issues": [],
  "rows": []
}
```

Procedure failures remain structured. The server preserves returned `STATUS`,
`CODE`, `MESSAGE`, `ISSUES`, identifiers, workflow state, validation details,
and result rows. Connector exceptions are sanitized to avoid leaking secrets,
private key paths, or stack traces.

## Safety Boundaries

- Read-only discovery is the default.
- `airlock_delete_files` defaults to `dry_run=true` and requires `confirm=true`
  before a mutating delete call.
- `airlock_edit_file_workflow` defaults to `validate_only=true`; set
  `validate_only=false` to apply the transition.
- Inline CSV and attachment payloads are capped by
  `AIRLOCK_MCP_MAX_INLINE_BYTES`.
- No tool grants broader access than the Snowflake user, active application role,
  Airlock roles, license state, and in-procedure PDP checks allow.

## Design Notes

See [docs/design.md](docs/design.md) for the server boundary and MVP workflow
map. See [docs/mcp_ai_agents_airlock_procedures.md](docs/mcp_ai_agents_airlock_procedures.md)
for the conceptual MCP and agent integration overview. For shipped user-to-agent
delegation semantics, see [docs/agent_delegation.md](docs/agent_delegation.md).
