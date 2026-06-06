# Airlock Spec Design Guide

Airlock specs work best when they separate submitted business facts from Airlock
control-plane state.

## Payload vs Airlock State

A file payload should contain the facts supplied by the person, agent, source
system, or business process. Airlock should carry the lifecycle around that
payload: file identity, path, filename, workflow state, audit events,
attachments, expectations, retention, and authorization.

For a submitted reimbursement, good payload fields are:

```text
employee_username, manager_username, receipt_date, merchant, amount, currency,
category, business_purpose
```

The receipt belongs in Airlock attachments. The file identity belongs in the
manifest path and filename. The approval journey belongs in Airlock workflow and
events.

Avoid asking a user or agent to invent fields such as:

```text
reimbursement_id, approval_status, approved_by, approved_at, workflow_status,
workflow_step, processing_context
```

Those values are either Airlock metadata, reviewer output, or downstream system
state. They should not be required in the initial submitter payload unless they
come from a real upstream system and are part of the business fact being
captured.

## Status Fields Are Not Banned

Status can be legitimate business data. For example, a Shopify product status,
a Bill.com payment status, or a source-system subscription status may be a real
source fact.

The rule is narrower: do not duplicate Airlock lifecycle state in the primary
payload. If the field means "where this file is in Airlock review," use Airlock
workflow. If it means "what the source system reported," model it explicitly and
name the source.

## Submit-To-Workflow Pattern

Some business workflows should skip a visible "extra click" for the submitter.
For example, an agent may prepare a reimbursement for asmith and land it in the
Submitted state so a reviewer can act immediately.

Keep that as Airlock workflow, not payload shape:

```text
validate business payload -> load file -> advance workflow to Submitted
```

An MCP tool or agent skill can present this as one action, such as "submit this
reimbursement", but the secure implementation is still `load_data` followed by
an authorized `edit_file_workflow` transition. If the reviewer has a problem,
they return the file to Draft with a workflow comment. The principal then sees
the returned Draft item in My Work, fixes or resends the content, and resubmits
before the expectation due date.

Do not add `submitted_at`, `approval_status`, `workflow_step`, or reviewer
notes to the source file just to support this journey.

## VARIANT Columns

Use `variant` for flexible business or provider details that are real evidence:
raw provider payloads, sparse optional attributes, nested review evidence, and
fields that are still evolving.

Do not use `variant` as a junk drawer for Airlock process state. If a field is
workflow, approval routing, UI state, debug output, or "for office use only"
metadata, put it in Airlock workflow/events/expectations or a separate review
or commitment spec.

When a nested field becomes operationally important, promote it deliberately:

```text
raw VARIANT payload -> variant_shape rule -> promoted path -> explicit column
```

Keep payloads bounded. Prefer one business event, source record, review result,
or provider response per row. If an upstream JSON document is an outer array of
records, model it as multiple rows or use a light adapter step rather than one
giant `variant`.

## Review And Commitment Specs

Derived specs are allowed to carry derived work products. A review spec can
record check results, evidence, recommendations, and references to the file it
reviewed. A payment commitment spec can record the outbound packet that was
prepared from approved upstream files.

Even there, prefer Airlock file identity for upstream references:

```text
reimbursement_spec_name, reimbursement_path, reimbursement_filename
```

Do not require a submitter-created id just so downstream records can link back.
If the upstream system already has a stable id, capture it. If not, Airlock's
manifest identity is the stable operational handle.

## Agent Rule

Agents should always call `describe_spec` before building a file. They should
send only columns declared in `column_config`, satisfy file rules and
attachments, and avoid inventing ids, approval fields, workflow fields, or extra
metadata columns. After a successful load, agents should report the returned
`PATH`, `FILENAME`, `STATUS`, `ISSUES`, and workflow state.
