# 销售团队 Cursor + Hermes Agent 协同办公与多智能体（Multi-Agent）搭建方案

> **产品说明**：Hermes Agent 是由 [Nous Research](https://nousresearch.com) 开发、2026 年 2 月开源发布的自主 AI Agent 平台（GitHub 16 万+ Star，MIT 协议）。官网：[hermes-agent.nousresearch.com](https://hermes-agent.nousresearch.com)

---

## 目录

1. [方案概述](#1-方案概述)
2. [安装与初始化](#2-安装与初始化)
3. [需求一：团队文件互通与共享工作区](#3-需求一团队文件互通与共享工作区)
4. [需求二：多智能体角色搭建与配置](#4-需求二多智能体角色搭建与配置)
5. [需求三：跨成员 Agent 相互调用与协同](#5-需求三跨成员-agent-相互调用与协同)
6. [进阶：团队共享记忆与技能分发](#6-进阶团队共享记忆与技能分发)
7. [落地实施三步走](#7-落地实施三步走)
8. [核心功能速查表](#8-核心功能速查表)

---

## 1. 方案概述

本系统由三个核心支柱组成：

| 支柱 | 目标 | 核心技术 |
|------|------|---------|
| **统一工作区** | 人与 Agent 看到的信息完全一致 | Git 仓库 / 企业云盘 |
| **多角色 Agent 团队** | 专业分工，任务自动委派 | Hermes Profiles + SOUL.md + AGENTS.md |
| **网关互联** | 打破单机限制，跨设备互调 | Tailscale + Hermes API Server |

```
[ 经理的 Cursor + Hermes ] <=========> [ 销售 A 的 Cursor + Hermes ]
            \                                    /
             \                                  /
          [ 共享工作区 (Git/网盘) ] <=====> [ 共享记忆库 (Honcho) ]
```

---

## 2. 安装与初始化

### Linux / macOS / WSL2

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows（PowerShell，早期 Beta）

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

### 初始配置

```bash
hermes setup
```

---

## 3. 需求一：团队文件互通与共享工作区

### 方案 A：Git 仓库（推荐，对 Agent 最友好）

在 GitHub / GitLab / Gitee 创建私有仓库 `sales-workspace`，推荐目录结构：

```
sales-workspace/
├── .cursorrules              # 全局 Cursor 提示词规范
├── AGENTS.md                 # 团队智能体通信录、分工与目录规则
├── inbox/                    # 原始客户背景、会议纪要、往来邮件
├── insights/                 # market-analyst 的输出目录
├── contracts/                # 合同草案与风险报告
├── manager/                  # 经理工作目录（日常文档、审批流）
├── sales_alice/              # 销售员 Alice 的日常工作目录
└── sales_bob/                # 销售员 Bob 的日常工作目录
```

**自动同步脚本（每日下班前运行）**：

```bash
git add . && git commit -m "Auto Sync $(date +%Y-%m-%d)" && git push
```

经理执行 `git pull` 即可在 Cursor 侧边栏查阅所有成员最新文件。

### 方案 B：企业云盘（OneDrive / 坚果云，适合非技术团队）

1. 安装 OneDrive 或坚果云，创建共享文件夹
2. 所有人在 Cursor 中 **Open Folder** 打开该共享文件夹
3. 保存即同步，无需手动操作

---

## 4. 需求二：多智能体角色搭建与配置

### 步骤 1：创建 Agent Profiles

```bash
# 创建"市场分析员"Profile
hermes profile create market-analyst --description "分析客户背景与市场信息，提炼销售切入点。"

# 创建"合同条款专家"Profile
hermes profile create contract-expert --description "审查合同条款，识别违约风险，提供修改建议。"
```

> 创建后，这两个 Profile 会自动生成对应命令：`market-analyst chat`、`contract-expert chat` 等。

### 步骤 2：编写各自的 SOUL.md（Agent 灵魂）

**`~/.hermes/profiles/market-analyst/SOUL.md`**

```markdown
# Identity
你是一名顶尖的销售市场分析师（Sales Market Analyst）。
你的职责是消化原始的客户聊天记录、新闻及行业数据，并将其提炼为销售切入点。

## Communication Style
- 风格理性、客观、极具战略眼光
- 拒绝空洞的套话或推销行话
- 使用结构化的要点（Bullet Points）交付洞察
- 每份报告必须包含：客户核心诉求 / 潜在顾虑 / 推荐切入角度
```

**`~/.hermes/profiles/contract-expert/SOUL.md`**

```markdown
# Identity
你是销售团队专属的合同与法律条款审核专家（Contract & Legal Expert）。

## Style & Posture
- 极度注重细节，风险规避型人格
- 审查合同时，清晰标出潜在的违约风险和责任边界
- 提供直接的修改建议（Redline Draft），而非含糊的批评
- 输出格式：风险等级（高/中/低）+ 原文引用 + 修改建议
```

### 步骤 3：配置 AGENTS.md（团队分工契约）

在共享工作区根目录新建 `AGENTS.md`，Hermes 启动时自动加载：

```markdown
# 销售团队智能体分工与流转契约

## 目录架构
- `/inbox/`：存放原始客户背景、会议纪要和往来邮件
- `/insights/`：market-analyst 的输出目录
- `/contracts/`：存放草拟的提案与合同文件

## 流转规则

### 1. 客户分析阶段（对应 /inbox/ 目录）
- 当新文件被放入 `/inbox/` 时，调用 `market-analyst` 分析业务背景
- 输出分析报告至 `/insights/{客户名称}_analysis.md`

### 2. 合同审查阶段（对应 /contracts/ 目录）
- 当 `/contracts/` 目录下生成新的合同草案时，调用 `contract-expert` 进行安全审查
- 输出风险报告至 `/contracts/{客户名称}_risk_report.md`
```

### 步骤 4：自动任务委派（delegate_task）

`delegate_task` 是 Hermes 内置工具，适合**短期推理子任务**：父 Agent 需要答案后才能继续时使用。

**使用场景**：在 Cursor 聊天框对主 Agent 说：
> "分析 /inbox/apple.txt 的客户背景，然后帮我起草一份合同。"

**执行过程**：主 Agent 自动调用 `delegate_task`，在后台分别拉起 `market-analyst` 和 `contract-expert` 子 Agent，各司其职，结果自动汇总返回。

### 步骤 5：多智能体看板（Kanban）— 并发任务场景

Hermes Kanban 是 **SQLite 持久化任务看板**，多个 Profile 可以协作处理共享任务队列。

```bash
# 启动看板调度器（在 gateway 内持续运行）
hermes kanban daemon start

# 查看看板状态
hermes kanban list

# 投递分析任务
hermes kanban create \
  --title "分析微软采购需求" \
  --assignee market-analyst \
  --body "参考 /inbox/microsoft.txt，输出至 /insights/"

# 投递合同审查任务
hermes kanban create \
  --title "审查微软合同条款" \
  --assignee contract-expert \
  --body "参考 /contracts/microsoft_draft.md，输出风险报告"
```

> **delegate_task vs Kanban 选择原则**：
> - `delegate_task`：短期、同步、结果直接回传父 Agent，秒级到分钟级
> - `Kanban`：持久化、异步、多人可见、可中断续接，适合跨会话长任务

---

## 5. 需求三：跨成员 Agent 相互调用与协同

### 环境准备

1. **安装 Tailscale**：每台电脑获得固定内网 IP（免费，[tailscale.com](https://tailscale.com)）
2. **开启 Hermes API Server**：在每个成员电脑的 Profile `.env` 文件中配置：

```env
# ~/.hermes/profiles/<profile-name>/.env 或默认 ~/.hermes/.env
API_SERVER_ENABLED=true
API_SERVER_PORT=8642
API_SERVER_KEY=each_member_unique_key   # 每人设置独有密钥
API_SERVER_HOST=0.0.0.0                 # 允许局域网访问（Tailscale 内网安全）
```

3. **启动 API Server**：

```bash
hermes gateway start   # gateway 启动时自动带起 API Server
```

### 在 AGENTS.md 中注册跨设备路由表

```markdown
## 跨设备智能体路由表

- **经理的 Agent（折扣审批 / 方案终审）**
  - URL: `http://100.115.x.manager:8642/v1`
  - Key: `manager-agent-key-xyz`

- **Alice 的 Agent（合同条款审核）**
  - URL: `http://100.115.x.alice:8642/v1`
  - Key: `alice-agent-key-123`

- **Bob 的 Agent（竞品分析专家）**
  - URL: `http://100.115.x.bob:8642/v1`
  - Key: `bob-agent-key-456`
```

### 互调体验

在 Cursor Chat 或 Hermes 终端输入：
> "帮我把 manager/proposal.md 发给 Alice 的 Agent，让她审核条款是否符合规范。"

你的 Agent 读取路由表，通过 Tailscale 内网向 Alice 电脑上的 Hermes 发送请求，结果直接呈现在你的 Cursor 中。

> **注意**：Kanban 看板的 `kanban.db` 是本机 SQLite，跨主机任务协作推荐使用 API Server 互调（`delegate_task` 远程模式）或消息队列桥接。

---

## 6. 进阶：团队共享记忆与技能分发

### 共享知识库（Honcho 共享记忆）

Hermes 内置 [Honcho](https://honcho.dev) 用户建模，支持将所有成员的 Agent 记忆库配置为同一个云端 Honcho ID：

```yaml
# config.yaml
memory:
  honcho:
    enabled: true
    app_id: "sales-team-shared"   # 全团队统一 app_id
    user_id: "{{member_name}}"    # 每人独立 user_id，但共享应用空间
```

**效果**：销售 A 的 Agent 记录了「XX 客户偏好茶文化，抗拒硬推销」后，销售 B 的 Agent 接待该客户时也能立刻调取这条记忆。

### 销售技能分发（Profile 导入导出）

```bash
# 经理将调教好的"金牌销售助手" Profile 推送至 Git
cd ~/.hermes/profiles/gold-sales-agent
git push origin main

# 新员工入职，一键导入
hermes profile import <your-sales-agent-profile-url>
```

新员工安装完成后立即拥有一模一样的销售专家助手，包含完整的 SOUL.md、技能库和工作流规则。

---

## 7. 落地实施三步走

### 第一阶段：文件铺底（第 1-3 天）

- [ ] 为团队所有成员安装 Cursor
- [ ] 创建共享 Git 仓库（或配置企业云盘）
- [ ] 按推荐目录结构组织 `inbox/`、`insights/`、`contracts/` 等文件夹
- [ ] 编写 `.cursorrules` 统一 AI 写作规范
- [ ] 让大家习惯在 Cursor 中编辑日常文档

### 第二阶段：Agent 角色定义与本地协作（第 4-7 天）

- [ ] 每台电脑安装 Hermes Agent
- [ ] 运行 `hermes profile create` 创建 `market-analyst` 和 `contract-expert`
- [ ] 编写各自的 `SOUL.md`
- [ ] 在共享目录配置 `AGENTS.md` 分工契约
- [ ] 测试 `delegate_task` 本地多 Agent 自动委派
- [ ] 测试 `hermes kanban` 并发任务流水线

### 第三阶段：组网互联与跨设备协作（第 8-14 天）

- [ ] 全员安装 Tailscale 并加入同一网络
- [ ] 各成员在 `.env` 中启用 `API_SERVER_ENABLED=true`
- [ ] 在 `AGENTS.md` 中录入跨设备路由表
- [ ] 测试跨设备 Agent 互调（如经理调用 Alice 的 Agent 审核合同）
- [ ] 配置 Honcho 共享记忆，验证客户信息跨成员同步
- [ ] 将调教好的 Profile 推送至 Git，供新员工一键导入

---

## 8. 核心功能速查表

| 功能 | 命令 / 文件 | 说明 |
|------|------------|------|
| 创建角色 | `hermes profile create <name>` | 创建独立 Profile，自动生成同名命令 |
| 定义性格 | `~/.hermes/profiles/<name>/SOUL.md` | 角色身份、沟通风格、输出格式 |
| 分工契约 | 工作区根目录 `AGENTS.md` | 目录规则、流转逻辑、路由表 |
| 子任务委派 | `delegate_task`（内置工具） | 短期同步子任务，结果回传父 Agent |
| 并发任务看板 | `hermes kanban create/list/daemon` | 持久化异步任务队列，多 Profile 协作 |
| 开放 API | `.env` 中 `API_SERVER_ENABLED=true` | 默认端口 8642，OpenAI 兼容接口 |
| 跨设备组网 | Tailscale + API Server | 固定内网 IP，安全互访 |
| 共享记忆 | Honcho 集成（`config.yaml`） | 客户信息跨成员 Agent 共享 |
| 技能导入 | `hermes profile import <url>` | 新员工一键获得完整销售助手配置 |
| 消息平台 | `hermes gateway start` | 支持飞书、钉钉、企业微信等 20+ 平台 |

---

*文档生成时间：2026-05-26 | 基于 Hermes Agent v2026.5.16 整理*
