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
    {
      "name": "request_id",
      "type": "string",
      "description": "Stable request identifier.",
      "tests": ["not_null"]
    },
    {
      "name": "request_date",
      "type": "date",
      "description": "Business date for the request.",
      "format": "%Y-%m-%d",
      "tests": ["not_null"]
    },
    {
      "name": "amount",
      "type": "number",
      "description": "Requested amount.",
      "tests": []
    },
    {
      "name": "processing_context",
      "type": "variant",
      "description": "Optional evolving context governed by validation rules.",
      "tests": []
    }
  ],
  "rules": [],
  "file_rules": {
    "file_format": {
      "file_type": "csv",
      "record_delimiter": "\n",
      "field_delimiter": ",",
      "field_optionally_enclosed_by": "\"",
      "escape_unenclosed_field": "\\",
      "encoding": "UTF8",
      "parse_header": true,
      "save_header": true
    }
  },
  "attachment_policy": {
    "attachments_enabled": true,
    "attachment_required": false
  }
}
```

This is a full admin spec-config shape for `airlock.admin.create_spec` or
`airlock.admin.alter_spec`. Do not paste it wholesale into
`airlock.user.create_spec_from_template`; that user procedure starts from an
assigned template and accepts narrow `spec_config_overrides`.

Date and datetime `format` values must use strftime tokens such as `%Y-%m-%d`
or `%Y-%m-%d %H:%M:%S`; display masks such as `YYYY-MM-DD` are invalid.

## Spec Creation Internal Dialog

Before drafting JSON, decide what the spec is governing. The hardest part to
change later is the data structure: row grain, column names, column types, and
which facts are typed versus nested. Control structures such as guest access,
workflow, references, expectations, and delegation are important, but they are
generally safer to alter after the core data shape is right.

Ask these questions in order:

1. **What is the governed object?** Is each row an observation, request,
   transaction, reimbursement, file, quote, review, approval, or commitment?
2. **What is the row grain?** One listing per capture? One quote per stay window
   and guest count? One transaction line? One reimbursement claim? Do not mix
   multiple grains in one row unless a `record_type` design is intentional.
3. **What identity survives reloads?** Define a stable id from source keys and
   business event facts, not from Airlock load time alone.
4. **What business time matters?** Airlock records who loaded data and when.
   Add typed columns such as `observed_at`, `captured_at`,
   `transaction_occurred_at`, `statement_period`, or `effective_at` when the
   business event happened before or outside the Airlock load.
5. **What evidence is required?** Screenshots, receipts, PDFs, exports, and
   supporting files should be Airlock attachments. Data columns or variants may
   store evidence labels, source URLs, hashes, page titles, or notes, but not
   attachment bytes.
6. **What metadata belongs in typed columns?** Promote source URL, source object
   id, platform, capture method, market, category, status, amount, date, and
   reference keys when humans will filter, join, audit, or report on them.
7. **What context may evolve?** Use a validated `variant` column for nested
   source context, extraction details, or agent notes that may grow over time.
   Keep required facts and workflow state out of the variant.
8. **What controlled vocabularies are needed?** For fields such as `record_type`,
   `platform`, `listing_role`, `quote_status`, or `capture_method`, prefer
   accepted-value rules when supported. Otherwise document the vocabulary in the
   description and examples.
9. **Who submits and who reviews?** After the data shape is clear, choose guest
   roles, path scopes, workflow states, expectations, and delegation policy.

Ask the human before proceeding when the answer affects row grain, required
attachments, event timestamps, or which fields must be typed columns. Those
choices are expensive to unwind after data starts landing. Decide guest access,
workflow, references, expectations, and delegation after the data model is clear.

### Scenario And Spec-Library Workflow

For common business setups, use the Airlock spec library as a pattern shelf:

1. Name the scenario in business language: reimbursements, weekly timesheets,
   budget requests, project catalog, invoice lines, ops issue register,
   governed posts/signals, Stripe payments, Square or Toast POS, QuickBooks or
   NetSuite accounting, Shopify or Etsy commerce, Salesforce or HubSpot CRM,
   Jira or Linear project work, ServiceNow support, marketing ads, analytics,
   treasury, or reconciliation.
2. If a local `airlock-specs/` directory or uploaded library folder is
   available, read `catalog.json` and then the closest collection/spec files.
   If only the public docs are available, use
   `https://reunionstudio.io/airlock/docs/spec-library.html` as browseable
   pattern context.
3. Identify whether the candidate pattern is an observation, commitment,
   reconciliation, or reference/master-data spec. Do not copy an observation
   shape when the user needs an approved outbound commitment.
4. Borrow candidate columns, source links, expectation ideas, attachment policy,
   and workflow states, but still answer the internal-dialog questions for the
   user's exact process.
5. Preserve durable typed fields from the pattern when they match the process;
   put sparse or evolving provider detail in validated `variant` columns.
6. If no library source is reachable, continue from the scenario family and the
   internal-dialog questions. Do not stop just because GitHub cloning or live web
   access is unavailable.
7. Verify the final descriptor against the installed Airlock procedures before
   creating or altering specs. Library examples may be ahead of, behind, or more
   general than the installed app version.

Do not assume CoCo can always clone GitHub or read arbitrary public URLs. Cloud
Agents can web-search, but outbound host access from the container can be
restricted and personal skills are workspace-scoped. Treat local or uploaded
skill/library files as the reliable source, public web pages as helpful context,
and installed Airlock documentation as the execution contract.

When reporting a draft, include a short pattern note: source used or unavailable,
candidate pattern, pattern type, key adaptations, and remaining human decisions.

### Observation Spec Pattern

For observation specs, distinguish the real-world thing observed from the act of
submitting the observation to Airlock.

Good typed fields for many observation specs:

- `observation_id`: stable id for the observation grain
- `observed_object_id`: listing id, transaction id, account id, or other source
  object key
- `observed_at` or `captured_at`: when the observation was made
- `source_url` or `source_object_key`: where the observation came from
- `source_platform`: source system or website
- `capture_method`: human entry, browser agent, export, OCR, API, etc.
- `observer_category` or business-specific role/category
- amount/date/status fields that are central to the business decision

Airlock load metadata answers who submitted the file and when it entered
Airlock. It does not answer when an observed quote was captured, when a
financial transaction occurred, or when an external record became effective.
Use separate typed columns for those event times.

If screenshots, receipts, PDFs, or exports are needed as evidence, enable
attachments and define attachment expectations. Do not place raw attachment
content inside `payload_json`; store only metadata such as source URL, file tag,
hash, or note when useful.

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
