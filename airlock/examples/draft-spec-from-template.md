# Draft Spec From Template

Use this pattern when a user asks to draft a new spec from an assigned or public
Airlock template.

## Preferred User Path

1. List Airlock roles:
   ```sql
   CALL airlock.user.list_my_roles();
   ```
2. Use `references/spec-design.md` and the provided templates to draft narrow
   overrides. Treat the bundled JSON templates as full admin spec-config
   examples, not as payloads to paste into `spec_config_overrides`. If
   user-facing template-list procedures are not installed, explain that an app
   admin may need to inspect template assignments.
3. Prepare override values from the user's request. Keep overrides narrow.
   Use dot-path keys such as `{"core_config.description": "FY26"}`, or nested
   JSON that flattens to the same editable paths. Use stable typed columns for
   durable business facts. When the user needs future flexibility for evolving
   context, add or request a `variant` column with explicit `variant_shape`
   validation instead of creating many speculative columns. Only override
   `column_config` or `guest_access` when the assigned template explicitly
   permits those paths.
4. Create from an assigned template:
   ```sql
   CALL airlock.user.create_spec_from_template(
     '<template_name>',
     '<new_spec_name>',
     '<spec_alias>',
     PARSE_JSON('<spec_config_overrides_json>')
   );
   ```

## Admin Path

For admin creation or alteration:

1. Call the relevant create/alter procedure with `validate_only => TRUE` when
   available.
2. Show the planned spec name, owner Airlock role, publication state, fields,
   workflow, attachment policy, guest access, and validation issues.
3. Ask for approval before the mutating call.
4. Preserve returned `STATUS`, `CODE`, `MESSAGE`, `ISSUES`, and `VALIDATION`.

Never write directly to `core.specs`, stages, generated views, or generated
tables.

## Troubleshooting Create Failures

`CREATE_SPEC_FAILED` with `VALIDATION.invalid_tabs` names the validation
sections that failed. It is not a list of unknown JSON keys. If a
create-from-template call returns `["column_config", "guest_access"]`, do not
infer a duplicate spec name and do not infer that `full_access` is invalid.
Duplicate names normally surface under `core`; guest access levels include
`full_access`, `append_access`, and `read_access`.

For `column_config`, check that each column has `name`, `type` or `data_type`,
`description`, and `tests` as a list; date and datetime columns also need a
strftime `format` such as `%Y-%m-%d` or `%Y-%m-%d %H:%M:%S`. Do not use display
masks such as `YYYY-MM-DD`. For enabled `guest_access`, check that guest roles
exist and that the config enables isolated directories or a public subfolder. If
`isolated_directories_enabled` is false, changing `guest_roles[].access_level`
will not fix missing shared access; enable `public_folder.enabled` plus one
`public_folder.subfolders.*.enabled` flag, or switch to isolated directories and
set `isolated_access_level`.

## Flexible Context Pattern

Use a `variant` column for contextual payloads that may change over time, such
as `processing_context`, `evidence`, or `agent_context`. Keep join keys,
required identifiers, dates, amounts, and workflow-driving fields as first-class
typed columns.

When the installed Airlock API supports it, pair the variant column with a
`variant_shape` rule. Admins can later alter the spec config to permit and
validate new nested keys without changing the physical table shape.

Only call `airlock.user.documentation(CONTENT_MODE => 'PROCEDURES')` when the
installed app's exact create-from-template signature is uncertain.
