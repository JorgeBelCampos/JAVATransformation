from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileChange:
    file_path: str
    change_type: str
    details: str


def summarize_project_changes(
    original_project_path: str,
    fixed_project_path: str,
) -> list[FileChange]:
    """Compare original and fixed project trees and summarize relevant file changes."""
    original_root = Path(original_project_path).resolve()
    fixed_root = Path(fixed_project_path).resolve()

    changes: list[FileChange] = []

    fixed_files = [
        path for path in fixed_root.rglob("*")
        if path.is_file()
    ]

    for fixed_file in fixed_files:
        try:
            relative_path = fixed_file.relative_to(fixed_root)
        except ValueError:
            continue

        original_file = original_root / relative_path

        if not original_file.exists():
            changes.append(
                FileChange(
                    file_path=str(relative_path),
                    change_type="added",
                    details="File exists only in fixed project copy.",
                )
            )
            continue

        try:
            original_text = original_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            original_text = original_file.read_text(encoding="latin-1")

        try:
            fixed_text = fixed_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            fixed_text = fixed_file.read_text(encoding="latin-1")

        if original_text == fixed_text:
            continue

        change_type = _classify_change(relative_path, original_text, fixed_text)
        details = _build_short_change_summary(original_text, fixed_text)

        changes.append(
            FileChange(
                file_path=str(relative_path),
                change_type=change_type,
                details=details,
            )
        )

    return sorted(changes, key=lambda c: c.file_path.lower())


def generate_unified_diffs(
    original_project_path: str,
    fixed_project_path: str,
    max_files: int | None = None,
) -> dict[str, str]:
    """Generate unified diffs for changed text files."""
    original_root = Path(original_project_path).resolve()
    fixed_root = Path(fixed_project_path).resolve()

    diffs: dict[str, str] = {}
    processed = 0

    fixed_files = [
        path for path in fixed_root.rglob("*")
        if path.is_file()
    ]

    for fixed_file in fixed_files:
        if max_files is not None and processed >= max_files:
            break

        try:
            relative_path = fixed_file.relative_to(fixed_root)
        except ValueError:
            continue

        original_file = original_root / relative_path
        if not original_file.exists():
            continue

        try:
            original_text = original_file.read_text(encoding="utf-8")
            fixed_text = fixed_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                original_text = original_file.read_text(encoding="latin-1")
                fixed_text = fixed_file.read_text(encoding="latin-1")
            except UnicodeDecodeError:
                continue

        if original_text == fixed_text:
            continue

        diff_lines = difflib.unified_diff(
            original_text.splitlines(),
            fixed_text.splitlines(),
            fromfile=str(original_file),
            tofile=str(fixed_file),
            lineterm="",
        )

        diff_text = "\n".join(diff_lines).strip()
        if diff_text:
            diffs[str(relative_path)] = diff_text
            processed += 1

    return diffs


def write_change_summary(
    changes: list[FileChange],
    output_path: str,
) -> None:
    """Write a human-readable summary of project changes."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# Change Summary")
    lines.append("")
    lines.append(f"- Total changed files: {len(changes)}")
    lines.append("")

    if not changes:
        lines.append("No file changes detected.")
    else:
        grouped: dict[str, list[FileChange]] = {}
        for change in changes:
            grouped.setdefault(change.change_type, []).append(change)

        for change_type in sorted(grouped.keys()):
            lines.append(f"## {change_type.title()} changes")
            lines.append("")
            for change in grouped[change_type]:
                lines.append(f"- `{change.file_path}`")
                lines.append(f"  - {change.details}")
            lines.append("")

    output_file.write_text("\n".join(lines), encoding="utf-8")


def write_diff_report(
    diffs: dict[str, str],
    output_path: str,
) -> None:
    """Write unified diffs to a markdown file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# Unified Diff Report")
    lines.append("")

    if not diffs:
        lines.append("No diffs generated.")
    else:
        for file_path, diff_text in diffs.items():
            lines.append(f"## {file_path}")
            lines.append("")
            lines.append("```diff")
            lines.append(diff_text[:20000])
            lines.append("```")
            lines.append("")

    output_file.write_text("\n".join(lines), encoding="utf-8")


def _classify_change(relative_path: Path, original_text: str, fixed_text: str) -> str:
    file_name = relative_path.name.lower()

    if file_name == "pom.xml":
        return "pom_update"

    if ".java" in file_name:
        if "javax.servlet" in original_text and "jakarta.servlet" in fixed_text:
            return "jakarta_import_migration"
        return "java_code_update"

    return "text_update"


def _build_short_change_summary(original_text: str, fixed_text: str) -> str:
    original_lines = original_text.splitlines()
    fixed_lines = fixed_text.splitlines()

    diff_count = 0
    for line in difflib.ndiff(original_lines, fixed_lines):
        if line.startswith("+ ") or line.startswith("- "):
            diff_count += 1

    servlet_migrated = (
        "javax.servlet" in original_text and "jakarta.servlet" in fixed_text
    )

    if servlet_migrated:
        return f"Detected servlet migration changes; approx. {diff_count} changed lines."

    return f"Approx. {diff_count} changed lines."