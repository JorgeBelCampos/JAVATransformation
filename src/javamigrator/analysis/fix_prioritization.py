from __future__ import annotations

from dataclasses import dataclass

from javamigrator.analysis.code_analysis import ImportFinding
from javamigrator.analysis.dependency_analysis import DependencyFinding


@dataclass
class FixCandidate:
    title: str
    category: str
    impact: str
    effort: str
    reason: str
    affected_files: int
    occurrences: int
    recommendation: str


def generate_top_fix_candidates(
    code_findings: list[ImportFinding],
    dependency_findings: list[DependencyFinding],
) -> list[FixCandidate]:
    """Generate prioritized fix candidates from code and dependency findings."""
    candidates: list[FixCandidate] = []

    # 1. Internal APIs
    internal_api_findings = [
        finding
        for finding in code_findings
        if finding.import_value.startswith(("com.sun.", "sun.", "jdk.internal."))
    ]
    if internal_api_findings:
        candidates.append(
            FixCandidate(
                title="Replace internal JDK API usages",
                category="internal_api",
                impact="HIGH",
                effort="LOW",
                reason="Internal or vendor-specific APIs are risky on newer Java versions and can break at runtime.",
                affected_files=len({finding.file_path for finding in internal_api_findings}),
                occurrences=len(internal_api_findings),
                recommendation="Replace com.sun.* / sun.* usages with supported public APIs before final migration validation.",
            )
        )

    reflection_findings = [
        finding
        for finding in code_findings
        if finding.message == "Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens"
    ]
    if reflection_findings:
        candidates.append(
            FixCandidate(
                title="Review reflection and encapsulation-sensitive code",
                category="reflection_risk",
                impact="HIGH",
                effort="MEDIUM",
                reason="Reflection-heavy code can fail under stronger encapsulation in Java 17+.",
                affected_files=len({finding.file_path for finding in reflection_findings}),
                occurrences=len(reflection_findings),
                recommendation="Review reflective access, setAccessible-style flows, and illegal-access warnings before finalizing Java 17+ migration.",
            )
        )

    # 2. Servlet migration in code
    servlet_code_findings = [
        finding
        for finding in code_findings
        if "javax.servlet" in finding.import_value
    ]
    if servlet_code_findings:
        candidates.append(
            FixCandidate(
                title="Plan javax.servlet to jakarta.servlet migration",
                category="servlet_migration",
                impact="VERY_HIGH",
                effort="MEDIUM",
                reason="Servlet APIs appear in code and are a common blocker for modern Jakarta-based runtimes.",
                affected_files=len({finding.file_path for finding in servlet_code_findings}),
                occurrences=len(servlet_code_findings),
                recommendation="If targeting Tomcat 10+ or Jakarta EE, migrate javax.servlet imports and dependencies to jakarta.servlet.",
            )
        )

    jaxb_findings = [
        finding
        for finding in code_findings
        if finding.message == "JAXB API removed from JDK after Java 11"
    ]
    if jaxb_findings:
        candidates.append(
            FixCandidate(
                title="Add explicit JAXB support for Java 11+",
                category="jaxb_removal",
                impact="HIGH",
                effort="LOW",
                reason="JAXB APIs were removed from the JDK and must be managed explicitly.",
                affected_files=len({finding.file_path for finding in jaxb_findings}),
                occurrences=len(jaxb_findings),
                recommendation="Add explicit JAXB API/runtime dependencies in Maven and verify XML binding flows on the target JDK.",
            )
        )

    jaxws_findings = [
        finding
        for finding in code_findings
        if finding.message == "JAX-WS API removed from JDK after Java 11"
    ]
    if jaxws_findings:
        candidates.append(
            FixCandidate(
                title="Add explicit JAX-WS dependencies",
                category="jaxws_removal",
                impact="HIGH",
                effort="MEDIUM",
                reason="JAX-WS APIs were removed from the JDK and often block Java 11+ upgrades.",
                affected_files=len({finding.file_path for finding in jaxws_findings}),
                occurrences=len(jaxws_findings),
                recommendation="Add explicit SOAP/JAX-WS dependencies and verify client/server code generation and runtime behavior.",
            )
        )

    activation_findings = [
        finding
        for finding in code_findings
        if finding.message == "javax.activation removed from JDK after Java 11"
    ]
    if activation_findings:
        candidates.append(
            FixCandidate(
                title="Add explicit activation dependency",
                category="activation_removal",
                impact="HIGH",
                effort="LOW",
                reason="javax.activation is no longer bundled in newer JDKs.",
                affected_files=len({finding.file_path for finding in activation_findings}),
                occurrences=len(activation_findings),
                recommendation="Add an explicit activation dependency compatible with the current codebase before re-running the build.",
            )
        )

    json_findings = [
        finding
        for finding in code_findings
        if finding.message == "Legacy javax.json API detected; explicit dependency or jakarta.json migration may be needed"
    ]
    if json_findings:
        candidates.append(
            FixCandidate(
                title="Review legacy javax.json usage",
                category="javax_json_review",
                impact="MEDIUM",
                effort="LOW",
                reason="Old javax.json APIs may need explicit dependency management on modern JDKs.",
                affected_files=len({finding.file_path for finding in json_findings}),
                occurrences=len(json_findings),
                recommendation="Add explicit javax.json dependency first, then evaluate whether jakarta.json migration is desirable.",
            )
        )

    # 3. Servlet dependencies
    servlet_dependency_findings = [
        finding
        for finding in dependency_findings
        if "servlet" in finding.artifact_id.lower() or "servlet" in finding.group_id.lower()
    ]
    if servlet_dependency_findings:
        candidates.append(
            FixCandidate(
                title="Upgrade legacy servlet dependencies",
                category="dependency_upgrade",
                impact="HIGH",
                effort="LOW",
                reason="Old servlet dependencies may block runtime modernization or container upgrades.",
                affected_files=0,
                occurrences=len(servlet_dependency_findings),
                recommendation="Review and replace old servlet artifacts such as servlet-api 2.5 / javax.servlet-api 3.x according to target container.",
            )
        )

    compiler_config_findings = [
        finding
        for finding in dependency_findings
        if "Legacy Maven compiler configuration detected" in finding.message
        or "Legacy Java compiler property detected" in finding.message
    ]
    if compiler_config_findings:
        candidates.append(
            FixCandidate(
                title="Modernize Maven compiler Java level",
                category="compiler_config",
                impact="VERY_HIGH",
                effort="LOW",
                reason="Old source/target/release values can make builds fail immediately on newer JDKs.",
                affected_files=0,
                occurrences=len(compiler_config_findings),
                recommendation="Raise compiler source/target/release and related properties to at least Java 8 before attempting higher-JDK validation.",
            )
        )

    # 4. General javax review
    general_javax_findings = [
        finding
        for finding in code_findings
        if finding.message == "javax.* usage detected; review whether migration is required"
    ]
    if general_javax_findings:
        candidates.append(
            FixCandidate(
                title="Review general javax usage",
                category="general_javax",
                impact="MEDIUM",
                effort="HIGH",
                reason="There is broad javax usage across the codebase, but not all of it requires migration.",
                affected_files=len({finding.file_path for finding in general_javax_findings}),
                occurrences=len(general_javax_findings),
                recommendation="Classify javax usages into Java SE, external libs, and Jakarta migration candidates before planning large-scale code changes.",
            )
        )

    priority_order = {
        "VERY_HIGH": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    }

    candidates.sort(
        key=lambda candidate: (
            -priority_order.get(candidate.impact, 0),
            -candidate.occurrences,
        )
    )

    return candidates
