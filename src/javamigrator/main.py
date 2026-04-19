from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import typer

from javamigrator.analysis.autofix import AutoFixSuggestion, generate_autofix_suggestions
from javamigrator.analysis.autofix_apply import apply_autofix_suggestions
from javamigrator.analysis.build_error_analysis import BuildErrorFinding, analyze_build_errors
from javamigrator.analysis.build_validation import BuildValidationResult, validate_maven_build
from javamigrator.analysis.change_tracking import (
    FileChange,
    generate_unified_diffs,
    summarize_project_changes,
    write_change_summary,
    write_diff_report,
)
from javamigrator.analysis.code_analysis import ImportFinding, analyze_problematic_imports, scan_java_imports
from javamigrator.analysis.compatibility import analyze_java_compatibility
from javamigrator.analysis.dependency_analysis import DependencyFinding, analyze_problematic_dependencies
from javamigrator.analysis.fix_prioritization import FixCandidate, generate_top_fix_candidates
from javamigrator.analysis.generators.cpp_generator import generate_cpp_project
from javamigrator.analysis.generators.python_generator import generate_python_project
from javamigrator.analysis.generators.rust_generator import generate_rust_project
from javamigrator.analysis.go_scaffolder import discover_java_endpoints, generate_go_project
from javamigrator.analysis.intelligence import generate_architecture_insights
from javamigrator.analysis.migration_strategy import MigrationStrategy, build_migration_strategy
from javamigrator.analysis.model_builder import build_project_model
from javamigrator.analysis.pom_autofix import apply_pom_autofix
from javamigrator.analysis.summary import ExecutiveSummary, build_executive_summary
from javamigrator.analysis.verification import VerificationSummary, build_verification_summary
from javamigrator.detectors.build_tool import detect_build_system
from javamigrator.detectors.dependencies import detect_maven_dependencies
from javamigrator.detectors.java_version import detect_java_version
from javamigrator.reports.json_report import generate_json_report, write_json_report
from javamigrator.reports.markdown_report import generate_markdown_report, write_markdown_report

app = typer.Typer(help="Java migrator agent CLI")


@dataclass
class AnalysisContext:
    build_tool: str
    java_version: str | None
    compatibility_messages: list[str]
    code_findings: list[ImportFinding]
    dependency_findings: list[DependencyFinding]
    architecture_insights: list[str]
    executive_summary: ExecutiveSummary
    migration_strategy: MigrationStrategy
    top_fix_candidates: list[FixCandidate]
    autofix_suggestions: list[AutoFixSuggestion]


@dataclass
class IterationResult:
    iteration: int
    source_project_path: str
    fixed_path: Path
    output_dir: Path
    analysis: AnalysisContext
    fixed_code_findings: list[ImportFinding]
    fixed_dependency_findings: list[DependencyFinding]
    verification: VerificationSummary
    pom_changes: list[str]
    build_validation: BuildValidationResult
    build_error_findings: list[BuildErrorFinding]
    changes: list[FileChange]
    next_autofix_suggestions: list[AutoFixSuggestion]
    next_fix_suggestions: list[str]


def _write_build_logs(
    output_dir: Path,
    build_validation: BuildValidationResult,
) -> tuple[Path, Path, Path]:
    stdout_log = output_dir / "build_stdout.log"
    stderr_log = output_dir / "build_stderr.log"
    combined_log = output_dir / "build_combined.log"

    stdout_text = build_validation.stdout or ""
    stderr_text = build_validation.stderr or ""
    combined_text = "\n".join(part for part in (stdout_text, stderr_text) if part)

    stdout_log.write_text(stdout_text, encoding="utf-8")
    stderr_log.write_text(stderr_text, encoding="utf-8")
    combined_log.write_text(combined_text, encoding="utf-8")

    return stdout_log, stderr_log, combined_log


def _print_build_error_summary(build_error_findings: list[BuildErrorFinding]) -> None:
    if not build_error_findings:
        typer.echo("  No structured build errors parsed.")
        return

    category_counts: dict[str, int] = {}
    for finding in build_error_findings:
        category_counts[finding.category] = category_counts.get(finding.category, 0) + 1

    typer.echo("")
    typer.echo("Build error summary:")
    for category, count in sorted(category_counts.items(), key=lambda item: (-item[1], item[0])):
        typer.echo(f"  - {category}: {count}")

    typer.echo("")
    typer.echo("Build error findings:")
    for finding in build_error_findings[:10]:
        location = ""
        if finding.file_path:
            location = f" ({finding.file_path}"
            if finding.line_number is not None:
                location += f":{finding.line_number}"
            location += ")"
        typer.echo(f"  [{finding.category}] {finding.message}{location}")


def _print_change_tracking_summary(changes_count: int, output_dir: Path) -> None:
    typer.echo("")
    typer.echo("Change tracking:")
    typer.echo(f"  Changed files: {changes_count}")
    typer.echo(f"  Reports: {output_dir / 'change_summary.md'}, {output_dir / 'diff_report.md'}")


def _default_output_path(language: str) -> str:
    return f"output/{language}_project"


def _generate_scaffold(language: str, project_path: str, output_path: str) -> Path:
    project_model = build_project_model(project_path)

    if language == "go":
        return generate_go_project(project_path=project_path, output_path=output_path)
    if language == "python":
        return generate_python_project(project_model=project_model, output_path=output_path)
    if language == "rust":
        return generate_rust_project(project_model=project_model, output_path=output_path)
    if language == "cpp":
        return generate_cpp_project(project_model=project_model, output_path=output_path)

    raise ValueError(f"Unsupported language: {language}")


def _analyze_project(project_path: str, target_java: int | None) -> AnalysisContext:
    build_tool = detect_build_system(project_path)
    java_version = detect_java_version(project_path)
    compatibility_messages = analyze_java_compatibility(java_version, target_java)

    dependencies = detect_maven_dependencies(project_path)
    dependency_findings = analyze_problematic_dependencies(dependencies)

    imports = scan_java_imports(project_path)
    code_findings = analyze_problematic_imports(imports)

    architecture_insights = generate_architecture_insights(
        code_findings,
        dependency_findings,
        java_version,
        target_java,
    )
    executive_summary = build_executive_summary(code_findings)
    migration_strategy = build_migration_strategy(
        detected_java_version=java_version,
        target_java_version=target_java,
        executive_summary=executive_summary,
    )
    top_fix_candidates = generate_top_fix_candidates(code_findings, dependency_findings)
    autofix_suggestions = generate_autofix_suggestions(code_findings)

    return AnalysisContext(
        build_tool=build_tool.value,
        java_version=java_version,
        compatibility_messages=compatibility_messages,
        code_findings=code_findings,
        dependency_findings=dependency_findings,
        architecture_insights=architecture_insights,
        executive_summary=executive_summary,
        migration_strategy=migration_strategy,
        top_fix_candidates=top_fix_candidates,
        autofix_suggestions=autofix_suggestions,
    )


def _execute_iteration(
    iteration: int,
    source_project_path: str,
    target_java: int | None,
    output_dir: Path,
    analysis: AnalysisContext,
) -> IterationResult:
    output_dir.mkdir(parents=True, exist_ok=True)

    fixed_path = apply_autofix_suggestions(
        project_path=source_project_path,
        suggestions=analysis.autofix_suggestions,
        output_path=str(output_dir / "fixed_project"),
    )
    pom_changes = apply_pom_autofix(str(fixed_path))

    fixed_dependencies = detect_maven_dependencies(str(fixed_path))
    fixed_dependency_findings = analyze_problematic_dependencies(fixed_dependencies)
    fixed_imports = scan_java_imports(str(fixed_path))
    fixed_code_findings = analyze_problematic_imports(fixed_imports)

    verification = build_verification_summary(
        original_code_findings=analysis.code_findings,
        fixed_code_findings=fixed_code_findings,
        original_dependency_findings=analysis.dependency_findings,
        fixed_dependency_findings=fixed_dependency_findings,
    )

    build_validation = validate_maven_build(str(fixed_path))
    build_error_findings = analyze_build_errors(
        stderr=build_validation.stderr,
        stdout=build_validation.stdout,
    )
    _write_build_logs(output_dir, build_validation)

    changes = summarize_project_changes(source_project_path, str(fixed_path))
    diffs = generate_unified_diffs(
        original_project_path=source_project_path,
        fixed_project_path=str(fixed_path),
        max_files=25,
    )
    write_change_summary(changes, output_dir / "change_summary.md")
    write_diff_report(diffs, output_dir / "diff_report.md")

    next_autofix_suggestions = generate_autofix_suggestions(fixed_code_findings)
    next_fix_suggestions = _derive_build_followup_suggestions(build_error_findings)

    _write_iteration_reports(
        output_dir=output_dir,
        project_path=source_project_path,
        target_java=target_java,
        analysis=analysis,
        verification=verification,
        build_validation=build_validation,
        build_error_findings=build_error_findings,
    )
    _write_iteration_summary(
        output_dir=output_dir,
        iteration=iteration,
        fixed_path=fixed_path,
        pom_changes=pom_changes,
        changes=changes,
        build_validation=build_validation,
        build_error_findings=build_error_findings,
        next_autofix_suggestions=next_autofix_suggestions,
        next_fix_suggestions=next_fix_suggestions,
    )

    return IterationResult(
        iteration=iteration,
        source_project_path=source_project_path,
        fixed_path=fixed_path,
        output_dir=output_dir,
        analysis=analysis,
        fixed_code_findings=fixed_code_findings,
        fixed_dependency_findings=fixed_dependency_findings,
        verification=verification,
        pom_changes=pom_changes,
        build_validation=build_validation,
        build_error_findings=build_error_findings,
        changes=changes,
        next_autofix_suggestions=next_autofix_suggestions,
        next_fix_suggestions=next_fix_suggestions,
    )


def _write_iteration_reports(
    output_dir: Path,
    project_path: str,
    target_java: int | None,
    analysis: AnalysisContext,
    verification: VerificationSummary,
    build_validation: BuildValidationResult,
    build_error_findings: list[BuildErrorFinding],
) -> None:
    report_content = generate_markdown_report(
        project_path=project_path,
        build_tool=analysis.build_tool,
        detected_java_version=analysis.java_version,
        target_java_version=target_java,
        compatibility_messages=analysis.compatibility_messages,
        code_findings=analysis.code_findings,
        dependency_findings=analysis.dependency_findings,
        executive_summary=analysis.executive_summary,
        migration_strategy=analysis.migration_strategy,
        top_fix_candidates=analysis.top_fix_candidates,
        verification_summary=verification,
        build_validation=build_validation,
        build_error_findings=build_error_findings,
    )
    write_markdown_report(report_content, output_dir / "report.md")

    json_report = generate_json_report(
        project_path=project_path,
        build_tool=analysis.build_tool,
        detected_java_version=analysis.java_version,
        target_java_version=target_java,
        compatibility_messages=analysis.compatibility_messages,
        code_findings=analysis.code_findings,
        dependency_findings=analysis.dependency_findings,
        executive_summary=analysis.executive_summary,
        migration_strategy=analysis.migration_strategy,
        architecture_insights=analysis.architecture_insights,
        top_fix_candidates=analysis.top_fix_candidates,
        autofix_suggestions=analysis.autofix_suggestions,
        verification_summary=verification,
        build_validation=build_validation,
        build_error_findings=build_error_findings,
    )
    write_json_report(json_report, output_dir / "report.json")


def _write_iteration_summary(
    output_dir: Path,
    iteration: int,
    fixed_path: Path,
    pom_changes: list[str],
    changes: list[FileChange],
    build_validation: BuildValidationResult,
    build_error_findings: list[BuildErrorFinding],
    next_autofix_suggestions: list[AutoFixSuggestion],
    next_fix_suggestions: list[str],
) -> None:
    summary_data = {
        "iteration": iteration,
        "fixed_project_path": str(fixed_path),
        "pom_changes": pom_changes,
        "changed_files": len(changes),
        "build_attempted": build_validation.attempted,
        "build_succeeded": build_validation.succeeded,
        "build_return_code": build_validation.return_code,
        "build_error_categories": [finding.category for finding in build_error_findings],
        "next_autofix_suggestions": len(next_autofix_suggestions),
        "next_fix_suggestions": next_fix_suggestions,
    }
    (output_dir / "iteration_summary.json").write_text(
        json.dumps(summary_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    lines = [
        f"# Iteration {iteration} Summary",
        "",
        f"- Fixed project: `{fixed_path}`",
        f"- Changed files: {len(changes)}",
        f"- POM changes: {len(pom_changes)}",
        f"- Build attempted: {'YES' if build_validation.attempted else 'NO'}",
        f"- Build succeeded: {'YES' if build_validation.succeeded else 'NO'}",
        f"- Return code: {build_validation.return_code if build_validation.return_code is not None else 'N/A'}",
        f"- Next autofix suggestions: {len(next_autofix_suggestions)}",
        "",
        "## Next Fix Suggestions",
        "",
    ]

    if next_fix_suggestions:
        lines.extend(f"- {suggestion}" for suggestion in next_fix_suggestions)
    else:
        lines.append("- No additional build-based fix suggestions generated.")

    (output_dir / "iteration_summary.md").write_text("\n".join(lines), encoding="utf-8")


def _write_aggregate_iteration_summary(base_output_dir: Path, results: list[IterationResult]) -> None:
    if len(results) <= 1:
        return

    summary_dir = base_output_dir / "iterations"
    summary_dir.mkdir(parents=True, exist_ok=True)

    json_payload = [
        {
            "iteration": result.iteration,
            "source_project_path": result.source_project_path,
            "fixed_project_path": str(result.fixed_path),
            "output_dir": str(result.output_dir),
            "changed_files": len(result.changes),
            "pom_changes": len(result.pom_changes),
            "build_succeeded": result.build_validation.succeeded,
            "build_return_code": result.build_validation.return_code,
            "next_fix_suggestions": result.next_fix_suggestions,
        }
        for result in results
    ]
    (summary_dir / "iteration_summary.json").write_text(
        json.dumps(json_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    lines = ["# Iterative Migration Summary", ""]
    for result in results:
        lines.extend(
            [
                f"## Iteration {result.iteration}",
                "",
                f"- Source project: `{result.source_project_path}`",
                f"- Fixed project: `{result.fixed_path}`",
                f"- Changed files: {len(result.changes)}",
                f"- POM changes: {len(result.pom_changes)}",
                f"- Build succeeded: {'YES' if result.build_validation.succeeded else 'NO'}",
                f"- Return code: {result.build_validation.return_code if result.build_validation.return_code is not None else 'N/A'}",
                "",
            ]
        )
        if result.next_fix_suggestions:
            lines.extend(f"- {suggestion}" for suggestion in result.next_fix_suggestions)
        else:
            lines.append("- No additional build-based fix suggestions generated.")
        lines.append("")

    (summary_dir / "iteration_summary.md").write_text("\n".join(lines), encoding="utf-8")


def _derive_build_followup_suggestions(build_error_findings: list[BuildErrorFinding]) -> list[str]:
    suggestions: list[str] = []
    seen: set[str] = set()

    for finding in build_error_findings:
        suggestion: str | None = None

        if finding.category == "java_source_target_mismatch":
            suggestion = "Raise Maven compiler source/target/release or related Java properties before the next build."
        elif finding.category == "missing_symbol":
            suggestion = "Inspect missing symbols and add explicit dependencies or replace removed APIs."
        elif finding.category == "missing_package":
            suggestion = "Inspect missing packages and add the corresponding dependency or migration replacement."
        elif finding.category == "missing_dependency":
            suggestion = "Add or upgrade missing Maven dependencies that were removed from the JDK or target platform."
        elif finding.category == "jakarta_javax_mismatch":
            suggestion = "Align javax/jakarta imports and dependencies consistently across code and pom.xml files."
        elif finding.category == "bytecode_version_mismatch":
            suggestion = "Align dependency bytecode level and compiler target with the chosen JDK."

        if suggestion and suggestion not in seen:
            seen.add(suggestion)
            suggestions.append(suggestion)

    return suggestions


def _print_analysis_context(analysis: AnalysisContext, target_java: int | None) -> None:
    typer.echo(f"Detected build tool: {analysis.build_tool}")
    typer.echo(f"Detected Java version: {analysis.java_version or 'not detected'}")
    if target_java is not None:
        typer.echo(f"Target Java version: {target_java}")

    for message in analysis.compatibility_messages:
        typer.echo(f"WARNING: {message}")

    if analysis.dependency_findings:
        typer.echo("")
        typer.echo("Dependency findings:")
        for finding in analysis.dependency_findings[:20]:
            typer.echo(f"[{finding.severity}] {finding.message}")
            typer.echo(f"  Group ID: {finding.group_id}")
            typer.echo(f"  Artifact ID: {finding.artifact_id}")
            typer.echo(f"  Version: {finding.version or 'not specified'}")
            typer.echo("")

    if analysis.code_findings:
        typer.echo("")
        typer.echo("Code findings:")
        for finding in analysis.code_findings[:20]:
            typer.echo(f"[{finding.severity}] {finding.message}")
            typer.echo(f"  File: {finding.file_path}")
            typer.echo(f"  Line: {finding.line_number}")
            typer.echo(f"  Import: {finding.import_value}")
            typer.echo("")

    if analysis.top_fix_candidates:
        typer.echo("")
        typer.echo("Top fix candidates:")
        for fix in analysis.top_fix_candidates[:10]:
            typer.echo(f"  - {fix.title} [{fix.impact}]")

    if analysis.autofix_suggestions:
        typer.echo("")
        typer.echo(f"Autofix suggestions: {len(analysis.autofix_suggestions)}")


def _print_iteration_result(result: IterationResult) -> None:
    typer.echo("")
    typer.echo("Verification summary:")
    typer.echo(
        f"  Code findings: {result.verification.original_code_findings} -> {result.verification.fixed_code_findings}"
    )
    typer.echo(
        f"  Dependency findings: {result.verification.original_dependency_findings} -> {result.verification.fixed_dependency_findings}"
    )
    typer.echo(
        f"  Servlet code findings: {result.verification.original_servlet_findings} -> {result.verification.fixed_servlet_findings}"
    )
    typer.echo(
        f"  Servlet dependency findings: {result.verification.original_servlet_dependencies} -> {result.verification.fixed_servlet_dependencies}"
    )

    if result.pom_changes:
        typer.echo("")
        typer.echo("POM autofix changes:")
        for change in result.pom_changes[:20]:
            typer.echo(f"  - {change}")

    typer.echo("")
    typer.echo("Build validation:")
    typer.echo(f"  Attempted: {'YES' if result.build_validation.attempted else 'NO'}")
    typer.echo(f"  Succeeded: {'YES' if result.build_validation.succeeded else 'NO'}")
    if result.build_validation.command:
        typer.echo(f"  Command: {' '.join(result.build_validation.command)}")
    if result.build_validation.return_code is not None:
        typer.echo(f"  Return code: {result.build_validation.return_code}")
    typer.echo(
        f"  Logs: {result.output_dir / 'build_combined.log'}, {result.output_dir / 'build_stdout.log'}, {result.output_dir / 'build_stderr.log'}"
    )

    _print_build_error_summary(result.build_error_findings)
    _print_change_tracking_summary(len(result.changes), result.output_dir)

    if result.next_fix_suggestions:
        typer.echo("")
        typer.echo("Next fix suggestions:")
        for suggestion in result.next_fix_suggestions:
            typer.echo(f"  - {suggestion}")

    typer.echo(f"Report written to {result.output_dir / 'report.md'}")
    typer.echo(f"JSON report written to {result.output_dir / 'report.json'}")


def _should_stop_iteration(result: IterationResult) -> tuple[bool, str]:
    if result.build_validation.succeeded:
        return True, "Build succeeded; stopping iterative migration."

    if not result.changes and not result.pom_changes:
        return True, "No safe changes were applied in this iteration; stopping."

    if not result.next_autofix_suggestions and not result.next_fix_suggestions:
        return True, "No further safe follow-up suggestions were generated; stopping."

    return False, ""


def _iteration_output_dir(base_output_dir: Path, iteration: int, max_iterations: int) -> Path:
    if max_iterations <= 1:
        return base_output_dir
    return base_output_dir / "iterations" / f"iteration_{iteration:02d}"


@app.command()
def scan(
    project_path: str = typer.Argument(".", help="Path to the Java project"),
    target_java: int | None = typer.Option(
        None,
        "--target-java",
        help="Optional target Java version for migration analysis",
    ),
    max_iterations: int = typer.Option(
        1,
        "--max-iterations",
        min=1,
        max=10,
        help="Maximum number of bounded migration iterations to execute.",
    ),
) -> None:
    """Scan a Java project, apply safe fixes, validate builds, and optionally iterate."""

    base_output_dir = Path("output")
    base_output_dir.mkdir(parents=True, exist_ok=True)

    current_project_path = project_path
    results: list[IterationResult] = []

    for iteration in range(1, max_iterations + 1):
        typer.echo("")
        typer.echo(f"=== Iteration {iteration}/{max_iterations} ===")

        analysis = _analyze_project(current_project_path, target_java)
        _print_analysis_context(analysis, target_java)

        output_dir = _iteration_output_dir(base_output_dir, iteration, max_iterations)
        result = _execute_iteration(
            iteration=iteration,
            source_project_path=current_project_path,
            target_java=target_java,
            output_dir=output_dir,
            analysis=analysis,
        )
        results.append(result)
        _print_iteration_result(result)

        should_stop, reason = _should_stop_iteration(result)
        if should_stop:
            typer.echo("")
            typer.echo(reason)
            break

        current_project_path = str(result.fixed_path)

    _write_aggregate_iteration_summary(base_output_dir, results)


@app.command("generate-go")
def generate_go(
    project_path: str = typer.Argument(".", help="Path to the Java project"),
    output_path: str = typer.Option(
        "output/go_project",
        "--output-path",
        help="Path where the Go scaffold will be generated",
    ),
) -> None:
    """Generate a Go scaffold from detected Java servlet-style endpoints."""

    typer.echo("Discovering Java endpoints...")
    endpoints = discover_java_endpoints(project_path)

    typer.echo(f"Detected endpoints: {len(endpoints)}")
    for endpoint in endpoints[:20]:
        typer.echo(
            f"  - {endpoint.class_name} | {endpoint.route} | {', '.join(endpoint.http_methods)}"
        )

    generated_path = generate_go_project(
        project_path=project_path,
        output_path=output_path,
    )

    typer.echo("")
    typer.echo(f"Generated Go scaffold at: {generated_path}")
    typer.echo("Generated files:")
    typer.echo(f"  - {generated_path / 'go.mod'}")
    typer.echo(f"  - {generated_path / 'cmd' / 'app' / 'main.go'}")
    typer.echo(f"  - {generated_path / 'internal' / 'handlers' / 'handlers.go'}")
    typer.echo(f"  - {generated_path / 'routes.md'}")


@app.command()
def generate(
    language: str = typer.Argument(..., help="Target language: go, python, rust, cpp"),
    project_path: str = typer.Argument(".", help="Path to the Java project"),
    output_path: str | None = typer.Option(
        None,
        "--output-path",
        help="Optional path where the generated scaffold will be written",
    ),
) -> None:
    """Generate a multi-language scaffold from a language-agnostic Java project model."""

    normalized_language = language.strip().lower()
    if normalized_language not in {"go", "python", "rust", "cpp"}:
        raise typer.BadParameter("Supported languages: go, python, rust, cpp")

    typer.echo("Building language-agnostic project model...")
    project_model = build_project_model(project_path)
    typer.echo(f"Detected endpoints: {len(project_model.endpoints)}")
    for endpoint in project_model.endpoints[:20]:
        typer.echo(f"  - {endpoint.name} | {endpoint.route} | {', '.join(endpoint.methods)}")

    resolved_output_path = output_path or _default_output_path(normalized_language)
    generated_path = _generate_scaffold(
        language=normalized_language,
        project_path=project_path,
        output_path=resolved_output_path,
    )

    typer.echo("")
    typer.echo(f"Generated {normalized_language} scaffold at: {generated_path}")


if __name__ == "__main__":
    app()
