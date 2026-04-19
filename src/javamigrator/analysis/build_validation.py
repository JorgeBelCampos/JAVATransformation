from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BuildValidationResult:
    attempted: bool
    succeeded: bool
    tool: str
    command: list[str]
    return_code: int | None
    stdout: str
    stderr: str
    working_directory: str


def validate_maven_build(project_path: str, timeout_seconds: int = 600) -> BuildValidationResult:
    """Run a Maven compile command on the given project path."""

    project_dir = Path(project_path)

    mvn_cmd = (
        shutil.which("mvn")
        or shutil.which("mvn.cmd")
        or shutil.which("mvn.bat")
    )

    if mvn_cmd is None:
        return BuildValidationResult(
            attempted=False,
            succeeded=False,
            tool="maven",
            command=[],
            return_code=None,
            stdout="",
            stderr="Maven executable not found in PATH.",
            working_directory=str(project_dir),
        )

    command = [
        mvn_cmd,
        "-B",
        "-e",
        "-Dstyle.color=never",
        "--no-transfer-progress",
        "-DskipTests",
        "compile",
    ]

    try:
        result = subprocess.run(
            command,
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            encoding="utf-8",
            errors="replace",
            shell=False,
        )
        return BuildValidationResult(
            attempted=True,
            succeeded=result.returncode == 0,
            tool="maven",
            command=command,
            return_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            working_directory=str(project_dir),
        )
    except subprocess.TimeoutExpired as exc:
        return BuildValidationResult(
            attempted=True,
            succeeded=False,
            tool="maven",
            command=command,
            return_code=None,
            stdout=exc.stdout or "",
            stderr=(exc.stderr or "") + f"\nBuild timed out after {timeout_seconds} seconds.",
            working_directory=str(project_dir),
        )
    except OSError as exc:
        return BuildValidationResult(
            attempted=False,
            succeeded=False,
            tool="maven",
            command=command,
            return_code=None,
            stdout="",
            stderr=str(exc),
            working_directory=str(project_dir),
        )
