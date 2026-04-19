from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path


MAVEN_NS = {"m": "http://maven.apache.org/POM/4.0.0"}
MAVEN_NAMESPACE_URI = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", MAVEN_NAMESPACE_URI)

LEGACY_JAVA_VERSION_PATTERN = re.compile(r"^(?:1\.)?(?P<major>\d+)$")
PROPERTY_REF_PATTERN = re.compile(r"^\$\{(?P<name>[^}]+)\}$")
MINIMUM_SUPPORTED_JAVA_LEVEL = "1.8"


def apply_pom_autofix(project_path: str) -> list[str]:
    """Apply safe pom.xml dependency and compiler upgrades inside a project copy.

    Returns a list of human-readable change messages.
    """
    root = Path(project_path)
    changes: list[str] = []

    for pom_file in root.rglob("pom.xml"):
        file_changes = _fix_single_pom(pom_file)
        changes.extend(file_changes)

    return changes


def _fix_single_pom(pom_path: Path) -> list[str]:
    changes: list[str] = []

    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()
    except (ET.ParseError, OSError):
        return changes

    modified = False

    if _fix_legacy_servlet_dependencies(root, pom_path, changes):
        modified = True

    if _fix_compiler_properties(root, pom_path, changes):
        modified = True

    if _fix_compiler_plugin_configurations(root, pom_path, changes):
        modified = True

    if modified:
        tree.write(pom_path, encoding="utf-8", xml_declaration=True)

    return changes


def _fix_legacy_servlet_dependencies(
    root: ET.Element,
    pom_path: Path,
    changes: list[str],
) -> bool:
    dependency_elements = root.findall(".//m:dependencies/m:dependency", MAVEN_NS)
    modified = False

    for dep in dependency_elements:
        group_id_elem = dep.find("m:groupId", MAVEN_NS)
        artifact_id_elem = dep.find("m:artifactId", MAVEN_NS)
        version_elem = dep.find("m:version", MAVEN_NS)
        scope_elem = dep.find("m:scope", MAVEN_NS)

        if group_id_elem is None or artifact_id_elem is None:
            continue

        group_id = (group_id_elem.text or "").strip()
        artifact_id = (artifact_id_elem.text or "").strip()

        if group_id == "javax.servlet" and artifact_id in {"javax.servlet-api", "servlet-api"}:
            old = (
                f"{group_id}:{artifact_id}:"
                f"{version_elem.text.strip() if version_elem is not None and version_elem.text else 'no-version'}"
            )

            group_id_elem.text = "jakarta.servlet"
            artifact_id_elem.text = "jakarta.servlet-api"

            if version_elem is None:
                version_elem = ET.SubElement(dep, _tag("version"))
            version_elem.text = "5.0.0"

            if scope_elem is None:
                scope_elem = ET.SubElement(dep, _tag("scope"))
            scope_elem.text = "provided"

            new = "jakarta.servlet:jakarta.servlet-api:5.0.0"
            changes.append(f"{pom_path}: {old} -> {new}")
            modified = True

    return modified


def _fix_compiler_properties(
    root: ET.Element,
    pom_path: Path,
    changes: list[str],
) -> bool:
    properties = root.find("m:properties", MAVEN_NS)
    if properties is None:
        return False

    modified = False
    property_names = {
        "maven.compiler.source",
        "maven.compiler.target",
        "maven.compiler.release",
        "java.version",
        "jdk.version",
        "java.target.version",
    }

    for child in properties:
        tag_name = child.tag.split("}", 1)[-1]
        if tag_name not in property_names or not child.text:
            continue

        current_value = child.text.strip()
        if not _needs_java_level_upgrade(current_value):
            continue

        child.text = MINIMUM_SUPPORTED_JAVA_LEVEL
        changes.append(
            f"{pom_path}: property {tag_name} {current_value} -> {MINIMUM_SUPPORTED_JAVA_LEVEL}"
        )
        modified = True

    return modified


def _fix_compiler_plugin_configurations(
    root: ET.Element,
    pom_path: Path,
    changes: list[str],
) -> bool:
    modified = False

    for plugin in root.findall(".//m:plugin", MAVEN_NS):
        artifact_id = plugin.find("m:artifactId", MAVEN_NS)
        if artifact_id is None or (artifact_id.text or "").strip() != "maven-compiler-plugin":
            continue

        configuration = plugin.find("m:configuration", MAVEN_NS)
        if configuration is None:
            continue

        for tag_name in ("source", "target", "release"):
            elem = configuration.find(f"m:{tag_name}", MAVEN_NS)
            if elem is None or not elem.text:
                continue

            current_value = elem.text.strip()
            if PROPERTY_REF_PATTERN.match(current_value):
                continue
            if not _needs_java_level_upgrade(current_value):
                continue

            elem.text = MINIMUM_SUPPORTED_JAVA_LEVEL
            changes.append(
                f"{pom_path}: maven-compiler-plugin {tag_name} {current_value} -> {MINIMUM_SUPPORTED_JAVA_LEVEL}"
            )
            modified = True

    return modified


def _needs_java_level_upgrade(value: str) -> bool:
    normalized = value.strip()
    match = LEGACY_JAVA_VERSION_PATTERN.match(normalized)
    if not match:
        return False

    major = int(match.group("major"))
    return major < 8


def _tag(local_name: str) -> str:
    return f"{{{MAVEN_NAMESPACE_URI}}}{local_name}"
