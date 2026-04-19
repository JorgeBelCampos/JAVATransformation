from __future__ import annotations

from pathlib import Path

from javamigrator.analysis.model import DataModel, Endpoint, ProjectModel, RequestParameter


def generate_python_project(
    project_model: ProjectModel,
    output_path: str = "output/python_project",
) -> Path:
    """Generate a minimal FastAPI scaffold from a language-agnostic project model."""
    output_root = Path(output_path)
    routers_dir = output_root / "routers"
    schemas_dir = output_root / "schemas"
    services_dir = output_root / "services"

    output_root.mkdir(parents=True, exist_ok=True)
    routers_dir.mkdir(parents=True, exist_ok=True)
    schemas_dir.mkdir(parents=True, exist_ok=True)
    services_dir.mkdir(parents=True, exist_ok=True)

    _write_package_init(output_root / "__init__.py")
    _write_package_init(routers_dir / "__init__.py")
    _write_package_init(schemas_dir / "__init__.py")
    _write_package_init(services_dir / "__init__.py")

    _write_main_file(output_root)
    _write_router_module(routers_dir, project_model)
    _write_services_module(services_dir, project_model)
    _write_schemas_module(schemas_dir, project_model)
    _write_requirements(output_root)
    _write_routes_summary(output_root, project_model)

    return output_root


def _write_package_init(file_path: Path) -> None:
    file_path.write_text("", encoding="utf-8")


def _write_main_file(output_root: Path) -> None:
    content = """from fastapi import FastAPI

from routers.api import router as api_router

app = FastAPI(title="Generated Java Migrator API")
app.include_router(api_router)
"""
    (output_root / "main.py").write_text(content, encoding="utf-8")


def _write_router_module(routers_dir: Path, project_model: ProjectModel) -> None:
    endpoint_blocks: list[str] = []
    uses_body_model = any(
        parameter.location == "body"
        for endpoint in project_model.endpoints
        for parameter in endpoint.request_parameters
    )

    for endpoint in project_model.endpoints:
        endpoint_blocks.append(_build_endpoint_block(endpoint, project_model.models))

    if not endpoint_blocks:
        endpoint_blocks.append(
            """@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
"""
        )

    imports = [
        "from fastapi import APIRouter",
        "from services.app_service import AppService",
    ]
    if uses_body_model:
        imports.append("from schemas.models import GenericPayload")

    content = f"""{chr(10).join(imports)}

router = APIRouter()
service = AppService()


{chr(10).join(endpoint_blocks)}
"""
    (routers_dir / "api.py").write_text(content, encoding="utf-8")


def _write_services_module(services_dir: Path, project_model: ProjectModel) -> None:
    service_methods: list[str] = []

    for endpoint in project_model.endpoints:
        method_name = _python_handler_name(endpoint.name, endpoint.methods)
        service_methods.append(
            f"""    def {method_name}(self) -> dict:
        return {{"message": "TODO", "endpoint": "{endpoint.name}", "route": "{endpoint.route}"}}
"""
        )

    if not service_methods:
        service_methods.append(
            """    def health(self) -> dict:
        return {"status": "ok"}
"""
        )

    content = f"""class AppService:
{chr(10).join(service_methods)}
"""
    (services_dir / "app_service.py").write_text(content, encoding="utf-8")


def _write_schemas_module(schemas_dir: Path, project_model: ProjectModel) -> None:
    model_blocks: list[str] = [
        """class GenericPayload(BaseModel):
    pass
"""
    ]

    for model in project_model.models:
        model_blocks.append(_build_schema_block(model))

    content = f"""from pydantic import BaseModel


{chr(10).join(model_blocks)}
"""
    (schemas_dir / "models.py").write_text(content, encoding="utf-8")


def _write_requirements(output_root: Path) -> None:
    content = """fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.0.0
"""
    (output_root / "requirements.txt").write_text(content, encoding="utf-8")


def _write_routes_summary(output_root: Path, project_model: ProjectModel) -> None:
    lines = ["# Generated Python Routes", ""]

    if not project_model.endpoints:
        lines.append("No endpoints detected.")
    else:
        for endpoint in project_model.endpoints:
            parameter_summary = ", ".join(
                f"{parameter.name}:{parameter.location}"
                for parameter in endpoint.request_parameters
            )
            lines.append(
                f"- `{endpoint.route}` -> `{endpoint.name}` ({', '.join(endpoint.methods)})"
            )
            if parameter_summary:
                lines.append(f"  Parameters: {parameter_summary}")

    (output_root / "routes.md").write_text("\n".join(lines), encoding="utf-8")


def _build_endpoint_block(endpoint: Endpoint, models: list[DataModel]) -> str:
    decorator_method = endpoint.methods[0].lower() if endpoint.methods else "get"
    handler_name = _python_handler_name(endpoint.name, endpoint.methods)
    signature_parts = [_build_parameter_signature(parameter, models) for parameter in endpoint.request_parameters]
    signature = ", ".join(part for part in signature_parts if part)
    if signature:
        signature = f", {signature}"

    return f"""@router.{decorator_method}("{endpoint.route}")
async def {handler_name}(service: AppService{signature}) -> dict:
    return service.{handler_name}()
"""


def _build_parameter_signature(
    parameter: RequestParameter,
    models: list[DataModel],
) -> str:
    python_name = _to_snake_case(parameter.name)
    if parameter.location == "body":
        schema_name = _resolve_body_schema_name(parameter, models)
        return f"{python_name}: {schema_name}"
    return f"{python_name}: {_map_python_type(parameter.data_type)} | None = None"


def _resolve_body_schema_name(parameter: RequestParameter, models: list[DataModel]) -> str:
    candidate_names = {
        parameter.data_type,
        parameter.name,
        parameter.name[:1].upper() + parameter.name[1:],
    }
    for model in models:
        if model.name in candidate_names:
            return model.name
    return "GenericPayload"


def _build_schema_block(model: DataModel) -> str:
    fields: list[str] = []

    for field in model.fields:
        fields.append(f"    {field.name}: {_map_python_type(field.data_type)} | None = None")

    if not fields:
        fields.append("    pass")

    return f"""class {model.name}(BaseModel):
{chr(10).join(fields)}
"""


def _map_python_type(java_type: str) -> str:
    normalized = java_type.strip()
    simple_type = normalized.split(".")[-1]
    mapping = {
        "String": "str",
        "int": "int",
        "Integer": "int",
        "long": "int",
        "Long": "int",
        "double": "float",
        "Double": "float",
        "float": "float",
        "Float": "float",
        "boolean": "bool",
        "Boolean": "bool",
        "BigDecimal": "float",
        "LocalDate": "str",
        "LocalDateTime": "str",
        "UUID": "str",
    }
    return mapping.get(simple_type, "str")


def _python_handler_name(endpoint_name: str, methods: list[str]) -> str:
    primary_method = methods[0].lower() if methods else "handle"
    return f"{primary_method}_{_to_snake_case(endpoint_name.replace('.', '_'))}"


def _to_snake_case(name: str) -> str:
    characters: list[str] = []
    for index, char in enumerate(name):
        if char in {"-", ".", " "}:
            characters.append("_")
            continue
        if char.isupper() and index > 0 and not name[index - 1].isupper() and name[index - 1] != "_":
            characters.append("_")
        characters.append(char.lower())
    return "".join(characters)
