def normalize_java_version(version: str) -> int:
    """Normalize Java version string to integer."""
    version = version.strip()

    if version.startswith("${") and version.endswith("}"):
        raise ValueError(f"Unresolved Maven property reference: {version}")

    if version.startswith("1."):
        return int(version.split(".")[1])  # 1.8 -> 8

    return int(version)


def analyze_java_compatibility(
    detected_version: str | None,
    target_version: int | None
) -> list[str]:
    """Analyze compatibility between detected and target Java versions."""

    if detected_version is None:
        return ["Java version could not be detected"]

    if target_version is None:
        return ["Target Java version not specified"]

    try:
        detected = normalize_java_version(detected_version)
    except ValueError:
        return [f"Detected Java version is not directly comparable: {detected_version}"]

    messages = []

    if detected < target_version:
        messages.append(f"Upgrade required: Java {detected} → {target_version}")

        if detected <= 8 and target_version >= 11:
            messages.append("JAXB and JAX-WS modules were removed from JDK after Java 11")

        if detected <= 8 and target_version >= 17:
            messages.append("Strong encapsulation may break reflection-based code")

    elif detected == target_version:
        messages.append("Project is already using the target Java version")

    else:
        messages.append("Warning: target Java version is lower than the project's current version")

    return messages