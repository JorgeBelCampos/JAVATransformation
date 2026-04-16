import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Union


MAVEN_NS = {"m": "http://maven.apache.org/POM/4.0.0"}


def detect_java_version(project_path: Union[str, Path]) -> str | None:
    """Detect the Java version from a Maven project's pom.xml.

    Searches for pom.xml in the provided path and parent directories.
    Extracts Java version from common Maven properties or compiler plugin config.

    Args:
        project_path: Directory or file path within the Maven project.

    Returns:
        The detected Java version as a string, or None if not found.
    """
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
    """Parse Java version from a pom.xml file."""
    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()

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
                    return elem.text.strip()

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
                    return elem.text.strip()

    except (ET.ParseError, OSError):
        return None

    return None