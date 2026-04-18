from __future__ import annotations

from dataclasses import dataclass

from javamigrator.analysis.code_analysis import ImportFinding
from javamigrator.analysis.dependency_analysis import DependencyFinding


@dataclass
class FixCandidate:
    title: str
    category: str
    impact: str
    effort: str
    reason: str
    affected_files: int
    occurrences: int
    recommendation: str


def generate_top_fix_candidates(
    code_findings: list[ImportFinding],
    dependency_findings: list[DependencyFinding],
) -> list[FixCandidate]:
    """Generate prioritized fix candidates from code and dependency findings."""
    candidates: list[FixCandidate] = []

    # 1. Internal APIs
    internal_api_findings = [
        finding
        for finding in code_findings
        if finding.import_value.startswith("com.sun.") or finding.import_value.startswith("sun.")
    ]
    if internal_api_findings:
        candidates.append(
            FixCandidate(
                title="Replace internal JDK API usages",
                category="internal_api",
                impact="HIGH",
                effort="LOW",
                reason="Internal or vendor-specific APIs are risky on newer Java versions and can break at runtime.",
                affected_files=len({finding.file_path for finding in internal_api_findings}),
                occurrences=len(internal_api_findings),
                recommendation="Replace com.sun.* / sun.* usages with supported public APIs before final migration validation.",
            )
        )

    # 2. Servlet migration in code
    servlet_code_findings = [
        finding
        for finding in code_findings
        if "javax.servlet" in finding.import_value
    ]
    if servlet_code_findings:
        candidates.append(
            FixCandidate(
                title="Plan javax.servlet to jakarta.servlet migration",
                category="servlet_migration",
                impact="VERY_HIGH",
                effort="MEDIUM",
                reason="Servlet APIs appear in code and are a common blocker for modern Jakarta-based runtimes.",
                affected_files=len({finding.file_path for finding in servlet_code_findings}),
                occurrences=len(servlet_code_findings),
                recommendation="If targeting Tomcat 10+ or Jakarta EE, migrate javax.servlet imports and dependencies to jakarta.servlet.",
            )
        )

    # 3. Servlet dependencies
    servlet_dependency_findings = [
        finding
        for finding in dependency_findings
        if "servlet" in finding.artifact_id.lower() or "servlet" in finding.group_id.lower()
    ]
    if servlet_dependency_findings:
        candidates.append(
            FixCandidate(
                title="Upgrade legacy servlet dependencies",
                category="dependency_upgrade",
                impact="HIGH",
                effort="LOW",
                reason="Old servlet dependencies may block runtime modernization or container upgrades.",
                affected_files=0,
                occurrences=len(servlet_dependency_findings),
                recommendation="Review and replace old servlet artifacts such as servlet-api 2.5 / javax.servlet-api 3.x according to target container.",
            )
        )

    # 4. General javax review
    general_javax_findings = [
        finding
        for finding in code_findings
        if finding.message == "javax.* usage detected; review whether migration is required"
    ]
    if general_javax_findings:
        candidates.append(
            FixCandidate(
                title="Review general javax usage",
                category="general_javax",
                impact="MEDIUM",
                effort="HIGH",
                reason="There is broad javax usage across the codebase, but not all of it requires migration.",
                affected_files=len({finding.file_path for finding in general_javax_findings}),
                occurrences=len(general_javax_findings),
                recommendation="Classify javax usages into Java SE, external libs, and Jakarta migration candidates before planning large-scale code changes.",
            )
        )

    priority_order = {
        "VERY_HIGH": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    }

    candidates.sort(
        key=lambda candidate: (
            -priority_order.get(candidate.impact, 0),
            -candidate.occurrences,
        )
    )

    return candidates