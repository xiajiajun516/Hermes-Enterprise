import hashlib, subprocess, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, "scripts")
from task_contract import authorized_input, parse_and_validate_contract

RUN = "20260730T155029-637"
INPUT_RUN = "20260730T150000-001"
SHA = "a" * 64


def contract_text(body=None, **changes):
    values = {
        "contract_version": '"1.0"', "run_id": f'"{RUN}"',
        "created_at_utc": '"2026-07-30T15:50:29.637Z"', "tier": '"P2"',
        "stage": '"2d"', "attempt": "1", "agent_display_name": '"Engineer"',
        "agent_slug": '"engineer"', "parent_run_id": "null", "language": '"zh-CN"',
    }
    values.update(changes)
    frontmatter = "\n".join(f"{key}: {value}" for key, value in values.items())
    return f'''---
{frontmatter}
inputs:
  - path: "artifacts/architect/{INPUT_RUN}__architecture.md"
    artifact_name: "architecture"
    sha256: "{SHA}"
    producer_run_id: "{INPUT_RUN}"
outputs:
  - agent_slug: "engineer"
    artifact_name: "implementation-report"
    target_path: "artifacts/engineer/{RUN}__implementation-report.md"
    template: "templates/task-contract-template.md"
    write_mode: "create-new"
---
{body or """## Run Identity
run_id: identity
created_at_utc: time
## Goal & Scope
goal: strict validation
scope: future run
## Source of Truth
source: approved architecture
## Environment SOP
command: repository gate
## Artifact I/O Contract
inputs: exact paths
outputs: create-new targets
## Checksum / Verification
sha256: lower hexadecimal
verification: exit evidence
## Hard Prohibitions
prohibited: legacy inputs
## Final Report Protocol
report: RED GREEN results
"""}'''


class ContractTests(unittest.TestCase):
    def parse(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "contract.md"
            path.write_text(text, encoding="utf-8")
            return parse_and_validate_contract(path)

    def test_valid_contract_has_exact_semantic_sections(self):
        self.assertEqual(self.parse(contract_text())["run_id"], RUN)

    def test_rejects_extra_or_empty_or_out_of_order_headings(self):
        for body in (
            contract_text().replace("## Final Report Protocol", "## Extra\nextra: no\n## Final Report Protocol"),
            contract_text().replace("## Goal & Scope\ngoal: strict validation\nscope: future run", "## Goal & Scope"),
            contract_text().replace("## Goal & Scope", "## Environment SOP", 1).replace("## Environment SOP\ncommand: repository gate", "## Goal & Scope\ngoal: strict validation\nscope: future run", 1),
        ):
            with self.subTest(body=body):
                with self.assertRaises(ValueError):
                    self.parse(body)

    def test_rejects_invalid_identity_and_input_consistency(self):
        cases = [
            contract_text(created_at_utc='"2026-07-30T15:50:29.638Z"'),
            contract_text(agent_slug='"unknown"'),
            contract_text().replace(f'producer_run_id: "{INPUT_RUN}"', 'producer_run_id: "not-a-run"'),
            contract_text().replace('artifact_name: "architecture"', 'artifact_name: "spec"', 1),
            contract_text().replace(f'{RUN}__implementation-report.md', f'{INPUT_RUN}__implementation-report.md'),
        ]
        for text in cases:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    self.parse(text)

    def test_authorized_input_requires_existing_tracked_actual_hash(self):
        relative = f"artifacts/architect/{INPUT_RUN}__architecture.md"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", directory], check=True)
            contract_path = root / "contract.md"
            contract_path.write_text(contract_text().replace(SHA, "b" * 64), encoding="utf-8")
            contract = parse_and_validate_contract(contract_path)
            self.assertFalse(authorized_input(contract, root, relative)["authorized"])
            target = root / relative
            target.parent.mkdir(parents=True)
            target.write_text("untracked", encoding="utf-8")
            self.assertFalse(authorized_input(contract, root, relative)["authorized"])
            subprocess.run(["git", "-C", directory, "add", relative], check=True)
            self.assertFalse(authorized_input(contract, root, relative)["authorized"])
            actual = hashlib.sha256(target.read_bytes()).hexdigest()
            contract["inputs"][0]["sha256"] = actual
            self.assertTrue(authorized_input(contract, root, relative)["authorized"])

    def test_template_and_master_skill_encode_complete_contract_prompt(self):
        template = Path("templates/task-contract-template.md").read_text(encoding="utf-8")
        master = Path("SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(template.startswith("---\n"))
        for heading in (
            "Run Identity", "Goal & Scope", "Source of Truth", "Environment SOP",
            "Artifact I/O Contract", "Checksum / Verification", "Hard Prohibitions",
            "Final Report Protocol",
        ):
            self.assertIn(f"## {heading}", template)
            self.assertIn(heading, master)
        for label in ("goal:", "scope:", "source:", "command:", "inputs:", "outputs:",
                      "sha256:", "verification:", "prohibited:", "report:"):
            self.assertIn(label, template)
        for field in ("contract_version:", "run_id:", "created_at_utc:", "agent_slug:",
                      "parent_run_id:", "language:"):
            self.assertIn(field, template)


if __name__ == "__main__":
    unittest.main()
