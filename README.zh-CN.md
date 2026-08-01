# 🚀 Hermes Enterprise

[English](./README.md) | [中文](./README.zh-CN.md)

面向 **Hermes Agent** 的企业级、工件驱动、自进化的 AI 软件工程团队 **Master Skill**。

---

## ⚡ 快速安装 Skill

你可以在所有 Hermes 会话中使用以下任一方法安装并使用此 skill:

### 方法 1:克隆到 Hermes 全局 Skills 目录(推荐)

**Linux / macOS / Git Bash:**
```bash
# 主编排 skill
git clone https://github.com/xiajiajun516/Hermes-Enterprise.git ~/.config/hermes/skills/software-engineering-team

# 安装子 agent skills(优化分发)
cp -r ~/.config/hermes/skills/software-engineering-team/skills/* ~/.config/hermes/skills/
```

**Windows (PowerShell / CMD):**
```cmd
git clone https://github.com/xiajiajun516/Hermes-Enterprise.git %USERPROFILE%\AppData\Local\hermes\skills\software-engineering-team

xcopy /E /I %USERPROFILE%\AppData\Local\hermes\skills\software-engineering-team\skills\* %USERPROFILE%\AppData\Local\hermes\skills\
```

克隆完成后,Hermes 会在 **所有** 会话和 profile 中全局自动索引这些 skills!

---

### 方法 2:通过 CLI 标志预加载
使用 `-s` 标志从本地克隆或 URL 预加载 skill:
```bash
hermes -s software-engineering-team
```

---

### 方法 3:在对话中调用
安装后,在任何活动的 Hermes 对话中直接调用该 skill:

> *"加载 skill software-engineering-team,并为这个仓库构建一个用户认证服务。"*

---

## 🌟 核心亮点

- **Master 编排入口**:`SKILL.md` 是 agent 的可执行逐步编排指南。
- **基于 Skill 的分发**(v1.1 优化):子 agents 通过 `skill_view()` 自行加载角色、方法论、模板和规则——无需手动注入冗长的提示词文件。Master Agent 只需指定 skill 名称 + 任务上下文。
- **零配置**:直接继承当前会话的 LLM 提供商、API 密钥和工具链。
- **工件驱动协作**:通过生成持久的 Markdown/代码工件(`spec.md`、`architecture.md`、`compliance-report.md` 等)消除对聊天历史的依赖。
- **最小上下文策略**:严格限制子 agent 上下文为必要工件,减少 token 消耗。
- **自动化验证门禁**:将 Python 脚本(`validate_artifact.py`、`update_kanban.py --check`)集成到执行管线中,实施 schema 强制。
- **合规门禁与自纠错循环**:在编码开始前自动依据设计/技术标准审计规格。
- **自进化治理**:`Rule Manager Agent` 根据事后复盘和用户指令更新规则及 Scope Recall 记忆(`project` / `ops` 目标范围)。
- **审批门禁**:高风险操作(删除、数据库迁移、部署)需要通过 Hermes `clarify` 进行人工确认。

---

## 🧠 记忆与插件集成

### Scope Recall 集成(推荐)
与 `scope-recall-hermes` 插件配合时,此 skill 会自动存储和检索域隔离记忆:
- **`target="project"`**:存储仓库架构约定、模块映射和实体规则。
- **`target="ops"`**:存储 CI/CD 参数、服务器 IP 和部署策略。
- **`target="user"`**:存储个人/团队代码风格偏好。
- **`target="memory"`**:存储通用技术陷阱和事后复盘经验。

---

## 📂 仓库结构

```text
Hermes-Enterprise/
├── SKILL.md                # Master 编排入口
├── PLAN.md                 # 架构与计划概览(英文)
├── README.md               # 概览与 Skill 安装指南(英文,默认)
├── README.zh-CN.md         # 概览与 Skill 安装指南(简体中文)
├── LICENSE                 # MIT License
├── skills/                 # 独立子 Agent Skills (v1.1)
│   ├── se-team-design/SKILL.md
│   ├── se-team-engineer/SKILL.md
│   ├── se-team-compliance-reviewer/SKILL.md
│   ├── se-team-qa-release/SKILL.md
│   ├── se-team-rule-manager/SKILL.md
│   └── se-team-rules/SKILL.md
├── templates/              # 标准交付工件模板
├── artifacts/              # 标准输出工件位置
├── kanban/                 # 任务管线看板跟踪(`kanban.md`)
└── scripts/                # 验证与辅助脚本
```

---

## 🤖 Agent 矩阵 (v1.1 — 基于 Skill)

| Agent | 角色 | Hermes Skill | 主要交付物 |
| :--- | :--- | :--- | :--- |
| **01. Workflow Manager** | 控制与管线管理 | `software-engineering-team` (Master) | 合同与 manifest |
| **02. Design Agent** | 需求、可行性与架构 | `se-team-design` | `research`、`spec-draft`、`spec`、`architecture`、`implementation-plan` |
| **03. Engineer Agent** | 代码与单元测试实现 | `se-team-engineer` | `implementation-report` |
| **04. Compliance Reviewer**| 静态门禁审计 | `se-team-compliance-reviewer` | `compliance-report` |
| **05. QA & Release** | 审查、测试与发布 | `se-team-qa-release` | `review`、`test-report`、`release` |
| **06. Rule Manager** | 治理与演进 | `se-team-rule-manager` | `governance-report` |
| — | 共享项目规则 | `se-team-rules` | 所有 agents 加载 |

### 分发如何工作(优化版)

**之前 (v1.0):** Master Agent 手动读取 3-6 个文件,拼接成一个巨大的上下文字符串。

**之后 (v1.1):** Master Agent 告诉子 agent 要加载哪个 skill:
```
delegate_task(
  goal="Design system architecture for user auth service",
  context="Load skill: se-team-design. Load se-team-rules for standards. Output artifacts/design/<run-id>__architecture.md. Respond in Chinese."
)
```

子 agent 调用 `skill_view('se-team-design')`,获得其角色、方法论、模板和禁令——全部自包含。规则通过 `skill_view('se-team-rules')` 加载。

---

## 🔄 自纠错循环

```text
[Product / Architect Agent] ──► Generates Spec / Architecture
                                         │
                                         ▼
[Compliance Reviewer] ─────────► Audits against se-team-rules
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   ▼                                           ▼
             STATUS: FAIL                                STATUS: PASS
                   │                                           │
                   ▼                                           ▼
[Return to Product/Architect for revision]       [Proceed to Implementation]
```

---

## 📄 许可证

基于 MIT License 分发。详见 `LICENSE`。
