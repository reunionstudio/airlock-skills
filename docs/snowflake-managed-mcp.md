# Snowflake-Managed MCP For Airlock

Use this path when the agent runs inside Snowflake: Cortex Code in Snowsight
(CoCo), Snowflake CoWork, or Cortex Agents. Airlock is already a Snowflake
Native App, so Snowflake-managed MCP is a first-class way to expose typed tools
without running a separate MCP process.

The portable MCP server in `src/airlock_mcp/` remains the first-class path for
non-Snowflake MCP clients. The canonical skill in `airlock_skills/` should be
used with both paths.

## Positioning

Snowflake-managed MCP should stay a thin transport layer:

```text
CoCo / CoWork / Cortex Agent
  -> Snowflake MCP SERVER object
      -> GENERIC stored-procedure tool
          -> AIRLOCK.USER.* or a thin customer-owned wrapper procedure
              -> Airlock procedures, PDP, events, owned storage
```

Do not point tools at Airlock-owned tables, stages, generated views, hybrid
tables, or secure views. Tools should call documented Airlock procedures or
wrapper procedures that call documented Airlock procedures.

## When To Use This Path

Use Snowflake-managed MCP when:

- the agent is CoCo, CoWork, or a Cortex Agent
- the account admin is comfortable creating MCP server objects
- the team wants typed tool calls without deploying a separate server
- Snowflake RBAC, OAuth, and account-level governance should own the tool layer

Use the portable MCP server when:

- the agent host is outside Snowflake
- the user wants one MCP configuration across many local/IDE agents
- the client needs the portable server's normalized result envelope, prompts, or
  resources

## Privileges

The setup role needs privileges to create the MCP server object in the chosen
schema. It also needs enough privileges for any referenced procedure and
warehouse. For external MCP connectors that use OAuth/API integrations, Snowflake
may also require account-level integration privileges. Keep those two cases
separate:

- Snowflake-managed MCP over Snowflake procedures: create an MCP server object in
  a schema and grant access to that object plus the underlying procedures.
- External MCP connector: create an API integration and external MCP server for a
  remote MCP endpoint.

The runtime user still needs normal Airlock access:

- Snowflake role with access to the installed Airlock application object
- Snowflake application role such as `AIRLOCK.app_user`
- Airlock role assignment inside Airlock
- Airlock license seat when user procedures require it
- Airlock PDP approval for the specific spec, path, workflow, attachment,
  expectation, or delegation action

## Starter Direct MCP Server

This direct version points MCP `GENERIC` tools at installed Airlock user
procedures. It is the simplest shape to understand and the right first test if
Snowflake accepts the installed Native App procedure identifiers in your account.

Examples assume:

- installed app object: `AIRLOCK`
- MCP object schema: `AIRLOCK_AGENT_TOOLS.MCP`
- execution warehouse: `COMPUTE_WH`

```sql
CREATE DATABASE IF NOT EXISTS AIRLOCK_AGENT_TOOLS;
CREATE SCHEMA IF NOT EXISTS AIRLOCK_AGENT_TOOLS.MCP;

CREATE OR REPLACE MCP SERVER AIRLOCK_AGENT_TOOLS.MCP.airlock_user_tools
  FROM SPECIFICATION $$
tools:
  - name: "airlock_list_my_roles"
    title: "List My Airlock Roles"
    type: "GENERIC"
    identifier: "AIRLOCK.USER.LIST_MY_ROLES"
    description: "List Airlock roles assigned to the current Snowflake user. Airlock roles are business roles, not Snowflake roles."
    config:
      type: "procedure"
      warehouse: "COMPUTE_WH"
      input_schema:
        type: "object"
        properties: {}

  - name: "airlock_list_specs"
    title: "List Airlock Specs"
    type: "GENERIC"
    identifier: "AIRLOCK.USER.LIST_MY_SPECS"
    description: "List Airlock specs visible to the caller under an optional Airlock role lens."
    config:
      type: "procedure"
      warehouse: "COMPUTE_WH"
      input_schema:
        type: "object"
        properties:
          in_app_role:
            type: "string"
            description: "Optional Airlock role lens. This is not a Snowflake role."
          include_managed_roles:
            type: "boolean"
            description: "Whether the role lens can include roles managed by the selected Airlock role."

  - name: "airlock_describe_spec"
    title: "Describe Airlock Spec"
    type: "GENERIC"
    identifier: "AIRLOCK.USER.DESCRIBE_SPEC"
    description: "Describe a spec visible to the caller, including fields, file rules, workflow, attachments, references, and accessible path scopes."
    config:
      type: "procedure"
      warehouse: "COMPUTE_WH"
      input_schema:
        type: "object"
        required: ["spec_name"]
        properties:
          spec_name:
            type: "string"
            description: "Airlock spec name."
          in_app_role:
            type: "string"
            description: "Optional Airlock role lens."
          include_managed_roles:
            type: "boolean"
            description: "Whether the role lens can include managed child Airlock roles."

  - name: "airlock_validate_inline_csv"
    title: "Validate Airlock Inline CSV"
    type: "GENERIC"
    identifier: "AIRLOCK.USER.VALIDATE_DATA"
    description: "Validate inline CSV for an Airlock spec without loading it. Use describe_spec first and preserve STATUS, CODE, MESSAGE, and ISSUES."
    config:
      type: "procedure"
      warehouse: "COMPUTE_WH"
      input_schema:
        type: "object"
        required: ["spec_name", "file_content"]
        properties:
          spec_name:
            type: "string"
          file_content:
            type: "string"
            description: "Inline CSV content. Do not log raw file content."
          in_app_role:
            type: "string"
            description: "Optional Airlock role lens."

  - name: "airlock_load_inline_csv"
    title: "Load Airlock Inline CSV"
    type: "GENERIC"
    identifier: "AIRLOCK.USER.LOAD_DATA"
    description: "Load inline CSV through Airlock after validation. Include required attachments in this call when the spec requires them."
    config:
      type: "procedure"
      warehouse: "COMPUTE_WH"
      input_schema:
        type: "object"
        required: ["spec_name", "file_content", "filename"]
        properties:
          spec_name:
            type: "string"
          file_content:
            type: "string"
            description: "Inline CSV content. Do not log raw file content."
          filename:
            type: "string"
            description: "Logical Airlock filename for the uploaded file."
          in_app_role:
            type: "string"
            description: "Optional Airlock role lens."
          path_scope:
            type: "string"
            description: "Path scope from describe_spec ACCESSIBLE_PATHS, such as public/full_access or public/append_access."
          attachment_content_base64:
            type: "string"
            description: "Optional attachment content for specs that require evidence. Do not log raw bytes."
          attachment_filename:
            type: "string"
            description: "Optional attachment filename."

  - name: "airlock_list_expectation_work"
    title: "List Airlock Expectation Work"
    type: "GENERIC"
    identifier: "AIRLOCK.USER.LIST_MY_EXPECTATION_WORK"
    description: "List expectation status visible to the caller. Expectations are cadence/order/work contracts, not column validation."
    config:
      type: "procedure"
      warehouse: "COMPUTE_WH"
      input_schema:
        type: "object"
        properties:
          spec_name:
            type: "string"
          in_app_role:
            type: "string"
          include_managed_roles:
            type: "boolean"
$$;
```

After creation, grant usage on the MCP server to the role that CoCo or the
Cortex Agent uses. Also grant whatever Snowflake privileges are needed to call
the installed Airlock procedures and use the warehouse.

```sql
GRANT USAGE ON MCP SERVER AIRLOCK_AGENT_TOOLS.MCP.airlock_user_tools
  TO ROLE AIRLOCK_AGENT_ROLE;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE AIRLOCK_AGENT_ROLE;
```

Granting access to the MCP server does not bypass Airlock. Airlock procedures
still evaluate Snowflake application roles, Airlock roles, licenses, delegation,
workflow state, attachment policy, references, and expectations.

## Preferred Wrapper Pattern

Direct procedure tools are useful for a first smoke test. For production, prefer
thin wrapper procedures in a customer-owned schema when either of these is true:

- direct Native App procedure identifiers are not accepted by Snowflake-managed
  MCP in the target account
- the Airlock procedure returns a table shape that CoCo does not handle cleanly
- you want one normalized `VARIANT` result for every tool

Wrapper procedures may normalize output, but must not add authorization or
business logic. They should call Airlock, collect the result, and return a small
object with the procedure name, rows, status/code/message/issue fields when
present, and delegation context when present.

Recommended wrapper names:

```text
AIRLOCK_AGENT_TOOLS.MCP.LIST_MY_ROLES_JSON()
AIRLOCK_AGENT_TOOLS.MCP.LIST_SPECS_JSON(in_app_role, include_managed_roles)
AIRLOCK_AGENT_TOOLS.MCP.DESCRIBE_SPEC_JSON(spec_name, in_app_role, include_managed_roles)
AIRLOCK_AGENT_TOOLS.MCP.VALIDATE_INLINE_CSV_JSON(spec_name, file_content, in_app_role)
AIRLOCK_AGENT_TOOLS.MCP.LOAD_INLINE_CSV_JSON(spec_name, file_content, filename, in_app_role, path_scope, attachment_content_base64, attachment_filename)
AIRLOCK_AGENT_TOOLS.MCP.LIST_EXPECTATION_WORK_JSON(spec_name, in_app_role, include_managed_roles)
```

The MCP server specification should then point at the wrapper procedures instead
of directly at `AIRLOCK.USER.*`.

## CoCo Usage Pattern

With the skill installed and the MCP server available, CoCo should use typed
calls like this instead of hand-writing SQL:

```json
{
  "tool": "airlock_describe_spec",
  "arguments": {
    "spec_name": "observations",
    "in_app_role": "observer",
    "include_managed_roles": true
  }
}
```

Then:

```json
{
  "tool": "airlock_validate_inline_csv",
  "arguments": {
    "spec_name": "observations",
    "in_app_role": "observer",
    "file_content": "observation_id,observed_at,url,notes\nobs-001,2026-06-11,https://example.com,Looks valid"
  }
}
```

The skill still matters. It teaches CoCo when to use these tools, how to choose
an Airlock role lens, why `managed_by_role: app_admin` is noise, how assignments
are shaped, when validation is useful, and why direct writes to Airlock-owned
objects are not allowed.

## Tool Set Guidance

Start with user-safe tools:

- `airlock_list_my_roles`
- `airlock_list_specs`
- `airlock_describe_spec`
- `airlock_validate_inline_csv`
- `airlock_load_inline_csv`
- `airlock_list_my_files`
- `airlock_select_files`
- `airlock_list_work_items`
- `airlock_edit_file_workflow`
- `airlock_list_expectation_work`
- `airlock_add_attachment`

Keep admin tools in a separate MCP server object, such as
`airlock_admin_tools`, and grant it only to roles intended to perform governance
changes. Admin tools should use `validate_only` for complex spec/template or
expectation changes and `dry_run` for destructive cleanup previews.

## Safety Checklist

- Install the Airlock skill as the agent guidance layer.
- Prefer typed MCP tools over hand-written SQL when the tool exists.
- Keep `airlock.user.*` and `airlock.admin.*` tools separate.
- Do not expose broad `SYSTEM_EXECUTE_SQL` as the main Airlock tool if typed
  tools are available.
- Do not log file content, attachment bytes, private keys, passphrases, OAuth
  tokens, or SQL stack traces.
- Preserve Airlock `STATUS`, `CODE`, `MESSAGE`, `ISSUES`, path, filename,
  workflow state, expectation status, and delegation context.
- Verify installed Airlock documentation after app upgrades and update the MCP
  server specification when procedure signatures change.
