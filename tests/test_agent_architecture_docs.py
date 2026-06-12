from __future__ import annotations

import importlib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_skill_points_to_agent_architecture_reference() -> None:
    skill = _read("airlock/SKILL.md")
    reference = _read("airlock/references/agent-architecture-patterns.md")

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


def test_coco_guidance_keeps_stored_procedures_primary() -> None:
    readme = _read("README.md")
    quickstart = _read("docs/quickstart-mcp.md")
    design = _read("docs/design.md")
    skill = _read("airlock/SKILL.md")

    assert "Airlock's primary API remains" in readme
    assert "CoCo" in readme
    assert "direct" in readme and "Airlock stored-procedure calls" in readme
    assert "Snowflake-native agents such as CoCo" in quickstart
    assert "Airlock procedures already provide the named" in quickstart
    assert "Airlock's first-class AI interface is its Snowflake stored procedure API" in design
    assert "Airlock procedures are the source-of-truth tool surface" in skill
    assert "snowflake-managed-mcp.md" not in readme + quickstart + design + skill


def test_assignment_guidance_uses_one_naming_convention() -> None:
    skill = _read("airlock/SKILL.md")
    cheat_sheet = _read("airlock/references/procedure-cheat-sheet.md")
    combined = _read("docs/airlock-skills.md")

    for text in (skill, cheat_sheet, combined):
        assert "assignment_name" in text
        assert "user_id" in text
        assert "assigned_role" in text
        assert "user_name" in text
        assert "role_name" in text
        assert "<assigned_role>.<normalized_user_id>" in text
        assert "observer.bert" in text
        assert "bert_observer" in text


def test_spec_creation_guidance_covers_observation_modeling() -> None:
    skill = _read("airlock/SKILL.md")
    spec_design = _read("airlock/references/spec-design.md")
    combined = _read("docs/airlock-skills.md")

    for text in (skill, spec_design):
        assert "Spec Creation Internal Dialog" in text
        assert "row grain" in text
        assert "Airlock load" in text
        assert "observed_at" in text
        assert "attachment bytes" in text
        assert "controlled vocabularies" in text

    assert "Observation Spec Pattern" in spec_design
    assert "source_url" in spec_design
    assert "transaction_occurred_at" in spec_design
    for phrase in ("guest access", "workflow", "references", "expectations", "delegation"):
        assert phrase in spec_design
    assert "what one row represents" in combined
    assert "business event rather than the Airlock" in combined
    assert "controlled vocabularies" in combined


def test_spec_library_guidance_is_operational_for_coco() -> None:
    skill = _read("airlock/SKILL.md")
    spec_design = _read("airlock/references/spec-design.md")
    combined = _read("docs/airlock-skills.md")

    for text in (skill, spec_design, combined):
        assert "airlock-specs" in text
        assert "catalog.json" in text
        assert "spec library" in text
        assert (
            "live" in text and ("internet" in text or "web access" in text)
        ) or "public URLs" in text
        assert "installed Airlock" in text
        assert "GitHub cloning" in text
        assert "do not block" in text or "Do not stop" in text or "instead of blocking" in text
        assert "source used or unavailable" in text or "source is unavailable" in text

    assert "Use The Spec Library As Patterns" in skill
    assert "Scenario And Spec-Library Workflow" in spec_design
    assert "pattern used" in skill
    assert "pattern note" in spec_design
    assert "pattern note" in combined
    for scenario in ("reimbursements", "timesheets", "budget", "ops issues", "payments"):
        assert scenario in skill + spec_design + combined


def test_skill_examples_use_valid_frontmatter_keys() -> None:
    skill = _read("airlock/SKILL.md")
    combined = _read("docs/airlock-skills.md")

    assert "allowed-tools:" in skill
    assert "allowed-tools:" in combined
    assert "\ntools:\n- snowflake_sql_execute" not in skill
    assert "\ntools:\n- snowflake_sql_execute" not in combined
