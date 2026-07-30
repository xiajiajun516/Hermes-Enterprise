---
name: software-engineering-team
version: 1.4.0
description: "Forward-only Contract-driven Software Engineering AI Team orchestration."
category: software-development
---
# Software Engineering AI Team — Master

## 派发前置规则

每次 future pipeline dispatch 必须先以 create-new / exclusive write 创建
`artifacts/runs/<run-id>__contract.md`。Master 只可将该 Contract 的精确路径与 SHA-256、
`inputs[]` 精确路径/SHA-256，以及声明的 create-new outputs 传给 Subagent。

禁止以 `latest`、glob、目录遍历、mtime、猜测文件名或根目录 `artifacts/*.md` legacy 文件选择输入。
future output 必须是 Git-tracked、不可覆盖的角色 artifact，且最终由 Git-tracked manifest 关联。
root-level legacy files 既不迁移也不作为 runtime input。

在每个动态 Task Contract 中先执行环境门：显式 `cd` 到仓库、断言 `pwd`、验证全部精确输入和
所需脚本存在。门禁失败必须报告 `BLOCKED`，不得写入任何路径。

## 必须传给每个 Subagent 的完整动态 Task Contract

复制下列正文到 `delegate_task` 的 context，并将所有 `<...>` 占位符替换为实际值；替换后不得
保留占位符。front matter 的 `inputs` / `outputs` 只能包含精确路径，不可使用推断规则。

```markdown
---
contract_version: "1.0"
run_id: "<YYYYMMDDTHHmmss-SSS>"
created_at_utc: "<YYYY-MM-DDTHH:mm:ss.SSSZ>"
tier: "<P0|P1|P2>"
stage: "<2a|2b|2c|2d|2e|2f>"
attempt: <positive-integer>
agent_display_name: "<display-name>"
agent_slug: "<product-research|architect|compliance-reviewer|engineer|qa-release|rule-manager>"
parent_run_id: <null-or-YYYYMMDDTHHmmss-SSS>
language: "zh-CN"
inputs:
  - path: "artifacts/<producer-slug>/<producer-run-id>__<artifact-name>.md"
    artifact_name: "<artifact-name>"
    sha256: "<64-lowercase-hex>"
    producer_run_id: "<producer-run-id>"
outputs:
  - agent_slug: "<agent-slug>"
    artifact_name: "<artifact-name>"
    target_path: "artifacts/<agent-slug>/<run-id>__<artifact-name>.md"
    template: "<exact-template-path>"
    write_mode: "create-new"
---

## Run Identity
run_id: <same-as-frontmatter>
created_at_utc: <same-as-frontmatter>

## Goal & Scope
goal: <specific-deliverable>
scope: <authorized-work-boundary>

## Source of Truth
source: <each-authoritative-input-path-and-SHA-256>

## Environment SOP
command: cd /c/Repository/hermes-enterprise-profile-push && test "$(pwd)" = "/c/Repository/hermes-enterprise-profile-push" && <prerequisite-checks>

## Artifact I/O Contract
inputs: <only-frontmatter-inputs; validate path, Git tracking and recomputed SHA before read>
outputs: <only-frontmatter-outputs; create-new, UTC naming, exclusive write and Git tracking>

## Checksum / Verification
sha256: <recalculate-every-input-and-output-SHA-256>
verification: <exact-commands, expected-exit-codes, and validation criteria>

## Hard Prohibitions
prohibited: legacy inputs, latest, glob, mtime, traversal, guessed inputs, overwrite, undeclared writes, and Git mutations unless explicitly authorized

## Final Report Protocol
report: 中文；列出 Contract run_id、精确输入/输出路径、SHA-256、实际命令和 exit code、验证结果、BLOCKED/风险及未执行项
```

Master 在派发前用 `python scripts/validate_artifact.py <exact-contract-path>` 验证 Contract；
只接受 tracked manifest 链路。

| Stage | slug | standard outputs |
|---|---|---|
|2a|product-research|research, spec-draft, spec|
|2b|architect|architecture, implementation-plan|
|2c|compliance-reviewer|compliance-report|
|2d|engineer|implementation-report|
|2e|qa-release|review, test-report, release|
|2f|rule-manager|governance-report|