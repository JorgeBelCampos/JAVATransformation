from __future__ import annotations

from dataclasses import dataclass

from javamigrator.detectors.dependencies import MavenDependency


@dataclass
class DependencyFinding:
    severity: str
    message: str
    group_id: str
    artifact_id: str
    version: str | None


def analyze_problematic_dependencies(
    dependencies: list[MavenDependency],
) -> list[DependencyFinding]:
    """Analyze Maven dependencies for likely migration concerns."""
    findings: list[DependencyFinding] = []

    for dep in dependencies:
        gav = f"{dep.group_id}:{dep.artifact_id}"

        if dep.group_id.startswith("javax.servlet") or dep.artifact_id.startswith("javax.servlet"):
            findings.append(
                DependencyFinding(
                    severity="HIGH",
                    message="Legacy javax.servlet dependency detected; may require jakarta migration depending on target runtime",
                    group_id=dep.group_id,
                    artifact_id=dep.artifact_id,
                    version=dep.version,
                )
            )

        if dep.group_id.startswith("javax.xml.bind") or "jaxb" in dep.artifact_id.lower():
            findings.append(
                DependencyFinding(
                    severity="HIGH",
                    message="JAXB-related dependency detected; verify compatibility on Java 11+",
                    group_id=dep.group_id,
                    artifact_id=dep.artifact_id,
                    version=dep.version,
                )
            )

        if dep.group_id.startswith("javax.xml.ws") or "jaxws" in dep.artifact_id.lower():
            findings.append(
                DependencyFinding(
                    severity="HIGH",
                    message="JAX-WS-related dependency detected; verify compatibility on Java 11+",
                    group_id=dep.group_id,
                    artifact_id=dep.artifact_id,
                    version=dep.version,
                )
            )

        if dep.group_id.startswith("javax"):
            findings.append(
                DependencyFinding(
                    severity="MEDIUM",
                    message="Legacy javax dependency detected; review whether replacement or explicit dependency management is needed",
                    group_id=dep.group_id,
                    artifact_id=dep.artifact_id,
                    version=dep.version,
                )
            )

        if dep.group_id.startswith("com.sun") or dep.group_id.startswith("sun"):
            findings.append(
                DependencyFinding(
                    severity="HIGH",
                    message="Internal or vendor-specific dependency detected; verify compatibility on newer Java versions",
                    group_id=dep.group_id,
                    artifact_id=dep.artifact_id,
                    version=dep.version,
                )
            )

        if dep.version is not None:
            version_lower = dep.version.lower()

            if version_lower in {"1.0", "1.1", "1.2"}:
                findings.append(
                    DependencyFinding(
                        severity="MEDIUM",
                        message="Very old dependency version detected; compatibility review recommended",
                        group_id=dep.group_id,
                        artifact_id=dep.artifact_id,
                        version=dep.version,
                    )
                )

    return _deduplicate_dependency_findings(findings)


def _deduplicate_dependency_findings(
    findings: list[DependencyFinding],
) -> list[DependencyFinding]:
    """Remove duplicate dependency findings."""
    seen: set[tuple[str, str, str, str | None]] = set()
    unique: list[DependencyFinding] = []

    for finding in findings:
        key = (
            finding.message,
            finding.group_id,
            finding.artifact_id,
            finding.version,
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(finding)

    return unique