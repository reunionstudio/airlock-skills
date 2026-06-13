# Airlock Procedure Cheat Sheet

Use this reference for common Airlock procedure paths. Query installed
documentation only when you need live app/version signatures or availability.

Examples assume the installed app object is named `airlock`; substitute the
account's installed app name when needed.

## Discovery

```sql
SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_WAREHOUSE();
CALL airlock.user.list_my_roles();
CALL airlock.user.list_my_specs('<airlock_role>');
CALL airlock.user.describe_spec('<spec_name>', '<airlock_role>');
```

Use installed docs as a registry check:

```sql
CALL airlock.user.documentation(CONTENT_MODE => 'PROCEDURES');
```

Do not call documentation as the default response to design or workflow
questions. The skill contains enough guidance for common usage.

## Spec Creation Surfaces

Use the shape that matches the procedure:

- `airlock.admin.create_spec(spec_config, validate_only, ...)` accepts a full
  canonical spec config with sections such as `core_config`, `column_config`,
  `file_rules`, `guest_access`, `attachment_policy`, and `rules`.
- `airlock.user.create_spec_from_template(template_name, new_spec_name,
  spec_alias, spec_config_overrides)` starts from an assigned or public template.
  Overrides should be narrow editable paths such as
  `{"core_config.description": "FY26"}`. Nested JSON is flattened to dot-path
  keys, but do not paste a full admin config unless the template's field-access
  rules explicitly allow those paths and the values pass validation.

If `CREATE_SPEC_FAILED` returns `VALIDATION.invalid_tabs`, treat those entries
as failed validation sections, not unknown JSON keys. For example,
`["column_config", "guest_access"]` means the core spec name/owner checks passed,
but column and guest-access validation failed. Do not diagnose that as a
duplicate spec name unless `core` is in `invalid_tabs` or `core_errors` says so.
Do not assume `full_access` is invalid; valid guest access levels include
`full_access`, `append_access`, and `read_access`.

When details are missing, apply the known validators before asking to drop or
recreate anything:

- `column_config` must be a non-empty list; every column needs `name`,
  `type`/`data_type`, `description`, and `tests` as a list. `date` and
  `datetime` columns need a strftime `format` such as `%Y-%m-%d` or
  `%Y-%m-%d %H:%M:%S`; display masks such as `YYYY-MM-DD` are invalid.
- CSV `file_rules.file_format` uses canonical keys such as
  `record_delimiter`, `field_delimiter`, `field_optionally_enclosed_by`,
  `escape_unenclosed_field`, `encoding`, `parse_header`, and `save_header`.
- `guest_access`, when enabled, needs real non-`app_admin` Airlock guest roles
  and at least one directory model: isolated directories with an access level,
  or a public folder with at least one enabled subfolder (`full_access`,
  `append_access`, or `read_access`).
  If `isolated_directories_enabled` is `false`, changing
  `guest_roles[].access_level` will not enable a shared folder; set
  `public_folder.enabled` and one `public_folder.subfolders.*.enabled` flag.

Date/datetime column examples:

```json
{
  "column_config": [
    {
      "name": "observed_date",
      "type": "date",
      "description": "Date captured.",
      "format": "%Y-%m-%d",
      "tests": ["not_null"]
    },
    {
      "name": "captured_at",
      "type": "datetime",
      "description": "Timestamp captured.",
      "format": "%Y-%m-%d %H:%M:%S",
      "tests": []
    }
  ]
}
```

Shared public-folder append example:

```json
{
  "guest_access": {
    "enabled": true,
    "guest_roles": [{"role_name": "observer"}],
    "isolated_directories_enabled": false,
    "isolated_access_level": null,
    "public_folder": {
      "enabled": true,
      "subfolders": {
        "append_access": {"enabled": true},
        "full_access": {"enabled": false},
        "read_access": {"enabled": false}
      }
    }
  }
}
```

Isolated role-folder example:

```json
{
  "guest_access": {
    "enabled": true,
    "guest_roles": [{"role_name": "observer", "access_level": "full_access"}],
    "isolated_directories_enabled": true,
    "isolated_access_level": "full_access",
    "isolated_directories_per_user": false,
    "public_folder": {"enabled": false}
  }
}
```

## Admin Roles And Assignments

Use exact descriptor keys for admin role and assignment procedures.

Role creation usually does not need `managed_by_role` when the intended manager
is `app_admin`; all Airlock roles are already manageable by `app_admin`.

```sql
CALL airlock.admin.create_roles(
  ARRAY_CONSTRUCT(
    OBJECT_CONSTRUCT(
      'role_name', 'observer',
      'description', 'Guest role for submitting observations'
    )
  ),
  FALSE
);
```

Assignment creation requires `assignment_name`, `user_id`, and `assigned_role`:

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

Use assignment names in the form `<assigned_role>.<normalized_user_id>` unless
the human supplies an existing name. Normalize the Snowflake user id to lower
case for `assignment_name`, keep `user_id` as the actual Snowflake user id, and
use a dot separator. Put the longer-lived Airlock role first and the occupant
user second. Good examples: `observer.bert`, `observer.aroberts`.
Avoid underscore-separated names such as `bert_observer`.

Do not use `user_name` or `role_name` for assignment descriptors. Do not probe
`list_assignments()` or fake `describe_assignment()` calls just to infer this
schema; use these keys or query installed documentation when the installed API
version is genuinely uncertain.

## Validate And Load Inline CSV

```sql
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
  path_scope => '<path_scope_from_describe_spec>'
);
```

For inline CSV, omit `path`. `path` is for staged file paths. Use named
arguments once optional parameters matter.

## Records JSON Authoring

Agents may author business payloads as records JSON:

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

Convert that shape to CSV `file_content` locally for the installed procedure.
Keep role, path, delegation, workflow, attachment, retry, and audit context
outside the record.

## Governed Posts Demo

The demo specs `posts` and `published_posts` are user-safe examples for agents.
`posts` is a materialized file spec where users and agents append shared posts.
`published_posts` is a read-only reference spec over that materialized table.

Agent discovery:

```sql
CALL airlock.user.list_my_roles();
CALL airlock.user.list_my_specs('agent', TRUE);
CALL airlock.user.describe_spec('posts', 'agent', TRUE);
CALL airlock.user.describe_spec('published_posts', 'agent', TRUE);
```

Agent post submission:

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

Read back through the reference spec:

```sql
CALL airlock.user.select_reference_data(
  spec_name => 'published_posts',
  object_key => 'posts',
  row_limit => 100,
  in_app_role => 'agent'
);
```

If `agent` is denied, verify the connection's `CURRENT_USER()` and the output of
`list_my_roles()` before trying anything else. Do not use admin procedures to
work around a missing user assignment.

## Load With Attachment

```sql
CALL airlock.user.load_data(
  spec_name => '<spec_name>',
  file_content => '<csv_header_and_rows>',
  filename => '<logical_filename>',
  in_app_role => '<airlock_role>',
  path_scope => '<path_scope_from_describe_spec>',
  attachment_content_base64 => '<base64_attachment>',
  attachment_filename => '<attachment_filename>'
);
```

If `attachment_policy.attachment_required` is true, include the attachment in
`load_data` unless installed documentation explicitly supports another sequence.

## Delegated Work

Delegation is not impersonation. The actor remains the Snowflake user executing
the procedure. The principal is passed as `on_behalf_of_user`.

```sql
CALL airlock.user.list_my_delegations('received');

CALL airlock.user.validate_data(
  spec_name => '<spec_name>',
  file_content => '<csv_header_and_rows>',
  in_app_role => '<principal_airlock_role>',
  on_behalf_of_user => '<principal_user>'
);
```

Pass `delegation_id` only when Airlock reports an ambiguous delegation. Preserve
actor, principal, delegation id, and denial codes in output.

## Submit For Review

A tool may present this as one action, but Airlock should still audit it as load
plus workflow movement:

```sql
CALL airlock.user.load_data(...);
CALL airlock.user.edit_file_workflow(
  spec_name => '<spec_name>',
  path => '<returned_path>',
  filename => '<returned_filename>',
  action => 'advance',
  comment => 'Submitted for review',
  on_behalf_of_user => '<principal_user>'
);
```

Only include `on_behalf_of_user` for delegated work, and only advance when the
spec policy and active grant allow workflow movement at the current step. If a
reviewer returns the item to Draft, report the workflow comment and expectation
due date instead of adding workflow fields to source data.

## Workflow And Expectations

```sql
CALL airlock.user.list_my_work_items('<spec_name>', '<airlock_role>', TRUE);
CALL airlock.user.list_my_expectation_work('<spec_name>', '<airlock_role>', TRUE);
CALL airlock.user.edit_file_workflow(
  spec_name => '<spec_name>',
  path => '<file_path>',
  filename => '<file_name>',
  action => '<advance_or_return>',
  comment => '<comment>',
  validate_only => TRUE,
  in_app_role => '<airlock_role>'
);
```

Run workflow transitions with `validate_only => TRUE` first when available.

## Admin Guardrails

Admin procedures affect governance. Ask before mutating. For simple role or
assignment creation, once the human approves, call the mutating procedure once
with `validate_only => FALSE`; Airlock validates and returns structured issues on
failure. Do not run validate-only and then the identical mutating call by
default. Use `validate_only => TRUE` for larger governance changes,
spec/template/expectation descriptors, unclear descriptors, or explicit human
preview requests. Use `dry_run => TRUE` only for destructive previews.
