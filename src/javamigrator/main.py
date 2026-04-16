import typer

from javamigrator.detectors.build_tool import BuildTool, detect_build_system
from javamigrator.detectors.java_version import detect_java_version

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
    """Scan a Java project and print the detected build tool and Java version."""
    build_tool = detect_build_system(project_path)
    typer.echo(f"Detected build tool: {build_tool.value}")

    java_version = detect_java_version(project_path)
    if java_version:
        typer.echo(f"Detected Java version: {java_version}")
    else:
        typer.echo("Java version: not detected")

    if target_java is not None:
        typer.echo(f"Target Java version: {target_java}")


if __name__ == "__main__":
    app()
