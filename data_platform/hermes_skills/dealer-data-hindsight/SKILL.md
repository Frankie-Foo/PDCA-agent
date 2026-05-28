---
name: dealer-data-hindsight
description: Capture reusable lessons from data work.
version: 0.1.0
author: Vertu Data Platform
metadata:
  hermes:
    category: productivity
    tags:
      - dealer
      - hindsight
      - retrospection
      - data-quality
      - metric-dictionary
---

# Dealer Data Hindsight

Use this skill after daily reports, weekly reports, monthly reports, and ad-hoc data requests to capture reusable lessons.

The goal is to reduce repeated mistakes:

- wrong metric definition
- missing sales alias
- missing target
- bad source file
- query that worked once but was not saved
- recurring business question
- repeated data quality issue

## When To Use

- A report is delivered.
- A data issue is fixed.
- A temporary request appears likely to repeat.
- A user corrects a mapping or metric.
- Hermes successfully pulls system data with a useful query.

## Output Location

Prefer writing notes under:

```text
D:\经销商PDCA\data_platform\hindsight
```

Suggested files:

```text
metric_lessons.md
source_lessons.md
sales_alias_lessons.md
report_prompt_lessons.md
im_push_lessons.md
```

## Capture Template

```markdown
# Hindsight Entry YYYY-MM-DD

## Context
-

## What Failed Or Was Corrected
-

## Root Cause
-

## Reusable Rule
-

## Files Updated
-

## Next Automation Candidate
-
```

## Current Known Lessons

- `DEHDAHOUMAIMA` must be mapped to `Lina`.
- Daily dealer report target total should be `582.0 万` under the current template.
- Temporary Excel files are not the formal source of truth unless explicitly confirmed.
- IM push must not be reported as sent unless webhook POST succeeds.

