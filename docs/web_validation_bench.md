# Web 规则验证台

Status: supporting validation surface
Date: 2026-05-18

线上地址：<https://startup-sim-khaki.vercel.app>

## 1. 定位

`frontend/` 不再是最终独立游戏表现层主线。后续正式游戏开发以 Godot 为主。

Web 前端继续保留三个价值：

1. 远程试玩入口：无需安装 Godot 即可快速体验当前规则。
2. 规则验证台：验证 API、命令解析、回合结算和玩家可读文案。
3. 对照样机：为 Godot UI 提供已经验证过的信息组织参考。

## 2. 边界

Web 可以做：

- 创建会话、提交回合、展示 settled facts。
- 展示命令预览、董事会、竞品、经营洞察和月度战报。
- 在没有线上后端时使用 demo fallback 保持页面可打开。
- 为 GitHub/Vercel 提供快速 smoke。

Web 不再做：

- 大规模视觉打磨。
- 新增只服务 React/PixiJS 的玩法系统。
- 作为最终桌面分发方案。
- 绕过 `TurnEngine` 或 C# Core 自行结算规则。

## 3. 本地运行

后端：

```powershell
cd D:\Startup-sim
uvicorn src.api.app:app --reload
```

前端：

```powershell
cd D:\Startup-sim\frontend
npm install
npm run dev
```

默认环境变量：

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

线上 Vercel 可以不配置真实后端；为空时前端进入 demo fallback。

## 4. 验证命令

```powershell
cd D:\Startup-sim\frontend
npm test -- --run
npm run build
npm run test:e2e
```

根目录回归：

```powershell
cd D:\Startup-sim
pytest tests/ -q
python scripts/check_docs_consistency.py
```

## 5. 与 Godot 的关系

Godot 是正式表现层；Web 是规则验证和远程演示面。

当 Godot 与 Web 对同一条玩家指令产生不同结果时，以 C# Core / Python 黄金样例为准，而不是以 Web UI 文案为准。
