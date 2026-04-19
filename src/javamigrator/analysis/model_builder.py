from __future__ import annotations

import re
from pathlib import Path

from javamigrator.analysis.model import (
    DataModel,
    Endpoint,
    ExceptionModel,
    ExternalDependency,
    HttpIntegrationHint,
    ModelField,
    PersistenceHint,
    ProjectModel,
    RequestParameter,
    Service,
)


SERVLET_CLASS_PATTERN = re.compile(
    r"class\s+(?P<class_name>[A-Za-z_][A-Za-z0-9_]*)\s+extends\s+HttpServlet"
)
WEB_SERVLET_PATTERN = re.compile(
    r'@WebServlet\s*\(\s*(?:value\s*=\s*)?"(?P<route>[^"]+)"'
)
METHOD_PATTERNS = {
    "GET": re.compile(r"\bdoGet\s*\("),
    "POST": re.compile(r"\bdoPost\s*\("),
    "PUT": re.compile(r"\bdoPut\s*\("),
    "DELETE": re.compile(r"\bdoDelete\s*\("),
    "PATCH": re.compile(r"\bdoPatch\s*\("),
}
CLASS_DECLARATION_PATTERN = re.compile(
    r"\b(class|interface|enum)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
)
IMPORT_PATTERN = re.compile(r"^\s*import\s+(?P<import_path>[A-Za-z0-9_.*]+);", re.MULTILINE)
FIELD_PATTERN = re.compile(
    r"^\s*(?:private|protected|public)\s+(?:static\s+|final\s+|transient\s+|volatile\s+)*"
    r"(?P<type>[A-Za-z0-9_<>,.?[\]]+)\s+(?P<name>[a-zA-Z_][A-Za-z0-9_]*)\s*(?:=.*)?;$",
    re.MULTILINE,
)
METHOD_SIGNATURE_PATTERN = re.compile(
    r"^\s*(?:public|protected|private)\s+(?:static\s+|final\s+|synchronized\s+)*"
    r"(?P<return_type>[A-Za-z0-9_<>,.?[\]]+)\s+"
    r"(?P<method_name>[A-Za-z_][A-Za-z0-9_]*)\s*\((?P<params>[^)]*)\)"
    r"(?:\s+throws\s+(?P<throws>[A-Za-z0-9_.,\s]+))?",
    re.MULTILINE,
)
REQUEST_PARAMETER_CALL_PATTERN = re.compile(
    r"\.(?P<call>getParameter|getHeader|getAttribute)\s*\(\s*\"(?P<name>[^\"]+)\"\s*\)"
)
SERVICE_CALL_PATTERN = re.compile(
    r"\b(?P<name>[a-zA-Z_][A-Za-z0-9_]*)\.(?P<method>[a-zA-Z_][A-Za-z0-9_]*)\s*\("
)
EXCEPTION_EXTENDS_PATTERN = re.compile(
    r"class\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s+extends\s+(?P<base>[A-Za-z_][A-Za-z0-9_]*)"
)
NEW_EXCEPTION_PATTERN = re.compile(r"new\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*Exception)\s*\(")
SQL_PATTERN = re.compile(r"\b(SELECT|INSERT|UPDATE|DELETE)\b", re.IGNORECASE)

SPRING_CONTROLLER_PATTERN = re.compile(r"@(?:RestController|Controller)\b")
SPRING_MAPPING_PATTERN = re.compile(
    r"@(?P<annotation>RequestMapping|GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)\s*"
    r"(?:\((?P<args>.*?)\))?",
    re.DOTALL,
)
REQUEST_METHOD_PATTERN = re.compile(
    r"RequestMethod\.(GET|POST|PUT|DELETE|PATCH)",
    re.IGNORECASE,
)
STRING_LITERAL_PATTERN = re.compile(r'"([^"]+)"')
PATH_ARGUMENT_PATTERN = re.compile(
    r"(?:path|value)\s*=\s*(?P<value>\{[^}]*\}|\"[^\"]*\")",
    re.DOTALL,
)
SPRING_PARAMETER_PATTERN = re.compile(
    r"@(?P<annotation>PathVariable|RequestParam|RequestBody)"
    r"(?:\((?P<args>[^)]*)\))?\s*"
    r"(?:(?:final|@Valid|@NotNull|@Nullable)\s+)*"
    r"(?P<data_type>[A-Za-z0-9_<>,.?[\]]+)\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
)
REQUIRED_FALSE_PATTERN = re.compile(r"required\s*=\s*false", re.IGNORECASE)
NAME_ARGUMENT_PATTERN = re.compile(r'(?:value|name)\s*=\s*"([^"]+)"')

MODEL_SUFFIXES = ("Dto", "DTO", "Request", "Response", "Model", "Entity", "VO", "Bean")
SERVICE_SUFFIXES = ("Service", "Manager", "Facade", "UseCase")
PERSISTENCE_HINT_PATTERNS = {
    "jpa": re.compile(r"\bEntityManager\b|\bJpaRepository\b|\bCrudRepository\b|@Entity\b|@Repository\b"),
    "jdbc": re.compile(r"\bJdbcTemplate\b|\bDataSource\b|\bPreparedStatement\b|\bDriverManager\b|\bConnection\b"),
    "hibernate": re.compile(r"\bSessionFactory\b|\bSession\b|\bHibernate\b"),
    "sql": SQL_PATTERN,
}
HTTP_INTEGRATION_PATTERNS = {
    "rest_template": re.compile(r"\bRestTemplate\b"),
    "web_client": re.compile(r"\bWebClient\b"),
    "http_client": re.compile(r"\bHttpClient\b|\bCloseableHttpClient\b|\bOkHttpClient\b"),
    "feign": re.compile(r"\bFeignClient\b"),
    "url_connection": re.compile(r"\bHttpURLConnection\b|\bURLConnection\b"),
}
IGNORED_SERVICE_CALL_NAMES = {
    "request",
    "response",
    "req",
    "resp",
    "this",
    "super",
    "System",
}


def build_project_model(project_path: str) -> ProjectModel:
    """Build a language-agnostic project model from Java source files."""
    root = Path(project_path)
    endpoints: list[Endpoint] = []
    models: list[DataModel] = []
    services: list[Service] = []
    external_dependencies: list[ExternalDependency] = []
    exceptions: list[ExceptionModel] = []
    persistence_hints: list[PersistenceHint] = []
    http_integrations: list[HttpIntegrationHint] = []

    for java_file in root.rglob("*.java"):
        content = _read_text_file(java_file)
        if not content:
            continue

        source_file = str(java_file)
        imports = _extract_imports(content)
        class_name = _extract_class_name(content)

        external_dependencies.extend(_build_external_dependencies(imports))
        persistence_hints.extend(_detect_persistence_hints(content, source_file))
        http_integrations.extend(_detect_http_integrations(content, source_file))
        endpoints.extend(_build_endpoints(content, class_name, source_file))

        data_model = _build_data_model(content, class_name, source_file)
        if data_model is not None:
            models.append(data_model)

        service = _build_service(content, class_name, source_file)
        if service is not None:
            services.append(service)

        exceptions.extend(_build_exception_models(content, class_name, source_file))

    endpoints.sort(key=lambda endpoint: (endpoint.route, endpoint.name))
    models.sort(key=lambda item: item.name)
    services.sort(key=lambda item: item.name)
    external_dependencies.sort(key=lambda item: (item.category, item.name, item.import_path))
    exceptions.sort(key=lambda item: item.name)
    persistence_hints.sort(key=lambda item: (item.kind, item.details, item.source_file or ""))
    http_integrations.sort(key=lambda item: (item.kind, item.details, item.source_file or ""))

    return ProjectModel(
        endpoints=_deduplicate_endpoints(endpoints),
        models=_deduplicate_models(models),
        services=_deduplicate_services(services),
        external_dependencies=_deduplicate_external_dependencies(external_dependencies),
        exceptions=_deduplicate_exceptions(exceptions),
        persistence_hints=_deduplicate_persistence_hints(persistence_hints),
        http_integrations=_deduplicate_http_integrations(http_integrations),
    )


def _build_endpoints(content: str, class_name: str | None, source_file: str) -> list[Endpoint]:
    endpoints: list[Endpoint] = []

    servlet_endpoint = _build_servlet_endpoint(content, class_name, source_file)
    if servlet_endpoint is not None:
        endpoints.append(servlet_endpoint)

    endpoints.extend(_build_spring_endpoints(content, class_name, source_file))
    return endpoints


def _build_servlet_endpoint(
    content: str,
    class_name: str | None,
    source_file: str,
) -> Endpoint | None:
    if class_name is None:
        return None

    class_match = SERVLET_CLASS_PATTERN.search(content)
    if not class_match:
        return None

    route_match = WEB_SERVLET_PATTERN.search(content)
    route = route_match.group("route") if route_match else f"/{class_name.lower()}"
    methods = [
        method_name
        for method_name, pattern in METHOD_PATTERNS.items()
        if pattern.search(content)
    ]
    if not methods:
        methods = ["GET"]

    return Endpoint(
        name=class_name,
        route=route,
        methods=methods,
        request_parameters=_extract_servlet_request_parameters(content),
        response_model=_guess_response_model(content),
        service_calls=_extract_service_calls(content),
        exceptions=_extract_exception_names(content),
        source_file=source_file,
    )


def _build_spring_endpoints(
    content: str,
    class_name: str | None,
    source_file: str,
) -> list[Endpoint]:
    if class_name is None:
        return []

    class_match = CLASS_DECLARATION_PATTERN.search(content)
    if class_match is None:
        return []

    class_annotation_block = _extract_annotation_block_before(content, class_match.start())
    if not SPRING_CONTROLLER_PATTERN.search(class_annotation_block):
        return []

    class_routes, class_methods = _extract_mapping_info(class_annotation_block)
    if not class_routes:
        class_routes = [""]

    endpoints: list[Endpoint] = []

    for method_match in METHOD_SIGNATURE_PATTERN.finditer(content):
        method_name = method_match.group("method_name").strip()
        if method_name in {"doGet", "doPost", "doPut", "doDelete", "doPatch"}:
            continue

        method_annotation_block = _extract_annotation_block_before(content, method_match.start())
        method_routes, method_methods = _extract_mapping_info(method_annotation_block)
        if not method_routes and not method_methods:
            continue

        combined_methods = method_methods or class_methods or ["GET"]
        if not method_routes:
            method_routes = [""]

        method_body = _extract_method_body(content, method_match)
        request_parameters = _extract_spring_request_parameters(method_match.group("params"))

        for class_route in class_routes:
            for method_route in method_routes:
                endpoints.append(
                    Endpoint(
                        name=f"{class_name}.{method_name}",
                        route=_join_routes(class_route, method_route),
                        methods=combined_methods,
                        request_parameters=request_parameters,
                        response_model=_guess_response_model(method_body or method_match.group(0)),
                        service_calls=_extract_service_calls(method_body or ""),
                        exceptions=_extract_exception_names(method_body or method_match.group(0)),
                        source_file=source_file,
                    )
                )

    return endpoints


def _build_data_model(content: str, class_name: str | None, source_file: str) -> DataModel | None:
    if class_name is None:
        return None
    if not _looks_like_data_model(content, class_name):
        return None

    kind = "entity" if "@Entity" in content or class_name.endswith("Entity") else "dto"
    fields = [
        ModelField(name=field_name, data_type=data_type)
        for data_type, field_name in _extract_fields(content)
    ]

    return DataModel(
        name=class_name,
        fields=fields,
        kind=kind,
        source_file=source_file,
    )


def _build_service(content: str, class_name: str | None, source_file: str) -> Service | None:
    if class_name is None:
        return None
    if not _looks_like_service(content, class_name):
        return None

    methods = [
        method_name
        for method_name, return_type, _ in _extract_method_signatures(content)
        if method_name not in {"doGet", "doPost", "doPut", "doDelete", "doPatch"} and return_type != "class"
    ]
    dependencies = _extract_service_dependencies(content)

    return Service(
        name=class_name,
        methods=sorted(dict.fromkeys(methods)),
        dependencies=sorted(dict.fromkeys(dependencies)),
        source_file=source_file,
    )


def _build_exception_models(
    content: str,
    class_name: str | None,
    source_file: str,
) -> list[ExceptionModel]:
    detected: list[ExceptionModel] = []

    if class_name is not None:
        extends_match = EXCEPTION_EXTENDS_PATTERN.search(content)
        if extends_match and "Exception" in extends_match.group("base"):
            detected.append(
                ExceptionModel(
                    name=class_name,
                    kind="custom",
                    source_file=source_file,
                )
            )

    for exception_name in _extract_exception_names(content):
        detected.append(
            ExceptionModel(
                name=exception_name,
                kind="usage",
                source_file=source_file,
            )
        )

    return detected


def _extract_imports(content: str) -> list[str]:
    return [match.group("import_path") for match in IMPORT_PATTERN.finditer(content)]


def _extract_class_name(content: str) -> str | None:
    match = CLASS_DECLARATION_PATTERN.search(content)
    return match.group("name") if match else None


def _extract_fields(content: str) -> list[tuple[str, str]]:
    fields: list[tuple[str, str]] = []
    for match in FIELD_PATTERN.finditer(content):
        fields.append((match.group("type").strip(), match.group("name").strip()))
    return fields


def _extract_method_signatures(content: str) -> list[tuple[str, str, str]]:
    signatures: list[tuple[str, str, str]] = []
    for match in METHOD_SIGNATURE_PATTERN.finditer(content):
        signatures.append(
            (
                match.group("method_name").strip(),
                match.group("return_type").strip(),
                (match.group("throws") or "").strip(),
            )
        )
    return signatures


def _extract_servlet_request_parameters(content: str) -> list[RequestParameter]:
    parameters: list[RequestParameter] = []
    seen: set[tuple[str, str]] = set()

    for match in REQUEST_PARAMETER_CALL_PATTERN.finditer(content):
        method_call = match.group("call")
        location = {
            "getParameter": "query",
            "getHeader": "header",
            "getAttribute": "attribute",
        }.get(method_call, "query")
        parameter = RequestParameter(
            name=match.group("name"),
            location=location,
        )
        key = (parameter.name, parameter.location)
        if key in seen:
            continue
        seen.add(key)
        parameters.append(parameter)

    return parameters


def _extract_spring_request_parameters(parameter_text: str) -> list[RequestParameter]:
    parameters: list[RequestParameter] = []

    for raw_parameter in _split_parameter_list(parameter_text):
        match = SPRING_PARAMETER_PATTERN.search(raw_parameter)
        if match is None:
            continue

        annotation = match.group("annotation")
        args = (match.group("args") or "").strip()
        parameter_name = _resolve_spring_parameter_name(args, match.group("name"))
        parameters.append(
            RequestParameter(
                name=parameter_name,
                location=_spring_parameter_location(annotation),
                data_type=match.group("data_type").strip(),
                required=_spring_parameter_required(annotation, args),
            )
        )

    return parameters


def _guess_response_model(content: str) -> str | None:
    for model_suffix in MODEL_SUFFIXES:
        match = re.search(
            rf"\bnew\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*{re.escape(model_suffix)})\s*\(",
            content,
        )
        if match:
            return match.group("name")
    return None


def _extract_service_calls(content: str) -> list[str]:
    calls: list[str] = []
    seen: set[str] = set()

    for match in SERVICE_CALL_PATTERN.finditer(content):
        call_name = match.group("name")
        if call_name in IGNORED_SERVICE_CALL_NAMES:
            continue
        if not call_name.lower().endswith(("service", "manager", "facade", "client")):
            continue

        call_signature = f"{call_name}.{match.group('method')}"
        if call_signature in seen:
            continue
        seen.add(call_signature)
        calls.append(call_signature)

    return calls


def _extract_exception_names(content: str) -> list[str]:
    exception_names: list[str] = []

    for _, _, throws_clause in _extract_method_signatures(content):
        if not throws_clause:
            continue
        for part in throws_clause.split(","):
            name = part.strip()
            if name:
                exception_names.append(name)

    for match in NEW_EXCEPTION_PATTERN.finditer(content):
        exception_names.append(match.group("name"))

    return sorted(dict.fromkeys(exception_names))


def _build_external_dependencies(imports: list[str]) -> list[ExternalDependency]:
    dependencies: list[ExternalDependency] = []

    for import_path in imports:
        if import_path.startswith(("java.", "javax.", "jakarta.")):
            continue

        category = "library"
        if import_path.startswith("org.springframework."):
            category = "framework"
        elif any(
            token in import_path.lower()
            for token in ("http", "client", "feign", "retrofit", "okhttp")
        ):
            category = "integration"
        elif any(
            token in import_path.lower()
            for token in ("jdbc", "jpa", "hibernate", "repository", "persistence")
        ):
            category = "database"

        dependencies.append(
            ExternalDependency(
                name=import_path.split(".")[-1],
                import_path=import_path,
                category=category,
            )
        )

    return dependencies


def _detect_persistence_hints(content: str, source_file: str) -> list[PersistenceHint]:
    hints: list[PersistenceHint] = []

    for kind, pattern in PERSISTENCE_HINT_PATTERNS.items():
        if not pattern.search(content):
            continue
        hints.append(
            PersistenceHint(
                kind=kind,
                details=_first_match_text(pattern, content),
                source_file=source_file,
            )
        )

    return hints


def _detect_http_integrations(content: str, source_file: str) -> list[HttpIntegrationHint]:
    hints: list[HttpIntegrationHint] = []

    for kind, pattern in HTTP_INTEGRATION_PATTERNS.items():
        if not pattern.search(content):
            continue
        hints.append(
            HttpIntegrationHint(
                kind=kind,
                details=_first_match_text(pattern, content),
                source_file=source_file,
            )
        )

    return hints


def _looks_like_data_model(content: str, class_name: str) -> bool:
    if class_name.endswith(MODEL_SUFFIXES):
        return True
    if "@Entity" in content:
        return True
    return False


def _looks_like_service(content: str, class_name: str) -> bool:
    if class_name.endswith(SERVICE_SUFFIXES):
        return True
    return "@Service" in content or "@Component" in content


def _extract_service_dependencies(content: str) -> list[str]:
    dependencies: list[str] = []

    for data_type, _ in _extract_fields(content):
        if data_type.endswith(SERVICE_SUFFIXES) or data_type.endswith(("Repository", "Client")):
            dependencies.append(data_type)

    return dependencies


def _extract_mapping_info(annotation_block: str) -> tuple[list[str], list[str]]:
    routes: list[str] = []
    methods: list[str] = []

    for match in SPRING_MAPPING_PATTERN.finditer(annotation_block):
        annotation = match.group("annotation")
        args = (match.group("args") or "").strip()
        routes.extend(_extract_routes_from_mapping_args(args))
        methods.extend(_extract_methods_from_mapping(annotation, args))

    return (
        _normalize_unique(routes) or [""],
        _normalize_unique(methods),
    )


def _extract_routes_from_mapping_args(args: str) -> list[str]:
    if not args:
        return [""]

    path_match = PATH_ARGUMENT_PATTERN.search(args)
    if path_match:
        return _extract_string_values(path_match.group("value")) or [""]

    bare_values = _extract_string_values(args)
    return bare_values or [""]


def _extract_methods_from_mapping(annotation: str, args: str) -> list[str]:
    fixed_methods = {
        "GetMapping": ["GET"],
        "PostMapping": ["POST"],
        "PutMapping": ["PUT"],
        "DeleteMapping": ["DELETE"],
        "PatchMapping": ["PATCH"],
    }
    if annotation in fixed_methods:
        return fixed_methods[annotation]
    return [method.upper() for method in REQUEST_METHOD_PATTERN.findall(args)]


def _extract_annotation_block_before(content: str, position: int) -> str:
    lines = content[:position].splitlines()
    collected: list[str] = []

    for line in reversed(lines):
        stripped = line.strip()
        if not stripped:
            if collected:
                break
            continue
        if stripped.startswith("@") or stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
            collected.append(line)
            continue
        if collected:
            break

    return "\n".join(reversed(collected))


def _extract_method_body(content: str, method_match: re.Match[str]) -> str:
    start = content.find("{", method_match.end())
    if start == -1:
        return method_match.group(0)

    end = _find_matching_brace(content, start)
    if end == -1:
        return content[start:]

    return content[start:end + 1]


def _find_matching_brace(content: str, start_index: int) -> int:
    depth = 0

    for index in range(start_index, len(content)):
        char = content[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index

    return -1


def _split_parameter_list(parameter_text: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0

    for char in parameter_text:
        if char in "(<[{":
            depth += 1
        elif char in ")>]}":
            depth = max(0, depth - 1)

        if char == "," and depth == 0:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
            continue

        current.append(char)

    tail = "".join(current).strip()
    if tail:
        parts.append(tail)

    return parts


def _resolve_spring_parameter_name(args: str, fallback_name: str) -> str:
    if not args:
        return fallback_name

    name_match = NAME_ARGUMENT_PATTERN.search(args)
    if name_match:
        return name_match.group(1)

    string_values = _extract_string_values(args)
    if string_values:
        return string_values[0]

    return fallback_name


def _spring_parameter_location(annotation: str) -> str:
    return {
        "PathVariable": "path",
        "RequestParam": "query",
        "RequestBody": "body",
    }.get(annotation, "query")


def _spring_parameter_required(annotation: str, args: str) -> bool:
    if annotation == "RequestBody":
        return not REQUIRED_FALSE_PATTERN.search(args)
    if annotation in {"PathVariable", "RequestParam"}:
        return not REQUIRED_FALSE_PATTERN.search(args)
    return False


def _extract_string_values(value: str) -> list[str]:
    return [match.group(1).strip() for match in STRING_LITERAL_PATTERN.finditer(value)]


def _join_routes(base_route: str, method_route: str) -> str:
    base = (base_route or "").strip()
    method = (method_route or "").strip()

    if not base and not method:
        return "/"
    if not base:
        return _normalize_route(method)
    if not method:
        return _normalize_route(base)

    return _normalize_route(f"{base.rstrip('/')}/{method.lstrip('/')}")


def _normalize_route(route: str) -> str:
    normalized = route.strip()
    if not normalized:
        return "/"
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    return normalized


def _normalize_unique(values: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()

    for value in values:
        normalized = value.strip()
        if normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)

    return ordered


def _first_match_text(pattern: re.Pattern[str], content: str) -> str:
    match = pattern.search(content)
    if match is None:
        return pattern.pattern
    return match.group(0)


def _read_text_file(file_path: Path) -> str | None:
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return file_path.read_text(encoding="latin-1")
        except UnicodeDecodeError:
            return None
    except OSError:
        return None


def _deduplicate_endpoints(endpoints: list[Endpoint]) -> list[Endpoint]:
    deduplicated: list[Endpoint] = []
    seen: set[tuple[str, str, tuple[str, ...]]] = set()

    for endpoint in endpoints:
        key = (
            endpoint.name,
            endpoint.route,
            tuple(endpoint.methods),
        )
        if key in seen:
            continue
        seen.add(key)
        deduplicated.append(endpoint)

    return deduplicated


def _deduplicate_models(models: list[DataModel]) -> list[DataModel]:
    deduplicated: list[DataModel] = []
    seen: set[tuple[str, str | None]] = set()

    for model in models:
        key = (model.name, model.source_file)
        if key in seen:
            continue
        seen.add(key)
        deduplicated.append(model)

    return deduplicated


def _deduplicate_services(services: list[Service]) -> list[Service]:
    deduplicated: list[Service] = []
    seen: set[tuple[str, str | None]] = set()

    for service in services:
        key = (service.name, service.source_file)
        if key in seen:
            continue
        seen.add(key)
        deduplicated.append(service)

    return deduplicated


def _deduplicate_external_dependencies(
    dependencies: list[ExternalDependency],
) -> list[ExternalDependency]:
    deduplicated: list[ExternalDependency] = []
    seen: set[tuple[str, str, str]] = set()

    for dependency in dependencies:
        key = (dependency.name, dependency.import_path, dependency.category)
        if key in seen:
            continue
        seen.add(key)
        deduplicated.append(dependency)

    return deduplicated


def _deduplicate_exceptions(exceptions: list[ExceptionModel]) -> list[ExceptionModel]:
    deduplicated: list[ExceptionModel] = []
    seen: set[tuple[str, str, str | None]] = set()

    for exception in exceptions:
        key = (exception.name, exception.kind, exception.source_file)
        if key in seen:
            continue
        seen.add(key)
        deduplicated.append(exception)

    return deduplicated


def _deduplicate_persistence_hints(
    hints: list[PersistenceHint],
) -> list[PersistenceHint]:
    deduplicated: list[PersistenceHint] = []
    seen: set[tuple[str, str, str | None]] = set()

    for hint in hints:
        key = (hint.kind, hint.details, hint.source_file)
        if key in seen:
            continue
        seen.add(key)
        deduplicated.append(hint)

    return deduplicated


def _deduplicate_http_integrations(
    hints: list[HttpIntegrationHint],
) -> list[HttpIntegrationHint]:
    deduplicated: list[HttpIntegrationHint] = []
    seen: set[tuple[str, str, str | None]] = set()

    for hint in hints:
        key = (hint.kind, hint.details, hint.source_file)
        if key in seen:
            continue
        seen.add(key)
        deduplicated.append(hint)

    return deduplicated
