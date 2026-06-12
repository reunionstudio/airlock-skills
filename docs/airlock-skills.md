# Airlock Skills for AI Agents

This guide combines the Airlock MCP server guidance and the Airlock AI-agent
skill guidance into one neutral reference for agent systems.

The goal is simple: make Airlock easy for agents to use while keeping Airlock's
Snowflake stored procedures as the source of truth for permissions, validation,
audit, retention, billing, and workflow.

Public toolkit repo:
[github.com/reunionstudio/airlock-skills](https://github.com/reunionstudio/airlock-skills).
It includes the canonical Airlock skill, MCP server guidance, docs, release
artifacts, and tests for keeping agent tooling aligned with the installed
Airlock procedure API.

## Positioning

Airlock is a policy-enforcing ingestion layer. Agents and MCP servers should use
documented Airlock stored procedures. They should not write directly to
Airlock-owned stages, hybrid tables, secure views, or generated replacement
apps.

An Airlock MCP server or agent skill is an adapter and teaching layer:

- the agent discovers the installed Airlock API
- the tool or skill maps user intent to documented procedure calls
- Snowflake grants, application roles, Airlock roles, licenses, and the Airlock
  PDP enforce authorization
- procedure results remain structured and auditable

The adapter must not reimplement Airlock business logic outside Snowflake.

## Core Concepts

Always distinguish:

- **Snowflake role**: controls access to the app object and procedure grants.
- **Snowflake application role**: `app_user` or `app_admin`.
- **Airlock role**: business role stored inside Airlock, used for granular spec,
  path, workflow, and admin scope.
- **Delegation**: user-to-agent authority for stored procedure calls. Delegation
  is not an Airlock role and is not a Streamlit identity mode.

When a caller has multiple Airlock roles, pass the intended `in_app_role` lens to
procedures that accept it. Do not mix Airlock roles with Snowflake roles in tool
names, descriptions, or error messages.

For role creation, do not set `managed_by_role` to `app_admin`. All Airlock roles
are already manageable by `app_admin`; use `managed_by_role` only when a
non-`app_admin` Airlock role should manage or include the new role.

For assignment creation, use the exact descriptor keys `assignment_name`,
`user_id`, and `assigned_role`. Do not use `user_name` or `role_name`. Generate
assignment names as `<assigned_role>.<normalized_user_id>`, such as
`observer.bert` or `observer.aroberts`, unless the human supplies an existing
name. Put the longer-lived Airlock role first and the occupant user second.
Avoid underscore-separated names such as `bert_observer`. For simple role or
assignment creation after human approval, call the mutating admin procedure
once; Airlock validates and returns structured issues on failure, so a separate
validate-only pass is not required by default.

## Agent Architecture Patterns

Airlock works best when agents are explicit participants in the business
process, not hidden shortcuts around human permissions.

Recommended patterns:

- Assign agents their own Airlock roles for direct agent work.
- Use delegation when an agent acts for one specific human. Keep the actor
  agent, principal user, and delegation id visible in procedure results and
  audit language. Delegation is not impersonation.
- Treat most production agents as tied to one accountable human or owner account
  unless the business has a clear reason and audit model for a shared agent.
- Use workflow for review, pushback, and handoff. A spec can land new files in
  `Submitted` so reviewers can act immediately, while `Draft` remains the
  pushback state when changes are needed.
- Prefer polling Airlock work lists, expectation work, materialized spec tables,
  or reference specs for watcher agents today. Snowflake notifications may be an
  advanced future pattern, but polling governed Airlock surfaces is simpler and
  easier to audit now.
- Use materialized specs plus read-only reference specs for high-read streams.
  The demo `posts` spec writes governed records to the materialized
  `AIRLOCK_DATA.ACTIVE.T_POSTS` table, while `published_posts` exposes that
  table back to users and agents through `airlock.user.select_reference_data`.
- Chain humans and agents through governed outputs rather than private memory.
  For example, a downstream budget-package agent can watch Approved budget
  requests; an onboarding agent can watch Accepted applications; a triage agent
  can watch `published_posts` and reply with linked posts.

The canonical skill reference for these decisions is
`airlock_skills/references/agent-architecture-patterns.md`.

## Spec Library Patterns

For new Airlock setups, agents should start from the business scenario and then
look for nearby spec-library patterns. The public spec library covers reusable
shapes for small-business operations such as projects, timesheets, invoices,
budget requests, reimbursements, ops issues, governed posts/signals, payments,
ecommerce, accounting, CRM, support, marketing, analytics, treasury, and
reconciliation.

When a local `airlock-specs/` repo or uploaded library folder is available, read
`catalog.json`, then the closest collection and spec JSON files. When only CoCo
web search is available, use the public spec-library page as context, but do not
depend on live internet or GitHub access for correctness. CoCo Cloud Agents can
web-search, but external host access from the container can be restricted; the
installed skill and local/uploaded files are the reliable working surface.

If no library source is reachable, agents should still proceed from the scenario
family and spec-design questions instead of blocking on GitHub cloning or live
web access.

Library specs are patterns, not commands to copy blindly. Adapt row grain, typed
fields, attachments, variants, guest access, workflow, source links,
expectations, and delegation to the user's actual process. Installed Airlock
documentation remains the execution contract for exact procedure signatures.

Agent responses should include a pattern note: source used or unavailable,
candidate pattern, pattern type, key adaptations, and remaining human decisions.

## MCP and Stored Procedures

MCP is a structured way for AI clients to discover and call external
capabilities through tools, resources, and optional prompts. Airlock is not an
MCP server by itself; it is a database-native API exposed through Snowflake
stored procedures.

The mapping is direct:

| MCP idea | Airlock analogue |
| --- | --- |
| Tool name | `airlock.user.*`, `airlock.admin.*`, `airlock.billing.*` procedures |
| Tool description | `airlock.user.documentation(...)`, `airlock.user.help(...)`, `airlock.admin.help(...)`, `airlock.billing.help(...)` |
| Catalog / discovery | `airlock.admin.api_info()` and installed documentation |
| Invocation | `CALL airlock.user.load_data(...)` and related procedure calls |
| Authorization | Snowflake grants, application roles, Airlock roles, licenses, and PDP checks |

Examples assume the installed app object is named `airlock`. If an account uses
a different app name, substitute that name or configure the adapter with it.

Airlock's stored procedures are already a named, documented, authorized tool
surface. For Snowflake-native agents such as CoCo, the skill plus direct
procedure calls should be the default path.

An MCP server can still make Airlock easier for agents that run outside
Snowflake or hosts that strongly prefer MCP tool discovery and JSON Schema. It
should remain a thin, auditable transport layer.

Recommended portable MCP shape:

```text
MCP client
  -> portable Airlock MCP server
      -> Snowflake connector or Snowflake CLI-compatible connection
          -> CALL airlock.user.* / airlock.admin.*
              -> Airlock procedures, PDP, events, owned storage
```

The server may be Python, Node, or another runtime. Each tool should map to one
documented Airlock operation or a small transparent sequence of documented
operations.

When a tool uses Snowflake CLI instead of a driver, prefer:

```bash
snow sql -c <connection> --format JSON_EXT --silent \
  -q "CALL airlock.user.documentation(CONTENT_MODE => 'PROCEDURES');"
```

`JSON_EXT` is the recommended agent format because it preserves Airlock VARIANT
columns such as `PAYLOAD`, `VALIDATION`, and `ISSUES` as nested JSON objects.
Plain `JSON` can serialize those values as strings. `TABLE` is appropriate for
human demos and Makefile logs, but agents should not scrape table art.

## Agent Skill Shape

An Airlock skill teaches an agent the workflow and safety model. This repo
publishes one canonical skill directory:

```text
airlock_skills/
  SKILL.md
  examples/
  references/
  templates/
```

Install it by importing or copying `airlock_skills/` into the agent's skill
system. Each AI tool is responsible for its own import mechanics. If an Airlock
MCP server exists, the skill should prefer typed Airlock tools. Without MCP, it
should call SQL procedures directly.

## Minimal Skill

```markdown
---
name: airlock
description: Use Airlock stored procedures for governed spec discovery, validation, file loading, workflow, attachments, delegations, and safe admin operations.
allowed-tools:
- snowflake_sql_execute
- snowflake_object_search
---

# When to Use

Use this skill when the user asks an AI agent to work with Airlock, submit data,
create or inspect specs, validate files, attach evidence, move workflow, inspect
expectations, create delegations, or automate governed ingestion into Snowflake.

# Core Rule

Airlock is the policy-enforcing ingestion layer. Do not write directly to
Airlock-owned stages, hybrid tables, secure views, or generated replacement
apps. Use installed Airlock stored procedures and preserve structured outputs.
Airlock SQL APIs are stored procedures: use `CALL`, not
`SELECT * FROM TABLE(...)`.

Keep submitted payloads clean. Send the business facts declared by the spec, not
Airlock lifecycle state. Do not invent ids or add workflow, approval, reviewer,
debug, or "for office use only" fields unless the spec explicitly declares them
as real source-system facts.

# First Steps

1. Confirm the active Snowflake connection and role.
2. Query installed Airlock documentation:
   `CALL airlock.user.documentation(CONTENT_MODE => 'PROCEDURES');`
3. List the caller's Airlock roles:
   `CALL airlock.user.list_my_roles();`
4. Use `airlock.user.list_my_specs(in_app_role, include_managed_roles)` and
   `airlock.user.describe_spec(spec_name, in_app_role, include_managed_roles)`
   before choosing any load, validate, attachment, workflow, or reference call.

# Safe Procedure Pattern

Airlock procedures are designed around a small set of families:

- `list_*`, `describe_*`, and `get_*` are read-only discovery.
- `create_*` and `alter_*` usually take a descriptor `VARIANT` and optional
  `validate_only`.
- Destructive operational previews use `dry_run`; drop-style configuration
  procedures use `force`.
- User data actions should use named arguments and omit unused optional
  arguments instead of passing placeholder `NULL` values or typed casts. `path`
  means staged file source
  in `validate_data` / `load_data`; `file_path` or workflow `path` identifies an
  existing manifest file; `path_scope` selects the target folder/lens for direct
  shared-folder writes.
- Delegated action procedures use trailing `on_behalf_of_user` and optional
  `delegation_id`. In the common case, pass only `on_behalf_of_user`; use
  `delegation_id` only to resolve an ambiguity reported by Airlock. Do not
  attempt delegation for `airlock.admin.*`.


For spec creation, make the data structure do the hard thinking before tuning
control structures. Ask what one row represents, what row grain and stable id it
needs, which timestamps belong to the business event rather than the Airlock
load, which facts deserve typed columns, what evidence should be Airlock
attachments, what context belongs in validated `variant` columns, and which
fields need controlled vocabularies. Decide guest access, workflow, references,
expectations, and delegation after the core data shape is sound; those controls
are usually easier to alter later than column structure.

For data submission:

1. Describe the spec.
2. Build CSV or file content that matches `column_config` and `file_rules`.
3. Call `airlock.user.validate_data(...)`.
4. Only if validation succeeds, call `airlock.user.load_data(...)`.
   `load_data` evaluates active Expectations before writing the file manifest.
   Strict unmet expectations return `EXPECTATION_BLOCKED` and do not load the
   file. Non-strict unmet expectations return `EXPECTATION_WARNING` while still
   loading the file.
5. If the spec requires attachments, include `attachment_content_base64` and
   `attachment_filename` in `load_data`, or use `add_attachment` afterward when
   the policy allows it. A `load_data` call with inline attachment content
   already registers that first attachment; add later evidence with a distinct
   `attachment_tag`.
6. If the spec is configured with `Submitted` as its initial workflow step, a
   successful load already creates the reviewer-facing item. If the spec starts
   in `Draft` and the user asked to submit for review, use
   `airlock.user.edit_file_workflow(...)` after a successful load. For delegated
   work, the same `on_behalf_of_user` must be passed and the spec policy plus
   active grant must allow `edit_file_workflow` at the current step.
7. Report `STATUS`, `CODE`, `MESSAGE`, `ISSUES`, returned path, filename, and
   workflow state.

For inline CSV, omit `path`; do not pass `path => NULL`. `path` is only for
staged file paths. Use
`path_scope` only when the caller is directly choosing a shared/public folder
such as `public/full_access`. For delegated inline calls, pass
`on_behalf_of_user`; Airlock resolves the principal's folder. If role-lensed
validation needs an explicit role, pass the principal's Airlock role as
`in_app_role`; Airlock checks it against the principal's assignments, not the
actor's. Other role-lensed validation, including FK or mapped-reference checks,
uses the principal lens for delegated calls and the caller lens for direct calls.

# Safety

- Ask before mutating admin configuration.
- Use `validate_only` selectively for complex or unclear declarative changes,
  especially spec, template, and expectation descriptors. Do not preflight simple
  role or assignment creation by default after human approval.
- Use `dry_run` for destructive operational previews when available.
- Do not hide Airlock reason codes.
- Do not suggest broad Snowflake privileges when an Airlock role, license,
  template, delegation, or workflow fix is the actual issue.
- Treat attachment replace/delete as permanent in Airlock unless installed docs
  say a tested restore path exists.
```

## Discovery First

Installed documentation beats repo docs. Agents should start with:

```sql
CALL airlock.user.documentation(CONTENT_MODE => 'PROCEDURES');
CALL airlock.user.list_my_roles();
CALL airlock.user.list_my_specs('<airlock_role>');
CALL airlock.user.describe_spec('<spec_name>', '<airlock_role>');
```

For admin work:

```sql
CALL airlock.admin.api_info();
CALL airlock.admin.list_specs('<airlock_role>');
CALL airlock.admin.describe_spec('<spec_name>');
```

Agents should preserve help output and procedure result payloads instead of
turning everything into prose.

## Recommended MCP Tool Surface

Use names that describe Airlock concepts and map clearly to procedures. Start
with user-safe tools, then add admin tools behind explicit configuration.

### Payload Discipline

Agents and MCP tools should treat `describe_spec` as the source of truth for
file shape. Build files from `column_config`, `file_rules`, and
`attachment_policy`; do not add extra columns because an agent finds them useful.

Airlock stores lifecycle state separately:

- file identity: returned `PATH` and `FILENAME`
- workflow: Airlock workflow state and events
- evidence: Airlock attachments
- timing and cadence: Airlock expectations
- review or commitment output: separate review/commitment specs

Status fields are allowed when they are real business/source facts, such as a
Shopify product status or Bill.com payment status. They should not duplicate
Airlock review state such as `approval_status`, `approved_by`, `approved_at`,
`workflow_status`, or `workflow_step` in a submitter payload.

### Records JSON Authoring

For agents and generated apps, records JSON is the preferred authoring shape:

```json
{
  "spec_name": "posts",
  "filename": "post_2026_06_07",
  "records": [
    {
      "post_id": "post-001",
      "body": "I wish submitting reimbursements were easier.",
      "tags": "#request #reimbursements",
      "details": {
        "request": {
          "desired_outcome": "Let an approved agent prepare the draft."
        }
      }
    }
  ]
}
```

Only business fields belong in `records`. Keep role, path, delegation,
workflow, attachment, retry, and audit context outside the record as
procedure/tool context.

The installed Airlock procedures still receive CSV `file_content`. Convert
records JSON to CSV locally only for flat specs or specs with declared
`variant` columns for nested values. Local conversion is not authorization;
Airlock validation and authorization in Snowflake remain authoritative.

### Governed Posts Demo

The `posts` demo is intentionally a file-spec demo, not a separate table-spec
feature. It shows how Airlock can govern small business signals with existing
spec mechanics:

- `posts`: a materialized file spec where users and agents append shared posts
  into `public/append_access`.
- `published_posts`: a read-only reference spec over the materialized
  `posts` table for governed read-back.

Agent-side discovery and use should stay on `airlock.user.*`:

```sql
CALL airlock.user.list_my_roles();
CALL airlock.user.list_my_specs('agent', TRUE);
CALL airlock.user.describe_spec('posts', 'agent', TRUE);
CALL airlock.user.describe_spec('published_posts', 'agent', TRUE);
```

If the caller does not have the `agent` Airlock role, `list_my_specs('agent',
TRUE)` should fail. That is an Airlock assignment or Snowflake connection
identity issue. Do not fall back to `airlock.admin.*` for a user/agent demo.

To submit a post, build records JSON from `describe_spec`, convert it locally to
CSV `file_content`, then call the user procedures:

```sql
CALL airlock.user.validate_data(
  spec_name => 'posts',
  file_content => '<csv_from_posts_records_json>',
  in_app_role => 'agent',
  path_scope => 'public/append_access'
);

CALL airlock.user.load_data(
  spec_name => 'posts',
  file_content => '<csv_from_posts_records_json>',
  filename => '<logical_post_file_name>',
  in_app_role => 'agent',
  path_scope => 'public/append_access'
);
```

To read the governed post stream:

```sql
CALL airlock.user.select_reference_data(
  spec_name => 'published_posts',
  object_key => 'posts',
  row_limit => 100,
  in_app_role => 'agent'
);
```

### Discovery Tools

| Tool | Maps to | Purpose |
| --- | --- | --- |
| `airlock_get_api_info` | `airlock.admin.api_info()` when admin; docs fallback via `documentation()` | Discover installed API version and procedure availability. |
| `airlock_get_documentation` | `airlock.user.documentation(...)` | Fetch TOC, procedure registry, sections, chunks, or full docs. |
| `airlock_list_my_roles` | `airlock.user.list_my_roles()` | Identify caller's Airlock roles. |
| `airlock_check_license` | `airlock.user.get_my_license_seat()` / `airlock.user.claim_license_seat()` when claim is approved | Tell agents whether user APIs can run. |
| `airlock_create_delegation` | `airlock.user.create_delegation(delegation_descriptor, validate_only)` | Let the current user grant their own agent scoped access to a spec they can write to. |
| `airlock_list_my_delegations` | `airlock.user.list_my_delegations(direction, spec_name, include_inactive)` | List delegations involving the caller; `received` is the agent action lens, `granted` is the principal audit lens. |

### Spec and Reference Tools

| Tool | Maps to | Purpose |
| --- | --- | --- |
| `airlock_list_specs` | `airlock.user.list_my_specs(in_app_role, include_managed_roles)` | List specs accessible to the caller. |
| `airlock_describe_spec` | `airlock.user.describe_spec(spec_name, in_app_role, include_managed_roles)` | Return fields, tests, file rules, workflow, attachments, path scopes, and reference guidance. |
| `airlock_select_reference_data` | `airlock.user.select_reference_data(...)` | Read approved reference-spec data for validation/planning. |

For reference specs, treat `reference_config.object_paths[].readable_columns`
and any provided `column_config` as one contract: if both are present, every
readable column must be documented in `column_config`.

### File and Data Tools

| Tool | Maps to | Purpose |
| --- | --- | --- |
| `airlock_validate_data` | `airlock.user.validate_data(...)` | Validate candidate file content without writing. |
| `airlock_load_data` | `airlock.user.load_data(...)` | Load data into a spec/path; supports inline CSV or staged file path; returns expectation warnings/errors in `ISSUES`. |
| `airlock_list_files` | `airlock.user.list_my_files(spec_name, ...)` | Discover active/history files the caller may see. |
| `airlock_select_files` | `airlock.user.select_my_files(spec_name, ...)` | Read file data through Airlock access checks. |
| `airlock_delete_files` | `airlock.user.delete_files(..., dry_run)` | Preview or perform file delete where allowed. |

For destructive operations, require explicit confirmation or `dry_run=false`, and
preserve Airlock's own dry-run output.

### Workflow Tools

| Tool | Maps to | Purpose |
| --- | --- | --- |
| `airlock_list_work_items` | `airlock.user.list_my_work_items(...)` | List files that can be moved through workflow. |
| `airlock_edit_file_workflow` | `airlock.user.edit_file_workflow(...)` | Move a file to an allowed workflow state; supports `on_behalf_of_user` only when explicitly delegated by spec policy and grant. |
| `airlock_submit_file` | `airlock.user.load_data(...)` + `airlock.user.edit_file_workflow(...)` | Convenience tool that validates, loads, attaches required evidence, and advances to Submitted only when workflow policy allows it. |
| `airlock_list_file_references` | `airlock.user.list_file_references(...)` | Inspect source-link pins between files. |
| `airlock_add_file_reference` | `airlock.user.add_file_reference(...)` | Pin eligible upstream files for downstream validation. |
| `airlock_remove_file_reference` | `airlock.user.remove_file_reference(...)` | Remove a file reference pin. |

Workflow changes are lifecycle actions, not necessarily destructive. Tool
descriptions should say whether the operation is reversible under the configured
workflow. A convenience "submit" tool must not set workflow columns inside the
submitted payload; it should call the same workflow procedure a human would use.

### Attachment Tools

| Tool | Maps to | Purpose |
| --- | --- | --- |
| `airlock_add_attachment` | `airlock.user.add_attachment(...)` | Attach evidence to an existing file; supports `on_behalf_of_user` for delegated follow-up attachments. |
| `airlock_replace_attachment` | `airlock.user.replace_attachment(...)` | Replace a logical attachment tag; supports `on_behalf_of_user` only when the spec policy and grant explicitly allow `replace_attachment`. |
| `airlock_delete_attachment` | `airlock.user.delete_attachment(...)` | Delete an attachment where allowed; direct-role destructive action. |

Attachment replace/delete should be described as permanent in Airlock unless a
tested restore contract is added later.

### Expectation Tools

| Tool | Maps to | Purpose |
| --- | --- | --- |
| `airlock_list_expectations` | `airlock.admin.list_expectations(...)` | Admin/spec-admin discovery of configured cadence/order contracts. |
| `airlock_describe_expectation` | `airlock.admin.describe_expectation(...)` | Inspect expectation clauses and scope. |
| `airlock_list_expectation_work` | `airlock.user.list_my_expectation_work(...)` | Show expectation status, human-friendly `DESCRIPTION`, due timing, active exceptions, and required follow-up for the current user/role lens. |

Expectation administration should stay admin/spec-admin scoped. User-facing
expectation work/status discovery should use user procedures so agents do not
need admin scope for operational follow-up. Agents should prefer `DESCRIPTION`
when telling a user what is expected, and use `TARGET_MILESTONE` only as the
workflow state that satisfies the expectation. For operational work rows, prefer
`DETAILS.summary` when present and then cite `DUE_AT`, `DAYS_UNTIL_DUE`,
`IS_STRICT`, and `ACTIVE_EXCEPTION_COUNT` as supporting facts. When explaining
an expectation definition, combine `DESCRIPTION`, `CLAUSES`, `EFFECTIVE_AT`, and
`EXPIRES_AT` so the human sees why it exists, what cadence or order it enforces,
and whether the contract is currently active.

### Admin Tools

Admin tools should be disabled by default unless explicitly configured.

Suggested groups:

- roles and assignments
- specs, spec versions, templates, and template assignments
- references and reference access
- retention policies and outdated file cleanup
- expectations and expectation exceptions
- events/observability via `airlock.admin.list_events`
- billing status and billing logs where the caller has the right application
  role

Admin tools need stricter descriptions, explicit destructive flags, and full
structured return payloads because they affect governance, access, and audit.

## MCP Resources

Resources should be read-only and should call procedures behind the scenes
instead of querying owned tables directly.

Useful resources:

- `airlock://documentation/toc`
- `airlock://documentation/procedures`
- `airlock://documentation/section/{section_id}`
- `airlock://specs/{spec_name}/descriptor?role={airlock_role}`
- `airlock://specs/{spec_name}/files?role={airlock_role}`
- `airlock://events?since={timestamp}` for admin mode only

## MCP Prompts

Optional prompts can help agents behave consistently:

- `submit_file_to_airlock`: discover role/spec, describe spec, validate, load,
  attach, then report status.
- `draft_spec_from_template`: list assigned templates, create a draft spec, and
  ask an admin to review when publication is required.
- `triage_expectation_work`: list expectation work, inspect late/missing items,
  and suggest next procedure calls.
- `admin_safe_spec_change`: validate-only first, show impact, then alter only
  after explicit human approval.

Prompts should instruct agents to use installed documentation as source of truth.

## Input and Output Contracts

Each MCP tool should use JSON Schema for arguments. Schemas should be generated
or curated from Airlock procedure documentation, then tested against real calls.

Successful return shape:

```json
{
  "ok": true,
  "procedure": "airlock.user.load_data",
  "status": "loaded",
  "code": null,
  "message": "Loaded file.",
  "payload": {},
  "issues": [],
  "rows": []
}
```

Failure return shape:

```json
{
  "ok": false,
  "procedure": "airlock.user.load_data",
  "status": "error",
  "code": "ATTACHMENT_REQUIRED",
  "message": "Attachment required for this spec.",
  "issues": [
    {"code": "ATTACHMENT_REQUIRED", "message": "Provide attachment_content_base64.", "severity": "error"}
  ],
  "rows": []
}
```

Do not flatten Airlock outputs into prose-only summaries. Agents need reason
codes, issue arrays, returned file identifiers, path scopes, workflow states,
delegation context, and validation details.

## Common Agent Workflows

### Submit Data

```text
$airlock Submit @budget.csv to FY26 Budget Requests as role finadmin.
```

Expected behavior:

1. Identify role and spec.
2. Describe spec.
3. Build only the columns declared by the spec; do not invent ids, workflow
   state, approval fields, or process metadata.
4. Validate file content.
5. Load only if valid.
6. If the request means "submit for review", check the loaded workflow state. If
   it is not already the reviewer-facing state, advance it through
   `edit_file_workflow` only when the spec workflow allows it.
7. Return loaded path/filename and workflow/attachment status.

### Submit Data with Attachment

```text
$airlock Submit this reimbursement CSV with @receipt.pdf as asmith.
```

Expected behavior:

1. Describe the reimbursement spec and attachment policy.
2. Build the CSV from the reimbursement business fields only; do not invent a
   reimbursement id or include Airlock approval/workflow columns.
3. Validate the CSV.
4. Base64 encode the receipt only for the procedure call.
5. Load with `attachment_content_base64` and `attachment_filename`.
6. If the user expects the reimbursement to reach reviewers immediately, first
   check whether the spec's initial step already placed it in Submitted. If not,
   move it to Submitted with `edit_file_workflow` after load, using the same
   delegation context when acting on behalf of someone else.
7. Do not log raw attachment bytes.

### Delegated Submit and Pushback

```text
$airlock Submit this reimbursement for asmith with @receipt.png.
```

Expected behavior:

1. Call `list_my_delegations('received')` and choose the active grant for the
   principal/spec.
2. Describe the spec and build only business payload columns.
3. Validate, load, and attach evidence with `on_behalf_of_user` set to the
   principal user.
4. If the grant allows `edit_file_workflow` at Draft, advance the file to
   Submitted. If not, report that the file is loaded but still Draft.
5. If a reviewer later returns the file to Draft, explain the workflow comment
   and expectation due date so the principal knows what to fix and resubmit.

MCP servers may expose this as one convenient tool, but under the hood it is
still load plus an authorized workflow transition. That distinction matters for
audit, delegation policy, and expectation gates.

### Draft a Spec

```text
$airlock Draft a spec for weekly vendor invoices from the default template.
```

Expected behavior:

1. List assigned templates.
2. Describe the chosen template.
3. Prepare overrides.
4. Call create-from-template or admin create with `validate_only` first.
5. Ask before mutating.

### Triage Late Work

```text
$airlock Check expectation work for the finance specs.
```

Expected behavior:

1. List accessible expectations/work.
2. Explain late/missing/exception states.
3. Suggest the next Airlock procedure call, not direct table edits.

## Delegated Work

Delegation is for agent/API execution, not a Streamlit "acting as" mode. The
Streamlit UI may help humans create, view, and revoke grants. Bots and agent
tools perform delegated work through stored procedures.

Keep delegation mappings aligned with installed Airlock procedure names:
`airlock.user.create_delegation`, `airlock.user.list_my_delegations`, and the
trailing `on_behalf_of_user` / `delegation_id` parameters on delegated user
actions such as `validate_data`, `load_data`, `add_attachment`,
`replace_attachment`, and `edit_file_workflow`.

When a human asks to set up their agent, use:

```sql
CALL airlock.user.create_delegation(...);
```

The current Snowflake user is always the principal. Do not pass a different
`principal_user`; the procedure rejects it. This prevents second-order
delegation.

Before delegated work, call:

```sql
CALL airlock.user.list_my_delegations('received');
```

Use `direction = 'received'` to discover grants where the current user is the
actor/delegate. Use `direction = 'granted'` to audit grants where another actor
may act for the current user. Use `include_inactive => TRUE` only when explaining
future, expired, or revoked delegations.

For active received rows:

- pass `PRINCIPAL_USER` as `on_behalf_of_user`
- use the same delegation arguments for `validate_data`, `load_data`, follow-up `add_attachment`, explicitly allowed `replace_attachment`, and explicitly allowed `edit_file_workflow`
- keep passing `on_behalf_of_user` on every follow-up delegated mutation; if it is omitted, Airlock treats the call as direct actor work and evaluates the actor's own path access
- omit `path` and `path_scope` for normal delegated inline loads; also omit `in_app_role` unless you are deliberately selecting the principal's role lens
- remember that inline attachments passed to `load_data` are already registered; use a new `attachment_tag` for extra evidence added later
- pass `DELEGATION_ID` as `delegation_id` only if Airlock reports an ambiguous delegation
- prefer structured `ACTION_CONTEXT` when available
- preserve actor, principal, and delegation id in output

Delegation is a `user.*` procedure feature only. MCP tools must not expose
`on_behalf_of_user` on `admin.*` tools, and they should reject prompts that try
to run an admin procedure under a delegation.

Spec creation/editing should rely on `admin.validate_spec` for
`delegation_policy` correctness. The policy allowlists must be arrays of known
delegable `user.*` actions. Admin action names are invalid, and per-step
workflow actions may only narrow the spec-level allowlist.

Workflow movement is delegated only when the spec `delegation_policy` and the
active grant both include `edit_file_workflow` for the file's current workflow
step. If an agent also has direct Airlock roles, a successful
`user.edit_file_workflow` call without `on_behalf_of_user` is still a direct
action, not delegated work. Likewise, `user.list_my_work_items` lists
direct-role workflow visibility; a delegated file load does not make the
principal's workflow items appear there.

For agent-assisted submission, the clean pattern is:

1. `describe_spec`
2. `validate_data`
3. `load_data` with any required attachment
4. If the spec's configured initial step is already Submitted, report the loaded
   reviewer-facing file. If the file is Draft, use
   `edit_file_workflow(action => 'advance')` to reach Submitted only when
   `edit_file_workflow` is allowed by both spec policy and grant.

If a reviewer pushes the file back to Draft, Airlock workflow comments and
expectations tell the principal what changed and when it must be resubmitted.
Do not encode that pushback state in payload columns.

Do not ask the agent to log in as the principal user.

Good:

```text
Submitted as agent_user for principal_user.
```

Bad:

```text
principal_user submitted the file.
```

Preserve delegation denial codes such as `DELEGATION_NOT_FOUND`,
`DELEGATION_EXPIRED`, `DELEGATION_REVOKED`, `DELEGATION_PRINCIPAL_ACCESS_DENIED`,
`INVALID_DELEGATION_POLICY`, or `AMBIGUOUS_DELEGATION`.
Delegated `validate_data` and `load_data` denials appear as `STATUS = 'error'`
rows with a stable code in `ISSUES`; delegated attachment denials set `CODE`;
delegated workflow denials set `VALIDATION.issues`. Agent tools should expose
those structured fields directly. Expectation findings also appear in
`load_data` `ISSUES`: `EXPECTATION_BLOCKED` is a strict failure that prevented
the load, while `EXPECTATION_WARNING` means the file loaded but an operational
expectation still needs attention.

## Safety Rules

1. Default to read-only discovery unless a mutating tool is explicitly called.
2. For destructive tools, require explicit confirmation and target identifiers.
3. Prefer Airlock `validate_only` modes for complex declarative spec, template,
   expectation, or unclear governance changes; avoid redundant preflight calls
   for simple role or assignment creation after human approval.
4. Prefer Airlock `dry_run` modes for destructive operational previews.
5. Never bypass Airlock procedures to write stages or owned tables directly.
6. Log tool calls with procedure name, status, duration, and stable error code,
   but not secret values or file contents.
7. Keep file-content logging off by default.
8. Return authorization denials as denials; do not suggest privilege escalation
   unless the reason code clearly indicates the required admin action.
9. Preserve structured `ISSUES`, `VALIDATION`, `ACTION_CONTEXT`, and delegation
   payloads.

## Configuration

Suggested environment variables:

- `AIRLOCK_SNOWFLAKE_ACCOUNT`
- `AIRLOCK_SNOWFLAKE_USER`
- `AIRLOCK_SNOWFLAKE_ROLE`
- `AIRLOCK_SNOWFLAKE_WAREHOUSE`
- `AIRLOCK_APPLICATION_NAME`
- `AIRLOCK_PRIVATE_KEY_PATH`
- `AIRLOCK_PRIVATE_KEY_PASSPHRASE`
- `AIRLOCK_TOOLS_ADMIN_MODE=0|1`
- `AIRLOCK_DEFAULT_AIRLOCK_ROLE`
- `AIRLOCK_MAX_INLINE_BYTES`

The tool layer should also support named Snowflake connection profiles where
that is more convenient for local development.

## Optional Hook Guardrails

Some agent hosts can enforce hooks or policy checks around tool use. For Airlock
projects, consider hooks that:

- block direct writes to Airlock-owned tables and stages
- warn before `DROP`, `DELETE`, `TRUNCATE`, or broad `ALTER` outside approved
  Airlock procedures
- require `validate_only` before mutating spec/template procedures
- require `dry_run` before destructive operational procedures when available
- log procedure calls and result codes for supportability

Hooks should stay fast and conservative. If uncertain, prefer warning over
silently rewriting commands.

## MVP

A useful first version can be small:

1. Connect to Snowflake and report session/application context.
2. Fetch installed documentation and procedure registry.
3. List the caller's Airlock roles.
4. List and describe accessible specs.
5. Validate inline CSV.
6. Load inline CSV with optional attachment.
7. List files and select file data.
8. Add, replace, and delete attachments.
9. List and use received delegations for delegated procedure calls.
10. Provide stable structured errors and tests for common denial paths.

This MVP is enough for an agent to submit budget files, reimbursement files with
receipts, and other governed workflows without direct stage access.

## Later Phases

Phase 2:

- workflow work-item listing and workflow transitions
- file references / source-link operations
- reference data reads
- better file streaming for larger attachments

Phase 3:

- admin mode for spec/template/reference/retention/expectation management
- generated JSON Schemas from installed Airlock docs
- resource URIs for cached documentation and spec descriptors
- prompt templates for common Airlock workflows

Phase 4:

- optional hosted MCP server for teams
- OAuth or workload identity support where available
- observability dashboard for tool calls and Airlock procedure outcomes

## Testing

The tool layer should have:

- unit tests for JSON argument validation and procedure-call construction
- contract tests using fake Snowflake rows for output normalization
- integration tests against a demo Airlock install for discovery, validate, load,
  attach, list, select, workflow, delegation, and denial paths
- destructive-operation tests that prove `dry_run` and confirmation gates work
- documentation tests that compare the tool list to the installed procedure
  registry so stale tools are caught

The integration suite should stay focused. Prefer unit tests for schema and
mapping logic; use integration tests only for Snowflake session behavior,
procedure authorization, real file/attachment flow, installed-doc discovery, and
delegation enforcement.

## Skill Quality Checklist

- The description is specific enough that the agent loads it only for Airlock
  work.
- The first steps force installed-doc discovery.
- The skill never asks an agent to edit Airlock-owned tables/stages directly.
- The skill preserves structured procedure output.
- Destructive operations require approval or dry-run preview.
- Examples cover submit file, submit with attachment, draft spec, delegation,
  and expectation work.
- The skill can work with either SQL tools or an Airlock MCP server.
- The skill states how to handle common blockers: missing license seat, wrong
  Snowflake role, missing Airlock role, template not assigned, attachment
  required, delegation denied, access denied by workflow state.

## Distribution

Use Git when the skill should version alongside Airlock docs and examples. Use a
Snowflake stage or other internal artifact system when customers want
role-controlled distribution.

Recommended versioning:

- name the minimum Airlock API version expected
- include a compatibility note such as:
  `Requires Airlock API v1 procedures: documentation, list_my_roles,
  list_my_specs, describe_spec, validate_data, load_data`
- update the skill and examples in the same release pass as procedure contract
  changes

## Related Airlock Docs

- `docs/airlock_api_v1.md` for stored procedure contracts
- `docs/airlock_spec_design.md` for payload discipline, workflow separation, and VARIANT use
- `docs/agent_delegation.md` for detailed delegation semantics
- `docs/procedure_cli_messaging.md` for deterministic agent-facing output
- `docs/ui_messaging_standards.md` for destructive/recovery language

## Open Product Questions

- Should admin and user MCP tools live in the same server with configuration
  gates, or in separate binaries?
- Should procedure schemas be generated at app build time, fetched from the
  installed app, or both?
- Should large files stream through the tool layer, require staged paths, or use
  signed upload flows?
- Should managed-table specs get a separate tool group once that product shape is
  implemented?

## Rule of Thumb

If a tool or skill makes Airlock easier for an agent to use while preserving
stored procedures as the source of truth, it belongs. If it creates a second path
around Airlock permissions, validation, audit, billing, or lifecycle semantics,
it does not.
