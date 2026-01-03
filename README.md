# MuMuAINovel 📚✨

<div align="center">

![Version](https://img.shields.io/badge/version-1.10.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)
![React](https://img.shields.io/badge/react-18.3.1-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue.svg)
![License](https://img.shields.io/badge/license-GPL%20v3-blue.svg)
![API](https://img.shields.io/badge/API%20Endpoints-200+-orange.svg)

**🚀 基于 AI 的智能小说创作助手 | AI-Powered Novel Writing Assistant**

[English](#-features) • [简体中文](#-特性) • [功能演示](#-项目预览) • [快速开始](#-快速开始) • [API 文档](#-api-文档)

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**

</div>

---

## 🎯 项目亮点

| 特性 | 描述 |
|------|------|
| 🤖 **多 AI 模型支持** | OpenAI / Gemini / Claude 无缝切换 |
| 📖 **智能章节生成** | RTCO 框架动态上下文，自动衔接剧情 |
| 🎭 **角色管理系统** | 人物关系图谱、组织架构、成长轨迹追踪 |
| 🔮 **伏笔管理** | 智能追踪剧情伏笔，AI 生成时自动注入 |
| 📊 **质量评分** | 基础指标 + AI 综合评估，S/A/B/C/D 分级 |
| 🔍 **一致性检测** | AI 分析角色行为一致性和剧情连贯性 |
| ⏱️ **时间线管理** | 故事事件时间轴追踪，可视化管理 |
| 🎨 **风格分析** | 学习写作风格，生成风格指南供 AI 参考 |
| 🔄 **重复检测** | 检测章节内部和章节间的重复内容 |
| 💾 **PostgreSQL** | 生产级数据库，支持 200+ 并发用户 |

---

## ✨ 特性

### 核心功能

- 🤖 **多 AI 模型** - 支持 OpenAI、Gemini、Claude 等主流模型，支持中转 API
- 📝 **智能向导** - AI 自动生成大纲、角色和世界观
- 👥 **角色管理** - 人物关系、组织架构可视化管理
- 📖 **章节编辑** - 支持创建、编辑、重新生成和润色
- 🌐 **世界观设定** - 构建完整的故事背景
- 💡 **灵感模式** - AI 驱动的创作灵感和点子生成
- ✍️ **自定义风格** - 支持自定义 AI 写作风格
- 📊 **思维链图谱** - 可视化章节逻辑关系

### 高级功能 (v1.3.0+)

- 🔮 **伏笔管理** - 智能追踪剧情伏笔，提醒未回收线索，AI 生成时自动注入伏笔上下文
- 🔍 **一致性检测** - AI 分析角色行为一致性和剧情连贯性，提供改进建议
- ⏱️ **时间线管理** - 故事事件时间轴追踪，支持按章节、类型筛选
- 🎨 **风格分析** - 学习项目写作风格，生成风格指南供 AI 参考
- 📊 **章节质量评分** - 基础指标 + AI 综合评估，返回分数和改进建议
- 🔄 **重复内容检测** - 检测章节内部和章节间的重复/相似内容
- 📈 **角色成长轨迹** - 追踪角色能力、关系、心理、状态变化

### 系统功能

- 🔐 **多种登录** - LinuxDO OAuth 或本地账户登录
- 💾 **PostgreSQL** - 生产级数据库，多用户数据隔离
- 🐳 **Docker 部署** - 一键启动，开箱即用
- 📤 **数据导入导出** - 项目数据、角色卡片的导入导出
- 🎯 **职业等级体系** - 自定义职业和等级系统

---

## 📸 项目预览

<details>
<summary>📷 点击展开截图</summary>

<div align="center">

### 登录界面
![登录界面](images/1.png)

### 主界面
![主界面](images/2.png)

### 项目管理
![项目管理](images/3.png)

</div>

</details>

---

## 🚀 快速开始

### 前置要求

- Docker 和 Docker Compose
- 至少一个 AI 服务的 API Key（OpenAI/Gemini/Claude）

### Docker Compose 部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/neosun100/MuMuAINovel.git
cd MuMuAINovel

# 2. 配置环境变量
cp backend/.env.example .env
# 编辑 .env 文件，填入 API Key 和数据库密码

# 3. 启动服务
docker-compose up -d

# 4. 访问应用
# 打开浏览器访问 http://localhost:8000
```

### 使用 Docker Hub 镜像

```bash
# 拉取最新镜像（已包含模型文件）
docker pull mumujie/mumuainovel:latest

# 配置并启动
cp backend/.env.example .env
docker-compose up -d
```

---

## ⚙️ 配置说明

### 必需配置 (.env)

```bash
# PostgreSQL 数据库
DATABASE_URL=postgresql+asyncpg://mumuai:your_password@postgres:5432/mumuai_novel
POSTGRES_PASSWORD=your_secure_password

# AI 服务（至少配置一个）
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_AI_PROVIDER=openai
DEFAULT_MODEL=gpt-4o-mini

# 本地账户登录
LOCAL_AUTH_ENABLED=true
LOCAL_AUTH_USERNAME=admin
LOCAL_AUTH_PASSWORD=your_password
```

### 可选配置

```bash
# LinuxDO OAuth
LINUXDO_CLIENT_ID=your_client_id
LINUXDO_CLIENT_SECRET=your_client_secret

# Gemini
GEMINI_API_KEY=your_gemini_key

# Claude
ANTHROPIC_API_KEY=your_anthropic_key

# 连接池优化（高并发）
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=30
```

---

## 📚 API 文档

### API 概览

本项目提供 **200+ RESTful API 端点**，覆盖小说创作全流程。

| 模块 | 端点数 | 描述 |
|------|--------|------|
| 认证 (Auth) | 8 | 登录、OAuth、会话管理 |
| 项目 (Projects) | 12 | 项目 CRUD、导入导出 |
| 大纲 (Outlines) | 15 | 大纲生成、编辑、AI 续写 |
| 角色 (Characters) | 18 | 角色管理、关系图谱 |
| 章节 (Chapters) | 25 | 章节生成、编辑、批量操作 |
| 伏笔 (Foreshadows) | 10 | 伏笔追踪、回收提醒 |
| 一致性 (Consistency) | 4 | 角色/剧情一致性检测 |
| 时间线 (Timeline) | 6 | 事件时间轴管理 |
| 风格分析 (Style) | 3 | 写作风格学习与分析 |
| 质量评分 (Quality) | 2 | 章节质量评估 |
| 重复检测 (Duplicate) | 2 | 重复内容检测 |
| 角色成长 (Growth) | 6 | 角色成长轨迹追踪 |
| 其他 | 89+ | 组织、职业、记忆、设置等 |

### 在线文档

启动服务后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 核心 API 示例

<details>
<summary>🔮 伏笔管理 API</summary>

```bash
# 创建伏笔
POST /api/foreshadows
{
  "project_id": "uuid",
  "title": "神秘信件",
  "description": "主角收到一封来自未来的信",
  "foreshadow_type": "plot",
  "planted_chapter": 3
}

# 获取待回收伏笔提醒
GET /api/foreshadows/reminders?project_id={id}&current_chapter=10

# 回收伏笔
POST /api/foreshadows/{id}/resolve
{
  "resolved_chapter": 15,
  "resolution_description": "信件的真相揭晓"
}
```

</details>

<details>
<summary>🔍 一致性检测 API</summary>

```bash
# 检测章节一致性
POST /api/consistency/chapter/{chapter_id}/check

# 响应示例
{
  "overall_score": 85,
  "character_consistency": {
    "score": 90,
    "issues": []
  },
  "plot_consistency": {
    "score": 80,
    "issues": ["时间线存在轻微矛盾"]
  },
  "suggestions": ["建议检查第5章的时间描述"]
}
```

</details>

<details>
<summary>⏱️ 时间线管理 API</summary>

```bash
# 创建时间线事件
POST /api/timeline
{
  "project_id": "uuid",
  "title": "主角觉醒",
  "event_type": "major_plot",
  "story_day": 1,
  "chapter_number": 5,
  "related_characters": ["角色A", "角色B"]
}

# 获取时间线
GET /api/timeline?project_id={id}&event_type=major_plot
```

</details>

<details>
<summary>🎨 风格分析 API</summary>

```bash
# 分析项目写作风格
POST /api/style-analysis/project/{project_id}/analyze

# 响应示例
{
  "narrative_style": "热情洋溢",
  "description_style": "细腻生动",
  "pacing": "张弛有度",
  "language_style": "现代白话",
  "emotional_tone": "积极向上",
  "style_summary": "该作品风格明快..."
}
```

</details>

<details>
<summary>📊 质量评分 API</summary>

```bash
# 获取基础质量指标
GET /api/quality/chapter/{chapter_id}/basic

# AI 综合评估
POST /api/quality/chapter/{chapter_id}/evaluate

# 响应示例
{
  "basic_total": 75,
  "ai_evaluation": {
    "writing_quality": 80,
    "pacing": 70,
    "plot_development": 75,
    "dialogue": 80
  },
  "grade": "B",
  "suggestions": ["可以增加更多环境描写"]
}
```

</details>

<details>
<summary>🔄 重复检测 API</summary>

```bash
# 检测章节内重复
GET /api/duplicate/chapter/{chapter_id}/check?threshold=0.7

# 检测项目级重复
GET /api/duplicate/project/{project_id}/check?threshold=0.7&max_chapters=20
```

</details>

<details>
<summary>📈 角色成长 API</summary>

```bash
# 创建成长记录
POST /api/character-growth
{
  "project_id": "uuid",
  "character_id": "uuid",
  "growth_type": "ability",
  "chapter_number": 10,
  "before_state": "普通人",
  "after_state": "觉醒者",
  "description": "主角在危机中觉醒了隐藏能力"
}

# 获取角色成长时间线
GET /api/character-growth/character/{character_id}?growth_type=ability
```

</details>

---

## 🏗️ 技术架构

### RTCO 上下文框架

章节生成采用 **RTCO (Real-Time Context Optimization)** 框架，动态调整上下文复杂度：

```
章节序号    上下文策略
─────────────────────────────────
第 1 章     仅大纲 + 角色
第 2-10 章  上章结尾 300 字 + 涉及角色
第 11-50 章 上章结尾 500 字 + 相关记忆 3 条
第 51+ 章   上章结尾 500 字 + 故事骨架 + 智能记忆 5 条
```

### 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | FastAPI • SQLAlchemy • Pydantic • Alembic |
| **数据库** | PostgreSQL 18 • 连接池优化 |
| **前端** | React 18 • TypeScript • Ant Design • Zustand |
| **AI** | OpenAI SDK • Gemini SDK • Anthropic SDK |
| **部署** | Docker • Docker Compose |

### 项目结构

```
MuMuAINovel/
├── backend/
│   ├── app/
│   │   ├── api/              # 26 个 API 模块
│   │   │   ├── auth.py           # 认证
│   │   │   ├── projects.py       # 项目管理
│   │   │   ├── chapters.py       # 章节管理
│   │   │   ├── characters.py     # 角色管理
│   │   │   ├── foreshadows.py    # 伏笔管理
│   │   │   ├── consistency.py    # 一致性检测
│   │   │   ├── timeline.py       # 时间线管理
│   │   │   ├── style_analysis.py # 风格分析
│   │   │   ├── quality.py        # 质量评分
│   │   │   ├── duplicate.py      # 重复检测
│   │   │   ├── character_growth.py # 角色成长
│   │   │   └── ...
│   │   ├── models/           # 21 个数据模型
│   │   ├── services/         # 31 个业务服务
│   │   │   ├── chapter_context_service.py  # RTCO 上下文
│   │   │   ├── consistency_checker.py      # 一致性检测
│   │   │   ├── duplicate_detector.py       # 重复检测
│   │   │   ├── quality_scorer.py           # 质量评分
│   │   │   ├── style_analyzer.py           # 风格分析
│   │   │   └── ...
│   │   ├── schemas/          # Pydantic 模式
│   │   └── main.py           # 应用入口
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/            # 25 个页面组件
│   │   ├── components/       # 通用组件
│   │   └── services/         # API 服务
│   └── package.json
├── docker-compose.yml
└── Dockerfile
```

---

## 📋 版本历史

### v1.10.0 (2026-01-04) - 当前版本

**Phase 3 完成 - 高级写作辅助功能**

| 版本 | 功能 | 描述 |
|------|------|------|
| v1.10.0 | 风格指南集成 | AI 生成时自动注入学习到的写作风格 |
| v1.9.0 | 角色成长轨迹 | 追踪角色能力、关系、心理、状态变化 |
| v1.8.0 | 重复内容检测 | 检测章节内部和章节间的重复内容 |
| v1.7.0 | 章节质量评分 | 基础指标 + AI 综合评估，S/A/B/C/D 分级 |
| v1.6.0 | 风格分析系统 | 学习项目写作风格，生成风格指南 |
| v1.5.0 | 时间线管理 | 故事事件时间轴追踪 |
| v1.4.0 | 一致性检测 | AI 分析角色行为和剧情连贯性 |
| v1.3.x | 伏笔管理 | 智能追踪伏笔，AI 生成时自动注入 |

### v1.2.x - 基础功能完善

- 职业等级体系
- 角色/组织卡片导入导出
- 章节阅读器
- 上下文构建系统重构 (RTCO)

### v1.1.x - 用户体验优化

- 中国风主题 UI
- AI 流式生成优化
- 灵感模式增强
- Gemini 适配器

### v1.0.x - 初始版本

- 核心小说创作功能
- 多 AI 模型支持
- PostgreSQL 数据库
- Docker 部署

<details>
<summary>📜 完整版本标签</summary>

```
v1.10.0  v1.9.0   v1.8.0   v1.7.0   v1.6.0
v1.5.0   v1.4.0   v1.3.1   v1.3.0   v1.2.4
v1.2.3   v1.2.2   v1.2.1   v1.2.0   v1.1.4
v1.1.3   v1.1.2   v1.1.1   v1.1.0   v1.0.11
v1.0.10  v1.0.9   v1.0.8   v1.0.7   v1.0.6
v1.0.5   v1.0.4   v1.0.3   v1.0.2
```

</details>

---

## 📋 TODO List

### ✅ 已完成功能

- [x] 灵感模式 - 创作灵感和点子生成
- [x] 自定义写作风格 - 支持自定义 AI 写作风格
- [x] 数据导入导出 - 项目数据的导入导出
- [x] Prompt 调整界面 - 可视化编辑 Prompt 模板
- [x] 章节字数限制 - 用户可设置生成字数
- [x] 思维链与章节关系图谱 - 可视化章节逻辑关系
- [x] 根据分析一键重写 - 根据分析建议重新生成
- [x] 职业等级体系 - 自定义职业和等级系统
- [x] 角色/组织卡片导入导出 - 跨项目数据共享
- [x] **伏笔管理** - 智能追踪剧情伏笔 ✨
- [x] **一致性检测** - AI 分析角色行为一致性 ✨
- [x] **时间线管理** - 故事事件时间轴追踪 ✨
- [x] **风格分析** - 学习写作风格，生成风格指南 ✨
- [x] **章节质量评分** - 基础指标 + AI 综合评估 ✨
- [x] **重复内容检测** - 检测重复/相似内容 ✨
- [x] **角色成长轨迹** - 追踪角色变化 ✨

### 📝 规划中功能

- [ ] **提示词工坊** - 社区驱动的 Prompt 模板分享平台
- [ ] **多语言支持** - 界面国际化
- [ ] **协作模式** - 多人协作创作

> 💡 欢迎提交 Issue 或 Pull Request！

---

## 🐳 Docker 部署详情

### 服务架构

```yaml
services:
  postgres:      # PostgreSQL 18 数据库
    - 端口: 5432
    - 优化: 支持 200 并发连接
    - 数据持久化: postgres_data volume

  mumuainovel:   # 主应用服务
    - 端口: 8000
    - 健康检查: 每 30 秒
    - 自动等待数据库就绪
```

### 常用命令

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f mumuainovel

# 重启
docker-compose restart

# 停止
docker-compose down

# 更新
docker-compose pull && docker-compose up -d
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 📝 许可证

本项目采用 [GNU General Public License v3.0](LICENSE)

- ✅ 可自由使用、修改和分发
- ✅ 可用于商业目的
- 📝 必须开源修改版本
- 📝 必须保留原作者版权

---

## 📧 联系方式

- 提交 [Issue](https://github.com/neosun100/MuMuAINovel/issues)
- Linux DO [讨论](https://linux.do/t/topic/1106333)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个 Star！**

Made with ❤️ by Neo

</div>

## Star History

<a href="https://www.star-history.com/#neosun100/MuMuAINovel&type=Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=neosun100/MuMuAINovel&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=neosun100/MuMuAINovel&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=neosun100/MuMuAINovel&type=Date" />
 </picture>
</a>
