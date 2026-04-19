from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from javamigrator.detectors.dependencies import MAVEN_NS, MavenDependency


PROPERTY_REF_PATTERN = re.compile(r"^\$\{(.+)\}$")
LEGACY_JAVA_VERSION_PATTERN = re.compile(r"^(?:1\.)?(?P<major>\d+)$")


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
    """Analyze Maven dependencies and compiler configuration for likely migration concerns."""
    findings: list[DependencyFinding] = []

    for dep in dependencies:
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
                    message="JAXB-related dependency detected; explicit dependency management is required on Java 11+",
                    group_id=dep.group_id,
                    artifact_id=dep.artifact_id,
                    version=dep.version,
                )
            )

        if dep.group_id.startswith("javax.xml.ws") or dep.group_id.startswith("javax.jws") or "jaxws" in dep.artifact_id.lower():
            findings.append(
                DependencyFinding(
                    severity="HIGH",
                    message="JAX-WS-related dependency detected; explicit SOAP stack dependencies are required on Java 11+",
                    group_id=dep.group_id,
                    artifact_id=dep.artifact_id,
                    version=dep.version,
                )
            )

        if dep.group_id.startswith("javax.activation") or (
            dep.group_id.startswith("com.sun.activation") and "activation" in dep.artifact_id.lower()
        ):
            findings.append(
                DependencyFinding(
                    severity="HIGH",
                    message="javax.activation dependency detected; verify explicit activation API/runtime support on Java 11+",
                    group_id=dep.group_id,
                    artifact_id=dep.artifact_id,
                    version=dep.version,
                )
            )

        if dep.group_id.startswith("javax.json") or "javax.json" in dep.artifact_id.lower():
            findings.append(
                DependencyFinding(
                    severity="MEDIUM",
                    message="Legacy javax.json dependency detected; review explicit dependency management or jakarta.json migration",
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

        if dep.group_id.startswith(("com.sun", "sun", "jdk.internal")):
            findings.append(
                DependencyFinding(
                    severity="HIGH",
                    message="Internal or vendor-specific dependency detected; verify compatibility on newer Java versions",
                    group_id=dep.group_id,
                    artifact_id=dep.artifact_id,
                    version=dep.version,
                )
            )

        if dep.version is not None and dep.version.lower() in {"1.0", "1.1", "1.2"}:
            findings.append(
                DependencyFinding(
                    severity="MEDIUM",
                    message="Very old dependency version detected; compatibility review recommended",
                    group_id=dep.group_id,
                    artifact_id=dep.artifact_id,
                    version=dep.version,
                )
            )

    source_poms = sorted({dep.source_pom for dep in dependencies if dep.source_pom})
    for pom_path in source_poms:
        findings.extend(_analyze_compiler_configuration(Path(pom_path)))

    return _deduplicate_dependency_findings(findings)


def _analyze_compiler_configuration(pom_path: Path) -> list[DependencyFinding]:
    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()
    except (ET.ParseError, OSError):
        return []

    findings: list[DependencyFinding] = []
    properties_map = _extract_properties(root)

    for property_name in (
        "maven.compiler.source",
        "maven.compiler.target",
        "maven.compiler.release",
        "java.version",
        "jdk.version",
        "java.target.version",
    ):
        resolved_value = _resolve_property_value(properties_map.get(property_name), properties_map)
        if _is_legacy_java_level(resolved_value):
            findings.append(
                DependencyFinding(
                    severity="HIGH",
                    message=f"Legacy Java compiler property detected ({property_name}={resolved_value}); newer JDKs may fail to compile",
                    group_id="maven-compiler-plugin",
                    artifact_id=property_name,
                    version=resolved_value,
                )
            )

    for plugin in root.findall(".//m:plugin", MAVEN_NS):
        artifact_id = _get_child_text(plugin, "artifactId")
        if artifact_id != "maven-compiler-plugin":
            continue

        configuration = plugin.find("m:configuration", MAVEN_NS)
        if configuration is None:
            continue

        for tag_name in ("source", "target", "release"):
            element = configuration.find(f"m:{tag_name}", MAVEN_NS)
            if element is None or not element.text:
                continue

            resolved_value = _resolve_property_value(element.text.strip(), properties_map)
            if not _is_legacy_java_level(resolved_value):
                continue

            findings.append(
                DependencyFinding(
                    severity="HIGH",
                    message=f"Legacy Maven compiler configuration detected ({tag_name}={resolved_value}); newer JDKs may fail to compile",
                    group_id="org.apache.maven.plugins",
                    artifact_id="maven-compiler-plugin",
                    version=resolved_value,
                )
            )

    return findings


def _extract_properties(root: ET.Element) -> dict[str, str]:
    properties_map: dict[str, str] = {}
    properties = root.find("m:properties", MAVEN_NS)
    if properties is None:
        return properties_map

    for child in properties:
        tag_name = child.tag.split("}", 1)[-1]
        if child.text:
            properties_map[tag_name] = child.text.strip()

    return properties_map


def _resolve_property_value(value: str | None, properties_map: dict[str, str]) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    match = PROPERTY_REF_PATTERN.match(normalized)
    if not match:
        return normalized

    return properties_map.get(match.group(1), normalized)


def _get_child_text(element: ET.Element, child_name: str) -> str | None:
    child = element.find(f"m:{child_name}", MAVEN_NS)
    if child is not None and child.text:
        return child.text.strip()
    return None


def _is_legacy_java_level(value: str | None) -> bool:
    if value is None:
        return False
    match = LEGACY_JAVA_VERSION_PATTERN.match(value.strip())
    if not match:
        return False
    return int(match.group("major")) < 8


def _deduplicate_dependency_findings(
    findings: list[DependencyFinding],
) -> list[DependencyFinding]:
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
