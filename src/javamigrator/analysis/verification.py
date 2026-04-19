from __future__ import annotations

from dataclasses import dataclass

from javamigrator.analysis.code_analysis import ImportFinding
from javamigrator.analysis.dependency_analysis import DependencyFinding


@dataclass
class VerificationSummary:
    original_code_findings: int
    fixed_code_findings: int
    original_dependency_findings: int
    fixed_dependency_findings: int
    original_servlet_findings: int
    fixed_servlet_findings: int
    original_servlet_dependencies: int
    fixed_servlet_dependencies: int


def count_servlet_code_findings(findings: list[ImportFinding]) -> int:
    return sum(1 for f in findings if "javax.servlet" in f.import_value)


def count_servlet_dependency_findings(findings: list[DependencyFinding]) -> int:
    return sum(
        1
        for f in findings
        if "servlet" in f.artifact_id.lower() or "servlet" in f.group_id.lower()
    )


def build_verification_summary(
    original_code_findings: list[ImportFinding],
    fixed_code_findings: list[ImportFinding],
    original_dependency_findings: list[DependencyFinding],
    fixed_dependency_findings: list[DependencyFinding],
) -> VerificationSummary:
    return VerificationSummary(
        original_code_findings=len(original_code_findings),
        fixed_code_findings=len(fixed_code_findings),
        original_dependency_findings=len(original_dependency_findings),
        fixed_dependency_findings=len(fixed_dependency_findings),
        original_servlet_findings=count_servlet_code_findings(original_code_findings),
        fixed_servlet_findings=count_servlet_code_findings(fixed_code_findings),
        original_servlet_dependencies=count_servlet_dependency_findings(original_dependency_findings),
        fixed_servlet_dependencies=count_servlet_dependency_findings(fixed_dependency_findings),
    )