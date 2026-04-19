from __future__ import annotations

from pathlib import Path

from javamigrator.analysis.model import ProjectModel


def generate_cpp_project(
    project_model: ProjectModel,
    output_path: str = "output/cpp_project",
) -> Path:
    """Generate a minimal C++ REST scaffold from a language-agnostic project model."""
    output_root = Path(output_path)
    src_dir = output_root / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    _write_main_cpp(src_dir, project_model)
    _write_cmake(output_root)
    _write_routes_summary(output_root, project_model)

    return output_root


def _write_main_cpp(src_dir: Path, project_model: ProjectModel) -> None:
    route_blocks: list[str] = []

    if not project_model.endpoints:
        route_blocks.append(
            """    CROW_ROUTE(app, "/health")
    ([]() {
        return crow::response(200, R"({"status":"ok"})");
    });
"""
        )
    else:
        for endpoint in project_model.endpoints:
            methods_literal = ", ".join(endpoint.methods)
            route_blocks.append(
                f"""    // Methods: {methods_literal}
    CROW_ROUTE(app, "{endpoint.route}")
    ([]() {{
        return crow::response(200, R"({{"message":"TODO","endpoint":"{endpoint.name}"}})");
    }});
"""
            )

    content = f"""#include "crow_all.h"

int main() {{
    crow::SimpleApp app;

{chr(10).join(route_blocks)}

    app.port(8080).multithreaded().run();
    return 0;
}}
"""
    (src_dir / "main.cpp").write_text(content, encoding="utf-8")


def _write_cmake(output_root: Path) -> None:
    content = """cmake_minimum_required(VERSION 3.16)
project(generated_cpp_app)

set(CMAKE_CXX_STANDARD 17)

add_executable(generated_cpp_app src/main.cpp)
"""
    (output_root / "CMakeLists.txt").write_text(content, encoding="utf-8")


def _write_routes_summary(output_root: Path, project_model: ProjectModel) -> None:
    lines = ["# Generated C++ Routes", ""]

    if not project_model.endpoints:
        lines.append("No endpoints detected.")
    else:
        for endpoint in project_model.endpoints:
            lines.append(f"- `{endpoint.route}` -> `{endpoint.name}` ({', '.join(endpoint.methods)})")

    (output_root / "routes.md").write_text("\n".join(lines), encoding="utf-8")
