from pathlib import Path
import shutil
from typing import List

from javamigrator.analysis.autofix import AutoFixSuggestion


def create_project_copy(source_path: str, output_path: str) -> Path:
    """Create a copy of the project to safely apply fixes."""
    src = Path(source_path)
    dst = Path(output_path)

    if dst.exists():
        shutil.rmtree(dst)

    shutil.copytree(src, dst)
    return dst


def apply_autofix_suggestions(
    project_path: str,
    suggestions: List[AutoFixSuggestion],
    output_path: str = "output/fixed_project"
) -> Path:
    """
    Apply autofix suggestions to a copy of the project.

    Returns the path to the modified project.
    """

    # 1. Crear copia
    fixed_project_path = create_project_copy(project_path, output_path)

    # 2. Agrupar sugerencias por archivo
    suggestions_by_file = {}

    for s in suggestions:
        file_path = Path(s.file_path)
        relative_path = file_path.relative_to(project_path)
        target_file = fixed_project_path / relative_path

        suggestions_by_file.setdefault(target_file, []).append(s)

    # 3. Aplicar cambios archivo por archivo
    for file_path, file_suggestions in suggestions_by_file.items():
        if not file_path.exists():
            continue

        content = file_path.read_text(encoding="utf-8")

        for suggestion in file_suggestions:
            if suggestion.original in content:
                content = content.replace(
                    suggestion.original,
                    suggestion.replacement
                )

        file_path.write_text(content, encoding="utf-8")

    return fixed_project_path