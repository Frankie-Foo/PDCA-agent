# Data Access Agent

`data-access-agent` 是中台数据小组的第一入口，负责把取数需求连接到 VPS/Odoo。

## 当前能力

- Hermes profile: `data-access-agent`
- 本地技能目录: `C:\Users\frank\.hermes\profiles\data-access-agent\skills`
- 数据调用脚本: `scripts\call-vps-data.ps1`
- 自然语言调用脚本: `scripts\invoke-data-access-agent.ps1`

第一阶段优先使用确定性的 `call-vps-data.ps1`，确保数据链路稳定。`invoke-data-access-agent.ps1` 用于后续让 Hermes 做自然语言解释和报告。

## 基础命令

检查登录：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\call-vps-data.ps1 -Mode whoami -Topic whoami
```

列 capabilities：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\call-vps-data.ps1 -Mode caps -Topic caps
```

查询当前用户：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\call-vps-data.ps1 `
  -Mode search `
  -ModelName res.users `
  -Domain 'id = @me' `
  -Fields '["id","name","login"]' `
  -Limit 1 `
  -Topic current-user
```

## 输出位置

脚本会把原始结果保存到：

```text
data_raw/{timestamp}_{topic}.json
```

后续 Agent 再读取 `data_raw`，生成：

```text
data_reports/{timestamp}_{topic}_summary.md
data_quality/{timestamp}_{topic}_issues.md
pdca_actions/{timestamp}_{topic}_actions.md
```

## 安全边界

- 只读查询。
- 不审批、不驳回、不发消息。
- 不写入、不删除、不导入业务数据。
- 不提交 `.env`、session、cookie、API Key。

