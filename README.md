# 🌐 Cloudflare IP 优选工具

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Cloudflare%20Pages-blue?style=flat-square&logo=cloudflare" alt="Platform">
  <img src="https://img.shields.io/badge/Protocol-VLESS-green?style=flat-square" alt="Protocol">
  <img src="https://img.shields.io/badge/Auto-Update-orange?style=flat-square" alt="Auto Update">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License">
</p>

<p align="center">
  <b>全自动优选 Cloudflare IP，自动生成免费 VLESS 节点</b>
</p>

---

## ✨ 功能特性

| 特性 | 说明 |
|------|------|
| 🌍 **多地区优选** | 支持美国 US、日本 JP、新加坡 SG、德国 DE、荷兰 NL 等地区 |
| ⚡ **自动测速** | 每 12 小时自动测试并更新最优 IP |
| 🔄 **动态节点** | Worker 实时拉取最新 IP，无需手动更新 |
| 🎨 **深色模式** | 节点生成器支持浅色/深色主题切换 |
| 📱 **响应式设计** | 完美适配手机、平板、电脑 |
| 🔒 **安全传输** | 基于 TLS + WebSocket 的 VLESS 协议 |

---

## 🚀 快速开始

### 方式一：一键部署（推荐）

1. **Fork 本仓库** → 点击右上角 `Fork` 按钮
2. **部署到 Cloudflare Pages**
   - 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
   - 进入 **Pages** → **Create a project** → **Connect to Git**
   - 选择你 Fork 的仓库，直接部署
3. **配置环境变量**（可选）
   - `UUID`：你的自定义 UUID
   - `PROXYIP`：反代 IP 地址

### 方式二：Worker 部署

复制 [`_worker.js`](./CF-Worker/_worker.js) 到 Cloudflare Workers 或 Pages Functions：

```javascript
// 修改以下配置
let 我的VL密钥 = '你的UUID';
let 反代IP = 'proxyip.cmliussss.net';
```

---

## 📁 项目结构

```
CloudflareIP/
├── 📄 _worker.js          # Cloudflare Worker 主文件
├── 📄 index.html          # 节点生成器页面（支持深色模式）
├── 📂 py/                 # 优选脚本
│   ├── cf_tester.py       # Cloudflare IP 测速（6地区合一）
│   ├── web_scraper.py     # 网页抓取解析（3源合一）
│   └── domain_tester.py   # 域名延迟测试（2模式合一）
├── 📂 ip/                 # 优选结果输出目录
│   ├── SG.txt             # 新加坡优选 IP
│   ├── JP.txt             # 日本优选 IP
│   ├── US.txt             # 美国优选 IP
│   ├── DE.txt             # 德国优选 IP
│   ├── NL.txt             # 荷兰优选 IP
│   ├── IP.txt             # 全球综合优选 IP
│   ├── Me.txt             # 运营商优选 IP
│   ├── Cdtools.txt        # 高速优选 IP
│   ├── Cfxyz.txt          # 实测优选 IP
│   ├── Domain.txt         # 域名优选列表
│   └── Vless.txt          # VLESS 节点列表
└── 📂 .github/workflows/
    └── update-all.yml     # 统一工作流（12合一）
```

---

## 🎨 节点生成器

访问你的部署域名即可使用：

<p align="center">
  <a href="https://ip.cloudip.ggff.net" target="_blank">
    <img src="https://img.shields.io/badge/在线演示-点击访问-brightgreen?style=for-the-badge&logo=google-chrome" alt="Demo">
  </a>
</p>

### 使用方法

1. 输入你的 **UUID**（建议修改默认 UUID）
2. 输入你的 **部署域名**
3. 选择 **IP 来源**（地区/运营商/测速）
4. 点击 **一键生成节点**
5. 复制节点链接导入 **v2ray** 或 **karing**

---

## ⚙️ 高级配置

### 自定义 UUID

```javascript
// _worker.js 中修改
let 我的VL密钥 = '2e16f730-f641-449a-9ca1-fa0cf3f16118';
```

### 自定义反代 IP

```javascript
// _worker.js 中修改
let 反代IP = 'proxyip.cmliussss.net';
```

### 调整更新频率

编辑 [`.github/workflows/update-all.yml`](./.github/workflows/update-all.yml)：

```yaml
schedule:
  - cron: '0 0,12 * * *'  # 每12小时（可改为每天/每小时）
```

---

## 🌍 支持地区

| 地区 | 代码 | 说明 |
|------|------|------|
| 🇸🇬 新加坡 | SG | 东南亚低延迟 |
| 🇯🇵 日本 | JP | 东亚高速节点 |
| 🇺🇸 美国 | US | 全球覆盖 |
| 🇩🇪 德国 | DE | 欧洲节点 |
| 🇳🇱 荷兰 | NL | 欧洲备用 |
| 🌐 全球 | IP | 综合优选 |

---

## 🛠️ 技术栈

- **前端**：HTML5 + CSS3（响应式 + 深色模式）
- **后端**：Cloudflare Workers / Pages Functions
- **协议**：VLESS + TLS + WebSocket
- **自动化**：GitHub Actions
- **语言**：Python 3.10+

---

## 📜 免责声明

本项目仅供学习和技术研究使用，请遵守当地法律法规。使用本项目产生的任何后果由使用者自行承担。

---

## 🙏 致谢

- [Cloudflare](https://www.cloudflare.com) 提供优秀的边缘网络服务
- [v2ray](https://www.v2ray.com) 和 [karing](https://karing.app) 提供客户端支持

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/wt20230521">wt20230521</a>
</p>
