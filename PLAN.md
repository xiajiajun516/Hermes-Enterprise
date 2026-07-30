# 🚀 Hermes Enterprise Profile Plan (软件工程 AI 团队完整方案)

## 一、 总体目标与核心原则

构建一个基于 Hermes Agent 的长期维护、产物驱动、具备合规自检与自我进化能力的企业级 AI 软件工程团队。

### 核心原则
1. **Single Profile**：统一命名为 `Software Engineering Team`，禁止创建散落的多 Profile。
2. **Artifact-Driven**：摒弃聊天上下文依赖，所有阶段性产物必须持久化为标准 Markdown/代码文件。
3. **Minimal Context**：按需隔离上下文，Agent 之间仅传递最小必要 Artifact。
4. **Compliance Gate**：建立“规范静态审查”与“自我修正循环 (Self-Correction Loop)”，质量问题在编码前拦截。
5. **Self-Evolution**：引入 Rule Manager，从用户指令与踩坑复盘中实时沉淀规则与记忆。
6. **Governance & Safety**：高风险操作强制触发表格/对话级 `clarify` 审批阻断；支持状态级重试与故障恢复，禁止整流重跑。

---

## 二、 Profile 目录结构 (Profile Layout)

```text
Software Engineering Team Profile/
├── skills/                 # Agent 技能定义 (Hermes Skills)
│   ├── se-team-workflow-manager
│   ├── se-team-product-research
│   ├── se-team-architect
│   ├── se-team-engineer
│   ├── se-team-compliance-reviewer
│   ├── se-team-qa-release
│   └── se-team-rule-manager
├── artifacts/              # 项目各阶段标准交付物
│   ├── spec.md
│   ├── research.md
│   ├── architecture.md
│   ├── implementation-plan.md
│   ├── compliance-report.md
│   ├── review.md
│   ├── test-report.md
│   └── release.md
├── rules/                  # 全局规范库 (已合并至 se-team-rules skill)
│   ├── design-system.md     # (历史参考，实际定义在 se-team-rules skill)
│   ├── tech-stack.md        # (历史参考，实际定义在 se-team-rules skill)
│   ├── security.md          # (历史参考，实际定义在 se-team-rules skill)
│   └── workflow-rules.md    # (历史参考，实际定义在 se-team-rules skill)
├── skills/                 # 分类公共技能库 (Backend/Frontend/Testing/etc.)
├── kanban/                 # 看板状态记录文件 (`kanban.md`)
└── scripts/                # 自动化辅助脚本 (如 kanban 校验工具)
```

---

## 三、 Agent 矩阵与职责定义

结合 Hermes 调度效率，将架构精简为 **5 个核心 Agent + 2 个治理 Agent**：

| Agent 名称 | 角色定位 | 核心职责 | 核心交付物 / 产物 | 禁忌规则 |
| :--- | :--- | :--- | :--- | :--- |
| **01. Workflow Manager** | 主控指挥官 | 调度 Workflow、解析看板、判定流程节点、发起 `clarify` 审批 | `kanban.md` 状态更新 | 🚫 严禁编写代码或擅自修改需求 |
| **02. Product & Research** | 需求与调研 | 需求梳理、User Story 划定、技术可行性调研 | `spec.md`, `research.md` | - |
| **03. Architect Agent** | 架构与规划 | 模块设计、DB Schema、接口定义、实施计划拆解 | `architecture.md`, `implementation-plan.md` | - |
| **04. Engineer Agent** | 开发实施 | 后端/前端/数据库/AI 模块代码编写与单元测试 | Source Code & Unit Tests | 🚫 严禁绕过架构设计随意引入未授权第三方库 |
| **05. Compliance Reviewer**| 规范合规审查 | 静态对比 Artifact 与 `se-team-rules`，检查规范冲突 | `compliance-report.md` | 🚫 仅负责挑刺并输出结果，不直接修改 Artifact |
| **06. QA & Release** | 质量与交付 | 执行集成测试、撰写 Review 报告、生成文档与发布单 | `review.md`, `test-report.md`, `release.md` | 🚫 未经 `clarify` 审批严禁部署生产环境 |
| **07. Rule Manager** | 规则管理与进化| 接收用户新规范指令、踩坑复盘并更新 `se-team-rules` 及 Scope Recall 记忆 | `se-team-rules skill`, Scope Recall 更新 | 🚫 修改核心安全规则必须经过用户 `clarify` 确认 |

---

## 四、 规则库与 Scope Recall 内存策略

为确保“团队记忆”不污染且按需检索，结合 `scope-recall-hermes` 插件设定 **Memory 作用域映射**：

```text
Memory & Rules 架构：
├── `se-team-rules skill` : 存放硬性团队标准 (UI Design Tokens, 框架选择, 安全红线)
├── target="user"          : 用户个人交互偏好、回复风格 (全局共享)
├── target="memory"        : 通用编程踩坑教训、环境避坑指南 (全局共享)
├── target="project"       : 当前项目的特定业务概念、Entity 映射、模块约定 (项目内隔离)
└── target="ops"           : CI/CD 端口区间、服务器 IP/环境参数、数据库 Migration 策略 (运维共享)
```

### 规则与记忆检索原则：
* **门控与 Context 注入 (Subagent Dispatch Protocol)**：在调用子 Agent (`delegate_task`) 时，Master 必须将 `skills/se-team-*` 技能定义、关联模板/规则以及语言指令注入 `context` 参数，确保隔离的 Subagent 严格遵循 Skill 规范。
* **脚本硬门禁 (Python Validation Gate)**：在产物生成后，Master 必须调用 `scripts/validate_artifact.py` 与 `scripts/validate_kanban.py` 进行硬性 Schema 校验。
* **时效控制 (`freshness`)**：对带有版本号的配置或依赖规范标记 TTL，过期自动拉起重新校验。

---

## 五、 规范合规审查与自我修正循环 (Self-Correction Loop)

在 `Planning` (需求) 和 `Design` (架构) 完成后，强制插入静态合规审查。

```text
               ┌───────────────────────────────────────────────┐
               ▼                                               │
   [生成/修改 Artifact] (如 PM 修改 spec.md)                    │
               │                                               │
               ▼                                               │ (Fail: 附带 compliance-report.md 修改意见)
   [Compliance Reviewer 静态审查]                              │
  (对比 se-team-rules & DESIGN.md)                                │
               │                                               │
        ┌──────┴──────┐                                        │
      PASS           FAIL ─────────────────────────────────────┘
        │
        ▼
   [进入下一阶段] (如 Architect 或 Engineer)
```

### 循环防护与重试限制 (Threshold Guard)：
1. **自动修正上限**：单个节点允许自动循环修正最多 **5 次**。
2. **人工介入 (`clarify`)**：若达到 5 次仍输出 `STATUS: FAIL`，Workflow Manager 挂起流程，使用 `clarify` 提示用户：
   > *"Spec 合规审查已重试 5 次仍有冲突：[违例项]。请选择：1. 强制忽略并继续 2. 手动指定修改建议 3. 中止任务"*

---

## 六、 分级执行流程与 Kanban 状态机

### 1. 任务通道分级 (Pipeline Tiering)
避免小任务过载，定义 3 种执行通道：
* **P0 / Fast-Track (小修小补/Typo)**：`Engineer` ➔ `QA & Release` ➔ `Done`
* **P1 / Standard (普通功能开发)**：`Product` ➔ `Architect` ➔ `Compliance Gate` ➔ `Engineer` ➔ `QA & Release` ➔ `Done`
* **P2 / Full-Spec (重大架构变更)**：跑完全套完整流程（包含多轮 Compliance 审查与 Rule Review）

### 2. 精简 Kanban 状态流
在 `kanban/kanban.md` 中维护 5+1 个核心状态：
`Backlog` ➔ `Planning` ➔ `Implementation` ➔ `In Review` ➔ `Done` (异常状态：`Blocked`)

---

## 七、 核心 Artifact 体系规范

所有 Agent 间交互必须基于标准 Markdown Artifact，必须包含关键 Standard 头部：

| 交付物名称 | 编写 Agent | 核心内容要求 |
| :--- | :--- | :--- |
| `spec.md` | Product & Research | Scope, User Stories, Requirements, Acceptance Criteria |
| `architecture.md` | Architect Agent | Directory Tree, Module Architecture, DB Schema, API Specs |
| `compliance-report.md` | Compliance Reviewer | Rules Checked, Violations List, Final Status Line (`STATUS: PASS/FAIL`) |
| `review.md` | QA & Release | Code Quality Check, Security Audit, Diff Assessment |
| `test-report.md` | QA & Release | Automated Unit/Integration Test Log, Acceptance Verification |
| `release.md` | QA & Release | Release Checklist, Version Tag, Rollback Plan |

---

## 八、 审批阻断机制 (Approval Gates)

在触发以下高风险操作时，Agent **禁止自行决策**，必须调用 Hermes 原生 `clarify` 工具向用户请求授权：

1. 物理删除文件或删除数据库表 structure/data (`drop / rm`)
2. 执行数据库 Migration 生产升级脚本
3. 修改 `.env` 或环境变量中的密钥与全局配置
4. 部署至生产/预发布环境 (Production Deployment)
5. 破坏性 API 变更 (Breaking Changes)
6. Rule Manager 修改 Profile 的核心 `rules/security.md` 文件

---

## 九、 团队自我进化机制 (Self-Evolution)

```text
                      ┌──────────────────────────────────────┐
                      ▼                                      │
           [触发场景: 用户新指令 / 踩坑复盘]                   │
                      │                                      │
                      ▼                                      │
            ┌───────────────────┐                            │
            │   Rule Manager    │ ──► [触发 clarify 审批]    │ (若涉及 core rules)
            └─────────┬─────────┘                            │
                      │ (更新规范)                            │
                      ▼                                      │
         ┌──────────────────────────┐                        │
         │  rules/ & Scope Recall   │ ◄──────────────────────┘
         └────────────┬─────────────┘
                      │ (自动应用至下一次 Compliance Review)
                      ▼
```

### 触发模式：
* **显式模式**：用户直接下达规范调整指令（如：“以后所有 API 错误响应格式必须带上 `error_code`”）。
* **隐式模式 (Post-Mortem)**：当 QA 验证环节发现严重重复性 Bug 或合规审查出现反复失败时，在任务完成后触发 Rule Manager，提炼出一条避坑规则存入 `target="memory"` 或 `target="project"`。

---

## 十、 最终交付 CheckList

配置完成后的 Profile 校验标准：
- [x] 目录结构齐全，包含 `skills/`, `artifacts/`, `rules/`, `kanban/`。
- [x] 5 核心 Agent + 2 治理 Agent 的 Skill 定义清晰，职责无冲突。
- [x] `se-team-rules` skill 包含完整规范（设计、技术栈、安全、工作流）。
- [x] 成功配置基于 `clarify` 的 Approval Gate 阻断逻辑。
- [x] `kanban.md` 标准文件创建完成，支持通过脚本或 Workflow Manager 维护。
- [x] 集成 `scope-recall-hermes` 插件并划分 `project`/`ops` 作用域。
