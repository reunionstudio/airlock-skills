# Airlock Spec Design

Use this reference when drafting or reviewing an Airlock spec. It is guidance
for the agent; exact installed procedure signatures still come from the active
Airlock app when execution is needed.

## What A Spec Is

An Airlock spec is the governed contract for a class of business output. It is
more than a table schema. It can include:

- core identity and ownership
- column configuration
- file rules
- validation rules
- attachment policy
- guest access and path scopes
- workflow states
- reference checks
- expectation contracts

The spec should teach an agent what valid work looks like before the agent
submits data.

## Common Shape

```json
{
  "core_config": {
    "spec_name": "example_requests",
    "spec_alias": "Example Requests",
    "description": "Governed intake for example requests.",
    "owner_role": "app_admin",
    "is_published": false,
    "is_archived": false
  },
  "column_config": [
    {"name": "request_id", "type": "string", "tests": ["not_null"]},
    {"name": "request_date", "type": "date", "tests": ["not_null"]},
    {"name": "amount", "type": "number", "tests": []},
    {"name": "processing_context", "type": "variant", "tests": []}
  ],
  "rules": [],
  "file_rules": {
    "file_format": {
      "file_type": "csv",
      "delimiter": ",",
      "has_header": true
    }
  },
  "attachment_policy": {
    "attachments_enabled": true,
    "attachment_required": false
  }
}
```

## Typed Columns Versus Variant Columns

Use stable typed columns for:

- durable identifiers
- dates, amounts, statuses, and workflow-driving fields
- reference keys
- values people filter, join, aggregate, audit, or report on

Use a `variant` column for flexible context:

- agent-generated processing context
- optional evidence metadata
- source-system hints
- policy inputs that may evolve
- nested payloads where only some paths matter today

Do not use `variant` as an unvalidated junk drawer for required business facts.
Put required, reportable facts in typed columns.

## Variant Shape Rule

Pair flexible variant columns with explicit validation:

```json
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
```

Admins can later alter the spec config to allow and validate new nested keys
without changing the physical data structure.

## Field Path Rule

Use a `field_path` rule when validation should inspect a scalar inside a
`variant` column. This is useful for reference checks against nested payloads.

```json
{
  "type": "foreign_key",
  "field_path": {
    "column": "processing_context",
    "json_path": "$.source.employee_id"
  },
  "ref": {
    "reference": "employees_ref",
    "column": "employee_id"
  }
}
```

## Expectations Are Not Column Tests

Expectations model business activity: due dates, order, cadence, intervals,
milestones, and approved exceptions. Use expectations to answer what is late or
blocked. Use column tests and rules to validate the shape and values of a file.

## Submit-To-Workflow Pattern

When a user asks an agent to submit work for review, keep submitted data clean:
validate and load the business payload, then advance the Airlock workflow to
Submitted if policy allows it. This can be one user-facing tool call, but it is
not one data payload shape. Reviewer pushback belongs in Airlock workflow
comments and expectations, not in columns such as `approval_status`,
`workflow_step`, or reviewer notes.

## Validation Path

For admin create or alter work:

1. Draft a descriptor.
2. Prefer `validate_only => TRUE` where the installed procedure supports it.
3. Show validation issues and expected changes.
4. Ask before mutating the spec.

Never write directly to Airlock-owned tables, stages, generated views, or
generated tables.
