from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class BuildErrorFinding:
    severity: str
    category: str
    message: str
    file_path: str | None = None
    line_number: int | None = None
    raw_line: str | None = None


ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
ERROR_PREFIX_PATTERN = re.compile(r"^\[(?:ERROR|WARNING|INFO)\]\s*")
COMPILATION_ERROR_PATTERN = re.compile(
    r"^(?:\[(?:ERROR|WARNING)\]\s*)?(?P<file>.+?\.(?:java|kt|groovy)):\[(?P<line>\d+)(?:,(?P<col>\d+))?\]\s+(?P<message>.+)$",
    re.IGNORECASE,
)
COMPILATION_PHASE_PATTERN = re.compile(r"compilation error", re.IGNORECASE)
FAILED_GOAL_PATTERN = re.compile(r"failed to execute goal", re.IGNORECASE)
COULD_NOT_RESOLVE_PATTERN = re.compile(
    r"could not resolve dependencies|could not find artifact|failed to collect dependencies",
    re.IGNORECASE,
)
GENERIC_COMPILER_ERROR_PATTERN = re.compile(
    r"^(?:error:)\s+(?P<message>.+)$",
    re.IGNORECASE,
)
CANNOT_FIND_SYMBOL_PATTERN = re.compile(r"cannot find symbol", re.IGNORECASE)
PACKAGE_DOES_NOT_EXIST_PATTERN = re.compile(r"package\s+.+\s+does not exist", re.IGNORECASE)
CLASS_FILE_WRONG_VERSION_PATTERN = re.compile(
    r"class file has wrong version|wrong version .* should be",
    re.IGNORECASE,
)
SOURCE_TARGET_OPTION_PATTERN = re.compile(
    r"(?:source|target) option \d+.*(?:not supported|no longer supported)|invalid target release|release version .* not supported",
    re.IGNORECASE,
)
JAKARTA_JAVAX_PATTERN = re.compile(r"\b(?:jakarta|javax)\.[\w.]+", re.IGNORECASE)
CANNOT_ACCESS_PATTERN = re.compile(r"cannot access", re.IGNORECASE)
INCOMPATIBLE_TYPES_PATTERN = re.compile(r"incompatible types", re.IGNORECASE)
MISSING_SYMBOL_DETAIL_PATTERN = re.compile(
    r"^(?:symbol|location|required|found):",
    re.IGNORECASE,
)
HELP_REFERENCE_PATTERN = re.compile(r"^->\s+\[Help\s+\d+\]$", re.IGNORECASE)
LIFECYCLE_EXCEPTION_PATTERN = re.compile(
    r"^(?:org\.apache\.maven\.)?.*?(?:LifecycleExecutionException|CompilationFailureException):",
    re.IGNORECASE,
)


def analyze_build_errors(stderr: str, stdout: str = "") -> list[BuildErrorFinding]:
    """Parse Maven build output and extract structured error findings."""
    findings: list[BuildErrorFinding] = []
    current_finding: BuildErrorFinding | None = None

    combined = _normalize_output(stdout=stdout, stderr=stderr)

    for raw_line in combined.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            current_finding = None
            continue

        match = COMPILATION_ERROR_PATTERN.match(stripped)
        if match:
            file_path = match.group("file").strip()
            line_number = int(match.group("line"))
            message = _strip_error_prefix(match.group("message").strip())

            current_finding = BuildErrorFinding(
                severity="HIGH",
                category=_categorize_message(message),
                message=message,
                file_path=file_path,
                line_number=line_number,
                raw_line=stripped,
            )
            findings.append(current_finding)
            continue

        compiler_error_match = GENERIC_COMPILER_ERROR_PATTERN.match(plain_line := _strip_error_prefix(stripped))
        if compiler_error_match:
            message = compiler_error_match.group("message").strip()
            current_finding = BuildErrorFinding(
                severity="HIGH",
                category=_categorize_message(message),
                message=message,
                raw_line=stripped,
            )
            findings.append(current_finding)
            continue

        if HELP_REFERENCE_PATTERN.match(plain_line):
            current_finding = None
            continue

        if current_finding and _is_continuation_line(stripped):
            current_finding.message = f"{current_finding.message} | {_strip_error_prefix(stripped)}"
            current_finding.raw_line = f"{current_finding.raw_line}\n{stripped}"
            current_finding.category = _categorize_message(current_finding.message)
            continue

        current_finding = None

        if COULD_NOT_RESOLVE_PATTERN.search(plain_line):
            findings.append(
                BuildErrorFinding(
                    severity="HIGH",
                    category="missing_dependency",
                    message=plain_line,
                    raw_line=stripped,
                )
            )
            continue

        if LIFECYCLE_EXCEPTION_PATTERN.match(plain_line):
            continue

        if FAILED_GOAL_PATTERN.search(plain_line):
            category = "compiler_plugin_failure" if COMPILATION_PHASE_PATTERN.search(plain_line) else "maven_goal_failure"
            findings.append(
                BuildErrorFinding(
                    severity="HIGH",
                    category=category,
                    message=plain_line,
                    raw_line=stripped,
                )
            )
            continue

        if _looks_like_standalone_error(plain_line):
            findings.append(
                BuildErrorFinding(
                    severity="HIGH",
                    category=_categorize_message(plain_line),
                    message=plain_line,
                    raw_line=stripped,
                )
            )
            continue

        if "BUILD FAILURE" in plain_line.upper():
            findings.append(
                BuildErrorFinding(
                    severity="HIGH",
                    category="build_failure",
                    message="Maven reported BUILD FAILURE",
                    raw_line=stripped,
                )
            )

    return _deduplicate_build_findings(findings)


def _normalize_output(stdout: str, stderr: str) -> str:
    normalized_parts = []
    for part in (stdout or "", stderr or ""):
        if not part:
            continue
        normalized_parts.append(
            ANSI_ESCAPE_PATTERN.sub("", part).replace("\r\n", "\n").replace("\r", "\n")
        )
    return "\n".join(normalized_parts)


def _strip_error_prefix(line: str) -> str:
    return ERROR_PREFIX_PATTERN.sub("", line).strip()


def _is_continuation_line(line: str) -> bool:
    plain_line = _strip_error_prefix(line)
    return bool(
        MISSING_SYMBOL_DETAIL_PATTERN.match(plain_line)
        or plain_line.startswith("symbol:")
        or plain_line.startswith("location:")
        or plain_line.startswith("required:")
        or plain_line.startswith("found:")
    )


def _looks_like_standalone_error(line: str) -> bool:
    return any(
        pattern.search(line)
        for pattern in (
            CANNOT_FIND_SYMBOL_PATTERN,
            PACKAGE_DOES_NOT_EXIST_PATTERN,
            CLASS_FILE_WRONG_VERSION_PATTERN,
            SOURCE_TARGET_OPTION_PATTERN,
            CANNOT_ACCESS_PATTERN,
            INCOMPATIBLE_TYPES_PATTERN,
        )
    )


def _categorize_message(message: str) -> str:
    normalized = message.lower()

    if CANNOT_FIND_SYMBOL_PATTERN.search(normalized):
        return "missing_symbol"
    if PACKAGE_DOES_NOT_EXIST_PATTERN.search(normalized):
        if "jakarta." in normalized or "javax." in normalized:
            return "jakarta_javax_mismatch"
        return "missing_package"
    if SOURCE_TARGET_OPTION_PATTERN.search(normalized):
        return "java_source_target_mismatch"
    if CLASS_FILE_WRONG_VERSION_PATTERN.search(normalized):
        return "bytecode_version_mismatch"
    if CANNOT_ACCESS_PATTERN.search(normalized) and JAKARTA_JAVAX_PATTERN.search(normalized):
        return "jakarta_javax_mismatch"
    if INCOMPATIBLE_TYPES_PATTERN.search(normalized) and (
        "jakarta." in normalized or "javax." in normalized
    ):
        return "jakarta_javax_mismatch"
    if "jakarta." in normalized and "javax." in normalized:
        return "jakarta_javax_mismatch"
    if COULD_NOT_RESOLVE_PATTERN.search(normalized):
        return "missing_dependency"
    return "compilation_error"


def _deduplicate_build_findings(
    findings: list[BuildErrorFinding],
) -> list[BuildErrorFinding]:
    seen: set[tuple[str, str | None, int | None, str]] = set()
    unique: list[BuildErrorFinding] = []

    for finding in findings:
        normalized_message = re.sub(r"\s+", " ", finding.message).strip()
        key = (
            finding.category,
            finding.file_path,
            finding.line_number,
            normalized_message,
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(finding)

    return unique
