# 🚀 Hermes Enterprise

为 **Hermes Agent** 打造的轻量、git 原生、三阶段 AI 软件工程团队 **Master Skill** —— 日常工具版 (v2.0)。

[English Version](./README.md)

---

## ⚡ 快速安装

在任何 Hermes 会话中使用此 skill：

### 方式 1:Git Clone 到 Hermes 全局 Skills 目录(推荐)

**Linux / macOS / Git Bash:**
```bash
# 主调度 skill
git clone https://github.com/xiajiajun516/Hermes-Enterprise.git ~/.config/hermes/skills/software-engineering-team

# 安装子角色 skills
cp -r ~/.config/hermes/skills/software-engineering-team/skills/* ~/.config/hermes/skills/
```

**Windows (PowerShell / CMD):**
```cmd
git clone https://github.com/xiajiajun516/Hermes-Enterprise.git %USERPROFILE%\AppData\Local\hermes\skills\software-engineering-team

xcopy /E /I %USERPROFILE%\AppData\Local\hermes\skills\software-engineering-team\skills\* %USERPROFILE%\AppData\Local\hermes\skills\
```

克隆后 Hermes 会自动在**所有**会话与 Profile 中全局索引这些 skills！

---

### 方式 2:CLI 预加载
```bash
hermes -s software-engineering-team
```

---

### 方式 3:会话内调用
> *"Load skill software-engineering-team and build a user authentication service for this repository."*

---

## 🌟 核心亮点

- **三阶段流水线**:`design → engineer → QA`。主控(Workflow Manager)只做策略与调度——不写业务代码、SQL 或文件,所有执行由子代理完成。
- **Git 原生信任**:不可变性、谱系、状态追踪全部交给 git——子代理自行提交(提交信息带 stage 标记),`git log` 即谱系。无手写 manifest/SHA 体系。
- **零配置**:直接继承当前会话的 LLM Provider、API Key 与工具链。
- **Skill 分发**:子代理通过 `skill_view()` 自加载角色,无需手动注入上下文。
- **软门禁 QA**:OCR 机械审查(参考信号)+ 人工审查,结论 `APPROVED / CHANGES_REQUESTED / REJECTED`;主控决定打回或放行,用户最终验收兜底。
- **打回闭环**:QA 发现的问题回到对应阶段(实现错误→engineer,需求/设计错误→design),携带 QA 报告作为输入;多次失败后升级给用户。
- **规则自演进**:QA 报告可附规则建议,主控直接 patch `se-team-rules`(治理属策略职责,非业务代码)。
- **轻量**:4 个角色 skill + 3 个模板 + 1 个同步脚本,其余在 v2.0 中全部精简。

---

## 📂 仓库结构

```text
Hermes-Enterprise/
├── SKILL.md                # 主控调度入口
├── README.md               # 概览与安装指南
├── LICENSE                 # MIT License
├── skills/                 # 子角色 Skills
│   ├── se-team-design/SKILL.md
│   ├── se-team-engineer/SKILL.md
│   ├── se-team-qa-release/SKILL.md
│   └── se-team-rules/SKILL.md
├── templates/              # 交付物模板(spec / report / review)
└── scripts/
    └── sync_skills.py      # 镜像仓库 skills 到 Hermes skills 目录
```

---

## 🤖 Agent 矩阵 (v2.0)

| Agent | 角色 | Hermes Skill | 主要交付物 |
| :--- | :--- | :--- | :--- |
| **Workflow Manager** | 仅策略与调度 | `software-engineering-team` (Master) | 4 字段运行约定 |
| **Design Agent** | 需求 + 架构 | `se-team-design` | 单个 `spec.md` |
| **Engineer Agent** | TDD 代码与单元测试 | `se-team-engineer` | 代码 + `implementation-report` |
| **QA & Release** | OCR 门禁 + 审查 | `se-team-qa-release` | `review.md`(结论) |
| — | 共享项目规则 | `se-team-rules` | 所有 agents 加载 |

### 分发如何工作 (v2.0)

主控以 **4 字段约定** 派发——无 contract 文件、无脚本校验;git ref 即校验:

```
delegate_task(
  goal="Design system architecture for user auth service",
  context="run: design-auth-flow. stage: design. "
          "output: docs/design/design-auth-flow-spec.md. "
          "rule: never overwrite other stages' output, never rewrite git history. "
          "Load skill: se-team-design. Load se-team-rules. Commit your deliverable yourself. Respond in Chinese."
)
```

子代理调用 `skill_view('se-team-design')` 获得角色与模板,基于当前 git HEAD 工作,自行提交。`git log` 成为可读谱系。

---

## 🔄 自纠错循环

```text
[Design Agent] ──► spec.md 提交
        │
        ▼
[Engineer Agent] ──► 代码 + report 提交 (TDD)
        │
        ▼
[QA & Release] ──► OCR 审查(参考)+ 人工审查 → 结论
        │
   ┌────┴────┐
   ▼         ▼
CHANGES_REQUESTED      APPROVED
   │                   │
   ▼                   ▼
回到对应阶段           用户最终验收
(engineer/design)
```

---

## 📄 License

MIT License。详见 `LICENSE`。
