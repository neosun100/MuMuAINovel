# MuMuAI小说系统 - 快速启动指南

## 🚀 新对话启动命令

每次新对话开始时，请告诉Kiro：

```
请阅读 /home/neo/upload/MuMuAINovel/docs/QUICKSTART.md 了解项目背景和操作流程。
```

---

## 📚 项目概述

**MuMuAINovel** 是一个AI驱动的小说创作系统，支持：
- 自动生成世界观、角色、大纲
- 批量生成100章×10000字的长篇小说
- RTCO上下文框架确保章节连贯
- 三段论生成策略（40%+40%+20%）

**系统地址**: http://localhost:8000
**登录账号**: 在 .env 中配置 LOCAL_AUTH_USERNAME / LOCAL_AUTH_PASSWORD

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

## 📂 关键文档

| 文档 | 说明 |
|------|------|
| `/docs/QUICKSTART.md` | 本文档，快速启动指南 |
| `/docs/KIRO_INTERACTION_GUIDE.md` | **完整交互指南（API详解）** |
| `/docs/NOVEL_CREATION_PIPELINE.md` | 详细API流程 |
| `/docs/KIRO_NOVEL_AGENT.md` | Kiro Agent工作流 |
| `/novel_pipeline.py` | 自动化Pipeline脚本 |
| `/auto_resume.py` | 自动恢复脚本 |

---

## 🎯 用户交互模板

### 创建新小说

```
帮我创作一部小说：
- 标题：《xxx》
- 类型：都市科幻/玄幻/历史穿越/...
- 主角：名字、职业、性格
- 背景：时代、地点、核心冲突
- 方向：开篇→发展→高潮→结局
- 特殊要求：真实人物、神秘元素等
```

### 检查项目进度

```
检查项目 PROJECT_ID 的生成进度
```

### 继续中断的任务

```
继续生成项目 PROJECT_ID 的剩余章节
```

---

## 📊 当前项目状态

### 盗火者的悲歌
- **Project ID**: `43a8d273-437a-4167-a67d-df53fadd5997`
- **类型**: 都市科幻
- **主角**: Leo Sun (AWS架构师，香港，Web3行业)
- **角色**: 135个
- **大纲**: 100章
- **状态**: 🟢 生成中

### 崇祯大帝（终极版）
- **Project ID**: `7cf21fed-567b-4f48-b0ee-f9458c02a8d7`
- **类型**: 历史穿越
- **状态**: 🟢 生成中 (45/100章)

### 龙霸星河
- **Project ID**: `61ee2c8d-b445-4406-bfaa-8527cdc6a97b`
- **类型**: 星际科幻
- **状态**: 🟢 生成中 (20/100章)

---

## ⚡ 快速命令

```bash
# 检查所有项目进度
curl -s -b /tmp/cookies.txt "http://localhost:8000/api/projects" | jq '.items[] | {title, id}'

# 检查特定项目章节进度
curl -s -b /tmp/cookies.txt "http://localhost:8000/api/chapters/project/{PROJECT_ID}?limit=200" | \
  jq '{total: .total, generated: [.items[] | select(.content | length > 100)] | length}'

# 提交批量生成
curl -s -b /tmp/cookies.txt -X POST "http://localhost:8000/api/chapters/project/{PROJECT_ID}/batch-generate" \
  -H "Content-Type: application/json" \
  -d '{"start_chapter_number": 1, "count": 100, "target_word_count": 10000}'
```

---

## 🔧 系统配置

### Schema修改记录
- `/backend/app/schemas/chapter.py` 第88行: `count` 上限从20改为100
- `/backend/app/schemas/chapter.py` 第91行: `target_word_count` 默认改为10000，上限改为20000

### 重启服务
```bash
cd /home/neo/upload/MuMuAINovel
docker-compose restart mumuainovel
```

---

## 📝 Kiro执行清单

当用户要求创建新小说时，Kiro应：

1. **搜索背景资料** - 使用web_search获取相关信息
2. **创建项目** - POST /api/projects
3. **设置世界观** - PUT /api/projects/{id}
4. **设计并创建角色** - POST /api/characters (80-150个)
5. **设计并创建大纲** - POST /api/outlines (100章)
6. **创建章节** - POST /api/chapters (100个)
7. **提交批量生成** - POST /api/chapters/project/{id}/batch-generate
8. **报告状态** - 返回Project ID和Batch ID

---

## 🔄 任务恢复机制

### 自动恢复（推荐）

Container重启后，运行自动恢复脚本：

```bash
# 一次性恢复所有中断任务
python auto_resume.py

# 后台持续监控模式（直到全部完成）
python auto_resume.py --daemon
```

### 手动恢复

```bash
# 1. 检查项目进度
curl -s -b /tmp/cookies.txt "http://localhost:8000/api/chapters/project/{PROJECT_ID}?limit=200" | \
  jq '{generated: [.items[] | select(.content | length > 100)] | length, total: .total}'

# 2. 从断点继续（假设已生成45章，共100章）
curl -s -b /tmp/cookies.txt -X POST "http://localhost:8000/api/chapters/project/{PROJECT_ID}/batch-generate" \
  -H "Content-Type: application/json" \
  -d '{"start_chapter_number": 46, "count": 55, "target_word_count": 10000}'
```

### 系统启动时自动检测

系统启动时会自动：
1. 检测所有 `running` 状态的任务
2. 标记为 `interrupted`
3. 记录已完成章节数
4. 日志输出恢复建议

---

## ❓ 常见问题

**Q: Container重启后任务会继续吗？**
A: 不会自动继续，但数据不会丢失。运行 `python auto_resume.py` 恢复。

**Q: 大纲生成API被阻塞怎么办？**
A: 直接用 `POST /api/outlines` 手动创建，绕过SSE流式接口。

**Q: 批量生成中断怎么办？**
A: 运行 `python auto_resume.py` 自动恢复，或手动查询进度后重新提交。

**Q: 如何查看生成日志？**
A: `docker logs mumuainovel --tail 100`

**Q: 如何后台持续监控直到完成？**
A: `nohup python auto_resume.py --daemon > resume.log 2>&1 &`

---

*最后更新: 2026-01-05*
