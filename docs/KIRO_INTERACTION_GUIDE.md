# Kiro 小说创作交互指南 (完整版)

## 🎯 推荐交互流程

### 新对话启动

**用户说：**
```
请阅读 /home/neo/upload/MuMuAINovel/docs/QUICKSTART.md 了解项目背景和操作流程。
```

**Kiro执行：**
1. 阅读文档，了解系统架构和API
2. 确认已准备就绪
3. 等待用户指令

---

### 场景1: 创建新小说

**用户输入模板：**
```
帮我创作一部小说：
- 标题：《xxx》
- 类型：都市科幻/玄幻/历史穿越/...
- 主角：名字、职业、性格
- 背景：时代、地点、核心冲突
- 方向：开篇→发展→高潮→结局
- 特殊要求：真实人物、神秘元素等
```

**Kiro执行流程：**
```
Step 1: 搜索背景资料 (web_search)
Step 2: 创建项目 (POST /api/projects)
Step 3: 设置世界观 (PUT /api/projects/{id})
Step 4: 设计并创建角色 (POST /api/characters × 80-150)
Step 5: 设计并创建大纲 (POST /api/outlines × 100)
Step 6: 创建章节 (POST /api/chapters × 100)
Step 7: 提交批量生成 (POST /api/chapters/project/{id}/batch-generate)
Step 8: 报告状态 (返回Project ID, Batch ID)
```

---

### 场景2: 检查项目进度

**用户说：**
```
检查盗火者的悲歌的进度
```

**Kiro执行：**
```bash
curl -s -b /tmp/cookies.txt "http://localhost:8000/api/chapters/project/{PROJECT_ID}?limit=200" | \
  jq '{total: .total, generated: [.items[] | select(.content | length > 100)] | length}'
```

---

### 场景3: 恢复中断任务

**用户说：**
```
恢复所有中断的任务
```

**Kiro执行：**
```bash
python auto_resume.py --daemon
```

---

## 📚 API 完整手册

### 1. 认证 API

#### POST /api/auth/local/login
**作用**: 本地账户登录，获取Session Cookie
```json
// Request
{"username": "admin", "password": "xxx"}

// Response 200
{"user_id": "xxx", "username": "admin"}
```
**本质**: 建立会话，后续所有API调用需携带Cookie

---

### 2. 项目 API

#### POST /api/projects
**作用**: 创建新小说项目
```json
// Request
{
  "title": "小说标题",
  "genre": "类型",
  "description": "简介",
  "target_words": 1000000,
  "chapter_count": 100
}

// Response 200
{"id": "PROJECT_ID", "title": "...", ...}
```
**本质**: 创建项目容器，所有角色/大纲/章节都关联到此ID

#### PUT /api/projects/{id}
**作用**: 更新项目信息，设置世界观
```json
// Request
{
  "world_time_period": "时代背景",
  "world_location": "地理设定",
  "world_atmosphere": "社会氛围",
  "world_rules": "核心规则"
}
```
**本质**: 世界观是AI生成章节时的全局上下文

#### GET /api/projects
**作用**: 获取所有项目列表
```json
// Response
{"items": [...], "total": N}
```

---

### 3. 角色 API

#### POST /api/characters
**作用**: 创建单个角色
```json
// Request
{
  "project_id": "PROJECT_ID",
  "name": "英文名 (中文名)",
  "role_type": "protagonist|supporting|antagonist",
  "gender": "男|女",
  "age": "38",
  "personality": "性格描述",
  "background": "背景故事",
  "abilities": "能力（可选）",
  "goals": "目标（可选）",
  "relationships": "关系（可选）"
}

// Response 200
{"id": "CHARACTER_ID", ...}
```
**本质**: 角色是AI生成时的人物参考，影响对话和行为描写

**角色分类建议**:
| 类型 | 数量 | 说明 |
|------|------|------|
| 主角家庭 | 5-10 | 核心情感线 |
| 工作同事 | 10-20 | 职场互动 |
| 客户/合作伙伴 | 10-15 | 业务线 |
| 反派/对手 | 5-15 | 冲突来源 |
| 真实人物 | 10-20 | 增加真实感 |
| 神秘角色 | 5-10 | 悬念元素 |
| 配角 | 20-50 | 丰富世界 |
| **总计** | **80-150** | |

#### GET /api/characters/project/{id}
**作用**: 获取项目所有角色
```json
// Response
{"items": [...], "total": N}
```

---

### 4. 大纲 API

#### POST /api/outlines
**作用**: 创建单章大纲
```json
// Request
{
  "project_id": "PROJECT_ID",
  "title": "第N章 章节标题",
  "content": "章节概要（100-300字）",
  "order_index": N
}

// Response 200
{"id": "OUTLINE_ID", ...}
```
**本质**: 大纲是AI生成章节的蓝图，决定情节走向

**大纲结构建议 (100章)**:
| 卷 | 章节 | 主题 |
|----|------|------|
| 第一卷 | 1-10 | 开篇/铺垫 |
| 第二卷 | 11-25 | 发展/冲突 |
| 第三卷 | 26-50 | 深入/转折 |
| 第四卷 | 51-75 | 高潮/对决 |
| 第五卷 | 76-100 | 结局/新篇 |

#### GET /api/outlines/project/{id}
**作用**: 获取项目所有大纲
```json
// Response
{"items": [...], "total": N}
```

---

### 5. 章节 API

#### POST /api/chapters
**作用**: 创建单个章节（空壳，待生成）
```json
// Request
{
  "project_id": "PROJECT_ID",
  "title": "第N章 章节标题",
  "summary": "章节摘要",
  "chapter_number": N,
  "outline_id": "OUTLINE_ID",
  "status": "pending"
}

// Response 200
{"id": "CHAPTER_ID", ...}
```
**本质**: 章节是内容容器，创建时为空，batch-generate填充内容

#### GET /api/chapters/project/{id}
**作用**: 获取项目所有章节
```json
// Request
GET /api/chapters/project/{id}?limit=200

// Response
{
  "items": [
    {"id": "...", "chapter_number": 1, "content": "...", "word_count": 10000, ...}
  ],
  "total": 100
}
```
**本质**: 用于监控生成进度，content有内容表示已生成

#### POST /api/chapters/project/{id}/batch-generate
**作用**: 提交批量生成任务
```json
// Request
{
  "start_chapter_number": 1,
  "count": 100,
  "target_word_count": 10000,
  "max_retries": 10
}

// Response 200
{
  "batch_id": "BATCH_ID",
  "chapters_to_generate": ["id1", "id2", ...]
}
```
**本质**: 核心生成API，后台异步执行，使用RTCO框架和三段论策略

**参数说明**:
| 参数 | 默认值 | 范围 | 说明 |
|------|--------|------|------|
| start_chapter_number | 1 | 1-N | 起始章节 |
| count | 10 | 1-100 | 生成数量 |
| target_word_count | 10000 | 1000-20000 | 每章字数 |
| max_retries | 10 | 0-20 | 最大重试次数 |

#### GET /api/chapters/project/{id}/batch-generate/active
**作用**: 检查是否有活动的生成任务
```json
// Response
{"has_active_task": true/false, "task": {...}}
```

---

## 🔧 系统机制

### RTCO 上下文框架
```
章节序号    上下文策略
─────────────────────────────────
第 1 章     仅大纲 + 角色
第 2-10 章  上章结尾 300 字 + 涉及角色
第 11-50 章 上章结尾 500 字 + 相关记忆 3 条
第 51+ 章   上章结尾 500 字 + 故事骨架 + 智能记忆 5 条
```

### 三段论生成策略
每章分三段生成：40% + 40% + 20%，确保结构完整

### 分阶段重试退避
| 重试次数 | 等待时间 | 说明 |
|----------|----------|------|
| 1-3 次 | 2, 4, 8 秒 | 快速重试 |
| 4-6 次 | 30 秒 | 中等等待 |
| 7-10 次 | 60 秒 | 长等待 |

---

## 📋 Kiro 执行清单

创建新小说时，按顺序执行：

- [ ] **Step 1**: 搜索背景资料 (web_search)
- [ ] **Step 2**: 登录系统 (POST /api/auth/local/login)
- [ ] **Step 3**: 创建项目 (POST /api/projects) → 获取 PROJECT_ID
- [ ] **Step 4**: 设置世界观 (PUT /api/projects/{id})
- [ ] **Step 5**: 设计角色 (80-150个)
- [ ] **Step 6**: 批量创建角色 (POST /api/characters × N)
- [ ] **Step 7**: 设计大纲 (100章)
- [ ] **Step 8**: 批量创建大纲 (POST /api/outlines × 100)
- [ ] **Step 9**: 批量创建章节 (POST /api/chapters × 100)
- [ ] **Step 10**: 提交批量生成 (POST /api/chapters/project/{id}/batch-generate)
- [ ] **Step 11**: 报告状态 (Project ID, Batch ID, 预计时间)

---

## 🔄 任务恢复

### 自动恢复脚本
```bash
# 一次性恢复
python auto_resume.py

# 后台持续监控
python auto_resume.py --daemon

# 后台运行并记录日志
nohup python auto_resume.py --daemon > resume.log 2>&1 &
```

### 手动恢复
```bash
# 1. 检查进度
curl -s -b /tmp/cookies.txt "http://localhost:8000/api/chapters/project/{PROJECT_ID}?limit=200" | \
  jq '{generated: [.items[] | select(.content | length > 100)] | length, total: .total}'

# 2. 从断点继续
curl -s -b /tmp/cookies.txt -X POST "http://localhost:8000/api/chapters/project/{PROJECT_ID}/batch-generate" \
  -H "Content-Type: application/json" \
  -d '{"start_chapter_number": 46, "count": 55, "target_word_count": 10000}'
```

---

## 📁 文件结构

```
/home/neo/upload/MuMuAINovel/
├── docs/
│   ├── QUICKSTART.md              ← 入口文档（必读）
│   ├── KIRO_INTERACTION_GUIDE.md  ← 本文档（完整交互指南）
│   ├── NOVEL_CREATION_PIPELINE.md ← API流程详解
│   └── KIRO_NOVEL_AGENT.md        ← Agent工作流
├── auto_resume.py                 ← 自动恢复脚本
├── novel_pipeline.py              ← Python自动化脚本
└── backend/app/
    ├── api/chapters.py            ← 章节API（含batch-generate）
    ├── schemas/chapter.py         ← 参数Schema
    └── main.py                    ← 启动入口（含恢复逻辑）
```

---

*最后更新: 2026-01-05*
