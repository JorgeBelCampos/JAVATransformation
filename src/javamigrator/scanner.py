from javamigrator.models import ScanResult


class Scanner:
    def __init__(self, path: str) -> None:
        self.path = path

    def scan(self) -> ScanResult:
        """Run all detectors and return a scan result."""
        result = ScanResult(path=self.path, dependencies=[])
        # Placeholder: add detection logic here.
        return result
