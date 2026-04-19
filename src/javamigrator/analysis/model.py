from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RequestParameter:
    name: str
    location: str = "query"
    data_type: str = "string"
    required: bool = False


@dataclass
class Endpoint:
    name: str
    route: str
    methods: list[str] = field(default_factory=list)
    request_parameters: list[RequestParameter] = field(default_factory=list)
    response_model: str | None = None
    service_calls: list[str] = field(default_factory=list)
    exceptions: list[str] = field(default_factory=list)
    source_file: str | None = None


@dataclass
class ModelField:
    name: str
    data_type: str = "Object"


@dataclass
class DataModel:
    name: str
    fields: list[ModelField] = field(default_factory=list)
    kind: str = "model"
    source_file: str | None = None


@dataclass
class Service:
    name: str
    methods: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    source_file: str | None = None


@dataclass
class ExternalDependency:
    name: str
    import_path: str
    category: str = "library"


@dataclass
class ExceptionModel:
    name: str
    kind: str = "application"
    source_file: str | None = None


@dataclass
class PersistenceHint:
    kind: str
    details: str
    source_file: str | None = None


@dataclass
class HttpIntegrationHint:
    kind: str
    details: str
    source_file: str | None = None


@dataclass
class ProjectModel:
    endpoints: list[Endpoint] = field(default_factory=list)
    models: list[DataModel] = field(default_factory=list)
    services: list[Service] = field(default_factory=list)
    external_dependencies: list[ExternalDependency] = field(default_factory=list)
    exceptions: list[ExceptionModel] = field(default_factory=list)
    persistence_hints: list[PersistenceHint] = field(default_factory=list)
    http_integrations: list[HttpIntegrationHint] = field(default_factory=list)
