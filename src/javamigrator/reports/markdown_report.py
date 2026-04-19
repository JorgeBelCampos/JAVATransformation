from __future__ import annotations

from pathlib import Path

from javamigrator.analysis.build_error_analysis import BuildErrorFinding
from javamigrator.analysis.build_validation import BuildValidationResult
from javamigrator.analysis.code_analysis import ImportFinding
from javamigrator.analysis.dependency_analysis import DependencyFinding
from javamigrator.analysis.fix_prioritization import FixCandidate
from javamigrator.analysis.migration_strategy import MigrationStrategy
from javamigrator.analysis.summary import ExecutiveSummary
from javamigrator.analysis.verification import VerificationSummary


def generate_markdown_report(
    project_path: str,
    build_tool: str,
    detected_java_version: str | None,
    target_java_version: int | None,
    compatibility_messages: list[str],
    code_findings: list[ImportFinding],
    dependency_findings: list[DependencyFinding],
    executive_summary: ExecutiveSummary,
    migration_strategy: MigrationStrategy,
    top_fix_candidates: list[FixCandidate],
    verification_summary: VerificationSummary | None = None,
    build_validation: BuildValidationResult | None = None,
    build_error_findings: list[BuildErrorFinding] | None = None,
) -> str:
    """Generate a Markdown report for Java migration analysis."""
    lines: list[str] = []

    lines.append("# Java Migration Analysis Report")
    lines.append("")

    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- **Migration complexity:** {executive_summary.migration_complexity}")
    lines.append(f"- **Total code findings:** {executive_summary.total_findings}")
    lines.append(f"- **Affected files:** {executive_summary.affected_files}")
    lines.append(f"- **Dependency findings:** {len(dependency_findings)}")
    lines.append("")

    if executive_summary.category_summaries:
        lines.append("### Categories")
        lines.append("")
        for category_summary in executive_summary.category_summaries:
            lines.append(
                f"- **{category_summary.category}** "
                f"({category_summary.severity}) - "
                f"{category_summary.count} findings in {category_summary.affected_files} files"
            )
        lines.append("")

    if executive_summary.top_affected_files:
        lines.append("### Top Affected Files")
        lines.append("")
        for file_path, count in executive_summary.top_affected_files:
            lines.append(f"- `{file_path}` - {count} findings")
        lines.append("")

    lines.append("## Migration Strategy")
    lines.append("")
    lines.append(
        f"- **Java upgrade required:** {'YES' if migration_strategy.java_upgrade_required else 'NO'}"
    )
    lines.append(f"- **Jakarta migration:** {migration_strategy.jakarta_migration}")
    lines.append(f"- **XML impact:** {migration_strategy.xml_impact}")
    lines.append(f"- **Internal API risk:** {migration_strategy.internal_api_risk}")
    lines.append(f"- **Estimated effort:** {migration_strategy.estimated_effort}")
    lines.append("")

    lines.append("### Suggested Plan")
    lines.append("")
    for idx, step in enumerate(migration_strategy.suggested_plan, start=1):
        lines.append(f"{idx}. {step}")
    lines.append("")

    lines.append("## Top Fix Candidates")
    lines.append("")
    if top_fix_candidates:
        for idx, fix in enumerate(top_fix_candidates, start=1):
            lines.append(f"### {idx}. {fix.title}")
            lines.append("")
            lines.append(f"- **Category:** {fix.category}")
            lines.append(f"- **Impact:** {fix.impact}")
            lines.append(f"- **Effort:** {fix.effort}")
            lines.append(f"- **Affected files:** {fix.affected_files}")
            lines.append(f"- **Occurrences:** {fix.occurrences}")
            lines.append(f"- **Reason:** {fix.reason}")
            lines.append(f"- **Recommendation:** {fix.recommendation}")
            lines.append("")
    else:
        lines.append("No prioritized fixes generated.")
        lines.append("")

    if verification_summary is not None:
        lines.append("## Verification Summary")
        lines.append("")
        lines.append(
            f"- **Code findings:** {verification_summary.original_code_findings} -> {verification_summary.fixed_code_findings}"
        )
        lines.append(
            f"- **Dependency findings:** {verification_summary.original_dependency_findings} -> {verification_summary.fixed_dependency_findings}"
        )
        lines.append(
            f"- **Servlet code findings:** {verification_summary.original_servlet_findings} -> {verification_summary.fixed_servlet_findings}"
        )
        lines.append(
            f"- **Servlet dependency findings:** {verification_summary.original_servlet_dependencies} -> {verification_summary.fixed_servlet_dependencies}"
        )
        lines.append("")

    if build_validation is not None:
        lines.append("## Build Validation")
        lines.append("")
        lines.append(f"- **Attempted:** {'YES' if build_validation.attempted else 'NO'}")
        lines.append(f"- **Succeeded:** {'YES' if build_validation.succeeded else 'NO'}")
        lines.append(f"- **Tool:** {build_validation.tool}")
        lines.append(f"- **Working directory:** `{build_validation.working_directory}`")
        if build_validation.command:
            lines.append(f"- **Command:** `{' '.join(build_validation.command)}`")
        if build_validation.return_code is not None:
            lines.append(f"- **Return code:** {build_validation.return_code}")
        lines.append("")

    if build_error_findings:
        lines.append("## Build Error Findings")
        lines.append("")
        for finding in build_error_findings[:50]:
            lines.append(f"### [{finding.severity}] {finding.category}")
            lines.append("")
            lines.append(f"- **Message:** {finding.message}")
            if finding.file_path:
                lines.append(f"- **File:** `{finding.file_path}`")
            if finding.line_number is not None:
                lines.append(f"- **Line:** {finding.line_number}")
            if finding.raw_line:
                lines.append(f"- **Raw:** `{finding.raw_line}`")
            lines.append("")

    lines.append("## Project")
    lines.append("")
    lines.append(f"- **Path:** `{project_path}`")
    lines.append(f"- **Build tool:** `{build_tool}`")
    lines.append(f"- **Detected Java version:** `{detected_java_version or 'not detected'}`")
    lines.append(f"- **Target Java version:** `{target_java_version if target_java_version is not None else 'not specified'}`")
    lines.append("")

    lines.append("## Compatibility Summary")
    lines.append("")
    if compatibility_messages:
        for message in compatibility_messages:
            lines.append(f"- {message}")
    else:
        lines.append("- No compatibility observations found.")
    lines.append("")

    lines.append("## Dependency Findings")
    lines.append("")
    if dependency_findings:
        high_count = sum(1 for finding in dependency_findings if finding.severity == "HIGH")
        medium_count = sum(1 for finding in dependency_findings if finding.severity == "MEDIUM")
        info_count = sum(1 for finding in dependency_findings if finding.severity == "INFO")

        lines.append(f"- **Total dependency findings:** {len(dependency_findings)}")
        lines.append(f"- **HIGH:** {high_count}")
        lines.append(f"- **MEDIUM:** {medium_count}")
        lines.append(f"- **INFO:** {info_count}")
        lines.append("")

        for finding in dependency_findings:
            lines.append(f"### [{finding.severity}] {finding.message}")
            lines.append("")
            lines.append(f"- **Group ID:** `{finding.group_id}`")
            lines.append(f"- **Artifact ID:** `{finding.artifact_id}`")
            lines.append(f"- **Version:** `{finding.version or 'not specified'}`")
            lines.append("")
    else:
        lines.append("No problematic dependencies detected.")
        lines.append("")

    lines.append("## Recommendations by Category")
    lines.append("")
    if executive_summary.category_summaries:
        for category_summary in executive_summary.category_summaries:
            lines.append(f"### {category_summary.category}")
            lines.append("")
            lines.append(f"- **Severity:** {category_summary.severity}")
            lines.append(f"- **Findings:** {category_summary.count}")
            lines.append(f"- **Affected files:** {category_summary.affected_files}")
            lines.append(f"- **Recommendation:** {category_summary.recommendation}")
            lines.append("")
    else:
        lines.append("No category recommendations available.")
        lines.append("")

    lines.append("## Code Findings Summary")
    lines.append("")
    if code_findings:
        total_findings = len(code_findings)
        affected_files = len({finding.file_path for finding in code_findings})
        high_count = sum(1 for finding in code_findings if finding.severity == "HIGH")
        medium_count = sum(1 for finding in code_findings if finding.severity == "MEDIUM")
        info_count = sum(1 for finding in code_findings if finding.severity == "INFO")

        lines.append(f"- **Total findings:** {total_findings}")
        lines.append(f"- **Affected files:** {affected_files}")
        lines.append(f"- **HIGH:** {high_count}")
        lines.append(f"- **MEDIUM:** {medium_count}")
        lines.append(f"- **INFO:** {info_count}")
    else:
        lines.append("- No problematic imports detected.")
    lines.append("")

    lines.append("## Detailed Findings")
    lines.append("")
    if code_findings:
        for finding in code_findings:
            lines.append(f"### [{finding.severity}] {finding.message}")
            lines.append("")
            lines.append(f"- **File:** `{finding.file_path}`")
            lines.append(f"- **Line:** {finding.line_number}")
            lines.append(f"- **Import:** `{finding.import_value}`")
            lines.append("")
    else:
        lines.append("No detailed findings.")
        lines.append("")

    return "\n".join(lines)


def write_markdown_report(report_content: str, output_path: str | Path) -> None:
    """Write the Markdown report to disk."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(report_content, encoding="utf-8")