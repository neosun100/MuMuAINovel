[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

<div align="center">

# MuMuAINovel 📚✨

**🚀 AI驅動的小說創作助手 | 自動生成百萬字長篇小說**

![Version](https://img.shields.io/badge/version-1.10.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)
![React](https://img.shields.io/badge/react-18.3.1-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue.svg)
![License](https://img.shields.io/badge/license-GPL%20v3-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)
![API](https://img.shields.io/badge/API%20Endpoints-200+-orange.svg)

**⭐ 如果這個專案對你有幫助，請給一個 Star！**

</div>

---

## 🎯 核心亮點

| 功能 | 說明 |
|------|------|
| 🤖 **多AI支援** | OpenAI / Gemini / Claude 無縫切換 |
| 📖 **智慧章節生成** | RTCO框架動態上下文，自動情節延續 |
| 🎭 **角色管理** | 關係圖譜、組織架構、成長追蹤 |
| 🔮 **伏筆系統** | 智慧追蹤，生成時自動注入 |
| 📊 **品質評分** | 基礎指標 + AI評估，S/A/B/C/D分級 |
| 🔍 **一致性檢測** | AI分析角色行為和情節連貫性 |
| ⏱️ **時間線管理** | 故事事件時間線追蹤和視覺化 |
| 🎨 **風格分析** | 學習寫作風格，生成風格指南 |
| 🔄 **重複檢測** | 檢測章節內和跨章節的重複內容 |
| 💾 **PostgreSQL** | 生產級資料庫，支援200+並發用戶 |
| 🚀 **批量生成** | 自動生成100章×10000字 |

---

## ✨ 功能特性

### 核心功能

- 🤖 **多AI模型** - 支援 OpenAI、Gemini、Claude 及自訂API端點
- 📝 **智慧嚮導** - AI自動生成大綱、角色、世界觀
- 👥 **角色管理** - 視覺化關係圖和組織架構管理
- 📖 **章節編輯器** - 建立、編輯、重新生成、潤色章節
- 🌐 **世界構建** - 完整的故事背景構建
- 💡 **靈感模式** - AI驅動的創意生成
- ✍️ **自訂風格** - 支援自訂AI寫作風格
- 📊 **思維導圖** - 視覺化章節邏輯關係

### 進階功能 (v1.3.0+)

- 🔮 **伏筆管理** - 追蹤情節伏筆，提醒未解決的線索
- 🔍 **一致性檢測** - AI分析角色行為和情節連貫性
- ⏱️ **時間線管理** - 故事事件時間線追蹤
- 🎨 **風格分析** - 學習專案寫作風格，生成風格指南
- 📊 **章節品質評分** - 基礎指標 + AI綜合評估
- 🔄 **重複檢測** - 檢測重複/相似內容
- 📈 **角色成長** - 追蹤角色能力、關係、心理變化

---

## 🚀 快速開始

### 前置條件

- Docker 和 Docker Compose
- 至少一個AI服務API Key（OpenAI/Gemini/Claude）

### Docker Compose 部署（推薦）

```bash
# 1. 複製專案
git clone https://github.com/neosun100/MuMuAINovel.git
cd MuMuAINovel

# 2. 設定環境變數
cp .env.example .env
# 編輯 .env 檔案，填入 API Key 和資料庫密碼

# 3. 啟動服務
docker-compose up -d

# 4. 存取應用
# 開啟瀏覽器存取 http://localhost:8000
```

### 使用 Docker Hub 映像

```bash
# 拉取最新映像（包含模型檔案）
docker pull mumujie/mumuainovel:latest

# 設定並啟動
cp .env.example .env
docker-compose up -d
```

---

## ⚙️ 設定說明

### 必需設定 (.env)

```bash
# PostgreSQL 資料庫
DATABASE_URL=postgresql+asyncpg://mumuai:your_password@postgres:5432/mumuai_novel
POSTGRES_PASSWORD=your_secure_password

# AI 服務（至少設定一個）
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_AI_PROVIDER=openai
DEFAULT_MODEL=gpt-4o-mini

# 本地帳戶登入
LOCAL_AUTH_ENABLED=true
LOCAL_AUTH_USERNAME=admin
LOCAL_AUTH_PASSWORD=your_password
```

### 可選設定

```bash
# LinuxDO OAuth
LINUXDO_CLIENT_ID=your_client_id
LINUXDO_CLIENT_SECRET=your_client_secret

# Gemini
GEMINI_API_KEY=your_gemini_key

# Claude
ANTHROPIC_API_KEY=your_anthropic_key

# 連線池（高並發）
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=30
```

---

## 📚 API 文件

### API 概覽

本專案提供 **200+ RESTful API 端點**，涵蓋完整的小說創作流程。

| 模組 | 端點數 | 說明 |
|------|--------|------|
| Auth | 8 | 登入、OAuth、會話管理 |
| Projects | 12 | 專案CRUD、匯入匯出 |
| Outlines | 15 | 大綱生成、編輯、AI續寫 |
| Characters | 18 | 角色管理、關係圖譜 |
| Chapters | 25 | 章節生成、編輯、批量操作 |
| Foreshadows | 10 | 伏筆追蹤、解決提醒 |
| Consistency | 4 | 角色/情節一致性檢測 |
| Timeline | 6 | 事件時間線管理 |
| Style | 3 | 寫作風格學習和分析 |
| Quality | 2 | 章節品質評估 |
| Duplicate | 2 | 重複內容檢測 |
| Growth | 6 | 角色成長追蹤 |

### 線上文件

啟動服務後存取：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔧 小說創作流水線

### 自動化工作流

MuMuAINovel 支援透過API實現全自動小說創作：

```
1. POST /api/auth/local/login           # 登入
2. POST /api/projects                    # 建立專案
3. PUT  /api/projects/{id}               # 設定世界觀
4. POST /api/characters (迴圈)           # 建立角色 (80-150個)
5. POST /api/outlines (迴圈)             # 建立大綱 (100章)
6. POST /api/chapters (迴圈)             # 建立章節 (100個)
7. POST /api/chapters/project/{id}/batch-generate  # 提交批量生成
8. GET  /api/chapters/project/{id}       # 監控進度
```

### 關鍵參數

| 參數 | 預設值 | 範圍 | 說明 |
|------|--------|------|------|
| count | 10 | 1-100 | 生成章節數 |
| target_word_count | 10000 | 1000-20000 | 每章字數 |
| max_retries | 10 | 0-20 | 最大重試次數 |

### RTCO 上下文框架

```
章節序號    上下文策略
─────────────────────────────────
第 1 章     僅大綱 + 角色
第 2-10 章  上章結尾 300 字 + 涉及角色
第 11-50 章 上章結尾 500 字 + 相關記憶 3 條
第 51+ 章   上章結尾 500 字 + 故事骨架 + 智慧記憶 5 條
```

### 重試策略（分階段退避）

| 重試次數 | 等待時間 | 說明 |
|----------|----------|------|
| 1-3 | 2, 4, 8 秒 | 快速重試 |
| 4-6 | 30 秒 | 中等等待 |
| 7-10 | 60 秒 | 長等待 |

---

## 🔄 任務恢復

### 自動恢復腳本

```bash
# 一次性恢復
python auto_resume.py

# 守護程序模式（直到全部完成）
python auto_resume.py --daemon

# 背景執行並記錄日誌
nohup python auto_resume.py --daemon > resume.log 2>&1 &
```

### 環境變數

```bash
export MUMUAI_BASE_URL=http://localhost:8000
export MUMUAI_USERNAME=admin
export MUMUAI_PASSWORD=your_password
```

---

## 🏗️ 技術棧

| 層級 | 技術 |
|------|------|
| **後端** | FastAPI • SQLAlchemy • Pydantic • Alembic |
| **資料庫** | PostgreSQL 18 • 連線池最佳化 |
| **前端** | React 18 • TypeScript • Ant Design • Zustand |
| **AI** | OpenAI SDK • Gemini SDK • Anthropic SDK |
| **部署** | Docker • Docker Compose |

### 專案結構

```
MuMuAINovel/
├── backend/
│   ├── app/
│   │   ├── api/              # 26個API模組
│   │   ├── models/           # 21個資料模型
│   │   ├── services/         # 31個業務服務
│   │   └── main.py           # 應用入口
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/            # 25個頁面元件
│   │   └── services/         # API服務
│   └── package.json
├── docs/                     # 文件
│   ├── QUICKSTART.md         # 快速啟動指南
│   ├── KIRO_INTERACTION_GUIDE.md  # 完整API指南
│   └── NOVEL_CREATION_PIPELINE.md # 流水線文件
├── auto_resume.py            # 自動恢復腳本
├── novel_pipeline.py         # Python自動化腳本
├── docker-compose.yml
└── Dockerfile
```

---

## 📋 版本歷史

### v1.10.0 (2026-01-05) - 當前版本

**第三階段完成 - 進階寫作輔助**

| 版本 | 功能 | 說明 |
|------|------|------|
| v1.10.0 | 風格指南整合 | AI生成時自動注入學習的寫作風格 |
| v1.9.0 | 角色成長 | 追蹤角色能力、關係、心理變化 |
| v1.8.0 | 重複檢測 | 檢測章節內和跨章節的重複內容 |
| v1.7.0 | 品質評分 | 基礎指標 + AI評估，S/A/B/C/D分級 |
| v1.6.0 | 風格分析 | 學習專案寫作風格，生成風格指南 |
| v1.5.0 | 時間線管理 | 故事事件時間線追蹤 |
| v1.4.0 | 一致性檢測 | AI分析角色行為和情節連貫性 |
| v1.3.x | 伏筆系統 | 智慧追蹤，生成時自動注入 |

---

## 🤝 貢獻指南

歡迎貢獻！請提交 Issues 和 Pull Requests。

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 📝 授權條款

本專案採用 [GNU General Public License v3.0](LICENSE) 授權條款

- ✅ 可自由使用、修改和分發
- ✅ 可用於商業用途
- 📝 修改版本必須開源
- 📝 必須保留原作者版權

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/MuMuAINovel&type=Date)](https://star-history.com/#neosun100/MuMuAINovel)

## 📱 關注公眾號

![公眾號](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

---

<div align="center">

**⭐ 如果這個專案對你有幫助，請給一個 Star！**

Made with ❤️ by Neo

</div>
