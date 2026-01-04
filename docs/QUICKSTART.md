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
| 🔮 高级功能 | 伏笔、一致性、质量评分、风格分析 |
| 🔌 MCP集成 | 33个工具，AI助手可直接调用 |

**系统地址**: http://localhost:8000  
**API文档**: http://localhost:8000/docs (Swagger) | http://localhost:8000/redoc (ReDoc)

---

## 📂 文档导航

| 文档 | 说明 | 何时阅读 |
|------|------|----------|
| **QUICKSTART.md** | 本文档，入口指南 | 🔴 必读 |
| **KIRO_INTERACTION_GUIDE.md** | 完整API交互指南 | 需要了解API细节时 |
| **API_MCP_COVERAGE.md** | API和MCP覆盖清单 | 需要查看功能覆盖时 |
| **MCP_USAGE_GUIDE.md** | MCP Server使用指南 | 配置MCP时 |
| **NOVEL_CREATION_PIPELINE.md** | 创作流水线详解 | 需要了解完整流程时 |
| **ROADMAP.md** | 未来发展路线图 | 了解项目规划时 |
| **TODO.md** | 详细开发任务清单 | 参与开发时 |

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
- 特殊要求：真实人物、神秘元素等
```

**AI执行流程:**
1. 搜索背景资料 (web_search)
2. 设计角色 (80-150个)
3. 设计大纲 (100章)
4. 调用 `novel_full_pipeline` 或分步API
5. 报告Project ID和进度

### 模式2: 检查进度

**用户说:**
```
检查盗火者的悲歌的进度
```

**AI执行:**
```
调用 novel_check_progress 或 curl API
```

### 模式3: 恢复任务

**用户说:**
```
恢复所有中断的任务
```

**AI执行:**
```bash
python auto_resume.py --daemon
# 或调用 novel_resume_all
```

---

## 📋 核心API流程

```
1. POST /api/auth/local/login           # 登录
2. POST /api/projects                    # 创建项目
3. PUT  /api/projects/{id}               # 设置世界观
4. POST /api/characters (循环)           # 创建角色 (80-150个)
5. POST /api/outlines (循环)             # 创建大纲 (100章)
6. POST /api/chapters (循环)             # 创建章节 (100个)
7. POST /api/chapters/project/{id}/batch-generate  # 批量生成
8. GET  /api/chapters/project/{id}       # 监控进度
```

---

## 🔌 MCP 工具速查

### 一键创建
```
novel_full_pipeline - 一键创建完整小说
```

### 项目管理
```
novel_list_projects    - 列出项目
novel_create_project   - 创建项目
novel_delete_project   - 删除项目
novel_export_project   - 导出项目
```

### 内容管理
```
novel_create_characters_batch  - 批量创建角色
novel_create_outlines_batch    - 批量创建大纲
novel_create_chapters_from_outlines - 从大纲创建章节
```

### 生成控制
```
novel_batch_generate     - 提交批量生成
novel_check_progress     - 检查进度
novel_cancel_generation  - 取消任务
novel_resume_all         - 恢复所有任务
```

### 质量检测
```
novel_check_quality      - 质量评分
novel_check_consistency  - 一致性检测
novel_check_duplicate    - 重复检测
```

---

## ⚡ 快速命令

### 环境变量
```bash
export MUMUAI_BASE_URL=http://localhost:8000
export MUMUAI_USERNAME=admin
export MUMUAI_PASSWORD=your_password
```

### 登录获取Cookie
```bash
curl -c /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/auth/local/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

### 查看所有项目
```bash
curl -s -b /tmp/cookies.txt "$MUMUAI_BASE_URL/api/projects" | jq '.items[] | {id, title}'
```

### 检查项目进度
```bash
curl -s -b /tmp/cookies.txt "$MUMUAI_BASE_URL/api/chapters/project/{PROJECT_ID}?limit=200" | \
  jq '{total: .total, generated: [.items[] | select(.content | length > 100)] | length}'
```

### 提交批量生成
```bash
curl -s -b /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/chapters/project/{PROJECT_ID}/batch-generate" \
  -H "Content-Type: application/json" \
  -d '{"start_chapter_number": 1, "count": 100, "target_word_count": 10000}'
```

### 恢复中断任务
```bash
python auto_resume.py --daemon
```

---

## 🔄 任务恢复机制

### Container重启后
```bash
# 自动恢复所有中断任务
python auto_resume.py

# 后台持续监控直到完成
python auto_resume.py --daemon

# 后台运行并记录日志
nohup python auto_resume.py --daemon > resume.log 2>&1 &
```

### 重试策略
| 重试次数 | 等待时间 | 说明 |
|----------|----------|------|
| 1-3 | 2, 4, 8秒 | 快速重试 |
| 4-6 | 30秒 | 中等等待 |
| 7-10 | 60秒 | 长等待 |

---

## 📊 当前项目状态

> 以下为示例，实际状态请通过API查询

| 项目 | 进度 | 状态 |
|------|------|------|
| 盗火者的悲歌 | 11/100章 | 🟢 生成中 |
| 龙霸星河 | 43/100章 | 🟢 生成中 |
| 崇祯大帝 | 70/100章 | 🟢 生成中 |

查询命令:
```bash
python auto_resume.py  # 会显示所有项目状态
```

---

## ❓ 常见问题

**Q: 如何创建新小说？**
A: 告诉AI助手标题、类型、主角、背景、方向，AI会自动完成全部流程。

**Q: Container重启后任务会继续吗？**
A: 不会自动继续，运行 `python auto_resume.py` 恢复。

**Q: 如何查看生成日志？**
A: `docker logs mumuainovel --tail 100`

**Q: 批量生成中断怎么办？**
A: 运行 `python auto_resume.py --daemon` 自动恢复。

**Q: 如何取消正在进行的任务？**
A: 调用 `novel_cancel_generation` 或 API `/api/chapters/batch-generate/{batch_id}/cancel`

**Q: 如何检测章节质量？**
A: 调用 `novel_check_quality`、`novel_check_consistency`、`novel_check_duplicate`

---

## 🔧 系统配置

### 关键参数
| 参数 | 默认值 | 范围 | 说明 |
|------|--------|------|------|
| count | 10 | 1-100 | 批量生成章节数 |
| target_word_count | 10000 | 1000-20000 | 每章字数 |
| max_retries | 10 | 0-20 | 最大重试次数 |

### 配置文件
- `.env` - 环境变量配置
- `.env.example` - 配置模板

---

## 📁 项目结构

```
MuMuAINovel/
├── docs/                          # 文档目录
│   ├── QUICKSTART.md              # 入口文档（本文档）
│   ├── KIRO_INTERACTION_GUIDE.md  # 完整API指南
│   ├── API_MCP_COVERAGE.md        # API/MCP覆盖清单
│   ├── MCP_USAGE_GUIDE.md         # MCP使用指南
│   └── NOVEL_CREATION_PIPELINE.md # 创作流水线
├── mcp_novel_server.py            # MCP Server (33个工具)
├── auto_resume.py                 # 自动恢复脚本
├── novel_pipeline.py              # Python自动化脚本
├── backend/                       # 后端代码
├── frontend/                      # 前端代码
├── docker-compose.yml             # Docker配置
└── README.md                      # 项目说明
```

---

## 🎓 AI助手学习路径

1. **阅读本文档** - 了解项目全貌和交互模式
2. **查看 API_MCP_COVERAGE.md** - 了解可用的工具和API
3. **参考 KIRO_INTERACTION_GUIDE.md** - 需要API细节时查阅
4. **实践** - 尝试创建小说或检查进度

---

*最后更新: 2026-01-05*
