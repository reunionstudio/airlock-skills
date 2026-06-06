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

Admin procedures affect governance. Use `validate_only => TRUE` for declarative
create/alter APIs when available, show the planned change, and ask before
mutating. Use `dry_run => TRUE` for destructive previews.
