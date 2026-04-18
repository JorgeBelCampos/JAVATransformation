import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Union


MAVEN_NS = {"m": "http://maven.apache.org/POM/4.0.0"}
PROPERTY_REF_PATTERN = re.compile(r"^\$\{(.+)\}$")


def detect_java_version(project_path: Union[str, Path]) -> str | None:
    """Detect the Java version from a Maven project's pom.xml."""
    root = Path(project_path)

    if root.is_file():
        root = root.parent

    try:
        for directory in (root, *root.parents):
            pom_file = directory / "pom.xml"
            if pom_file.exists():
                return _parse_java_version_from_pom(pom_file)
    except OSError:
        return None

    return None


def _parse_java_version_from_pom(pom_path: Path) -> str | None:
    """Parse Java version from a pom.xml file, resolving simple property references."""
    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()

        properties_map = _extract_properties(root)

        # 1) Common properties
        properties = root.find("m:properties", MAVEN_NS)
        if properties is not None:
            for key in (
                "maven.compiler.release",
                "maven.compiler.source",
                "maven.compiler.target",
                "java.version",
            ):
                elem = properties.find(f"m:{key}", MAVEN_NS)
                if elem is not None and elem.text:
                    return _resolve_property_reference(elem.text.strip(), properties_map)

        # 2) maven-compiler-plugin configuration
        plugins = root.findall(".//m:plugin", MAVEN_NS)
        for plugin in plugins:
            artifact_id = plugin.find("m:artifactId", MAVEN_NS)
            if artifact_id is None or artifact_id.text != "maven-compiler-plugin":
                continue

            configuration = plugin.find("m:configuration", MAVEN_NS)
            if configuration is None:
                continue

            for tag in ("release", "source", "target"):
                elem = configuration.find(f"m:{tag}", MAVEN_NS)
                if elem is not None and elem.text:
                    return _resolve_property_reference(elem.text.strip(), properties_map)

    except (ET.ParseError, OSError):
        return None

    return None


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
    """Resolve simple Maven property references like ${jdk.version}."""
    match = PROPERTY_REF_PATTERN.match(value)
    if not match:
        return value

    property_name = match.group(1)
    return properties_map.get(property_name, value)