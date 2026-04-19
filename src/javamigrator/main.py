import typer
from pathlib import Path

from javamigrator.analysis.autofix import generate_autofix_suggestions
from javamigrator.analysis.autofix_apply import apply_autofix_suggestions
from javamigrator.analysis.build_error_analysis import BuildErrorFinding, analyze_build_errors
from javamigrator.analysis.build_validation import BuildValidationResult, validate_maven_build
from javamigrator.analysis.code_analysis import analyze_problematic_imports, scan_java_imports
from javamigrator.analysis.compatibility import analyze_java_compatibility
from javamigrator.analysis.dependency_analysis import analyze_problematic_dependencies
from javamigrator.analysis.fix_prioritization import generate_top_fix_candidates
from javamigrator.analysis.intelligence import generate_architecture_insights
from javamigrator.analysis.migration_strategy import build_migration_strategy
from javamigrator.analysis.pom_autofix import apply_pom_autofix
from javamigrator.analysis.summary import build_executive_summary
from javamigrator.analysis.verification import build_verification_summary
from javamigrator.detectors.build_tool import detect_build_system
from javamigrator.detectors.dependencies import detect_maven_dependencies
from javamigrator.detectors.java_version import detect_java_version
from javamigrator.reports.json_report import generate_json_report, write_json_report
from javamigrator.reports.markdown_report import generate_markdown_report, write_markdown_report

app = typer.Typer(help="Java migrator agent CLI")


def _write_build_logs(
    output_dir: Path,
    build_validation: BuildValidationResult,
) -> tuple[Path, Path, Path]:
    stdout_log = output_dir / "build_stdout.log"
    stderr_log = output_dir / "build_stderr.log"
    combined_log = output_dir / "build_combined.log"

    stdout_text = build_validation.stdout or ""
    stderr_text = build_validation.stderr or ""
    combined_text = "\n".join(
        part for part in (stdout_text, stderr_text) if part
    )

    stdout_log.write_text(stdout_text, encoding="utf-8")
    stderr_log.write_text(stderr_text, encoding="utf-8")
    combined_log.write_text(combined_text, encoding="utf-8")

    return stdout_log, stderr_log, combined_log


def _print_build_error_summary(
    build_error_findings: list[BuildErrorFinding],
) -> None:
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


@app.command()
def scan(
    project_path: str = typer.Argument(".", help="Path to the Java project"),
    target_java: int | None = typer.Option(
        None,
        "--target-java",
        help="Optional target Java version for migration analysis",
    ),
) -> None:
    """Scan a Java project, generate reports, apply safe autofixes, verify results, and analyze build errors."""

    build_tool = detect_build_system(project_path)
    typer.echo(f"Detected build tool: {build_tool.value}")

    java_version = detect_java_version(project_path)
    if java_version:
        typer.echo(f"Detected Java version: {java_version}")
    else:
        typer.echo("Java version: not detected")

    if target_java is not None:
        typer.echo(f"Target Java version: {target_java}")

    # Compatibility analysis
    messages = analyze_java_compatibility(java_version, target_java)
    for message in messages:
        typer.echo(f"⚠️ {message}")

    # Dependency analysis
    dependencies = detect_maven_dependencies(project_path)
    dependency_findings = analyze_problematic_dependencies(dependencies)

    if dependency_findings:
        typer.echo("")
        typer.echo("Dependency findings:")

    for finding in dependency_findings:
        typer.echo(f"[{finding.severity}] {finding.message}")
        typer.echo(f"  Group ID: {finding.group_id}")
        typer.echo(f"  Artifact ID: {finding.artifact_id}")
        typer.echo(f"  Version: {finding.version or 'not specified'}")
        typer.echo("")

    # Code analysis
    imports = scan_java_imports(project_path)
    code_findings = analyze_problematic_imports(imports)

    if code_findings:
        typer.echo("")
        typer.echo("Code findings:")

    for finding in code_findings:
        typer.echo(f"[{finding.severity}] {finding.message}")
        typer.echo(f"  File: {finding.file_path}")
        typer.echo(f"  Line: {finding.line_number}")
        typer.echo(f"  Import: {finding.import_value}")
        typer.echo("")

    # Architecture insights
    insights = generate_architecture_insights(
        code_findings,
        dependency_findings,
        java_version,
        target_java,
    )

    if insights:
        typer.echo("")
        typer.echo("Architecture insights:")
        for insight in insights:
            typer.echo(f"🧠 {insight}")

    # Executive summary and strategy
    executive_summary = build_executive_summary(code_findings)

    migration_strategy = build_migration_strategy(
        detected_java_version=java_version,
        target_java_version=target_java,
        executive_summary=executive_summary,
    )

    # Fix prioritization
    top_fixes = generate_top_fix_candidates(
        code_findings,
        dependency_findings,
    )

    if top_fixes:
        typer.echo("")
        typer.echo("Top fix candidates:")

        for fix in top_fixes:
            typer.echo(f"🔥 {fix.title}")
            typer.echo(f"  Category: {fix.category}")
            typer.echo(f"  Impact: {fix.impact} | Effort: {fix.effort}")
            typer.echo(f"  Affected files: {fix.affected_files}")
            typer.echo(f"  Occurrences: {fix.occurrences}")
            typer.echo(f"  Reason: {fix.reason}")
            typer.echo(f"  Recommendation: {fix.recommendation}")
            typer.echo("")

    # Autofix suggestions
    autofix_suggestions = generate_autofix_suggestions(code_findings)

    if autofix_suggestions:
        typer.echo("")
        typer.echo("Autofix suggestions:")

        for suggestion in autofix_suggestions[:20]:
            typer.echo(f"🛠 {suggestion.file_path}:{suggestion.line_number}")
            typer.echo(f"  Replace: {suggestion.original}")
            typer.echo(f"  With:    {suggestion.replacement}")
            typer.echo(f"  Confidence: {suggestion.confidence}")
            typer.echo("")

    # Apply code autofixes in safe mode
    typer.echo("")
    typer.echo("Applying autofixes (safe mode)...")

    fixed_path = apply_autofix_suggestions(
        project_path=project_path,
        suggestions=autofix_suggestions,
        output_path="output/fixed_project",
    )

    typer.echo(f"✅ Fixed project generated at: {fixed_path}")

    # Apply pom.xml autofixes on the copied project
    pom_changes = apply_pom_autofix(str(fixed_path))

    if pom_changes:
        typer.echo("")
        typer.echo("POM autofix changes:")
        for change in pom_changes:
            typer.echo(f"📦 {change}")

    # Verification: re-scan fixed project
    fixed_dependencies = detect_maven_dependencies(str(fixed_path))
    fixed_dependency_findings = analyze_problematic_dependencies(fixed_dependencies)

    fixed_imports = scan_java_imports(str(fixed_path))
    fixed_code_findings = analyze_problematic_imports(fixed_imports)

    verification = build_verification_summary(
        original_code_findings=code_findings,
        fixed_code_findings=fixed_code_findings,
        original_dependency_findings=dependency_findings,
        fixed_dependency_findings=fixed_dependency_findings,
    )

    typer.echo("")
    typer.echo("Verification summary:")
    typer.echo(
        f"  Code findings: {verification.original_code_findings} -> {verification.fixed_code_findings}"
    )
    typer.echo(
        f"  Dependency findings: {verification.original_dependency_findings} -> {verification.fixed_dependency_findings}"
    )
    typer.echo(
        f"  Servlet code findings: {verification.original_servlet_findings} -> {verification.fixed_servlet_findings}"
    )
    typer.echo(
        f"  Servlet dependency findings: {verification.original_servlet_dependencies} -> {verification.fixed_servlet_dependencies}"
    )

    # Build validation
    build_validation = validate_maven_build(str(fixed_path))
    build_error_findings = analyze_build_errors(
        stderr=build_validation.stderr,
        stdout=build_validation.stdout,
    )

    # Save full build logs
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    stdout_log, stderr_log, combined_log = _write_build_logs(output_dir, build_validation)

    typer.echo("")
    typer.echo("Build validation:")
    typer.echo(f"  Attempted: {'YES' if build_validation.attempted else 'NO'}")
    typer.echo(f"  Succeeded: {'YES' if build_validation.succeeded else 'NO'}")
    if build_validation.command:
        typer.echo(f"  Command: {' '.join(build_validation.command)}")
    if build_validation.return_code is not None:
        typer.echo(f"  Return code: {build_validation.return_code}")
    typer.echo(f"  Logs: {combined_log}, {stdout_log}, {stderr_log}")

    _print_build_error_summary(build_error_findings)

    # Markdown report
    report_content = generate_markdown_report(
        project_path=project_path,
        build_tool=build_tool.value,
        detected_java_version=java_version,
        target_java_version=target_java,
        compatibility_messages=messages,
        code_findings=code_findings,
        dependency_findings=dependency_findings,
        executive_summary=executive_summary,
        migration_strategy=migration_strategy,
        top_fix_candidates=top_fixes,
        verification_summary=verification,
        build_validation=build_validation,
        build_error_findings=build_error_findings,
    )
    write_markdown_report(report_content, "output/report.md")
    typer.echo("Report written to output/report.md")

    # JSON report
    json_report = generate_json_report(
        project_path=project_path,
        build_tool=build_tool.value,
        detected_java_version=java_version,
        target_java_version=target_java,
        compatibility_messages=messages,
        code_findings=code_findings,
        dependency_findings=dependency_findings,
        executive_summary=executive_summary,
        migration_strategy=migration_strategy,
        architecture_insights=insights,
        top_fix_candidates=top_fixes,
        autofix_suggestions=autofix_suggestions,
        verification_summary=verification,
        build_validation=build_validation,
        build_error_findings=build_error_findings,
    )
    write_json_report(json_report, "output/report.json")
    typer.echo("JSON report written to output/report.json")


if __name__ == "__main__":
    app()
