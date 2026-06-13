from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_canonical_skill_folder_is_airlock() -> None:
    assert (REPO_ROOT / "airlock" / "SKILL.md").is_file()
    assert not (REPO_ROOT / "airlock_skills").exists()


def test_airlock_skill_body_stays_lean_enough_for_coco() -> None:
    skill_lines = (REPO_ROOT / "airlock" / "SKILL.md").read_text(encoding="utf-8").splitlines()

    assert len(skill_lines) <= 500


def test_validate_skill_accepts_canonical_airlock_folder() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "validate_skill.py"),
            "airlock",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Skill is valid!" in result.stdout


def test_package_coco_skill_creates_airlock_folder_and_zip(tmp_path: Path) -> None:
    output_dir = tmp_path / "coco"

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "package_coco_skill.py"),
            "--output-dir",
            str(output_dir),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    skill_dir = output_dir / "airlock"
    assert skill_dir.is_dir()
    assert not (output_dir / "airlock_skills").exists()
    assert (skill_dir / "SKILL.md").is_file()
    assert (skill_dir / "references" / "spec-design.md").is_file()
    assert "Created CoCo skill folder:" in result.stdout
    assert "Created CoCo skill zip:" in result.stdout

    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    assert "name: airlock" in skill_text
    assert "allowed-tools:" in skill_text

    zip_path = output_dir / "airlock.zip"
    assert zip_path.is_file()
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())

    assert "airlock/SKILL.md" in names
    assert "airlock/references/spec-design.md" in names
    assert not any(name.startswith("airlock_skills/") for name in names)


def test_bundled_spec_templates_use_canonical_csv_file_rules() -> None:
    for template_name in (
        "spec-config-minimal.json",
        "spec-config-with-variant-context.json",
    ):
        template = json.loads(
            (REPO_ROOT / "airlock" / "templates" / template_name).read_text(encoding="utf-8")
        )
        file_format = template["file_rules"]["file_format"]

        assert file_format["file_type"] == "csv"
        for key in (
            "record_delimiter",
            "field_delimiter",
            "field_optionally_enclosed_by",
            "escape_unenclosed_field",
            "encoding",
            "parse_header",
            "save_header",
        ):
            assert key in file_format
        assert "delimiter" not in file_format
        assert "has_header" not in file_format


def test_bundled_spec_templates_show_strftime_date_format() -> None:
    for template_name in (
        "spec-config-minimal.json",
        "spec-config-with-variant-context.json",
    ):
        template = json.loads(
            (REPO_ROOT / "airlock" / "templates" / template_name).read_text(encoding="utf-8")
        )
        date_columns = [
            column
            for column in template["column_config"]
            if column.get("type") in {"date", "datetime"}
        ]

        assert date_columns
        for column in date_columns:
            assert column["description"]
            assert isinstance(column["tests"], list)
            assert column["format"].startswith("%")
            assert "YYYY" not in column["format"]


def test_coco_install_docs_name_airlock_folder() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    combined_docs = (REPO_ROOT / "docs" / "airlock-skills.md").read_text(encoding="utf-8")
    release_process = (REPO_ROOT / "docs" / "release_process.md").read_text(encoding="utf-8")

    for text in (readme, combined_docs, release_process):
        assert "scripts/package_coco_skill.py" in text
        assert ".snowflake/cortex/skills/airlock" in text


def test_package_coco_skill_does_not_zip_itself(tmp_path: Path) -> None:
    output_dir = tmp_path / "coco"
    zip_path = output_dir / "airlock" / "airlock.zip"

    subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "package_coco_skill.py"),
            "--output-dir",
            str(output_dir),
            "--zip-path",
            str(zip_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())

    assert "airlock/SKILL.md" in names
    assert "airlock/airlock.zip" not in names
