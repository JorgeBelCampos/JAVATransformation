from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


IMPORT_PATTERN = re.compile(r"^\s*import\s+([^;]+);")

JAKARTA_CANDIDATE_PREFIXES = (
    "javax.servlet.",
    "javax.ws.rs.",
    "javax.persistence.",
    "javax.ejb.",
    "javax.validation.",
    "javax.enterprise.",
    "javax.inject.",
    "javax.faces.",
    "javax.jms.",
    "javax.annotation.",
)

JAVA_SE_JAVAX_PREFIXES = (
    "javax.swing.",
    "javax.crypto.",
    "javax.xml.crypto.",
    "javax.security.",
    "javax.naming.",
    "javax.net.",
    "javax.sound.",
    "javax.imageio.",
    "javax.print.",
    "javax.sql.",
)

JAXB_PREFIXES = (
    "javax.xml.bind.",
    "javax.xml.bind.annotation.",
)

JAXWS_PREFIXES = (
    "javax.xml.ws.",
    "javax.jws.",
    "javax.jws.soap.",
)

ACTIVATION_PREFIXES = (
    "javax.activation.",
)

JSON_PREFIXES = (
    "javax.json.",
)

INTERNAL_JDK_PREFIXES = (
    "sun.",
    "com.sun.",
    "jdk.internal.",
)

REFLECTION_RISK_PREFIXES = (
    "java.lang.reflect.",
    "sun.reflect.",
    "jdk.internal.reflect.",
)


@dataclass
class ImportFinding:
    severity: str
    message: str
    file_path: str
    line_number: int
    import_value: str


def scan_java_imports(project_path: str) -> list[tuple[str, int, str]]:
    """Recursively scan all .java files and extract imports with file and line."""
    root = Path(project_path)
    if not root.exists():
        return []

    findings: list[tuple[str, int, str]] = []

    for java_file in root.rglob("*.java"):
        if not java_file.is_file():
            continue

        try:
            content = java_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = java_file.read_text(encoding="latin-1")
            except OSError:
                continue
        except OSError:
            continue

        for line_number, line in enumerate(content.splitlines(), start=1):
            match = IMPORT_PATTERN.match(line)
            if match:
                findings.append(
                    (
                        str(java_file),
                        line_number,
                        match.group(1).strip(),
                    )
                )

    return findings


def analyze_problematic_imports(imports: list[tuple[str, int, str]]) -> list[ImportFinding]:
    """Analyze Java imports and return structured migration findings."""
    findings: list[ImportFinding] = []
    seen: set[tuple[str, str, int, str]] = set()

    for file_path, line_number, import_value in imports:
        rules: list[tuple[str, str]] = []

        if import_value.startswith(JAKARTA_CANDIDATE_PREFIXES):
            rules.append(("HIGH", "Likely javax -> jakarta migration candidate"))

        elif import_value.startswith("javax.") and not import_value.startswith(JAVA_SE_JAVAX_PREFIXES):
            rules.append(("MEDIUM", "javax.* usage detected; review whether migration is required"))

        if import_value.startswith(JAXB_PREFIXES) or "xml.bind" in import_value:
            rules.append(("HIGH", "JAXB API removed from JDK after Java 11"))

        if import_value.startswith(JAXWS_PREFIXES) or "xml.ws" in import_value or ".ws." in import_value:
            rules.append(("HIGH", "JAX-WS API removed from JDK after Java 11"))

        if import_value.startswith(ACTIVATION_PREFIXES):
            rules.append(("HIGH", "javax.activation removed from JDK after Java 11"))

        if import_value.startswith(JSON_PREFIXES):
            rules.append(("MEDIUM", "Legacy javax.json API detected; explicit dependency or jakarta.json migration may be needed"))

        if import_value.startswith(INTERNAL_JDK_PREFIXES):
            rules.append(("HIGH", "Internal JDK APIs are risky and may break on newer Java versions"))

        if import_value.startswith(REFLECTION_RISK_PREFIXES) or import_value == "java.lang.invoke.MethodHandles":
            rules.append(("MEDIUM", "Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens"))

        for severity, message in rules:
            key = (file_path, message, line_number, import_value)
            if key in seen:
                continue
            seen.add(key)

            findings.append(
                ImportFinding(
                    severity=severity,
                    message=message,
                    file_path=file_path,
                    line_number=line_number,
                    import_value=import_value,
                )
            )

    return findings
