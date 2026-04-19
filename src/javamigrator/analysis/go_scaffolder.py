from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from javamigrator.analysis.model import DataModel, Endpoint, ProjectModel, RequestParameter
from javamigrator.analysis.model_builder import build_project_model


GO_MODULE_NAME = "generated/goapp"


@dataclass
class JavaEndpoint:
    class_name: str
    file_path: str
    route: str
    http_methods: list[str]


def discover_java_endpoints(project_path: str) -> list[JavaEndpoint]:
    """Compatibility wrapper for the legacy Go command output."""
    project_model = build_project_model(project_path)
    endpoints: list[JavaEndpoint] = []

    for endpoint in project_model.endpoints:
        endpoints.append(
            JavaEndpoint(
                class_name=endpoint.name,
                file_path=endpoint.source_file or "",
                route=endpoint.route,
                http_methods=endpoint.methods,
            )
        )

    return endpoints


def generate_go_project(
    project_path: str,
    output_path: str = "output/go_project",
) -> Path:
    """Generate a production-like Go scaffold from the language-agnostic project model."""
    project_model = build_project_model(project_path)

    output_root = Path(output_path)
    cmd_dir = output_root / "cmd" / "app"
    handlers_dir = output_root / "internal" / "handlers"
    services_dir = output_root / "internal" / "services"
    models_dir = output_root / "internal" / "models"
    routes_dir = output_root / "internal" / "routes"

    cmd_dir.mkdir(parents=True, exist_ok=True)
    handlers_dir.mkdir(parents=True, exist_ok=True)
    services_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)
    routes_dir.mkdir(parents=True, exist_ok=True)

    _write_go_mod(output_root)
    _write_main_go(cmd_dir)
    _write_models_go(models_dir, project_model)
    _write_services_go(services_dir, project_model)
    _write_handlers_go(handlers_dir, project_model)
    _write_routes_go(routes_dir, project_model)
    _write_routes_md(output_root, project_model)

    return output_root


def _write_go_mod(output_root: Path) -> None:
    content = f"""module {GO_MODULE_NAME}

go 1.22
"""
    (output_root / "go.mod").write_text(content, encoding="utf-8")


def _write_main_go(cmd_dir: Path) -> None:
    content = f"""package main

import (
\t"log"
\t"net/http"

\t"{GO_MODULE_NAME}/internal/routes"
)

func main() {{
\tmux := http.NewServeMux()
\troutes.Register(mux)

\tlog.Println("Go scaffold listening on :8080")
\tif err := http.ListenAndServe(":8080", mux); err != nil {{
\t\tlog.Fatal(err)
\t}}
}}
"""
    (cmd_dir / "main.go").write_text(content, encoding="utf-8")


def _write_models_go(models_dir: Path, project_model: ProjectModel) -> None:
    blocks: list[str] = ["package models\n"]

    if not project_model.models:
        blocks.append(
            """type GenericPayload struct{}
"""
        )
    else:
        for model in project_model.models:
            blocks.append(_build_model_block(model))

    (models_dir / "models.go").write_text("\n".join(blocks), encoding="utf-8")


def _write_services_go(services_dir: Path, project_model: ProjectModel) -> None:
    methods: list[str] = []

    if not project_model.endpoints:
        methods.append(
            """func (s *Service) Health() map[string]string {
\treturn map[string]string{
\t\t"status": "ok",
\t}
}
"""
        )
    else:
        for endpoint in project_model.endpoints:
            service_method = _service_method_name(endpoint)
            methods_literal = ", ".join(endpoint.methods)
            methods.append(
                f"""func (s *Service) {service_method}() map[string]string {{
\treturn map[string]string{{
\t\t"message": "TODO: migrate logic from {endpoint.name}",
\t\t"route": "{endpoint.route}",
\t\t"http_methods": "{methods_literal}",
\t}}
}}
"""
            )

    content = f"""package services

type Service struct{{}}

func New() *Service {{
\treturn &Service{{}}
}}

{chr(10).join(methods)}
"""
    (services_dir / "service.go").write_text(content, encoding="utf-8")


def _write_handlers_go(handlers_dir: Path, project_model: ProjectModel) -> None:
    blocks: list[str] = [
        f"""package handlers

import (
\t"encoding/json"
\t"net/http"

\t"{GO_MODULE_NAME}/internal/services"
)

type Handler struct {{
\tservice *services.Service
}}

func New(service *services.Service) *Handler {{
\treturn &Handler{{service: service}}
}}
"""
    ]

    if not project_model.endpoints:
        blocks.append(
            """func (h *Handler) Health(w http.ResponseWriter, r *http.Request) {
\tw.Header().Set("Content-Type", "application/json")
\t_ = json.NewEncoder(w).Encode(h.service.Health())
}
"""
        )
    else:
        for endpoint in project_model.endpoints:
            blocks.append(_build_handler_block(endpoint))

    (handlers_dir / "handlers.go").write_text("\n".join(blocks), encoding="utf-8")


def _write_routes_go(routes_dir: Path, project_model: ProjectModel) -> None:
    route_lines: list[str] = [
        '\tmux.HandleFunc("/health", handler.Health)',
    ]

    if project_model.endpoints:
        route_lines = []
        for endpoint in project_model.endpoints:
            route_lines.append(
                f'\tmux.HandleFunc("{endpoint.route}", handler.{_handler_name(endpoint.name)})'
            )

    content = f"""package routes

import (
\t"net/http"

\t"{GO_MODULE_NAME}/internal/handlers"
\t"{GO_MODULE_NAME}/internal/services"
)

func Register(mux *http.ServeMux) {{
\tservice := services.New()
\thandler := handlers.New(service)

{chr(10).join(route_lines)}
}}
"""
    (routes_dir / "routes.go").write_text(content, encoding="utf-8")


def _write_routes_md(output_root: Path, project_model: ProjectModel) -> None:
    lines = ["# Detected Java Endpoints", ""]

    if not project_model.endpoints:
        lines.append("No servlet-style or controller endpoints were detected.")
    else:
        for endpoint in project_model.endpoints:
            lines.append(f"## {endpoint.name}")
            lines.append(f"- Route: `{endpoint.route}`")
            lines.append(f"- Methods: {', '.join(endpoint.methods)}")
            if endpoint.request_parameters:
                lines.append(
                    f"- Parameters: {', '.join(_format_parameter_summary(parameter) for parameter in endpoint.request_parameters)}"
                )
            if endpoint.response_model:
                lines.append(f"- Response model: `{endpoint.response_model}`")
            lines.append("")

    (output_root / "routes.md").write_text("\n".join(lines), encoding="utf-8")


def _build_model_block(model: DataModel) -> str:
    struct_name = _exported_name(model.name)
    fields: list[str] = []

    for field in model.fields:
        field_name = _exported_name(field.name)
        go_type = _map_go_type(field.data_type)
        json_name = _json_field_name(field.name)
        fields.append(f"\t{field_name} {go_type} `json:\"{json_name},omitempty\"`")

    if not fields:
        fields.append("\tPlaceholder string `json:\"placeholder,omitempty\"`")

    return f"""type {struct_name} struct {{
{chr(10).join(fields)}
}}
"""


def _build_handler_block(endpoint: Endpoint) -> str:
    handler_name = _handler_name(endpoint.name)
    service_method = _service_method_name(endpoint)
    method_guard = _build_method_guard(endpoint.methods)

    return f"""func (h *Handler) {handler_name}(w http.ResponseWriter, r *http.Request) {{
{method_guard}\tw.Header().Set("Content-Type", "application/json")
\t_ = json.NewEncoder(w).Encode(h.service.{service_method}())
}}
"""


def _build_method_guard(methods: list[str]) -> str:
    normalized_methods = [method.upper() for method in methods]
    if not normalized_methods:
        return ""
    if len(normalized_methods) == 1:
        method = normalized_methods[0]
        return (
            f'\tif r.Method != http.Method{method.title()} {{\n'
            '\t\tw.WriteHeader(http.StatusMethodNotAllowed)\n'
            '\t\treturn\n'
            '\t}\n'
        )

    conditions = " && ".join(
        f"r.Method != http.Method{method.title()}" for method in normalized_methods
    )
    return (
        f"\tif {conditions} {{\n"
        '\t\tw.WriteHeader(http.StatusMethodNotAllowed)\n'
        '\t\treturn\n'
        '\t}\n'
    )


def _service_method_name(endpoint: Endpoint) -> str:
    return _exported_name(_snake_to_pascal(_to_snake_case(endpoint.name)))


def _handler_name(name: str) -> str:
    return f"{_exported_name(_snake_to_pascal(_to_snake_case(name)))}Handler"


def _exported_name(name: str) -> str:
    cleaned = name.replace(".", "_").replace("-", "_")
    if not cleaned:
        return "GeneratedName"
    return cleaned[:1].upper() + cleaned[1:]


def _snake_to_pascal(name: str) -> str:
    parts = [part for part in name.split("_") if part]
    if not parts:
        return "generated"
    return "".join(part[:1].upper() + part[1:] for part in parts)


def _to_snake_case(name: str) -> str:
    characters: list[str] = []
    previous_lower = False

    for char in name:
        if char in {"-", ".", " "}:
            if characters and characters[-1] != "_":
                characters.append("_")
            previous_lower = False
            continue

        if char.isupper() and previous_lower and characters and characters[-1] != "_":
            characters.append("_")
        characters.append(char.lower())
        previous_lower = char.isalpha() and char.islower()

    return "".join(characters).strip("_")


def _json_field_name(name: str) -> str:
    return _to_snake_case(name)


def _map_go_type(java_type: str) -> str:
    simple_type = java_type.strip().split(".")[-1]
    mapping = {
        "String": "string",
        "int": "int",
        "Integer": "int",
        "long": "int64",
        "Long": "int64",
        "double": "float64",
        "Double": "float64",
        "float": "float32",
        "Float": "float32",
        "boolean": "bool",
        "Boolean": "bool",
        "BigDecimal": "float64",
    }
    return mapping.get(simple_type, "string")


def _format_parameter_summary(parameter: RequestParameter) -> str:
    return f"{parameter.name}:{parameter.location}"
