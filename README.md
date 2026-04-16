# java-migrator-agent

A Python CLI agent for scanning Java projects, detecting build and dependency information, and generating migration reports.

## Project layout

- `src/javamigrator/main.py` — application entrypoint and CLI
- `src/javamigrator/models.py` — shared data models
- `src/javamigrator/scanner.py` — project scanning utilities
- `src/javamigrator/detectors/build_tool.py` — build tool detection logic
- `src/javamigrator/detectors/java_version.py` — Java version detection
- `src/javamigrator/detectors/dependencies.py` — dependency detection
- `src/javamigrator/reports/markdown_report.py` — Markdown report generation
- `src/javamigrator/reports/json_report.py` — JSON report generation
- `src/javamigrator/utils/files.py` — file helper utilities

## Usage

Install the package in editable mode and run the CLI:

```bash
python -m pip install -e .
javamigrator --help
```
