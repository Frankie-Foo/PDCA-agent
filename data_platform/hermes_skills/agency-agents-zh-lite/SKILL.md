---
name: agency-agents-zh-lite
description: Coordinate Chinese business data agents.
version: 0.1.0
author: Vertu Data Platform
metadata:
  hermes:
    category: autonomous-ai-agents
    tags:
      - chinese
      - multi-agent
      - dealer
      - data-platform
---

# Agency Agents ZH Lite

Use this skill when Hermes needs to split a Chinese business/data request into specialist agents and then merge their outputs.

This is a lightweight local substitute for agency-agents-zh until a trusted official package is available.

## Default Dealer Data Agency

For dealer data platform tasks, use this agency:

```text
调度中枢：Hermes
工作台：Cursor
数据源：Odoo/VPS + Git/files
交付渠道：IM 群 / Markdown / Excel / PPT
```

## Agent Roles

### 1. 需求分诊员

Clarify:

- 日报、周报、月报、临时需求、数据异常？
- 时间范围是什么？
- 输出给谁？
- 是否要推 IM？

### 2. 数据取数员

Pull:

- Odoo/VPS data
- system JSON
- Excel exports
- targets/pipeline configs

### 3. 指标口径员

Check:

- 当月业绩
- 当月目标
- 达成率
- 当日录单收款
- 在途业绩
- 环比/同比

### 4. 数据核对员

Check:

- missing fields
- missing targets
- sales aliases
- negative performance
- suspicious totals
- partial source files

### 5. 经营洞察员

Summarize:

- 谁落后
- 谁异常
- 哪组需要核对
- 哪个问题要业务确认

### 6. 交付包装员

Package:

- IM message
- Markdown report
- Excel output
- PPT outline

## Standard Response Shape

```markdown
## 任务判断
-

## 调度链路
-

## 各 Agent 输出
-

## 最终交付
-

## 后续沉淀
-
```

## Rules

- 用中文输出，除非用户要求英文。
- 先给结论，再给明细。
- 数据类任务必须标明口径和数据源。
- 需要发群时必须确认发送状态。

