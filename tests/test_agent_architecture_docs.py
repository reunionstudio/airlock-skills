from __future__ import annotations

import importlib
import json
import re
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


def test_spec_creation_guidance_handles_create_failure_tabs() -> None:
    skill = _read("airlock/SKILL.md")
    cheat_sheet = _read("airlock/references/procedure-cheat-sheet.md")
    draft_example = _read("airlock/examples/draft-spec-from-template.md")
    combined = _read("docs/airlock-skills.md")

    for text in (skill, cheat_sheet, draft_example, combined):
        assert "CREATE_SPEC_FAILED" in text
        assert "invalid_tabs" in text
        assert "sections" in text
        assert "failed" in text
        assert "duplicate spec name" in text
        assert "full_access" in text
        assert "append_access" in text
        assert "read_access" in text
        assert "isolated_directories_enabled" in text
        assert "guest_roles[].access_level" in text
        assert "public_folder.enabled" in text
        assert "strftime" in text
        assert "%Y-%m-%d" in text
        assert "YYYY-MM-DD" in text

    assert "airlock.user.create_spec_from_template" in skill
    assert "spec_config_overrides" in skill
    assert "dot-path" in cheat_sheet
    assert "column_config" in cheat_sheet
    assert "guest_access" in cheat_sheet
    assert "public_folder.subfolders" in cheat_sheet
    assert "isolated_access_level" in cheat_sheet


def test_spec_design_common_shape_has_validator_required_column_fields() -> None:
    spec_design = _read("airlock/references/spec-design.md")
    match = re.search(r"```json\n(?P<json>.*?)\n```", spec_design, re.DOTALL)

    assert match is not None
    config = json.loads(match.group("json"))
    for column in config["column_config"]:
        assert column["name"]
        assert column["type"]
        assert "description" in column
        assert isinstance(column["tests"], list)
        if column["type"] in {"date", "datetime"}:
            assert column.get("format")
            assert "%" in column["format"]


def test_procedure_cheat_sheet_column_config_date_examples_are_valid_json() -> None:
    cheat_sheet = _read("airlock/references/procedure-cheat-sheet.md")
    json_blocks = re.findall(r"```json\n(.*?)\n```", cheat_sheet, re.DOTALL)
    column_examples = [json.loads(block) for block in json_blocks if "column_config" in block]

    assert column_examples
    columns = column_examples[0]["column_config"]
    formats = {column["name"]: column["format"] for column in columns}
    assert formats["observed_date"] == "%Y-%m-%d"
    assert formats["captured_at"] == "%Y-%m-%d %H:%M:%S"


def test_procedure_cheat_sheet_guest_access_examples_are_valid_json() -> None:
    cheat_sheet = _read("airlock/references/procedure-cheat-sheet.md")
    json_blocks = re.findall(r"```json\n(.*?)\n```", cheat_sheet, re.DOTALL)
    guest_examples = [json.loads(block) for block in json_blocks if "guest_access" in block]

    assert len(guest_examples) == 2
    public_guest = guest_examples[0]["guest_access"]
    assert public_guest["enabled"] is True
    assert public_guest["isolated_directories_enabled"] is False
    assert public_guest["public_folder"]["enabled"] is True
    assert public_guest["public_folder"]["subfolders"]["append_access"]["enabled"] is True

    isolated_guest = guest_examples[1]["guest_access"]
    assert isolated_guest["enabled"] is True
    assert isolated_guest["isolated_directories_enabled"] is True
    assert isolated_guest["isolated_access_level"] == "full_access"
    assert isolated_guest["guest_roles"][0]["access_level"] == "full_access"


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
