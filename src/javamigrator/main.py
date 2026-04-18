import typer

from javamigrator.analysis.autofix import generate_autofix_suggestions
from javamigrator.analysis.autofix_apply import apply_autofix_suggestions
from javamigrator.analysis.code_analysis import analyze_problematic_imports, scan_java_imports
from javamigrator.analysis.compatibility import analyze_java_compatibility
from javamigrator.analysis.dependency_analysis import analyze_problematic_dependencies
from javamigrator.analysis.fix_prioritization import generate_top_fix_candidates
from javamigrator.analysis.intelligence import generate_architecture_insights
from javamigrator.analysis.migration_strategy import build_migration_strategy
from javamigrator.analysis.summary import build_executive_summary
from javamigrator.detectors.build_tool import detect_build_system
from javamigrator.detectors.dependencies import detect_maven_dependencies
from javamigrator.detectors.java_version import detect_java_version
from javamigrator.reports.json_report import generate_json_report, write_json_report
from javamigrator.reports.markdown_report import generate_markdown_report, write_markdown_report

app = typer.Typer(help="Java migrator agent CLI")


@app.command()
def scan(
    project_path: str = typer.Argument(".", help="Path to the Java project"),
    target_java: int | None = typer.Option(
        None,
        "--target-java",
        help="Optional target Java version for migration analysis",
    ),
) -> None:
    """Scan a Java project, generate reports, and apply safe autofixes."""

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
    )
    write_json_report(json_report, "output/report.json")
    typer.echo("JSON report written to output/report.json")

    # Apply autofixes in safe mode to a copied project
    if autofix_suggestions:
        typer.echo("")
        typer.echo("Applying autofixes (safe mode)...")

        fixed_path = apply_autofix_suggestions(
            project_path=project_path,
            suggestions=autofix_suggestions,
            output_path="output/fixed_project",
        )

        typer.echo(f"✅ Fixed project generated at: {fixed_path}")


if __name__ == "__main__":
    app()