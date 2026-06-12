from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_canonical_skill_folder_is_airlock() -> None:
    assert (REPO_ROOT / "airlock" / "SKILL.md").is_file()
    assert not (REPO_ROOT / "airlock_skills").exists()


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
