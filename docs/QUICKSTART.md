# MuMuAINovel 快速启动指南

> **这是入口文档**，AI助手（Kiro/Claude）请先阅读此文档了解项目全貌。

---

## 🚀 新对话启动

每次新对话开始时，请告诉AI助手：

```
请阅读 /home/neo/upload/MuMuAINovel/docs/QUICKSTART.md 了解项目背景和操作流程。
```

---

## 📚 项目概述

**MuMuAINovel** 是一个AI驱动的小说创作系统，核心能力：

| 能力 | 说明 |
|------|------|
| 🤖 多AI支持 | OpenAI / Gemini / Claude |
| 📖 批量生成 | 100章 × 10000字 = 100万字 |
| 🎭 角色管理 | 支持80-150个角色 |
| ✨ 二次优化 | Claude Opus/Sonnet 三段式精修 |
| 🔍 质量检测 | 一致性、重复、质量评分（支持流式） |
| 🔌 MCP集成 | 33个工具，AI助手可直接调用 |

**系统地址**: http://localhost:8000  
**API文档**: http://localhost:8000/docs (Swagger) | http://localhost:8000/redoc (ReDoc)

---

## 📂 文档导航

| 文档 | 说明 | 何时阅读 |
|------|------|----------|
| **QUICKSTART.md** | 本文档，入口指南 | 🔴 必读 |
| **COMPLETE_USAGE_GUIDE.md** | 完整使用指南（含二次优化） | 🔴 必读 |
| **KIRO_INTERACTION_GUIDE.md** | 完整API交互指南 | 需要了解API细节时 |
| **API_MCP_COVERAGE.md** | API和MCP覆盖清单 | 需要查看功能覆盖时 |
| **MCP_USAGE_GUIDE.md** | MCP Server使用指南 | 配置MCP时 |
| **plans/PLAN_00_REFINEMENT.md** | 二次优化系统详细设计 | 深入了解优化机制时 |

---

## 🎯 完整工作流程（5个阶段）

```
Phase 1: 准备 ──▶ Phase 2: 生成 ──▶ Phase 3: 优化 ──▶ Phase 4: 验证 ──▶ Phase 5: 导出
   │                  │                  │                  │                  │
创建项目           批量生成           二次优化           质量检测           导出TXT
设置世界观         100章内容          三段精修           一致性检测         导出Markdown
创建角色           RTCO上下文         Opus/Sonnet        重复检测           优化报告
创建大纲           自动重试           版本对比           质量评分
```

**📖 详细操作请阅读**: [COMPLETE_USAGE_GUIDE.md](COMPLETE_USAGE_GUIDE.md)

---

## 🎯 交互模式

### 模式1: 创建新小说

**用户说:**
```
帮我创作一部小说：
- 标题：《xxx》
- 类型：都市科幻/玄幻/历史穿越/...
- 主角：名字、职业、性格
- 背景：时代、地点、核心冲突
- 方向：开篇→发展→高潮→结局
```

**AI执行流程:**
1. 搜索背景资料 (web_search)
2. 设计角色 (80-150个)
3. 设计大纲 (100章)
4. 调用 `novel_full_pipeline` 或分步API
5. 报告Project ID和进度

### 模式2: 检查进度

```bash
python auto_resume.py  # 显示所有项目状态
```

### 模式3: 恢复任务

```bash
python auto_resume.py --daemon  # 后台恢复所有中断任务
```

---

## ⚡ 快速命令

### 环境准备
```bash
export MUMUAI_BASE_URL=http://localhost:8000
export MUMUAI_USERNAME=admin
export MUMUAI_PASSWORD=your_password

# 登录
curl -c /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/auth/local/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$MUMUAI_USERNAME\", \"password\": \"$MUMUAI_PASSWORD\"}"
```

### 核心操作
```bash
# 查看项目
curl -s -b /tmp/cookies.txt "$MUMUAI_BASE_URL/api/projects" | jq '.items[] | {id, title}'

# 批量生成
curl -b /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/chapters/project/{PROJECT_ID}/batch-generate" \
  -H "Content-Type: application/json" \
  -d '{"start_chapter_number": 1, "count": 100, "target_word_count": 10000}'

# 二次优化
curl -b /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/refinement/project/{PROJECT_ID}/all" \
  -H "Content-Type: application/json" \
  -d '{"model": "opus"}'

# 质量检测（流式）
curl -b /tmp/cookies.txt "$MUMUAI_BASE_URL/api/duplicate/project/{PROJECT_ID}/check-stream?max_chapters=50"

# 导出小说
curl -b /tmp/cookies.txt "$MUMUAI_BASE_URL/api/refinement/project/{PROJECT_ID}/export?format=txt" -o novel.txt
```

---

## 🔌 MCP 工具速查

### 一键操作
```
novel_full_pipeline      - 一键创建完整小说
novel_resume_all         - 恢复所有中断任务
```

### 项目管理
```
novel_list_projects      - 列出项目
novel_create_project     - 创建项目
novel_check_progress     - 检查进度
novel_export_project     - 导出项目
```

### 质量检测
```
novel_check_quality      - 质量评分
novel_check_consistency  - 一致性检测
novel_check_duplicate    - 重复检测
```

---

## ❓ 常见问题

| 问题 | 解决方案 |
|------|----------|
| 批量生成中断 | `python auto_resume.py --daemon` |
| 查看生成日志 | `docker logs mumuainovel --tail 100` |
| 取消任务 | `POST /api/chapters/batch-generate/{batch_id}/cancel` |
| Container重启后 | 任务不会自动继续，需运行 `auto_resume.py` |

---

## 📁 项目结构

```
MuMuAINovel/
├── docs/
│   ├── QUICKSTART.md              # 入口文档（本文档）
│   ├── COMPLETE_USAGE_GUIDE.md    # 完整使用指南 ⭐
│   ├── KIRO_INTERACTION_GUIDE.md  # API交互指南
│   └── plans/PLAN_00_REFINEMENT.md # 二次优化设计
├── mcp_novel_server.py            # MCP Server (33个工具)
├── auto_resume.py                 # 自动恢复脚本
├── backend/                       # 后端代码
├── frontend/                      # 前端代码
└── docker-compose.yml             # Docker配置
```

---

## 🎓 AI助手学习路径

1. **阅读本文档** - 了解项目全貌
2. **阅读 COMPLETE_USAGE_GUIDE.md** - 掌握完整流程
3. **查看 API_MCP_COVERAGE.md** - 了解可用工具
4. **实践** - 尝试创建小说或检查进度

---

*最后更新: 2026-01-07 | 版本: v1.11.0*
