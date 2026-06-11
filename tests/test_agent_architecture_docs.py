from __future__ import annotations

import importlib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_skill_points_to_agent_architecture_reference() -> None:
    skill = _read("airlock_skills/SKILL.md")
    reference = _read("airlock_skills/references/agent-architecture-patterns.md")

    assert "references/agent-architecture-patterns.md" in skill
    assert "Delegation is not impersonation" in reference
    assert "`posts` materializes to `AIRLOCK_DATA.ACTIVE.T_POSTS`" in reference
    assert "`published_posts` is a read-only reference spec" in reference
    assert "CALL airlock.user.list_my_specs('agent', TRUE);" in reference
    assert "CALL airlock.user.select_reference_data" in reference


def test_public_guides_include_posts_and_architecture_patterns() -> None:
    docs = _read("docs/airlock-skills.md")
    quickstart = _read("docs/quickstart-mcp.md")
    design = _read("docs/design.md")

    for text in (docs, quickstart):
        assert "posts" in text
        assert "published_posts" in text
        assert "Airlock roles" in text
        assert "delegation" in text
        assert "reference spec" in text

    assert "airlock_select_reference_data" in quickstart
    assert "Do not switch to admin procedures" in quickstart
    assert "agent-architecture-patterns.md" in design


def test_mcp_architecture_prompt_teaches_practical_agent_patterns() -> None:
    server = importlib.import_module("airlock_mcp.server")

    prompt = server.explain_airlock_architecture("business leader")

    assert "separate Airlock roles for agents" in prompt
    assert "one accountable human" in prompt
    assert "workflow states and comments" in prompt
    assert "watcher agents" in prompt
    assert "posts/published_posts" in prompt


def test_snowflake_managed_mcp_is_first_class() -> None:
    readme = _read("README.md")
    quickstart = _read("docs/quickstart-mcp.md")
    design = _read("docs/design.md")
    skill = _read("airlock_skills/SKILL.md")
    managed = _read("docs/snowflake-managed-mcp.md")

    for text in (readme, quickstart, design, skill):
        assert "snowflake-managed-mcp.md" in text

    assert "CREATE OR REPLACE MCP SERVER AIRLOCK_AGENT_TOOLS.MCP.airlock_user_tools" in managed
    assert "Snowflake-managed MCP" in readme
    assert "portable MCP" in readme
    assert "CoCo" in managed
    assert "AIRLOCK.USER.DESCRIBE_SPEC" in managed
    assert "thin wrapper procedures" in managed
    assert "Do not point tools at Airlock-owned tables" in managed
