from __future__ import annotations

from pathlib import Path

from javamigrator.analysis.model import ProjectModel


def generate_rust_project(
    project_model: ProjectModel,
    output_path: str = "output/rust_project",
) -> Path:
    """Generate a minimal Actix Web scaffold from a language-agnostic project model."""
    output_root = Path(output_path)
    src_dir = output_root / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    _write_cargo_toml(output_root)
    _write_main_rs(src_dir, project_model)
    _write_routes_summary(output_root, project_model)

    return output_root


def _write_cargo_toml(output_root: Path) -> None:
    content = """[package]
name = "generated_rust_app"
version = "0.1.0"
edition = "2021"

[dependencies]
actix-web = "4"
serde_json = "1"
"""
    (output_root / "Cargo.toml").write_text(content, encoding="utf-8")


def _write_main_rs(src_dir: Path, project_model: ProjectModel) -> None:
    handler_blocks: list[str] = []
    route_blocks: list[str] = []

    if not project_model.endpoints:
        handler_blocks.append(
            """async fn health() -> impl Responder {
    HttpResponse::Ok().json(json!({"status": "ok"}))
}
"""
        )
        route_blocks.append('            .route("/health", web::get().to(health))')
    else:
        for endpoint in project_model.endpoints:
            handler_name = _rust_handler_name(endpoint.name, endpoint.methods)
            methods_literal = ", ".join(endpoint.methods)
            handler_blocks.append(
                f"""async fn {handler_name}() -> impl Responder {{
    HttpResponse::Ok().json(json!({{"message": "TODO", "endpoint": "{endpoint.name}", "methods": "{methods_literal}"}}))
}}
"""
            )
            for method in endpoint.methods:
                route_blocks.append(
                    f'            .route("{endpoint.route}", web::{method.lower()}().to({handler_name}))'
                )

    content = f"""use actix_web::{{web, App, HttpResponse, HttpServer, Responder}};
use serde_json::json;

{chr(10).join(handler_blocks)}

#[actix_web::main]
async fn main() -> std::io::Result<()> {{
    HttpServer::new(|| {{
        App::new()
{chr(10).join(route_blocks)}
    }})
    .bind(("127.0.0.1", 8080))?
    .run()
    .await
}}
"""
    (src_dir / "main.rs").write_text(content, encoding="utf-8")


def _write_routes_summary(output_root: Path, project_model: ProjectModel) -> None:
    lines = ["# Generated Rust Routes", ""]

    if not project_model.endpoints:
        lines.append("No endpoints detected.")
    else:
        for endpoint in project_model.endpoints:
            lines.append(f"- `{endpoint.route}` -> `{endpoint.name}` ({', '.join(endpoint.methods)})")

    (output_root / "routes.md").write_text("\n".join(lines), encoding="utf-8")


def _rust_handler_name(endpoint_name: str, methods: list[str]) -> str:
    primary_method = methods[0].lower() if methods else "handle"
    return f"{primary_method}_{_to_snake_case(endpoint_name)}"


def _to_snake_case(name: str) -> str:
    characters: list[str] = []
    for index, char in enumerate(name):
        if char.isupper() and index > 0 and not name[index - 1].isupper():
            characters.append("_")
        characters.append(char.lower())
    return "".join(characters)
