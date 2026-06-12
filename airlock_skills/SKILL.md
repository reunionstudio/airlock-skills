---
name: airlock
description: Use when the user wants to understand, get started with, configure, or operate Airlock; design governed specs; submit or review data; use Airlock stored procedures or MCP tools; manage workflow, attachments, expectations, delegations, and safe admin operations.
allowed-tools:
- snowflake_sql_execute
- snowflake_object_search
---

# Source Of Truth

The canonical source for this skill is the `airlock_skills/` directory in the
`airlock-skills` repository. Install it by importing or copying this directory
into your agent's skill system.

# When to Use

Use this skill when the user asks an AI agent to work with Airlock, submit data,
create or inspect specs, validate files, attach evidence, move workflow, inspect
expectations, automate governed ingestion into Snowflake, or explain Airlock's
agent-oriented architecture and product philosophy.

# Core Rule

Airlock is the policy-enforcing ingestion layer. Do not write directly to
Airlock-owned stages, hybrid tables, secure views, generated views, generated
tables, or replacement apps. Use installed Airlock stored procedures, or Airlock
MCP tools that call those procedures, and preserve structured outputs.

# Use The Skill First

This skill is the working guide. Do not reflexively answer conceptual Airlock
questions by calling `airlock.user.documentation`. Use the guidance, examples,
templates, and references bundled with this skill first.

Use installed Airlock documentation when you need live app/version truth:

- before executing a procedure whose exact signature matters
- when a procedure is missing, denied, or returns an unexpected shape
- after an Airlock app upgrade
- when the user asks what the installed app supports

For spec design, variant rules, expectations, architecture, install behavior, or
how to use Airlock safely, answer from this skill unless the user explicitly asks
you to verify the installed app.

# Business Leader Starting Path

When the user is evaluating Airlock or asking how to begin, start from the
business process rather than stored-procedure syntax:

1. Pick one process where humans or agents produce important business records.
2. Define what done means: fields, evidence, validation, deadline, reviewer.
3. Identify who can submit, who can review, and who can delegate to an agent.
4. Decide what shared reference data must be checked.
5. Decide whether workflow or expectations matter.
6. Start with a small demo spec before automating the broader process.

After this framing, use spec templates, local or uploaded spec-library patterns,
or installed Airlock procedures to turn the process into a governed spec.

# Working Procedure Cheat Sheet

Common user calls, assuming the installed app object is named `airlock`:

```sql
CALL airlock.user.list_my_roles();
CALL airlock.user.list_my_specs('<airlock_role>');
CALL airlock.user.describe_spec('<spec_name>', '<airlock_role>');
CALL airlock.user.validate_data(
  spec_name => '<spec_name>',
  file_content => '<csv_header_and_rows>',
  in_app_role => '<airlock_role>'
);
CALL airlock.user.load_data(
  spec_name => '<spec_name>',
  file_content => '<csv_header_and_rows>',
  filename => '<logical_filename>',
  in_app_role => '<airlock_role>',
  path_scope => '<path_scope_from_accessible_paths>'
);
CALL airlock.user.list_my_files('<spec_name>', '<airlock_role>');
CALL airlock.user.select_my_files('<spec_name>');
CALL airlock.user.list_my_work_items('<spec_name>', '<airlock_role>', TRUE);
CALL airlock.user.list_my_expectation_work('<spec_name>', '<airlock_role>', TRUE);
```

For inline CSV, omit `path`; `path` is only for staged file paths. Prefer named
arguments once optional parameters matter. Omit optional arguments you are not
using instead of passing placeholder `NULL` values.

Only call installed documentation as a live registry check:

```sql
CALL airlock.user.documentation(CONTENT_MODE => 'PROCEDURES');
```

# First Steps For Real Calls

1. Confirm the active Snowflake connection, current user, active Snowflake role,
   warehouse, and application/database context.
2. List the caller's Airlock roles with `airlock.user.list_my_roles()`.
3. Before validation, loading, attachment, or workflow calls, list and describe
   the target spec with `airlock.user.list_my_specs(in_app_role)` and
   `airlock.user.describe_spec(spec_name, in_app_role)`.
4. Query installed documentation only when the live procedure registry is needed.

Examples assume the installed app object is named `airlock`. If the account uses
a different app name, substitute that object name in SQL examples and verify the
active application/database context before calling procedures.

Use the public Airlock documentation site for more product concepts and examples:
`https://reunionstudio.io/airlock/docs/index.html`. Use the Airlock spec library
for reusable spec-shape ideas and business-object modeling:
`https://reunionstudio.io/airlock/docs/spec-library.html`. Do not treat either
public page as the exact procedure contract for an installed app; always verify
procedure signatures with installed documentation before execution when exact
parameters matter.

# Use The Spec Library As Patterns

When the user asks for a setup, scenario, or new small-business process, look
for a nearby spec pattern before inventing a schema. Good starting families
include reimbursements, timesheets, projects, invoices, budgets, ops issues,
posts/signals, CRM, payments, ecommerce, ads, accounting, support, and local
operations.

Use this source order:

1. If a local `airlock-specs/` repo or uploaded spec-library folder is
   available, read `catalog.json`, then only the closest `collections/*.json`
   and `specs/**/*.json` files.
2. If only the public spec-library page is available, use it as pattern context,
   not as an execution contract.
3. If no library source is available, keep working from the scenario family and
   `references/spec-design.md`; do not block on GitHub cloning or live web
   access.

In CoCo Cloud Agents, prefer workspace skills and uploaded/local files over live
internet, live web access, or GitHub access. If a pattern source is unavailable,
say which source was unavailable, proceed with a reasonable draft or questions,
and mark any assumptions.

Use library specs as examples, not as unquestioned truth. Always report the
pattern used, whether it is an observation, commitment, reconciliation, or
reference/master-data shape, and what you adapted: row grain, typed fields,
attachments, variants, guest roles, path scopes, workflow, expectations,
references, and delegation. If no close pattern exists, use
`references/spec-design.md` and ask only the spec-creation questions that affect
row grain, required attachments, event timestamps, or typed fields before
drafting JSON.

For install, app permissions, uninstall, reinstall, and Native App security
questions, read `references/marketplace-install-and-security.md`.
For architecture philosophy and "why Airlock" questions, read
`references/architecture-playbook.md`.
For process-design questions involving humans, agents, generated apps,
delegation, watcher/reviewer handoffs, polling, workflow pushback, or
published reference specs, read
`references/agent-architecture-patterns.md`.


# Spec Creation Internal Dialog

When drafting a spec, reason about the governed business object before writing
JSON. Ask yourself, and ask the human when the answer changes the data model:

1. What object, event, observation, or commitment is one row about? Define the
   row grain before defining columns.
2. Which facts are durable business data that people will filter, join, report,
   or audit? Make those typed columns.
3. Which timestamps belong to the business event or observation itself? Airlock
   already records load user and load time; add fields such as `observed_at`,
   `transaction_occurred_at`, or `effective_at` only when the business event
   time is different from the Airlock load time.
4. What evidence belongs as Airlock attachments? Use attachments for screenshots,
   receipts, PDFs, exports, or other files. Keep attachment bytes out of data
   columns and variants; store only evidence metadata when useful.
5. What metadata is source context rather than core fact? Use validated `variant`
   fields for evolving context, but do not bury required business facts there.
6. What controlled vocabularies are needed for enum-like fields such as type,
   role, platform, status, or capture method?
7. After the data structure is sound, decide guest access, workflow, references,
   expectations, and delegation. These control structures can usually be altered
   later more safely than the core data shape.

For observation specs, prefer typed columns for the observed object's identity,
source URL or source key, observed/captured timestamp, observer-facing category,
and business status. Use Airlock load metadata for submission audit only; do not
mistake it for when the observed real-world thing happened.

# Role Model

Keep these separate:

- Snowflake role: account role used for the Snowflake session, warehouse, and
  grants to the installed Native App.
- Snowflake application role: `app_user` can call user procedures; `app_admin`
  can call admin procedures when granted by Snowflake.
- Airlock role: business role inside Airlock for spec, path, workflow,
  attachment, reference, and expectation access.
- Airlock spec owner: the Airlock role named as a spec's owner role. The owner
  can see all data for that spec and manage its file workflows, even if that
  role is not a spec admin.
- Airlock spec admin: an Airlock role flag for delegated spec administration
  inside Airlock. It is needed for editing spec configuration or expectations,
  but it is not required to own a spec. It is not the same as Snowflake
  `app_admin`, and it does not by itself grant `airlock.admin.*` procedure
  access.

If the caller has multiple Airlock roles, pass the intended `in_app_role` lens to
procedures that accept it.

For agent architectures, do not blur direct role authority with delegated
authority. Assign agents their own Airlock roles for direct work, then use
user-to-agent delegation when the agent should act for one specific human. Most
business agents should map to one accountable human or owner account unless the
business has a clear reason and audit model for a shared agent.

Airlock role hierarchy uses `managed_by_role`: if role `child` is managed by
role `parent`, then a `parent` lens can include the managed `child` role when a
procedure supports managed-role expansion. The child does not automatically get
the parent's access. Use `include_managed_roles=false` when the exact role lens
matters.

Do not set `managed_by_role` to `app_admin` when creating roles. All Airlock
roles are already manageable by `app_admin`, so adding `managed_by_role: "app_admin"`
is redundant and noisy. Use `managed_by_role` only when a non-`app_admin`
Airlock role should manage or include the new role, such as a
business manager role that should see work for subordinate roles.

# Admin Role And Assignment Calls

When creating Airlock roles or assignments, use the documented descriptor keys.
Do not invent friendly aliases.

For assignments, use:

```sql
CALL airlock.admin.create_assignments(
  ARRAY_CONSTRUCT(
    OBJECT_CONSTRUCT(
      'assignment_name', 'observer.bert',
      'user_id', 'BERT',
      'assigned_role', 'observer'
    )
  ),
  FALSE
);
```

Required assignment descriptor keys are `assignment_name`, `user_id`, and
`assigned_role`. Do not use `user_name` or `role_name`; Airlock will reject those
because they are not the assignment contract.

Use this recommended assignment-name convention unless the human supplies an
existing name: `<assigned_role>.<normalized_user_id>`. Normalize the Snowflake
user id to lower case for the `assignment_name` only, keep `user_id` as the
actual Snowflake user id, and use a dot as the separator. Put the longer-lived
Airlock role first and the occupant user second. Examples: `observer.bert`,
`observer.aroberts`, `agent.deb`. Do not generate
underscore-separated assignment names such as `bert_observer`.

Do not probe `list_assignments()` or fake `describe_assignment()` calls just to
infer this schema; use these keys and naming convention, or query installed
documentation when the installed API version is genuinely uncertain.

For roles, omit `managed_by_role` unless a non-`app_admin` Airlock role should
manage or include the new role. Do not set `managed_by_role` to `app_admin`; all
roles are already manageable by `app_admin`.

Use `validate_only => TRUE` selectively. For simple role or assignment creation,
once the human has approved the change, call the mutating procedure once with
`validate_only => FALSE`; Airlock validates the descriptor during the mutating
call and returns structured `STATUS`, `CODE`, `MESSAGE`, and `ISSUES` on failure.
Do not run a validate-only call and then the same mutating call by default. Use a
separate validate-only pass for larger governance changes, spec/template/expectation
descriptors, unclear descriptors, or when the human asks to preview before
mutation.

# Safe User Procedure Pattern

For data submission:

1. Describe the spec.
2. Build business records from `column_config`, `file_rules`, and accessible
   paths. Agents and generated apps may author those records as records JSON,
   then convert to the installed procedure's CSV `file_content` shape.
3. Call `airlock.user.validate_data(...)`.
4. Only if validation succeeds, call `airlock.user.load_data(...)`.
5. If `attachment_policy.attachment_required` is true, include
   `attachment_content_base64` and `attachment_filename` in `load_data` unless
   installed documentation allows another sequence.
6. If the human intent is submit-for-review, advance the loaded file with
   `airlock.user.edit_file_workflow(...)` only when workflow policy allows it.
   For delegated work, keep passing the same `on_behalf_of_user`.
7. Report `STATUS`, `CODE`, `MESSAGE`, `ISSUES`, returned path, filename, row
   count, workflow state, and attachment result. Do not flatten the result into
   prose-only output.

For Snowflake-native agents such as CoCo, call installed Airlock stored
procedures directly unless the environment already provides suitable Airlock MCP
tools. Airlock procedures are the source-of-truth tool surface inside Snowflake.
If a procedure is hard for agents to use, prefer installed documentation,
examples, or procedure-contract improvements over adding a static MCP wrapper.

If Airlock MCP tools are available in a non-Snowflake agent host, prefer typed
tools such as `airlock_describe_spec`, `airlock_validate_data`,
`airlock_load_data`, `airlock_edit_file_workflow`, `airlock_submit_file`,
`airlock_list_files`, and `airlock_add_attachment`.

# Records JSON Authoring

For agents and generated apps, use records JSON as the authoring shape:

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

Records contain business data only. Keep `in_app_role`, `path_scope`,
`on_behalf_of_user`, `delegation_id`, workflow movement, attachment content,
retry state, and audit facts outside the record as procedure/tool context.

The installed Airlock procedure contract still receives CSV `file_content`.
Convert records JSON to CSV locally only for flat specs or specs with declared
`variant` columns for nested values. Local conversion is a convenience bridge;
Airlock validation and authorization in Snowflake remain authoritative.

# Governed Posts Demo

Some Airlock demos include a materialized file spec named `posts` and a
read-only reference spec named `published_posts`. This demonstrates the current
file-spec model for small governed business signals: users and agents append
posts into a shared governed folder, while readers query the materialized table
through reference-spec access.

This is also the day-one pattern for generated apps and watcher agents: write
through a governed spec, materialize the official records, then read back
through a reference spec instead of querying Airlock-owned tables directly.

For a demo agent assigned the Airlock role `agent`, use only user procedures:

```sql
CALL airlock.user.list_my_roles();
CALL airlock.user.list_my_specs('agent', TRUE);
CALL airlock.user.describe_spec('posts', 'agent', TRUE);
CALL airlock.user.describe_spec('published_posts', 'agent', TRUE);
```

To submit a post, describe `posts` first, build records JSON from the declared
columns, convert it locally to CSV `file_content`, then validate and load to the
shared append path:

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

To read the governed post stream, use the reference spec:

```sql
CALL airlock.user.select_reference_data(
  spec_name => 'published_posts',
  object_key => 'posts',
  row_limit => 100,
  in_app_role => 'agent'
);
```

If `agent` is denied, first check whether `list_my_roles()` actually returns
`agent` for the Snowflake user in that connection. Do not switch to
`airlock.admin.*` for this demo; missing `agent` is an assignment or connection
identity issue, not an admin-discovery issue.

# Delegation

Delegation is not impersonation. Use `airlock_list_my_delegations` or
`airlock.user.list_my_delegations('received')` to discover active grants where
the current user is the actor. Use `on_behalf_of_user` and `delegation_id`
instead of logging in as the principal user. Report delegated work as actor
acting for principal, for example `Submitted as agent_user for principal_user`.

Only pass delegation parameters to procedures that support delegated actions,
such as `validate_data`, `load_data`, `add_attachment`, `replace_attachment`,
and `edit_file_workflow` in the current user API. Preserve delegation denial
codes plus actor, principal, and delegation id in structured output. Do not use
delegated destructive or governance actions unless installed docs and spec
policy explicitly allow them.

For delegated submit-for-review workflows, model the user-facing action as
`validate_data` -> `load_data` -> optional `edit_file_workflow(action =>
'advance')`. The workflow advance requires both spec policy and active grant. If
a reviewer returns the file to Draft, explain the workflow comment and any
expectation due date; do not add workflow or reviewer state to payload columns.

# Flexible Variant Fields

When drafting or altering specs, prefer stable typed columns for durable
identifiers, amounts, dates, workflow keys, reference keys, and values users will
filter, join, or report on. Use a `variant` column for contextual business
payloads that may evolve, such as agent-generated processing context, evidence
metadata, source-system hints, or policy inputs.

Pair every flexible `variant` column with explicit Airlock validation such as
`variant_shape` rules or documented `field_path` checks when the installed API
supports them. This lets admins alter the spec config later to accept and
validate new nested keys without changing the physical data structure. Do not
use `variant` as an unvalidated junk drawer for required business facts.

Minimal spec fragment:

```json
{
  "column_config": [
    {"name": "record_id", "type": "string", "tests": ["not_null"]},
    {"name": "amount", "type": "number", "tests": []},
    {"name": "processing_context", "type": "variant", "tests": []}
  ],
  "rules": [
    {
      "type": "variant_shape",
      "field": "processing_context",
      "allowed_root_keys": ["source", "policy", "notes"],
      "paths": [
        {"json_path": "$.source.system", "type": "string", "required": false},
        {"json_path": "$.policy.requires_review", "type": "boolean", "required": false},
        {"json_path": "$.notes.reason", "type": "string", "required": false}
      ]
    }
  ]
}
```

Use `field_path` rules when a validation, such as a reference lookup, needs to
target a scalar nested inside a `variant` column.

# Expectation Work

Expectations are business activity contracts: cadence, order, interval, due
dates, milestone status, and approved exceptions. They are not column
validation. Use them to answer questions like "what is late?", "what is due
next?", "what is blocked by sequence?", or "which files need follow-up?"

For user-visible status, prefer the MCP tool `airlock_list_expectation_work` if
available. Otherwise call:

```sql
CALL airlock.user.list_my_expectation_work('<spec_name>', '<airlock_role>', TRUE);
```

Then cross-check workflow context with `airlock_list_work_items` or
`airlock.user.list_my_work_items(...)` before suggesting a transition. Do not
edit files, manifests, expectation tables, or events directly. If a strict
expectation blocks workflow movement, report the expectation name, target
milestone, strictness, status, due time, matching file count, active
exception count, and Airlock reason code.

# Safety

- Ask before mutating admin configuration.
- Use `validate_only => TRUE` selectively for complex or unclear declarative
  changes, especially spec, template, and expectation descriptors. Do not
  preflight simple role or assignment creation by default after human approval.
- Use `dry_run => TRUE` for destructive operational previews when available.
- Ask for explicit approval before destructive operations or mutating admin
  calls.
- Do not hide Airlock reason codes or `ISSUES` arrays.
- Do not suggest broad Snowflake privileges when an Airlock role, template,
  license, path, or workflow-state fix is the actual issue.
- Treat attachment replace/delete as permanent unless installed documentation
  says a tested restore path exists.
- Do not log raw file contents, attachment bytes, private keys, passphrases, or
  SQL stack traces.
- When drafting specs, consult local or uploaded spec-library files first, or
  public spec-library context when available, for candidate fields, attachments,
  workflow, references, and path-scope ideas. Then validate against installed
  Airlock procedures and the target spec/template rules.

# Common Blockers

- `LICENSE_SEAT_REQUIRED`: ask an app admin to adjust or assign named license
  seats, or use the documented claim flow if approved.
- Missing spec or no rows from `describe_spec`: check the Airlock role lens,
  assignment, publication state, guest access, and license state.
- Template not assigned: ask an app admin to assign the template to the Airlock
  role or make the template public.
- `ATTACHMENT_REQUIRED`: provide an attachment in `load_data` or use an allowed
  attachment sequence.
- `ACCESS_DENIED_WORKFLOW_STATE`: inspect workflow state and available actions;
  do not edit manifest tables directly.

# Examples and Templates

Read only the relevant file when needed:

- `examples/submit-file-with-attachment.md` for CSV plus receipt/evidence flows.
- `examples/draft-spec-from-template.md` for safe draft-spec creation.
- `examples/triage-expectation-work.md` for cadence/order work checks.
- `references/procedure-cheat-sheet.md` for common Airlock procedure patterns
  and when to query installed documentation.
- `references/spec-design.md` for spec structure, spec-creation questions,
  observation metadata, attachments, variant fields, and advanced validation
  rules.
- `references/agent-architecture-patterns.md` for human/agent process design,
  dedicated agent pairing, workflow pushback, polling, published reference
  specs, and chained watcher/reviewer patterns.
- `templates/spec-config-minimal.json` for a minimal spec-config starting point.
- `templates/spec-config-with-variant-context.json` for a governed flexible
  context column with `variant_shape` validation.
- `references/marketplace-install-and-security.md` for Marketplace install,
  privileges, data retention, uninstall, and reinstall guidance.
- `references/architecture-playbook.md` for architecture philosophy,
  product context, and the agent-oriented system-of-record narrative.
