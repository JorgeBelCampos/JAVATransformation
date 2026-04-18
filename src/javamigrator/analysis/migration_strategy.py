from __future__ import annotations

from dataclasses import dataclass

from javamigrator.analysis.summary import ExecutiveSummary


@dataclass
class MigrationStrategy:
    java_upgrade_required: bool
    jakarta_migration: str
    xml_impact: str
    internal_api_risk: str
    estimated_effort: str
    suggested_plan: list[str]


def build_migration_strategy(
    detected_java_version: str | None,
    target_java_version: int | None,
    executive_summary: ExecutiveSummary,
) -> MigrationStrategy:
    """Build a high-level migration strategy from executive summary data."""
    categories = {category.category: category for category in executive_summary.category_summaries}

    java_upgrade_required = False
    if detected_java_version is not None and target_java_version is not None:
        normalized = _normalize_java_version(detected_java_version)
        if normalized is not None and normalized < target_java_version:
            java_upgrade_required = True

    if "Jakarta Servlet Migration" in categories:
        jakarta_migration = "CONDITIONAL"
    else:
        jakarta_migration = "NOT REQUIRED"

    xml_related_categories = {"JAXB Removal", "JAX-WS Removal", "General javax Review"}
    xml_hits = sum(
        category.count
        for category in executive_summary.category_summaries
        if category.category in xml_related_categories
    )
    if xml_hits >= 50:
        xml_impact = "HIGH"
    elif xml_hits > 0:
        xml_impact = "MEDIUM"
    else:
        xml_impact = "LOW"

    if "Internal JDK APIs" in categories:
        internal_api_risk = "HIGH"
    else:
        internal_api_risk = "LOW"

    estimated_effort = _estimate_effort(executive_summary)

    suggested_plan = _build_suggested_plan(
        java_upgrade_required=java_upgrade_required,
        jakarta_migration=jakarta_migration,
        xml_impact=xml_impact,
        internal_api_risk=internal_api_risk,
    )

    return MigrationStrategy(
        java_upgrade_required=java_upgrade_required,
        jakarta_migration=jakarta_migration,
        xml_impact=xml_impact,
        internal_api_risk=internal_api_risk,
        estimated_effort=estimated_effort,
        suggested_plan=suggested_plan,
    )


def _normalize_java_version(version: str) -> int | None:
    """Normalize Java version string like 1.8 -> 8, 17 -> 17."""
    version = version.strip()

    if version.startswith("${") and version.endswith("}"):
        return None

    if version.startswith("1."):
        try:
            return int(version.split(".")[1])
        except (IndexError, ValueError):
            return None

    try:
        return int(version)
    except ValueError:
        return None


def _estimate_effort(executive_summary: ExecutiveSummary) -> str:
    """Estimate overall migration effort."""
    if executive_summary.migration_complexity == "HIGH":
        return "HIGH"

    has_high_category = any(
        category.severity == "HIGH" for category in executive_summary.category_summaries
    )
    if has_high_category:
        return "MEDIUM"

    return "LOW"


def _build_suggested_plan(
    java_upgrade_required: bool,
    jakarta_migration: str,
    xml_impact: str,
    internal_api_risk: str,
) -> list[str]:
    """Build a suggested step-by-step migration plan."""
    plan: list[str] = []

    if java_upgrade_required:
        plan.append("Upgrade the build configuration and runtime baseline to the target Java version.")

    if xml_impact in {"MEDIUM", "HIGH"}:
        plan.append("Review XML-related APIs and add explicit dependencies where JDK-bundled components were removed.")

    if jakarta_migration == "CONDITIONAL":
        plan.append("Evaluate the target servlet container and decide whether javax.servlet must be migrated to jakarta.servlet.")

    if internal_api_risk == "HIGH":
        plan.append("Replace internal JDK API usages with supported public alternatives before final upgrade validation.")

    plan.append("Run compilation, tests, and smoke validation on the upgraded target runtime.")

    return plan