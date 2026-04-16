from dataclasses import dataclass, field
from typing import List


@dataclass
class ScanResult:
    path: str
    build_tool: str | None = None
    java_version: str | None = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ReportSummary:
    title: str
    content: str