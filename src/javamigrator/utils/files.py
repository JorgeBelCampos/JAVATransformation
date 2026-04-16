from pathlib import Path
from typing import List


class FileUtils:
    def list_files(self, path: str, patterns: List[str] | None = None) -> List[Path]:
        """List project files optionally filtered by pattern."""
        folder = Path(path)
        if not folder.exists():
            return []
        return [p for p in folder.rglob("*") if p.is_file()]
