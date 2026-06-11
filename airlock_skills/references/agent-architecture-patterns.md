# Agent Architecture Patterns

Use this reference when a user asks how to design an Airlock process with
humans, AI agents, generated apps, Snowflake, workflow, delegation, or readback
patterns. This is product guidance, not a replacement for installed Airlock
procedure documentation.

## Core Mental Model

Airlock lets flexible people, agents, and generated apps produce work while the
business keeps governance, validation, workflow, and records centralized in
Snowflake.

The app or agent can be temporary. The governed output contract should endure.

## Agent Identity

Assign agents their own Airlock roles. Do not reuse a human's role assignment
just because the agent works for that human.

Use delegation when an agent should act for a specific person. A delegated call
should keep both identities visible:

- `actor_user`: the agent or service account that called Airlock
- `principal_user`: the person on whose behalf the work was performed
- `delegation_id`: the explicit grant authorizing that action

Delegation is not impersonation. Good audit wording is:

```text
Deb submitted a reimbursement on behalf of asmith.
```

Bad audit wording is:

```text
asmith submitted the reimbursement.
```

## Dedicated Agent Pairing

For most business workflows, model an agent as owned or operated by one human
or one accountable owner account, similar to a dedicated assistant. Group-owned
agents are possible, but they require clearer operating rules, stronger audit
expectations, and a good reason to share one agent identity.

A useful default:

- The human has direct Airlock roles for their own work.
- The agent has its own Airlock role for direct agent work.
- The human grants the agent a scoped delegation when the agent should work on
  the human's behalf.
- Direct-role work and delegated work stay separate in reports and audit events.

## Workflow As Pushback And Handoff

Use Airlock workflow for review, pushback, and handoff. Do not encode workflow
state, approval state, reviewer notes, or "for office use only" fields in the
submitted payload unless they are real source-system facts.

Two good submission shapes:

- Configure `Submitted` as the initial workflow step. A successful load creates
  the reviewer-facing item immediately. Keep `Draft` as the pushback state when
  a reviewer needs changes.
- Configure `Draft` as the initial workflow step. A submit tool validates,
  loads, then calls `edit_file_workflow(action => 'advance')` only when Airlock
  policy allows that transition.

If a reviewer returns work to `Draft`, the workflow comment tells the submitter
or delegated agent what to fix. Expectations can tell them when it is due.

## Polling Before Notifications

For current Airlock automation, prefer polling governed Airlock surfaces:

- `user.list_my_work_items(...)` for direct workflow work
- `user.list_my_expectation_work(...)` for due/late work
- materialized spec tables exposed through reference specs
- user-safe file and reference-data listing procedures

Snowflake notifications or event-driven follow-up may be a useful future
integration pattern, but polling Airlock's governed surfaces is simpler,
portable across agents, and easier to audit today.

## Published Reference Specs

Use a materialized write spec plus a read-only reference spec when many agents
or apps need to read governed output efficiently.

The demo pattern:

- `posts` is a file spec. Users and agents append governed post records.
- `posts` materializes to `AIRLOCK_DATA.ACTIVE.T_POSTS`.
- `published_posts` is a read-only reference spec over that materialized table.
- Agents read `published_posts` with `user.select_reference_data(...)`, not by
  querying Airlock-owned tables directly.

This pattern is useful for request/response streams, agent observation logs,
internal forums, approved decisions, and other high-read business signals.

Use the public Airlock spec library for reusable spec shapes such as `posts`.
If the skill is installed without the spec library repo, discover the installed
specs with `user.list_my_specs(...)` and `user.describe_spec(...)` instead of
guessing the shape.

## Chained Agents And Reviewers

Chain agents through governed outputs, not private memory.

Examples:

- A budget-request reviewer approves a department budget file. A downstream
  budget-package agent watches approved budget requests and prepares the next
  higher-level budget packet.
- An application is accepted. A downstream onboarding agent watches accepted
  applications and begins the invitation or account-setup process.
- A request is posted in `posts`. A triage agent reads `published_posts`,
  responds with a linked post, and another agent watches accepted responses.

Each step should have its own Airlock spec, workflow state, reference checks,
and permissions when the responsibilities differ.

## When To Use One Spec Or Several

Use one spec when the records are the same business object at the same
responsibility level. The demo `posts` spec can represent requests, responses,
observations, thanks, issues, and validation notes because they are all posts
with tags and optional structured `details`.

Use multiple specs when the records have different lifecycle, ownership,
validation, evidence, or review responsibilities. For example, a reimbursement
submission, finance review, and payment commitment may be separate specs even
when they link to each other.

## Day-One Demo Checks

After the Airlock demo is installed:

```sql
CALL airlock.user.list_my_roles();
CALL airlock.user.list_my_specs('agent', TRUE);
CALL airlock.user.describe_spec('posts', 'agent', TRUE);
CALL airlock.user.describe_spec('published_posts', 'agent', TRUE);
```

For a demo agent such as Deb, validate/load a `posts` record into
`public/append_access`, then read it back through `published_posts`:

```sql
CALL airlock.user.select_reference_data(
  spec_name => 'published_posts',
  object_key => 'posts',
  row_limit => 100,
  in_app_role => 'agent'
);
```

If the agent cannot see `agent`, `posts`, or `published_posts`, fix the Airlock
role assignment or demo setup. Do not switch to `airlock.admin.*` for normal
agent work.
