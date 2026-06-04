# 经销商线上经营（已并入客流分析台）

**已并入** `walkin-cockpit` 客流分析页（`online-merged-insights.js`）。本目录 `index.html` 仅做跳转。

## 访问

- http://127.0.0.1:8767/walkin-cockpit/#oi-merged
- 旧链接 http://127.0.0.1:8767/online-cockpit/ 会自动重定向

## 维护渠道/OKR 参考数据

```powershell
python D:\经销商PDCA\data_platform\data_role_pdca_mvp\scripts\build_online_channel_reference_once.py
```

写入 `modules/walkin_cockpit/data/online_channel_reference.json`。
