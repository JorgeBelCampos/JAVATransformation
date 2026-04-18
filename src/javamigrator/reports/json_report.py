from __future__ import annotations

import json
from pathlib import Path

from javamigrator.analysis.autofix import AutoFixSuggestion
from javamigrator.analysis.code_analysis import ImportFinding
from javamigrator.analysis.dependency_analysis import DependencyFinding
from javamigrator.analysis.fix_prioritization import FixCandidate
from javamigrator.analysis.migration_strategy import MigrationStrategy
from javamigrator.analysis.summary import ExecutiveSummary


def generate_json_report(
    project_path: str,
    build_tool: str,
    detected_java_version: str | None,
    target_java_version: int | None,
    compatibility_messages: list[str],
    code_findings: list[ImportFinding],
    dependency_findings: list[DependencyFinding],
    executive_summary: ExecutiveSummary,
    migration_strategy: MigrationStrategy,
    architecture_insights: list[str],
    top_fix_candidates: list[FixCandidate],
    autofix_suggestions: list[AutoFixSuggestion],
) -> dict:
    """Generate a structured JSON report for Java migration analysis."""
    return {
        "project": {
            "path": project_path,
            "build_tool": build_tool,
            "detected_java_version": detected_java_version,
            "target_java_version": target_java_version,
        },
        "compatibility_summary": compatibility_messages,
        "executive_summary": {
            "migration_complexity": executive_summary.migration_complexity,
            "total_code_findings": executive_summary.total_findings,
            "affected_files": executive_summary.affected_files,
            "categories": [
                {
                    "category": category.category,
                    "severity": category.severity,
                    "count": category.count,
                    "affected_files": category.affected_files,
                    "recommendation": category.recommendation,
                }
                for category in executive_summary.category_summaries
            ],
            "top_affected_files": [
                {"file_path": file_path, "count": count}
                for file_path, count in executive_summary.top_affected_files
            ],
        },
        "migration_strategy": {
            "java_upgrade_required": migration_strategy.java_upgrade_required,
            "jakarta_migration": migration_strategy.jakarta_migration,
            "xml_impact": migration_strategy.xml_impact,
            "internal_api_risk": migration_strategy.internal_api_risk,
            "estimated_effort": migration_strategy.estimated_effort,
            "suggested_plan": migration_strategy.suggested_plan,
        },
        "architecture_insights": architecture_insights,
        "top_fix_candidates": [
            {
                "title": fix.title,
                "category": fix.category,
                "impact": fix.impact,
                "effort": fix.effort,
                "reason": fix.reason,
                "affected_files": fix.affected_files,
                "occurrences": fix.occurrences,
                "recommendation": fix.recommendation,
            }
            for fix in top_fix_candidates
        ],
        "dependency_findings": [
            {
                "severity": finding.severity,
                "message": finding.message,
                "group_id": finding.group_id,
                "artifact_id": finding.artifact_id,
                "version": finding.version,
            }
            for finding in dependency_findings
        ],
        "code_findings": [
            {
                "severity": finding.severity,
                "message": finding.message,
                "file_path": finding.file_path,
                "line_number": finding.line_number,
                "import_value": finding.import_value,
            }
            for finding in code_findings
        ],
        "autofix_suggestions": [
            {
                "file_path": suggestion.file_path,
                "line_number": suggestion.line_number,
                "original": suggestion.original,
                "replacement": suggestion.replacement,
                "reason": suggestion.reason,
                "confidence": suggestion.confidence,
            }
            for suggestion in autofix_suggestions
        ],
    }


def write_json_report(report_data: dict, output_path: str | Path) -> None:
    """Write JSON report to disk."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(report_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )