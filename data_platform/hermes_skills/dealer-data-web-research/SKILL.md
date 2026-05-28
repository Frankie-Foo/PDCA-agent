---
name: dealer-data-web-research
description: Research dealer market evidence for reports.
version: 0.1.0
author: Vertu Data Platform
metadata:
  hermes:
    category: research
    tags:
      - dealer
      - tavily
      - jina-reader
      - web-research
      - weekly-report
---

# Dealer Data Web Research

Use this skill when dealer weekly/monthly reports need external evidence, market context, competitor activity, public dealer information, regional retail facts, or page reading.

This skill is the safe wrapper for Tavily and Jina Reader style work. It does not assume API keys are present. If keys/tools are unavailable, produce a research task card and ask Hermes to route it to an enabled web research tool.

## When To Use

- 周报需要市场/竞品/区域背景。
- 需要读取公开网页、新闻、PDF、官网、公开代理商页面。
- 需要给印度、俄罗斯、中亚等区域的经销商分析补外部证据。
- 需要验证某个客户或潜在代理商的公开信息。

## Preferred Tooling

1. Tavily: broad web search and market research.
2. Jina Reader: clean extraction from specific URLs and webpages.
3. Native Hermes web/search tools if Tavily/Jina are unavailable.

## Required Inputs

```yaml
business_question:
region_or_country:
dealer_or_topic:
time_scope:
known_urls:
output_format: markdown_summary | report_evidence | source_table
```

## Output

```markdown
# 外部研究摘要

## 结论
-

## 证据
| 来源 | 时间 | 事实 | 对周报/月报的意义 |
|---|---|---|---|

## 可用于报告的话术
-

## 需要业务确认
-
```

## Rules

- Do not invent sources.
- Separate verified facts from inference.
- Keep source URLs with the evidence table.
- Do not use external research to replace Odoo/VPS internal data.
- For daily dealer reports, external research is usually unnecessary.

