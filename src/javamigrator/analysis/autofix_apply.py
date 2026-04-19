from __future__ import annotations

import os
import shutil
import stat
from datetime import datetime
from pathlib import Path
from typing import List

from javamigrator.analysis.autofix import AutoFixSuggestion


def _handle_remove_readonly(func, path, exc_info) -> None:
    """Handle Windows readonly files when deleting directories."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except OSError:
        pass


def _ignore_copy_patterns(directory: str, names: list[str]) -> set[str]:
    """Ignore folders/files that should not be copied to the fixed project."""
    ignored: set[str] = set()

    for name in names:
        if name in {
            ".git",
            ".idea",
            ".vs",
            ".vscode",
            "__pycache__",
            "target",
            "bin",
            "out",
            ".mvn",
            ".gradle",
            "node_modules",
        }:
            ignored.add(name)

        if name.endswith((".class", ".jar", ".war", ".zip", ".log")):
            ignored.add(name)

    return ignored


def _build_unique_output_path(base_output_path: str) -> Path:
    """Create a unique timestamped output path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = Path(base_output_path)
    return base.parent / f"{base.name}_{timestamp}"


def create_project_copy(source_path: str, output_path: str) -> Path:
    """Create a clean copy of the project to safely apply fixes."""
    src = Path(source_path).resolve()
    dst = _build_unique_output_path(output_path).resolve()

    print(f"[autofix] Creating project copy from: {src}")
    print(f"[autofix] Destination: {dst}")
    print("[autofix] Copying project files...")

    shutil.copytree(
        src,
        dst,
        ignore=_ignore_copy_patterns,
    )

    print("[autofix] Copy completed.")
    return dst


def apply_autofix_suggestions(
    project_path: str,
    suggestions: List[AutoFixSuggestion],
    output_path: str = "output/fixed_project",
) -> Path:
    """
    Apply autofix suggestions to a copy of the project.

    Returns the path to the modified project.
    """
    source_root = Path(project_path).resolve()
    fixed_project_path = create_project_copy(project_path, output_path)

    suggestions_by_file: dict[Path, list[AutoFixSuggestion]] = {}

    for suggestion in suggestions:
        original_file = Path(suggestion.file_path).resolve()

        try:
            relative_path = original_file.relative_to(source_root)
        except ValueError:
            continue

        target_file = fixed_project_path / relative_path
        suggestions_by_file.setdefault(target_file, []).append(suggestion)

    print(f"[autofix] Files with suggested changes: {len(suggestions_by_file)}")

    for index, (file_path, file_suggestions) in enumerate(suggestions_by_file.items(), start=1):
        if not file_path.exists():
            continue

        print(f"[autofix] Applying fixes to file {index}/{len(suggestions_by_file)}: {file_path}")

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = file_path.read_text(encoding="latin-1")

        for suggestion in file_suggestions:
            if suggestion.original in content:
                content = content.replace(
                    suggestion.original,
                    suggestion.replacement,
                )

        file_path.write_text(content, encoding="utf-8")

    print("[autofix] Autofix application completed.")
    return fixed_project_path