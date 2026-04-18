from __future__ import annotations

from dataclasses import dataclass

from javamigrator.analysis.code_analysis import ImportFinding


@dataclass
class AutoFixSuggestion:
    file_path: str
    line_number: int
    original: str
    replacement: str
    reason: str
    confidence: str


def generate_autofix_suggestions(
    code_findings: list[ImportFinding],
) -> list[AutoFixSuggestion]:
    """Generate safe autofix suggestions for known migration patterns."""
    suggestions: list[AutoFixSuggestion] = []

    for finding in code_findings:
        import_value = finding.import_value

        # Safe first target: javax.servlet -> jakarta.servlet
        if import_value.startswith("javax.servlet."):
            suggestions.append(
                AutoFixSuggestion(
                    file_path=finding.file_path,
                    line_number=finding.line_number,
                    original=import_value,
                    replacement=import_value.replace("javax.servlet", "jakarta.servlet", 1),
                    reason="Servlet API migration candidate for Jakarta-based runtimes",
                    confidence="HIGH",
                )
            )

    return _deduplicate_suggestions(suggestions)


def _deduplicate_suggestions(
    suggestions: list[AutoFixSuggestion],
) -> list[AutoFixSuggestion]:
    """Remove duplicate autofix suggestions."""
    seen: set[tuple[str, int, str, str]] = set()
    unique: list[AutoFixSuggestion] = []

    for suggestion in suggestions:
        key = (
            suggestion.file_path,
            suggestion.line_number,
            suggestion.original,
            suggestion.replacement,
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(suggestion)

    return unique