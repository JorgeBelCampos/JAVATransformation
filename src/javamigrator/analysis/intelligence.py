from __future__ import annotations

from javamigrator.analysis.code_analysis import ImportFinding
from javamigrator.analysis.dependency_analysis import DependencyFinding


def generate_architecture_insights(
    code_findings: list[ImportFinding],
    dependency_findings: list[DependencyFinding],
    detected_java_version: str | None,
    target_java_version: int | None,
) -> list[str]:
    """Generate high-level architecture insights from combined analysis."""

    insights: list[str] = []

    # 🔥 Detect servlet usage in code
    servlet_code = any("javax.servlet" in f.import_value for f in code_findings)

    # 🔥 Detect servlet in dependencies
    servlet_dep = any(
        "servlet" in f.artifact_id.lower() for f in dependency_findings
    )

    if servlet_code and servlet_dep:
        insights.append(
            "Project uses javax.servlet both in code and dependencies → Jakarta migration likely required for modern runtimes"
        )

    # 🔥 Detect legacy Java + XML heavy
    xml_usage = any("javax.xml" in f.import_value for f in code_findings)

    if detected_java_version and detected_java_version.startswith("1."):
        insights.append(
            "Legacy Java version detected with XML-heavy usage → High migration complexity expected"
        )

    # 🔥 Detect very old dependencies
    old_deps = any(
        f.version is not None and f.version in {"1.0", "1.1", "2.0", "2.5"}
        for f in dependency_findings
    )

    if old_deps:
        insights.append(
            "Very old dependencies detected → Dependency upgrade required before or during migration"
        )

    # 🔥 Detect mismatch strategy
    if detected_java_version and target_java_version:
        if detected_java_version.startswith("1.") and target_java_version >= 17:
            insights.append(
                "Large Java version jump detected → Incremental upgrade path recommended (8 → 11 → 17)"
            )

    return insights