from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from javamigrator.analysis.code_analysis import ImportFinding


@dataclass
class FindingCategorySummary:
    category: str
    severity: str
    count: int
    affected_files: int
    recommendation: str


@dataclass
class ExecutiveSummary:
    migration_complexity: str
    total_findings: int
    affected_files: int
    category_summaries: list[FindingCategorySummary]
    top_affected_files: list[tuple[str, int]]


def classify_finding_category(finding: ImportFinding) -> str:
    """Classify a finding into a higher-level migration category."""
    import_value = finding.import_value

    if import_value.startswith("javax.servlet."):
        return "Jakarta Servlet Migration"

    if import_value.startswith("javax.xml.bind.") or "xml.bind" in import_value:
        return "JAXB Removal"

    if import_value.startswith("javax.xml.ws.") or "xml.ws" in import_value or ".ws." in import_value:
        return "JAX-WS Removal"

    if import_value.startswith("javax.activation."):
        return "Activation Removal"

    if import_value.startswith("javax.json."):
        return "Legacy JSON API"

    if (
        import_value.startswith("java.lang.reflect.")
        or import_value == "java.lang.invoke.MethodHandles"
        or import_value.startswith("sun.reflect.")
        or import_value.startswith("jdk.internal.reflect.")
    ):
        return "Reflection Encapsulation Risks"

    if import_value.startswith("sun.") or import_value.startswith("com.sun.") or import_value.startswith("jdk.internal."):
        return "Internal JDK APIs"

    if import_value.startswith("javax."):
        return "General javax Review"

    return "Other"


def recommendation_for_category(category: str) -> str:
    """Return a default recommendation for a finding category."""
    recommendations = {
        "Jakarta Servlet Migration": (
            "If the target runtime is Tomcat 10+ or Jakarta EE, plan a javax.servlet -> jakarta.servlet migration. "
            "If staying on Tomcat 9 or equivalent, verify whether keeping javax.servlet is acceptable."
        ),
        "JAXB Removal": (
            "Add explicit JAXB dependencies and verify marshalling/unmarshalling flows on Java 11+."
        ),
        "JAX-WS Removal": (
            "Add explicit JAX-WS dependencies or replace legacy SOAP stack components where needed."
        ),
        "Activation Removal": (
            "Add an explicit activation dependency because javax.activation is no longer bundled in newer JDKs."
        ),
        "Legacy JSON API": (
            "Add explicit javax.json dependency first, then evaluate whether migration to jakarta.json is desirable."
        ),
        "Reflection Encapsulation Risks": (
            "Review reflective access patterns because Java 17+ strong encapsulation can require refactoring or --add-opens."
        ),
        "Internal JDK APIs": (
            "Replace internal JDK API usage with supported public alternatives as these are high-risk on newer Java versions."
        ),
        "General javax Review": (
            "Review whether these javax APIs belong to Java SE, legacy Java EE, or external libraries before planning migration changes."
        ),
        "Other": (
            "Review manually."
        ),
    }
    return recommendations.get(category, "Review manually.")


def calculate_migration_complexity(total_findings: int) -> str:
    """Estimate migration complexity based on total findings."""
    if total_findings >= 150:
        return "HIGH"
    if total_findings >= 50:
        return "MEDIUM"
    return "LOW"


def build_executive_summary(code_findings: list[ImportFinding]) -> ExecutiveSummary:
    """Build an executive summary from structured code findings."""
    total_findings = len(code_findings)
    affected_files = len({finding.file_path for finding in code_findings})

    category_counter: Counter[str] = Counter()
    category_files: dict[str, set[str]] = {}
    category_severity: dict[str, str] = {}
    file_counter: Counter[str] = Counter()

    severity_rank = {"HIGH": 3, "MEDIUM": 2, "INFO": 1}

    for finding in code_findings:
        category = classify_finding_category(finding)
        category_counter[category] += 1
        file_counter[finding.file_path] += 1

        if category not in category_files:
            category_files[category] = set()
        category_files[category].add(finding.file_path)

        current = category_severity.get(category)
        if current is None or severity_rank[finding.severity] > severity_rank[current]:
            category_severity[category] = finding.severity

    category_summaries: list[FindingCategorySummary] = []
    for category, count in category_counter.most_common():
        category_summaries.append(
            FindingCategorySummary(
                category=category,
                severity=category_severity[category],
                count=count,
                affected_files=len(category_files[category]),
                recommendation=recommendation_for_category(category),
            )
        )

    top_affected_files = file_counter.most_common(10)

    return ExecutiveSummary(
        migration_complexity=calculate_migration_complexity(total_findings),
        total_findings=total_findings,
        affected_files=affected_files,
        category_summaries=category_summaries,
        top_affected_files=top_affected_files,
    )
