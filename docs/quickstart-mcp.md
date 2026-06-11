# Portable MCP Server Quickstart

Use this path when an MCP-capable agent runs outside Snowflake or strongly
prefers MCP tool discovery over direct Snowflake SQL. The portable Airlock
Skills MCP server exposes typed Airlock tools that call documented
`airlock.user.*` stored procedures through Snowflake.

For Snowflake-native agents such as CoCo, prefer the Airlock skill plus direct
stored-procedure calls first. Airlock procedures already provide the named,
authorized, documented operation surface inside the customer's Snowflake
account.

Examples assume the installed app object is named `airlock`. If an account uses
a different app name, set `AIRLOCK_APPLICATION_NAME`.

## Prerequisites

- Airlock is installed from the
  [Snowflake Marketplace listing](https://app.snowflake.com/marketplace/listing/GZTSZ1QRFJ6L/reunion-studio-airlock).
- The Snowflake user has a role that can use the installed Airlock app and
  activate the required Snowflake application role.
- The user has the required Airlock role assignment and license seat for the
  workflow.
- The agent host can pass Snowflake connection settings through environment
  variables or a Snowflake connector profile.

## Install

After the package is published for a release, run the server without a permanent
install:

```bash
uvx --from airlock-skills airlock-mcp
```

Equivalent command alias:

```bash
uvx --from airlock-skills airlock-skills-mcp
```

From a local clone:

```bash
uv run airlock-mcp
```

## Configure

Set connection values in the environment used by your MCP client:

```bash
export AIRLOCK_SNOWFLAKE_ACCOUNT="org-account"
export AIRLOCK_SNOWFLAKE_USER="AIRLOCK_AGENT"
export AIRLOCK_SNOWFLAKE_ROLE="AIRLOCK_APP_USER_ROLE"
export AIRLOCK_SNOWFLAKE_WAREHOUSE="COMPUTE_WH"
export AIRLOCK_APPLICATION_NAME="AIRLOCK"
export AIRLOCK_PRIVATE_KEY_PATH="/path/to/rsa_key.p8"
export AIRLOCK_PRIVATE_KEY_PASSPHRASE="optional-passphrase"
```

For local development, a named Snowflake connection profile can be simpler:

```bash
export AIRLOCK_SNOWFLAKE_CONNECTION_NAME="airlock-dev"
```

Optional Airlock settings:

```bash
export AIRLOCK_MCP_DEFAULT_AIRLOCK_ROLE="automation_user"
export AIRLOCK_MCP_MAX_INLINE_BYTES="1048576"
export AIRLOCK_MCP_ADMIN_TOOLS="0"
```

Prefer key-pair authentication for automation users. Password authentication is
accepted only when the Snowflake account policy allows it.

## MCP Client Example

For MCP clients that use JSON server configuration:

```json
{
  "mcpServers": {
    "airlock-skills": {
      "command": "uvx",
      "args": ["--from", "airlock-skills", "airlock-mcp"],
      "env": {
        "AIRLOCK_SNOWFLAKE_CONNECTION_NAME": "airlock-dev",
        "AIRLOCK_APPLICATION_NAME": "AIRLOCK",
        "AIRLOCK_MCP_ADMIN_TOOLS": "0"
      }
    }
  }
}
```

Keep secrets in the host's secret storage or environment. Do not commit private
keys, passwords, or passphrases into MCP configuration files.

## First Checks

After connecting, ask the agent to call read-only discovery tools first:

1. `airlock_get_connection_context`
2. `airlock_get_documentation` with `content_mode="PROCEDURES"`
3. `airlock_list_my_roles`
4. `airlock_list_specs`

Then use the normal Airlock pattern:

```text
describe_spec -> validate_data -> load_data -> list/select/workflow/attach
```

## Governed Posts Smoke

Many demo and onboarding installs include two user-safe specs:

- `posts`: a materialized file spec where users and agents append governed
  business posts, requests, replies, observations, and agent updates.
- `published_posts`: a read-only reference spec over the materialized `posts`
  table for governed readback.

This is the recommended first smoke test for an agent account because it proves
the agent can discover its Airlock role, validate a payload, write through a
spec, and read back through a reference spec without direct access to
Airlock-owned tables.

```text
airlock_list_my_roles
airlock_list_specs(in_app_role="agent")
airlock_describe_spec(spec_name="posts", in_app_role="agent")
airlock_validate_data(spec_name="posts", ...)
airlock_load_data(spec_name="posts", ...)
airlock_describe_spec(spec_name="published_posts", in_app_role="agent")
airlock_select_reference_data(spec_name="published_posts", object_key="posts")
```

If the agent cannot see `agent`, `posts`, or `published_posts`, fix the Airlock
role assignment or demo setup first. Do not switch to admin procedures as a
workaround for missing user access.

## Architecture Pattern

For generated apps and AI agents, keep Airlock as the governance layer:

- Assign agents their own Airlock roles instead of sharing a human role.
- Use delegation only when an agent acts for one specific accountable human.
- Use workflow comments and pushback states for remediation instead of adding
  workflow columns to payloads.
- Prefer polling governed Airlock work lists, materialized specs, or reference
  specs for watcher agents. Snowflake notifications can be explored later, but
  polling is the simpler default.
- For high-read streams, write through a materialized spec and expose readback
  through a reference spec, as `posts` and `published_posts` demonstrate.

## Snowflake-Native Agents

For CoCo and other Snowflake-native agents, do not add an MCP layer just to make
Airlock callable. Use the Airlock skill and call installed Airlock procedures
directly. If the agent struggles with procedure signatures or result shapes,
improve the installed Airlock documentation, examples, or stored-procedure
contracts first.

A Snowflake `CREATE MCP SERVER` object can be useful for a small account-local
starter toolset, but it is static metadata and should not be treated as the full
Airlock MCP. A full MCP adapter should be owned and versioned by Airlock so it
can update as the Airlock procedure API evolves.
