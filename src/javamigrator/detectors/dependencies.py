from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


MAVEN_NS = {"m": "http://maven.apache.org/POM/4.0.0"}
PROPERTY_REF_PATTERN = re.compile(r"^\$\{(.+)\}$")


@dataclass
class MavenDependency:
    group_id: str
    artifact_id: str
    version: str | None
    scope: str | None = None
    source_pom: str | None = None


def detect_maven_dependencies(project_path: str | Path) -> list[MavenDependency]:
    """Detect Maven dependencies from all pom.xml files found in the project tree."""
    root = Path(project_path)

    if root.is_file():
        root = root.parent

    dependencies: list[MavenDependency] = []

    try:
        for pom_file in root.rglob("pom.xml"):
            dependencies.extend(_parse_dependencies_from_pom(pom_file))
    except OSError:
        return []

    return _deduplicate_dependencies(dependencies)


def _parse_dependencies_from_pom(pom_path: Path) -> list[MavenDependency]:
    """Parse dependencies from a Maven pom.xml."""
    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()
        properties_map = _extract_properties(root)

        dependencies: list[MavenDependency] = []

        # Dependencias normales
        dependency_elements = root.findall(".//m:dependencies/m:dependency", MAVEN_NS)

        for dep in dependency_elements:
            group_id = _get_child_text(dep, "groupId")
            artifact_id = _get_child_text(dep, "artifactId")
            version = _get_child_text(dep, "version")
            scope = _get_child_text(dep, "scope")

            if not group_id or not artifact_id:
                continue

            resolved_group_id = _resolve_property_reference(group_id, properties_map)
            resolved_artifact_id = _resolve_property_reference(artifact_id, properties_map)
            resolved_version = _resolve_property_reference(version, properties_map) if version else None
            resolved_scope = _resolve_property_reference(scope, properties_map) if scope else None

            dependencies.append(
                MavenDependency(
                    group_id=resolved_group_id,
                    artifact_id=resolved_artifact_id,
                    version=resolved_version,
                    scope=resolved_scope,
                    source_pom=str(pom_path),
                )
            )

        return dependencies

    except (ET.ParseError, OSError):
        return []


def _extract_properties(root: ET.Element) -> dict[str, str]:
    """Extract Maven properties into a dictionary."""
    properties_map: dict[str, str] = {}

    properties = root.find("m:properties", MAVEN_NS)
    if properties is None:
        return properties_map

    for child in properties:
        tag_name = child.tag.split("}", 1)[-1]
        if child.text:
            properties_map[tag_name] = child.text.strip()

    return properties_map


def _resolve_property_reference(value: str, properties_map: dict[str, str]) -> str:
    """Resolve simple Maven property references like ${my.version}."""
    value = value.strip()
    match = PROPERTY_REF_PATTERN.match(value)
    if not match:
        return value

    property_name = match.group(1)
    return properties_map.get(property_name, value)


def _get_child_text(element: ET.Element, child_name: str) -> str | None:
    """Get text of a child element using Maven namespace."""
    child = element.find(f"m:{child_name}", MAVEN_NS)
    if child is not None and child.text:
        return child.text.strip()
    return None


def _deduplicate_dependencies(dependencies: list[MavenDependency]) -> list[MavenDependency]:
    """Remove duplicate dependencies across multiple pom.xml files."""
    seen: set[tuple[str, str, str | None, str | None]] = set()
    unique: list[MavenDependency] = []

    for dep in dependencies:
        key = (dep.group_id, dep.artifact_id, dep.version, dep.scope)
        if key in seen:
            continue
        seen.add(key)
        unique.append(dep)

    return unique