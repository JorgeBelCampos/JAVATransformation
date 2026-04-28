from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path


IMPORT_PATTERN = re.compile(r"^\s*import\s+([^;]+);", re.MULTILINE)
PACKAGE_PATTERN = re.compile(r"^\s*package\s+([^;]+);", re.MULTILINE)
CLASS_PATTERN = re.compile(
    r"\b(?:public\s+|protected\s+|private\s+)?(?:abstract\s+|final\s+)?"
    r"(class|interface|enum)\s+(?P<name>[A-Z][A-Za-z0-9_]*)"
)
METHOD_PATTERN = re.compile(
    r"^\s*(?:public|protected|private)\s+(?:static\s+|final\s+|synchronized\s+)*"
    r"[A-Za-z0-9_<>,.?[\]]+\s+(?P<name>[a-zA-Z_][A-Za-z0-9_]*)\s*\(",
    re.MULTILINE,
)
FIELD_PATTERN = re.compile(
    r"^\s*(?:private|protected|public)\s+(?:static\s+|final\s+|transient\s+|volatile\s+)*"
    r"(?P<type>[A-Z][A-Za-z0-9_<>,.?[\]]*)\s+(?P<name>[a-zA-Z_][A-Za-z0-9_]*)\s*(?:=.*)?;$",
    re.MULTILINE,
)
CALL_SITE_PATTERN = re.compile(
    r"\b(?P<receiver>[A-Za-z_][A-Za-z0-9_]*)\.(?P<method>[a-zA-Z_][A-Za-z0-9_]*)\s*\("
)

DATABASE_HINT_PATTERNS = {
    "java.sql": re.compile(r"\bjava\.sql\b|\bConnection\b|\bPreparedStatement\b|\bResultSet\b"),
    "javax.sql": re.compile(r"\bjavax\.sql\b|\bDataSource\b"),
    "JdbcTemplate": re.compile(r"\bJdbcTemplate\b"),
    "EntityManager": re.compile(r"\bEntityManager\b"),
    "Repository": re.compile(r"\b@Repository\b|\bRepository\b|\bJpaRepository\b|\bCrudRepository\b"),
}
HTTP_HINT_PATTERNS = {
    "HttpClient": re.compile(r"\bHttpClient\b"),
    "RestTemplate": re.compile(r"\bRestTemplate\b"),
    "WebClient": re.compile(r"\bWebClient\b"),
    "URLConnection": re.compile(r"\bURLConnection\b|\bHttpURLConnection\b"),
}
FILESYSTEM_HINT_PATTERNS = {
    "java.io.File": re.compile(r"\bjava\.io\.File\b|\bnew\s+File\s*\("),
    "java.nio.file.Files": re.compile(r"\bjava\.nio\.file\.Files\b|\bFiles\."),
    "Path": re.compile(r"\bjava\.nio\.file\.Path\b|\bPath\b"),
}
SECURITY_HINT_PATTERNS = {
    "DocumentBuilder": re.compile(r"\bDocumentBuilder\b"),
    "Transformer": re.compile(r"\bTransformer\b"),
    "XPath": re.compile(r"\bXPath\b"),
    "Cipher": re.compile(r"\bCipher\b"),
    "Signature": re.compile(r"\bSignature\b"),
    "KeyStore": re.compile(r"\bKeyStore\b"),
}

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
MAX_JAVA_FILE_SIZE_BYTES = 2_000_000


@dataclass
class ArchitectureNode:
    id: str
    name: str
    file_path: str
    package: str | None
    component_type: str
    methods: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    database_hints: list[str] = field(default_factory=list)
    http_hints: list[str] = field(default_factory=list)
    filesystem_hints: list[str] = field(default_factory=list)
    security_hints: list[str] = field(default_factory=list)


@dataclass
class ArchitectureEdge:
    source: str
    target: str
    edge_type: str
    details: str | None = None


@dataclass
class ArchitectureMap:
    nodes: list[ArchitectureNode] = field(default_factory=list)
    edges: list[ArchitectureEdge] = field(default_factory=list)


def build_architecture_map(project_path: str) -> ArchitectureMap:
    root = Path(project_path)
    nodes: list[ArchitectureNode] = []
    raw_contents: dict[str, str] = {}
    field_types_by_node: dict[str, dict[str, str]] = {}
    class_names_by_node: dict[str, str] = {}
    qualified_names_by_node: dict[str, str] = {}

    for java_file in _iter_java_files(root):
        content = _read_text_file(java_file)
        if not content:
            continue

        class_match = CLASS_PATTERN.search(content)
        if class_match is None:
            continue

        class_name = class_match.group("name")
        package_name = _extract_package_name(content)
        qualified_name = f"{package_name}.{class_name}" if package_name else class_name
        imports = _extract_imports(content)
        methods = _extract_methods(content)
        field_types = _extract_field_types(content)

        node = ArchitectureNode(
            id=_build_node_id(qualified_name),
            name=class_name,
            file_path=str(java_file),
            package=package_name,
            component_type=_detect_component_type(class_name, content, imports),
            methods=methods,
            imports=imports,
            database_hints=_detect_hints(content, DATABASE_HINT_PATTERNS),
            http_hints=_detect_hints(content, HTTP_HINT_PATTERNS),
            filesystem_hints=_detect_hints(content, FILESYSTEM_HINT_PATTERNS),
            security_hints=_detect_hints(content, SECURITY_HINT_PATTERNS),
        )
        nodes.append(node)
        raw_contents[node.id] = content
        field_types_by_node[node.id] = field_types
        class_names_by_node[node.id] = class_name
        qualified_names_by_node[node.id] = qualified_name

    node_ids_by_class_name = _group_node_ids_by_class_name(class_names_by_node)
    node_id_by_qualified_name = {
        qualified_name: node_id for node_id, qualified_name in qualified_names_by_node.items()
    }
    edges = _build_edges(
        nodes=nodes,
        raw_contents=raw_contents,
        field_types_by_node=field_types_by_node,
        node_ids_by_class_name=node_ids_by_class_name,
        node_id_by_qualified_name=node_id_by_qualified_name,
    )

    nodes.sort(key=lambda node: node.name)
    edges.sort(key=lambda edge: (edge.source, edge.target, edge.edge_type, edge.details or ""))

    return ArchitectureMap(nodes=nodes, edges=_deduplicate_edges(edges))


def write_architecture_markdown(architecture_map: ArchitectureMap, output_path: str | Path) -> Path:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    node_names = {node.id: node.name for node in architecture_map.nodes}

    lines = ["# Architecture Map", ""]
    lines.append(f"- Nodes: {len(architecture_map.nodes)}")
    lines.append(f"- Edges: {len(architecture_map.edges)}")
    lines.append("")

    if architecture_map.nodes:
        lines.append("## Components")
        lines.append("")
        for node in architecture_map.nodes:
            lines.append(f"### {node.name}")
            lines.append(f"- Type: `{node.component_type}`")
            if node.package:
                lines.append(f"- Package: `{node.package}`")
            lines.append(f"- File: `{node.file_path}`")
            if node.methods:
                lines.append(f"- Methods: {', '.join(node.methods[:20])}")
            if node.database_hints:
                lines.append(f"- Database hints: {', '.join(node.database_hints)}")
            if node.http_hints:
                lines.append(f"- HTTP hints: {', '.join(node.http_hints)}")
            if node.filesystem_hints:
                lines.append(f"- Filesystem hints: {', '.join(node.filesystem_hints)}")
            if node.security_hints:
                lines.append(f"- XML/Security hints: {', '.join(node.security_hints)}")
            lines.append("")

    if architecture_map.edges:
        lines.append("## Relations")
        lines.append("")
        for edge in architecture_map.edges[:200]:
            detail_suffix = f" ({edge.details})" if edge.details else ""
            source_name = node_names.get(edge.source, edge.source)
            target_name = node_names.get(edge.target, edge.target)
            lines.append(f"- `{source_name}` -[{edge.edge_type}]-> `{target_name}`{detail_suffix}")

    return _safe_write_text(output_file, "\n".join(lines))


def write_architecture_json(architecture_map: ArchitectureMap, output_path: str | Path) -> Path:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "nodes": [asdict(node) for node in architecture_map.nodes],
        "edges": [asdict(edge) for edge in architecture_map.edges],
    }
    return _safe_write_text(output_file, json.dumps(payload, indent=2, ensure_ascii=False))


def write_architecture_mermaid(architecture_map: ArchitectureMap, output_path: str | Path) -> Path:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    lines = ["flowchart TD"]
    for node in architecture_map.nodes:
        label = f"{node.name}\\n[{node.component_type}]"
        lines.append(f'    {node.id}["{label}"]')

    for edge in architecture_map.edges:
        edge_label = edge.edge_type
        if edge.details:
            edge_label = f"{edge.edge_type}: {edge.details}"
        lines.append(f'    {edge.source} -->|"{edge_label}"| {edge.target}')

    return _safe_write_text(output_file, "\n".join(lines))


def _extract_package_name(content: str) -> str | None:
    match = PACKAGE_PATTERN.search(content)
    return match.group(1).strip() if match else None


def _extract_imports(content: str) -> list[str]:
    return sorted({match.group(1).strip() for match in IMPORT_PATTERN.finditer(content)})


def _extract_methods(content: str) -> list[str]:
    return [match.group("name").strip() for match in METHOD_PATTERN.finditer(content)]


def _extract_field_types(content: str) -> dict[str, str]:
    field_types: dict[str, str] = {}
    for match in FIELD_PATTERN.finditer(content):
        field_types[match.group("name").strip()] = match.group("type").split("<", 1)[0].strip()
    return field_types


def _detect_component_type(class_name: str, content: str, imports: list[str]) -> str:
    if "@RestController" in content or "@Controller" in content or class_name.endswith("Controller"):
        return "controller"
    if "extends HttpServlet" in content or "@WebServlet" in content or class_name.endswith("Servlet"):
        return "servlet"
    if "@Service" in content or class_name.endswith(("Service", "Manager", "Facade", "UseCase")):
        return "service"
    if "@Repository" in content or class_name.endswith(("Repository", "Dao")):
        return "repository"
    if class_name.endswith("Client") or any(
        hint in " ".join(imports)
        for hint in ("RestTemplate", "WebClient", "HttpClient", "URLConnection", "FeignClient")
    ):
        return "client"
    if "@Entity" in content or class_name.endswith(("Dto", "DTO", "Model", "Entity", "Request", "Response", "VO", "Bean")):
        return "model"
    if "@Configuration" in content or class_name.endswith(("Config", "Configuration")):
        return "config"
    if class_name.endswith(("Util", "Utils", "Helper")):
        return "util"
    return "unknown"


def _detect_hints(content: str, patterns: dict[str, re.Pattern[str]]) -> list[str]:
    hints: list[str] = []
    for hint_name, pattern in patterns.items():
        if pattern.search(content):
            hints.append(hint_name)
    return hints


def _build_edges(
    nodes: list[ArchitectureNode],
    raw_contents: dict[str, str],
    field_types_by_node: dict[str, dict[str, str]],
    node_ids_by_class_name: dict[str, list[str]],
    node_id_by_qualified_name: dict[str, str],
) -> list[ArchitectureEdge]:
    edges: list[ArchitectureEdge] = []

    for node in nodes:
        for import_path in node.imports:
            target_id = node_id_by_qualified_name.get(import_path)
            if target_id is None:
                imported_name = import_path.rsplit(".", 1)[-1]
                candidate_ids = node_ids_by_class_name.get(imported_name, [])
                if len(candidate_ids) == 1:
                    target_id = candidate_ids[0]

            if target_id is not None and target_id != node.id:
                edges.append(
                    ArchitectureEdge(
                        source=node.id,
                        target=target_id,
                        edge_type="imports",
                        details=import_path,
                    )
                )

        field_types = field_types_by_node.get(node.id, {})
        content = raw_contents.get(node.id, "")

        for field_name, field_type in field_types.items():
            candidate_ids = node_ids_by_class_name.get(field_type, [])
            if len(candidate_ids) == 1 and candidate_ids[0] != node.id:
                edges.append(
                    ArchitectureEdge(
                        source=node.id,
                        target=candidate_ids[0],
                        edge_type="uses",
                        details=field_name,
                    )
                )

        for call_match in CALL_SITE_PATTERN.finditer(content):
            receiver = call_match.group("receiver")
            method_name = call_match.group("method")

            target_type = field_types.get(receiver)
            target_ids = node_ids_by_class_name.get(target_type, [])
            if len(target_ids) == 1 and target_ids[0] != node.id:
                edges.append(
                    ArchitectureEdge(
                        source=node.id,
                        target=target_ids[0],
                        edge_type="calls",
                        details=method_name,
                    )
                )
                continue

            candidate_ids = node_ids_by_class_name.get(receiver, [])
            if len(candidate_ids) == 1 and candidate_ids[0] != node.id:
                edges.append(
                    ArchitectureEdge(
                        source=node.id,
                        target=candidate_ids[0],
                        edge_type="calls",
                        details=method_name,
                    )
                )

    return edges


def _group_node_ids_by_class_name(class_names_by_node: dict[str, str]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for node_id, class_name in class_names_by_node.items():
        grouped.setdefault(class_name, []).append(node_id)
    return grouped


def _build_node_id(qualified_name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", qualified_name)


def _iter_java_files(root: Path):
    for current_root, dir_names, file_names in os.walk(root):
        dir_names[:] = [
            directory for directory in dir_names
            if directory not in IGNORED_DIRECTORIES
        ]

        for file_name in file_names:
            if not file_name.endswith(".java"):
                continue

            file_path = Path(current_root) / file_name
            try:
                if file_path.stat().st_size > MAX_JAVA_FILE_SIZE_BYTES:
                    continue
            except OSError:
                continue

            yield file_path


def _deduplicate_edges(edges: list[ArchitectureEdge]) -> list[ArchitectureEdge]:
    deduplicated: list[ArchitectureEdge] = []
    seen: set[tuple[str, str, str, str | None]] = set()

    for edge in edges:
        key = (edge.source, edge.target, edge.edge_type, edge.details)
        if key in seen:
            continue
        seen.add(key)
        deduplicated.append(edge)

    return deduplicated


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
