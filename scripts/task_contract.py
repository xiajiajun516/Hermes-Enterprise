"""Restricted task Contract parsing and authorization."""
import re
import subprocess
from pathlib import Path

from artifact_io import sha256_file
from artifact_naming import ALLOWED_SLUGS, RUN_RE, iso_utc_for_run_id, validate_output, validate_relative_path

SHA_RE = re.compile(r"^[0-9a-f]{64}$")
HEADERS = [
    "Run Identity",
    "Goal & Scope",
    "Source of Truth",
    "Environment SOP",
    "Artifact I/O Contract",
    "Checksum / Verification",
    "Hard Prohibitions",
    "Final Report Protocol",
]
TIERS = {"P0", "P1", "P2"}
STAGES = {"2a", "2b", "2c", "2d", "2e", "2f"}
STAGE_SLUGS = {
    "2a": "product-research",
    "2b": "architect",
    "2c": "compliance-reviewer",
    "2d": "engineer",
    "2e": "qa-release",
    "2f": "rule-manager",
}
LANGUAGES = {"en-US"}
SECTION_LABELS = {
    "Run Identity": {"run_id", "created_at_utc"},
    "Goal & Scope": {"goal", "scope"},
    "Source of Truth": {"source"},
    "Environment SOP": {"command"},
    "Artifact I/O Contract": {"inputs", "outputs"},
    "Checksum / Verification": {"sha256", "verification"},
    "Hard Prohibitions": {"prohibited"},
    "Final Report Protocol": {"report"},
}


def _scalar(value):
    value = value.strip()
    if value == "[]":
        return []
    if value in ("null", "~"):
        return None
    if value.isdigit():
        return int(value)
    if len(value) >= 2 and value[0] in "\"'" and value[-1] == value[0]:
        return value[1:-1]
    return value


def _frontmatter(text):
    if not text.startswith("---\n"):
        raise ValueError("missing frontmatter")
    end = text.find("\n---", 4)
    if end < 0:
        raise ValueError("unterminated frontmatter")
    lines, data, current, item = text[4:end].splitlines(), {}, None, None
    for line in lines:
        if "\t" in line or any(marker in line for marker in "&*!"):
            raise ValueError("ambiguous YAML")
        if re.match(r"^[^ :]+:", line):
            key, value = line.split(":", 1)
            if key in data:
                raise ValueError("duplicate key")
            data[key] = [] if not value.strip() else _scalar(value)
            current, item = key, None
        elif line.startswith("  - "):
            if not isinstance(data.get(current), list):
                raise ValueError("invalid list")
            key, value = line[4:].split(":", 1)
            item = {key: _scalar(value)}
            data[current].append(item)
        elif line.startswith("    ") and item is not None:
            key, value = line.strip().split(":", 1)
            if key in item:
                raise ValueError("duplicate key")
            item[key] = _scalar(value)
        else:
            raise ValueError("unsupported YAML")
    return data, text[end + 5:]


def _validate_sections(body):
    matches = list(re.finditer(r"^## (.+)$", body, re.M))
    if [match.group(1) for match in matches] != HEADERS:
        raise ValueError("exactly eight ordered headings required")
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        content = body[match.end():end].strip()
        labels = {label.lower() for label in re.findall(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:", content, re.M)}
        if not content or not SECTION_LABELS[match.group(1)] <= labels:
            raise ValueError("missing section semantic fields")


def _artifact_identity(path):
    parts = path.split("/")
    if len(parts) != 3 or parts[0] != "artifacts" or parts[1] not in ALLOWED_SLUGS:
        return None
    match = re.fullmatch(r"(\d{8}T\d{6}-\d{3})(?:-\d{3})?__([a-z0-9-]+)\.md", parts[2])
    return (parts[1], *match.groups()) if match else None


def parse_and_validate_contract(path):
    data, body = _frontmatter(Path(path).read_text(encoding="utf-8"))
    _validate_sections(body)
    required = {
        "contract_version", "run_id", "created_at_utc", "tier", "stage", "attempt",
        "agent_display_name", "agent_slug", "parent_run_id", "language", "inputs", "outputs",
    }
    if set(data) != required or data["contract_version"] != "1.0" or not RUN_RE.fullmatch(str(data["run_id"])):
        raise ValueError("invalid identity")
    if data["created_at_utc"] != iso_utc_for_run_id(data["run_id"]) or not isinstance(data["attempt"], int) or data["attempt"] < 1:
        raise ValueError("invalid identity")
    string_fields = all(isinstance(data[key], str) and data[key] for key in ("tier", "stage", "agent_display_name", "language"))
    if not string_fields or data["agent_slug"] not in ALLOWED_SLUGS:
        raise ValueError("invalid identity")
    if data["tier"] not in TIERS or data["stage"] not in STAGES or data["language"] not in LANGUAGES:
        raise ValueError("invalid identity")
    if STAGE_SLUGS[data["stage"]] != data["agent_slug"]:
        raise ValueError("invalid identity")
    if data["parent_run_id"] is not None and not RUN_RE.fullmatch(str(data["parent_run_id"])):
        raise ValueError("invalid identity")
    if not isinstance(data["inputs"], list) or not isinstance(data["outputs"], list):
        raise ValueError("invalid contract lists")
    for item in data["inputs"]:
        identity = _artifact_identity(item.get("path", "")) if isinstance(item, dict) else None
        valid_input = isinstance(item, dict) and set(item) == {"path", "artifact_name", "sha256", "producer_run_id"}
        if not valid_input or not validate_relative_path(item["path"]) or not SHA_RE.fullmatch(item["sha256"]):
            raise ValueError("invalid input")
        consistent = identity and item["artifact_name"] == identity[2] and item["producer_run_id"] == identity[1]
        if not consistent or not RUN_RE.fullmatch(item["producer_run_id"]):
            raise ValueError("inconsistent input")
    for item in data["outputs"]:
        valid_output = (
            item["write_mode"] == "create-new"
            and validate_output(item["agent_slug"], item["artifact_name"], item["target_path"])
        )
        if set(item) != {"agent_slug", "artifact_name", "target_path", "template", "write_mode"} or not valid_output:
            raise ValueError("invalid output")
        identity = _artifact_identity(item["target_path"])
        if item["agent_slug"] != data["agent_slug"] or not identity or identity[1] != data["run_id"]:
            raise ValueError("inconsistent output")
        if item["template"] != f"templates/{item['artifact_name']}-template.md":
            raise ValueError("invalid output template reference")
    return data


def validate_template_files(contract, root):
    """Every declared output template must exist under templates/ relative to root."""
    for output in contract.get("outputs", []):
        template = (Path(root).resolve() / output["template"]).resolve()
        if not template.is_file():
            raise ValueError(f"BLOCKED: template not found: {output['template']}")


def _tracked(root, relative_path):
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--error-unmatch", "--", relative_path],
        text=True, capture_output=True,
    )
    return result.returncode == 0


def authorized_input(contract, root, path):
    root, path = Path(root).resolve(), str(path)
    item = next((entry for entry in contract.get("inputs", []) if entry.get("path") == path), None)
    if item is None or not validate_relative_path(path):
        return {"authorized": False, "reason": "BLOCKED: unauthorized, legacy, or hash-mismatched input"}
    target = (root / path).resolve()
    if root not in target.parents or not target.is_file() or not _tracked(root, path):
        return {"authorized": False, "reason": "BLOCKED: input missing or untracked"}
    if sha256_file(target) != item["sha256"]:
        return {"authorized": False, "reason": "BLOCKED: unauthorized, legacy, or hash-mismatched input"}
    return {"authorized": True, "reason": None}
