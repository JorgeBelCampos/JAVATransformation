from enum import Enum
from pathlib import Path
from typing import Union


class BuildTool(str, Enum):
    """Supported Java build tools."""

    MAVEN = "maven"
    GRADLE = "gradle"
    UNKNOWN = "unknown"


def detect_build_system(project_path: Union[str, Path]) -> BuildTool:
    """Detect the Java build system for a project.

    The detector checks the provided path and its parent directories for
    Maven or Gradle build files. If a file path is provided, its parent
    directory is used for detection.

    Args:
        project_path: Directory or file path within the Java project.

    Returns:
        BuildTool.MAVEN if pom.xml is found, BuildTool.GRADLE if build.gradle
        or build.gradle.kts is found, otherwise BuildTool.UNKNOWN.
    """
    root = Path(project_path)
    if root.is_file():
        root = root.parent

    try:
        for directory in (root, *root.parents):
            if (directory / "pom.xml").exists():
                return BuildTool.MAVEN
            if (directory / "build.gradle").exists() or (directory / "build.gradle.kts").exists():
                return BuildTool.GRADLE
    except OSError:
        return BuildTool.UNKNOWN

    return BuildTool.UNKNOWN
