"""Forward-only naming and path policy."""
import re
from datetime import datetime, timezone

ALLOWED_SLUGS = {
    "product-research": {"research", "spec-draft", "spec"},
    "architect": {"architecture", "implementation-plan"},
    "compliance-reviewer": {"compliance-report"},
    "engineer": {"implementation-report"},
    "qa-release": {"review", "test-report", "release"},
    "rule-manager": {"governance-report"},
}
RUN_RE = re.compile(r"^\d{8}T\d{6}-\d{3}$")
ART_RE = re.compile(r"^\d{8}T\d{6}-\d{3}(?:-\d{3})?__[a-z0-9-]+\.md$")


def run_id_from_datetime(value):
    if value.tzinfo is None:
        raise ValueError("UTC-aware datetime required")
    return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S-") + f"{value.microsecond // 1000:03d}"


def iso_utc_for_run_id(run_id):
    if not RUN_RE.fullmatch(run_id):
        raise ValueError("invalid run id")
    parsed = datetime.strptime(run_id, "%Y%m%dT%H%M%S-%f").replace(tzinfo=timezone.utc)
    return parsed.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def artifact_path(slug, name, instant, sequence=None):
    if slug not in ALLOWED_SLUGS or name not in ALLOWED_SLUGS[slug]:
        raise ValueError("unknown slug or artifact name")
    suffix = "" if sequence is None else f"-{sequence:03d}"
    return f"artifacts/{slug}/{run_id_from_datetime(instant)}{suffix}__{name}.md"


def validate_relative_path(path):
    if not isinstance(path, str) or chr(92) in path or path.startswith("/") or ".." in path.split("/") or "latest" in path:
        return False
    parts = path.split("/")
    if len(parts) == 3 and parts[0] == "artifacts" and parts[1] in ALLOWED_SLUGS:
        return bool(ART_RE.fullmatch(parts[2]))
    if len(parts) == 3 and parts[:2] == ["artifacts", "runs"]:
        return bool(re.fullmatch(r"\d{8}T\d{6}-\d{3}__(contract\.md|manifest\.json)", parts[2]))
    return False


def validate_output(slug, name, path):
    return (
        slug in ALLOWED_SLUGS
        and name in ALLOWED_SLUGS[slug]
        and validate_relative_path(path)
        and path.startswith(f"artifacts/{slug}/")
        and path.endswith(f"__{name}.md")
    )
