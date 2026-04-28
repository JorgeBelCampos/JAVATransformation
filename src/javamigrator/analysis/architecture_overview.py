from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from javamigrator.analysis.architecture_mapper import ArchitectureMap, ArchitectureNode


IGNORED_DIRECTORIES = {
    ".git",
    ".idea",
    ".mvn",
    ".settings",
    "bin",
    "build",
    "dist",
    "node_modules",
    "out",
    "output",
    "target",
}
MAX_TEXT_FILE_SIZE_BYTES = 1_000_000
TEXT_FILE_SUFFIXES = {
    ".java",
    ".jsp",
    ".html",
    ".htm",
    ".css",
    ".js",
    ".xml",
    ".properties",
    ".yml",
    ".yaml",
    ".txt",
}
EXAMPLE_LIMIT = 5
EXTERNAL_LABELS = {
    "database": "Database",
    "external_systems": "External Systems",
    "filesystem": "Filesystem",
    "xml_processing": "XML Processing",
    "crypto_security": "Crypto / Security",
    "messaging": "Messaging",
}
RESOURCE_PATTERNS = {
    "database": [
        re.compile(r"\bjava\.sql\b|\bConnection\b|\bPreparedStatement\b|\bResultSet\b"),
        re.compile(r"\bjavax\.sql\b|\bDataSource\b"),
        re.compile(r"\bJdbcTemplate\b|\bEntityManager\b"),
    ],
    "external_systems": [
        re.compile(r"\bHttpClient\b|\bRestTemplate\b|\bWebClient\b"),
        re.compile(r"\bURLConnection\b|\bHttpURLConnection\b|\bURL\b"),
        re.compile(r"https?://"),
        re.compile(r"\bSOAP\b|\bJAX-WS\b|\bFeignClient\b"),
    ],
    "filesystem": [
        re.compile(r"\bjava\.io\.File\b|\bFileInputStream\b|\bFileOutputStream\b"),
        re.compile(r"\bFiles\."), re.compile(r"\bPath\b|\bPaths\b"),
    ],
    "xml_processing": [
        re.compile(r"\bDocumentBuilder\b|\bDocumentBuilderFactory\b"),
        re.compile(r"\bTransformer\b|\bXPath\b"),
        re.compile(r"\bSAXParser\b|\bXMLConstants\b"),
    ],
    "crypto_security": [
        re.compile(r"\bCipher\b|\bSignature\b|\bKeyStore\b"),
        re.compile(r"\bMessageDigest\b|\bCertificate\b"),
        re.compile(r"\bPrivateKey\b|\bPublicKey\b"),
    ],
    "messaging": [
        re.compile(r"\bJMS\b|\bQueue\b|\bTopic\b"),
        re.compile(r"\bKafka\b|\bRabbitMQ\b|\bActiveMQ\b"),
    ],
}


@dataclass
class ArchitectureComponent:
    id: str
    label: str
    component_type: str
    class_count: int = 0
    files: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    technologies: list[str] = field(default_factory=list)
    hints: list[str] = field(default_factory=list)
    detected: bool = True


@dataclass
class ArchitectureConnection:
    source: str
    target: str
    label: str


@dataclass
class ArchitectureOverview:
    project_path: str
    class_count: int
    relation_count: int
    components: list[ArchitectureComponent] = field(default_factory=list)
    connections: list[ArchitectureConnection] = field(default_factory=list)
    detected_layers: list[str] = field(default_factory=list)
    external_resources: dict[str, list[str]] = field(default_factory=dict)


def build_architecture_overview(
    project_path: str,
    architecture_map: ArchitectureMap,
) -> ArchitectureOverview:
    project_root = Path(project_path)
    file_scan = _scan_project_files(project_root)
    node_lookup = {node.id: node for node in architecture_map.nodes}
    incoming_sources: dict[str, list[ArchitectureNode]] = {}

    for edge in architecture_map.edges:
        source_node = node_lookup.get(edge.source)
        if source_node is None:
            continue
        incoming_sources.setdefault(edge.target, []).append(source_node)

    grouped_nodes: dict[str, list[ArchitectureNode]] = {
        "controllers": [],
        "services": [],
        "dao": [],
        "models": [],
        "utilities": [],
    }

    for node in architecture_map.nodes:
        layer_id = _classify_node(node, incoming_sources.get(node.id, []))
        grouped_nodes[layer_id].append(node)

    components: list[ArchitectureComponent] = []
    components.append(
        ArchitectureComponent(
            id="frontend",
            label="Cliente / Frontend",
            component_type="frontend",
            class_count=file_scan["frontend_file_count"],
            files=file_scan["frontend_files"][:EXAMPLE_LIMIT],
            examples=file_scan["frontend_examples"][:EXAMPLE_LIMIT],
            technologies=file_scan["frontend_technologies"],
            hints=["src/main/webapp"] if file_scan["has_webapp_dir"] else [],
            detected=file_scan["frontend_detected"],
        )
    )

    for layer_id, label in (
        ("controllers", "Controllers / Servlets"),
        ("services", "Services / Business Logic"),
        ("dao", "DAO / Persistence"),
        ("models", "Models / DTOs"),
        ("utilities", "Utilities / Unknown"),
    ):
        components.append(_build_component(layer_id, label, grouped_nodes[layer_id]))

    external_resources = _collect_external_resources(architecture_map, file_scan)
    for resource_id, label in EXTERNAL_LABELS.items():
        hints = external_resources.get(resource_id, [])
        components.append(
            ArchitectureComponent(
                id=resource_id,
                label=label,
                component_type=resource_id,
                class_count=0,
                technologies=hints[:EXAMPLE_LIMIT],
                hints=hints[:EXAMPLE_LIMIT],
                detected=bool(hints),
            )
        )

    connections = _build_overview_connections(components)
    detected_layers = [
        component.label
        for component in components
        if component.detected or component.class_count > 0
    ]

    return ArchitectureOverview(
        project_path=str(project_root),
        class_count=len(architecture_map.nodes),
        relation_count=len(architecture_map.edges),
        components=components,
        connections=connections,
        detected_layers=detected_layers,
        external_resources=external_resources,
    )


def write_architecture_overview_mermaid(
    overview: ArchitectureOverview,
    output_path: str | Path,
) -> Path:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    return _safe_write_text(output_file, _build_mermaid_text(overview))


def write_architecture_overview_markdown(
    overview: ArchitectureOverview,
    output_path: str | Path,
) -> Path:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    mermaid_lines = ["```mermaid", *_build_mermaid_text(overview).splitlines(), "```"]

    lines = [
        "# Architecture Overview",
        "",
        f"- Project: `{overview.project_path}`",
        f"- Classes detected: {overview.class_count}",
        f"- Technical relations detected: {overview.relation_count}",
        f"- Layers detected: {', '.join(overview.detected_layers) if overview.detected_layers else 'None'}",
        "",
        "## Diagram",
        "",
        *mermaid_lines,
        "",
        "## Layers",
        "",
        "| Layer | Classes | Examples |",
        "| --- | ---: | --- |",
    ]

    for component in overview.components:
        if component.id in EXTERNAL_LABELS:
            continue
        examples = ", ".join(component.examples[:EXAMPLE_LIMIT]) or "-"
        lines.append(
            f"| {component.label} | {component.class_count} | {examples} |"
        )

    lines.extend(
        [
            "",
            "## External Resources",
            "",
            "| Resource | Detected | Hints |",
            "| --- | --- | --- |",
        ]
    )

    for resource_id, label in EXTERNAL_LABELS.items():
        hints = overview.external_resources.get(resource_id, [])
        lines.append(
            f"| {label} | {'Yes' if hints else 'No'} | {', '.join(hints[:EXAMPLE_LIMIT]) or '-'} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This overview is based on approximate static analysis.",
            "- The executive diagram is intentionally aggregated by layer and may hide low-level technical relationships.",
        ]
    )

    return _safe_write_text(output_file, "\n".join(lines))


def _classify_node(node: ArchitectureNode, incoming_sources: list[ArchitectureNode]) -> str:
    node_type = node.component_type

    if node_type in {"controller", "servlet", "rest_controller", "endpoint"}:
        return "controllers"
    if node_type in {"service"}:
        return "services"
    if node_type in {"repository"}:
        return "dao"
    if node_type in {"model"}:
        return "models"
    if node_type in {"client"}:
        return "services"
    if node_type in {"config", "util"}:
        return "utilities"

    package_name = (node.package or "").lower()
    if ".dao." in package_name or ".repository." in package_name or ".persistence." in package_name:
        return "dao"
    if ".service." in package_name:
        return "services"

    if any(source.component_type in {"controller", "servlet"} for source in incoming_sources):
        return "services"

    if node.name.endswith(("Bean", "Manager", "Facade", "UseCase")):
        return "services"

    if any(import_path.startswith(("javax.enterprise.", "jakarta.enterprise.", "javax.inject", "jakarta.inject")) for import_path in node.imports):
        return "services"

    if _looks_like_model(node):
        return "models"

    if _has_business_methods(node):
        return "services"

    return "utilities"


def _looks_like_model(node: ArchitectureNode) -> bool:
    if node.name.endswith(("Dto", "DTO", "Entity", "Model", "Request", "Response", "VO", "Bean")):
        return True

    methods = [method for method in node.methods if method]
    if not methods:
        return False

    accessor_methods = [method for method in methods if _is_accessor_method(method)]
    return len(accessor_methods) == len(methods)


def _has_business_methods(node: ArchitectureNode) -> bool:
    business_methods = [
        method for method in node.methods
        if not _is_accessor_method(method) and method not in {"init", "main"}
    ]
    return bool(business_methods)


def _is_accessor_method(method_name: str) -> bool:
    return method_name.startswith(("get", "set", "is"))


def _build_component(
    component_id: str,
    label: str,
    nodes: list[ArchitectureNode],
) -> ArchitectureComponent:
    files = sorted({node.file_path for node in nodes})
    technologies: set[str] = set()
    hints: set[str] = set()

    for node in nodes:
        if node.component_type == "servlet":
            technologies.add("Servlet")
        if node.component_type == "controller":
            technologies.add("Spring MVC")
        if any(import_path.startswith(("javax.enterprise.", "jakarta.enterprise.", "javax.inject", "jakarta.inject")) for import_path in node.imports):
            technologies.add("CDI")
        hints.update(node.database_hints)
        hints.update(node.http_hints)
        hints.update(node.filesystem_hints)
        hints.update(node.security_hints)

    return ArchitectureComponent(
        id=component_id,
        label=label,
        component_type=component_id,
        class_count=len(nodes),
        files=files,
        examples=[node.name for node in nodes[:EXAMPLE_LIMIT]],
        technologies=sorted(technologies),
        hints=sorted(hints)[:EXAMPLE_LIMIT],
        detected=bool(nodes),
    )


def _build_overview_connections(
    components: list[ArchitectureComponent],
) -> list[ArchitectureConnection]:
    component_by_id = {component.id: component for component in components}
    connections: list[ArchitectureConnection] = []

    if component_by_id["frontend"].detected and component_by_id["controllers"].class_count > 0:
        connections.append(ArchitectureConnection("frontend", "controllers", "serves"))
    if component_by_id["controllers"].class_count > 0 and component_by_id["services"].class_count > 0:
        connections.append(ArchitectureConnection("controllers", "services", "calls"))
    if component_by_id["services"].class_count > 0 and component_by_id["dao"].class_count > 0:
        connections.append(ArchitectureConnection("services", "dao", "queries"))
    if component_by_id["dao"].class_count > 0 and component_by_id["database"].detected:
        connections.append(ArchitectureConnection("dao", "database", "stores"))
    if component_by_id["services"].class_count > 0 and component_by_id["external_systems"].detected:
        connections.append(ArchitectureConnection("services", "external_systems", "integrates"))
    if component_by_id["services"].class_count > 0 and component_by_id["filesystem"].detected:
        connections.append(ArchitectureConnection("services", "filesystem", "reads/writes"))
    if component_by_id["services"].class_count > 0 and component_by_id["xml_processing"].detected:
        connections.append(ArchitectureConnection("services", "xml_processing", "parses"))
    if component_by_id["services"].class_count > 0 and component_by_id["crypto_security"].detected:
        connections.append(ArchitectureConnection("services", "crypto_security", "secures"))
    if component_by_id["services"].class_count > 0 and component_by_id["messaging"].detected:
        connections.append(ArchitectureConnection("services", "messaging", "publishes"))

    return connections


def _collect_external_resources(
    architecture_map: ArchitectureMap,
    file_scan: dict[str, object],
) -> dict[str, list[str]]:
    resources = {
        "database": set(),
        "external_systems": set(),
        "filesystem": set(),
        "xml_processing": set(),
        "crypto_security": set(),
        "messaging": set(),
    }

    for node in architecture_map.nodes:
        resources["database"].update(node.database_hints)
        resources["external_systems"].update(node.http_hints)
        resources["filesystem"].update(node.filesystem_hints)

        for hint in node.security_hints:
            if hint in {"DocumentBuilder", "Transformer", "XPath"}:
                resources["xml_processing"].add(hint)
            else:
                resources["crypto_security"].add(hint)

        for import_path in node.imports:
            lowered = import_path.lower()
            if any(token in lowered for token in ("jms", "kafka", "rabbit", "activemq")):
                resources["messaging"].add(import_path.rsplit(".", 1)[-1])

    for resource_id, hints in file_scan["resource_hints"].items():
        resources[resource_id].update(hints)

    return {
        resource_id: sorted(values)
        for resource_id, values in resources.items()
    }


def _scan_project_files(project_root: Path) -> dict[str, object]:
    frontend_detected = False
    frontend_files: list[str] = []
    frontend_examples: set[str] = set()
    frontend_technologies: set[str] = set()
    has_webapp_dir = (project_root / "src" / "main" / "webapp").exists()
    resource_hints = {
        "database": set(),
        "external_systems": set(),
        "filesystem": set(),
        "xml_processing": set(),
        "crypto_security": set(),
        "messaging": set(),
    }

    for current_root, dir_names, file_names in os.walk(project_root):
        dir_names[:] = [directory for directory in dir_names if directory not in IGNORED_DIRECTORIES]

        for file_name in file_names:
            suffix = Path(file_name).suffix.lower()
            file_path = Path(current_root) / file_name

            if suffix in {".jsp", ".html", ".htm", ".css", ".js"}:
                frontend_detected = True
                frontend_files.append(str(file_path))
                frontend_examples.add(file_name)
                if suffix == ".jsp":
                    frontend_technologies.add("JSP")
                elif suffix in {".html", ".htm"}:
                    frontend_technologies.add("HTML")
                elif suffix == ".css":
                    frontend_technologies.add("CSS")
                elif suffix == ".js":
                    frontend_technologies.add("JavaScript")

            if suffix not in TEXT_FILE_SUFFIXES:
                continue

            try:
                if file_path.stat().st_size > MAX_TEXT_FILE_SIZE_BYTES:
                    continue
            except OSError:
                continue

            content = _read_text_file(file_path)
            if not content:
                continue

            for resource_id, patterns in RESOURCE_PATTERNS.items():
                for pattern in patterns:
                    match = pattern.search(content)
                    if match:
                        resource_hints[resource_id].add(match.group(0))

    if has_webapp_dir:
        frontend_detected = True
        frontend_technologies.add("WebApp")

    return {
        "frontend_detected": frontend_detected or has_webapp_dir,
        "frontend_file_count": len(frontend_files),
        "frontend_files": frontend_files,
        "frontend_examples": sorted(frontend_examples),
        "frontend_technologies": sorted(frontend_technologies),
        "has_webapp_dir": has_webapp_dir,
        "resource_hints": resource_hints,
    }


def _component_label(component: ArchitectureComponent) -> str:
    count_text = f"{component.class_count} clases" if component.class_count != 1 else "1 clase"
    examples = ", ".join(component.examples[:3]) if component.examples else "No detectado"
    return f"{component.label}<br/>{count_text}<br/>{examples}"


def _alias(component_id: str) -> str:
    aliases = {
        "frontend": "FRONT",
        "controllers": "CTRL",
        "services": "SVC",
        "dao": "DAO",
        "database": "DB",
        "external_systems": "EXT",
        "filesystem": "FS",
        "xml_processing": "XML",
        "crypto_security": "SEC",
        "messaging": "MSG",
    }
    return aliases.get(component_id, component_id.upper())


def _resource_alias(resource_id: str) -> str:
    return _alias(resource_id)


def _build_mermaid_text(overview: ArchitectureOverview) -> str:
    component_by_id = {component.id: component for component in overview.components}
    frontend = component_by_id["frontend"]
    controllers = component_by_id["controllers"]
    services = component_by_id["services"]
    dao = component_by_id["dao"]

    lines = ["flowchart LR"]
    lines.append('    subgraph CLIENT["Cliente / Frontend"]')
    lines.append(f'        FRONT["{_component_label(frontend)}"]')
    lines.append("    end")
    lines.append("")
    lines.append('    subgraph APP["Aplicación Java"]')
    lines.append(f'        CTRL["{_component_label(controllers)}"]')
    lines.append(f'        SVC["{_component_label(services)}"]')
    lines.append(f'        DAO["{_component_label(dao)}"]')
    lines.append("    end")

    for resource_id in (
        "database",
        "external_systems",
        "filesystem",
        "xml_processing",
        "crypto_security",
        "messaging",
    ):
        component = component_by_id[resource_id]
        if not component.detected:
            continue
        if resource_id == "database":
            lines.append(f'    DB[("{component.label}")]')
        else:
            lines.append(f'    {_resource_alias(resource_id)}["{component.label}"]')

    lines.append("")
    for connection in overview.connections:
        lines.append(f"    {_alias(connection.source)} --> {_alias(connection.target)}")

    return "\n".join(lines)


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


def _safe_write_text(output_file: Path, content: str) -> Path:
    try:
        output_file.write_text(content, encoding="utf-8")
        return output_file
    except PermissionError:
        fallback_file = _next_available_output_path(output_file)
        fallback_file.write_text(content, encoding="utf-8")
        return fallback_file


def _next_available_output_path(output_file: Path) -> Path:
    for index in range(1, 1000):
        candidate = output_file.with_name(
            f"{output_file.stem}_{index:02d}{output_file.suffix}"
        )
        if not candidate.exists():
            return candidate

    return output_file.with_name(
        f"{output_file.stem}_{os.getpid()}{output_file.suffix}"
    )
