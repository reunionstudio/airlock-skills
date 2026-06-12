#!/usr/bin/env python3
"""Package the Airlock skill as a CoCo-ready folder and zip."""

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "airlock"
INSTALL_SKILL_NAME = "airlock"
IGNORED_NAMES = {".DS_Store", "__pycache__"}


def _iter_skill_files(source_dir: Path) -> Iterable[tuple[Path, Path]]:
    for source_path in sorted(source_dir.rglob("*")):
        relative_path = source_path.relative_to(source_dir)
        if any(part in IGNORED_NAMES for part in relative_path.parts):
            continue
        if source_path.is_file():
            yield source_path, relative_path


def _validate_source_skill(source_dir: Path) -> None:
    skill_path = source_dir / "SKILL.md"
    if not skill_path.exists():
        raise SystemExit(f"Missing required source skill file: {skill_path}")

    content = skill_path.read_text(encoding="utf-8")
    if not content.startswith("---\n") or "\n---\n" not in content[4:]:
        raise SystemExit(f"Invalid skill frontmatter in: {skill_path}")

    frontmatter = content.split("---\n", 2)[1]
    if "name: airlock" not in frontmatter.splitlines():
        raise SystemExit("Source skill frontmatter must use `name: airlock`.")
    if "allowed-tools:" not in frontmatter.splitlines():
        raise SystemExit("Source skill frontmatter must use `allowed-tools:`.")


def _copy_skill(source_dir: Path, output_dir: Path) -> Path:
    target_dir = output_dir / INSTALL_SKILL_NAME
    resolved_source = source_dir.resolve()
    resolved_target = target_dir.resolve()
    if resolved_target == resolved_source or resolved_source in resolved_target.parents:
        raise SystemExit("Output target must not be inside the source skill directory.")

    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    for source_path, relative_path in _iter_skill_files(source_dir):
        target_path = target_dir / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)

    return target_dir


def _write_zip(target_dir: Path, zip_path: Path) -> Path:
    if zip_path.exists():
        zip_path.unlink()
    zip_path.parent.mkdir(parents=True, exist_ok=True)

    resolved_zip_path = zip_path.resolve()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source_path, relative_path in _iter_skill_files(target_dir):
            if source_path.resolve() == resolved_zip_path:
                continue
            archive.write(source_path, Path(target_dir.name) / relative_path)

    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a CoCo-ready Airlock skill package.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "dist" / "coco-skill",
        help="Directory that will receive the generated `airlock/` folder.",
    )
    parser.add_argument(
        "--zip-path",
        type=Path,
        help="Optional zip output path. Defaults to <output-dir>/airlock.zip.",
    )
    parser.add_argument(
        "--no-zip",
        action="store_true",
        help="Only create the `airlock/` folder; do not create a zip archive.",
    )
    args = parser.parse_args()

    source_dir = SOURCE_DIR
    output_dir = args.output_dir
    zip_path = args.zip_path or output_dir / f"{INSTALL_SKILL_NAME}.zip"

    _validate_source_skill(source_dir)
    target_dir = _copy_skill(source_dir, output_dir)
    print(f"Created CoCo skill folder: {target_dir}")

    if not args.no_zip:
        archive_path = _write_zip(target_dir, zip_path)
        print(f"Created CoCo skill zip: {archive_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
