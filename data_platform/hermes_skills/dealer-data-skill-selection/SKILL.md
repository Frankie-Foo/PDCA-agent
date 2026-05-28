---
name: dealer-data-skill-selection
description: Choose useful skills for dealer data workflows.
version: 0.1.0
author: Vertu Data Platform
metadata:
  hermes:
    category: productivity
    tags:
      - dealer
      - hermes
      - skills
      - data-platform
---

# Dealer Data Skill Selection

Use this skill when deciding whether to install or enable extra Hermes skills for the dealer data platform.

## Current Priority

The dealer data platform currently needs:

1. Odoo/VPS data query.
2. Daily dealer performance report.
3. IM group push.
4. Weekly report evidence extraction.
5. Temporary data analysis.
6. Reusable metric definitions.

## Recommended Now

### Jina Reader

Use for reading external webpages, competitor pages, public dealer websites, LinkedIn-like public pages, and article/PDF content when building weekly report context.

Install only when a reliable source URL and API/auth method are available.

### Tavily

Use for web research: market news, competitor moves, India/Russia/Central Asia dealer context, product/retail intelligence.

Install only when a Tavily API key is available.

### hindsight

Use for report retrospectives and workflow memory: what broke, what query worked, which report wording was accepted, which data source had recurring issues.

Recommended for data platform work if available from a trusted source.

### agency-agents-zh

Use as Chinese multi-agent workflow prompts/templates. Helpful for Hermes routing and Chinese business task decomposition.

Recommended if it is a trusted local or official skill package.

## Not Recommended For This Phase

### Fal.ai

Useful for image/video generation. Not needed for daily dealer reports, Odoo data, or IM pushing.

### RTK

If RTK means Redux Toolkit or frontend state tooling, it is not needed unless building a web dashboard.

If RTK means another internal skill, confirm its source and purpose before installing.

### Tokscale / Tailscale

If this means Tailscale, it is infrastructure, not a report skill. Use only when Hermes must be accessed across devices or private networks.

### Hermes Agent Self-Evolution

High leverage but high risk. Do not enable before daily report and IM push are stable. It can change behavior unexpectedly if not constrained.

## Rule

For the current dealer data platform, install skills in this order:

1. Core Odoo/VPS skills.
2. Dealer daily report skill.
3. IM/message skill.
4. Jina Reader or Tavily only after API keys are ready.
5. Hindsight after one week of stable operations.
6. Self-evolution last, and only with review gates.

