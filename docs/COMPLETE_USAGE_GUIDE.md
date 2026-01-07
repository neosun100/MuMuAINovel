# MuMuAINovel 完整使用指南

> **版本**: v1.11.0 | **更新日期**: 2026-01-07  
> **目标**: 从创意到百万字小说的全自动化流程，包含二次优化和质量验证

---

## 📋 目录

1. [系统概述](#1-系统概述)
2. [快速开始](#2-快速开始)
3. [完整工作流程](#3-完整工作流程)
4. [Phase 1: 项目准备](#4-phase-1-项目准备)
5. [Phase 2: 内容生成](#5-phase-2-内容生成)
6. [Phase 3: 二次优化](#6-phase-3-二次优化)
7. [Phase 4: 质量验证](#7-phase-4-质量验证)
8. [Phase 5: 导出发布](#8-phase-5-导出发布)
9. [自动化脚本](#9-自动化脚本)
10. [故障排除](#10-故障排除)

---

## 1. 系统概述

### 1.1 核心能力

| 能力 | 说明 |
|------|------|
| 🤖 多AI支持 | OpenAI / Gemini / Claude 无缝切换 |
| 📖 批量生成 | 100章 × 10,000字 = 100万字自动生成 |
| 🎭 角色管理 | 支持80-150个角色，关系图谱可视化 |
| 🔮 伏笔系统 | 智能追踪，生成时自动注入 |
| ✨ 二次优化 | Claude Opus/Sonnet 三段式精修 |
| 🔍 质量检测 | 一致性、重复、质量评分全覆盖 |
| 📊 流式API | 长任务实时进度反馈 |

### 1.2 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    MuMuAINovel 工作流程                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1: 准备          Phase 2: 生成         Phase 3: 优化     │
│  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐   │
│  │ 创建项目    │  ──▶  │ 批量生成    │  ──▶  │ 二次优化    │   │
│  │ 设置世界观  │       │ 100章内容   │       │ 三段精修    │   │
│  │ 创建角色    │       │ RTCO上下文  │       │ Opus/Sonnet │   │
│  │ 创建大纲    │       │ 自动重试    │       │ 版本对比    │   │
│  └─────────────┘       └─────────────┘       └─────────────┘   │
│         │                     │                     │           │
│         ▼                     ▼                     ▼           │
│  Phase 4: 验证          Phase 5: 发布                           │
│  ┌─────────────┐       ┌─────────────┐                         │
│  │ 一致性检测  │  ──▶  │ 导出TXT     │                         │
│  │ 重复检测    │       │ 导出Markdown│                         │
│  │ 质量评分    │       │ 优化报告    │                         │
│  └─────────────┘       └─────────────┘                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 访问地址

| 服务 | 地址 |
|------|------|
| Web界面 | http://localhost:8000 |
| Swagger API文档 | http://localhost:8000/docs |
| ReDoc API文档 | http://localhost:8000/redoc |

---

## 2. 快速开始

### 2.1 环境准备

```bash
# 1. 克隆项目
git clone https://github.com/neosun100/MuMuAINovel.git
cd MuMuAINovel

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 API Key 和数据库密码

# 3. 启动服务
docker-compose up -d

# 4. 验证服务
curl http://localhost:8000/health
```

### 2.2 设置Shell环境变量

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export MUMUAI_BASE_URL=http://localhost:8000
export MUMUAI_USERNAME=admin
export MUMUAI_PASSWORD=your_password
```

### 2.3 登录获取Cookie

```bash
# 登录并保存Cookie
curl -c /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/auth/local/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$MUMUAI_USERNAME\", \"password\": \"$MUMUAI_PASSWORD\"}"
```

---

## 3. 完整工作流程

### 3.1 流程总览

```
用户输入 ──▶ 项目准备 ──▶ 批量生成 ──▶ 二次优化 ──▶ 质量验证 ──▶ 导出发布
   │            │            │            │            │            │
   │            │            │            │            │            │
   ▼            ▼            ▼            ▼            ▼            ▼
 创意构思    1-2小时      8-24小时     4-8小时      1-2小时      即时
```

### 3.2 时间估算（100章 × 10000字）

| 阶段 | 预计时间 | 说明 |
|------|----------|------|
| 项目准备 | 1-2小时 | 创建项目、角色、大纲 |
| 批量生成 | 8-24小时 | 取决于AI服务响应速度 |
| 二次优化 | 4-8小时 | 使用Claude Opus精修 |
| 质量验证 | 1-2小时 | 一致性、重复、质量检测 |
| 导出发布 | 即时 | TXT/Markdown导出 |
| **总计** | **14-36小时** | 全自动，无需人工干预 |

---

## 4. Phase 1: 项目准备

### 4.1 创建项目

```bash
# 创建新项目
curl -b /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "龙霸星河",
    "description": "小兵传奇续集，统一宇宙15年后的新冒险",
    "genre": "星际科幻",
    "target_words": 1000000,
    "outline_mode": "one-to-many"
  }'

# 返回: {"id": "PROJECT_ID", ...}
```

### 4.2 设置世界观

```bash
# 更新项目世界观
curl -b /tmp/cookies.txt -X PUT "$MUMUAI_BASE_URL/api/projects/{PROJECT_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "world_time_period": "宇宙历2150年，大唐帝国统一宇宙15年后",
    "world_location": "银河系中心，帝国首都星",
    "world_atmosphere": "表面繁荣，暗流涌动",
    "world_rules": "星际战舰、能量武器、AI生命体"
  }'
```

### 4.3 批量创建角色（80-150个）

```bash
# 创建单个角色
curl -b /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/characters" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "PROJECT_ID",
    "name": "唐龙",
    "role_type": "protagonist",
    "gender": "男",
    "age": "45",
    "personality": "痞气、护短、热血、重情义",
    "background": "从小兵成长为宇宙皇帝，统治宇宙15年",
    "abilities": "战神级战斗力，战略天才",
    "goals": "守护帝国，保护家人"
  }'
```

**角色分类建议**：
| 类型 | 数量 | 说明 |
|------|------|------|
| 主角团 | 5-10 | 主角及核心伙伴 |
| 家族成员 | 10-15 | 家人、亲属 |
| 盟友势力 | 15-20 | 友方阵营重要人物 |
| 反派阵营 | 15-20 | 敌对势力 |
| 中立角色 | 10-15 | 商人、情报贩子等 |
| 配角龙套 | 30-50 | 背景人物 |

### 4.4 批量创建大纲（100章）

```bash
# 创建单个大纲
curl -b /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/outlines" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "PROJECT_ID",
    "title": "第1章 帝国十五年",
    "content": "唐龙视察帝国，展现繁荣景象。皇子唐天成年礼临近，暗示新一代崛起。边境传来异常信号，暗示危机将至。",
    "order_index": 1
  }'
```

**大纲结构建议**（100章）：
| 卷 | 章节 | 内容 |
|------|------|------|
| 第一卷 | 1-10 | 开篇铺垫，世界观展示 |
| 第二卷 | 11-25 | 冲突引入，危机初现 |
| 第三卷 | 26-50 | 深入发展，多线并进 |
| 第四卷 | 51-75 | 高潮迭起，决战序幕 |
| 第五卷 | 76-100 | 终极对决，结局收尾 |

### 4.5 从大纲创建章节

```bash
# 从大纲展开创建章节
curl -b /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/outlines/{OUTLINE_ID}/expand-stream" \
  -H "Content-Type: application/json" \
  -d '{
    "target_chapter_count": 1,
    "auto_create_chapters": true
  }'
```

---

## 5. Phase 2: 内容生成

### 5.1 提交批量生成任务

```bash
# 提交100章批量生成
curl -b /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/chapters/project/{PROJECT_ID}/batch-generate" \
  -H "Content-Type: application/json" \
  -d '{
    "start_chapter_number": 1,
    "count": 100,
    "target_word_count": 10000,
    "max_retries": 10
  }'

# 返回: {"batch_id": "BATCH_ID", "status": "running", ...}
```

### 5.2 监控生成进度

```bash
# 查看批量任务状态
curl -b /tmp/cookies.txt "$MUMUAI_BASE_URL/api/chapters/batch-generate/{BATCH_ID}/status"

# 查看章节完成情况
curl -b /tmp/cookies.txt "$MUMUAI_BASE_URL/api/chapters/project/{PROJECT_ID}?limit=200" | \
  jq '{
    total: .total,
    completed: [.items[] | select(.content | length > 100)] | length,
    pending: [.items[] | select(.content == null or .content == "")] | length
  }'
```

### 5.3 RTCO上下文框架

系统自动根据章节位置调整上下文策略：

| 章节范围 | 上下文策略 |
|----------|------------|
| 第1章 | 仅大纲 + 角色设定 |
| 第2-10章 | 前章结尾300字 + 涉及角色 |
| 第11-50章 | 前章结尾500字 + 相关记忆3条 |
| 第51章+ | 前章结尾500字 + 故事骨架 + 智能记忆5条 |

### 5.4 任务恢复（中断后）

```bash
# 自动恢复所有中断任务
python auto_resume.py

# 后台持续监控直到完成
python auto_resume.py --daemon

# 后台运行并记录日志
nohup python auto_resume.py --daemon > resume.log 2>&1 &
```

---

## 6. Phase 3: 二次优化

### 6.1 优化模型选择

| 模型 | 说明 | 推荐场景 |
|------|------|----------|
| `opus` | Claude Opus 4.5 | 历史类、文学性强的小说 |
| `sonnet` | Claude Sonnet 4.5 | 网文、爽文、快节奏小说 |

### 6.2 单章优化

```bash
# 优化单个章节
curl -b /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/refinement/chapter/{CHAPTER_ID}" \
  -H "Content-Type: application/json" \
  -d '{"model": "opus"}'
```

### 6.3 批量优化（推荐）

```bash
# 优化项目所有章节
curl -b /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/refinement/project/{PROJECT_ID}/all" \
  -H "Content-Type: application/json" \
  -d '{
    "start_chapter": 1,
    "end_chapter": 100,
    "model": "opus"
  }'
```

### 6.4 查看优化进度

```bash
# 查看优化状态
curl -b /tmp/cookies.txt "$MUMUAI_BASE_URL/api/refinement/project/{PROJECT_ID}/status"

# 返回示例:
# {
#   "total": 100,
#   "completed": 45,
#   "failed": 0,
#   "pending": 55,
#   "current_chapter": 46,
#   "status": "running"
# }
```

### 6.5 查看优化对比

```bash
# 查看单章优化前后对比
curl -b /tmp/cookies.txt "$MUMUAI_BASE_URL/api/refinement/chapter/{CHAPTER_ID}/diff"

# 返回包含原文和优化后的三段内容对比
```

### 6.6 回滚到原版

```bash
# 如果优化效果不满意，可以回滚
curl -b /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/refinement/chapter/{CHAPTER_ID}/rollback"
```

---

## 7. Phase 4: 质量验证

### 7.1 一致性检测

检测角色行为和情节是否与设定一致。

```bash
# 同步检测（适合单章，约20秒）
curl -b /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/consistency/chapter/{CHAPTER_ID}/check"

# 流式检测（推荐，实时进度）
curl -b /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/consistency/chapter/{CHAPTER_ID}/check-stream"
```

**返回示例**：
```json
{
  "chapter_id": "xxx",
  "character_consistency": {"score": 85, "issues": []},
  "plot_coherence": {"score": 78, "issues": []},
  "overall_score": 81.5
}
```

### 7.2 重复检测

检测章节内部和章节间的重复内容。

```bash
# 同步检测（适合少量章节）
curl -b /tmp/cookies.txt "$MUMUAI_BASE_URL/api/duplicate/project/{PROJECT_ID}/check?max_chapters=20"

# 流式检测（推荐，适合大量章节）
curl -b /tmp/cookies.txt "$MUMUAI_BASE_URL/api/duplicate/project/{PROJECT_ID}/check-stream?max_chapters=50"
```

**返回示例**：
```json
{
  "chapters_checked": 50,
  "internal_issues": [...],
  "cross_chapter_duplicates": [...],
  "total_issues": 12,
  "has_issues": true
}
```

### 7.3 质量评分

综合评估章节质量，给出S/A/B/C/D等级。

```bash
# 评估单章质量
curl -b /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/quality/chapter/{CHAPTER_ID}/score"
```

**评分维度**：
- 文字流畅度
- 情节吸引力
- 角色塑造
- 对话质量
- 描写细节

### 7.4 人工审核

```bash
# 标记章节审核状态
curl -b /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/refinement/chapter/{CHAPTER_ID}/review" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "notes": "质量良好，无需修改"
  }'

# status 可选: pending / approved / rejected / needs_revision
```

### 7.5 获取审核汇总

```bash
curl -b /tmp/cookies.txt "$MUMUAI_BASE_URL/api/refinement/project/{PROJECT_ID}/review-summary"
```

---

## 8. Phase 5: 导出发布

### 8.1 导出优化后的小说

```bash
# 导出为TXT格式
curl -b /tmp/cookies.txt "$MUMUAI_BASE_URL/api/refinement/project/{PROJECT_ID}/export?format=txt" \
  -o novel.txt

# 导出为Markdown格式
curl -b /tmp/cookies.txt "$MUMUAI_BASE_URL/api/refinement/project/{PROJECT_ID}/export?format=markdown" \
  -o novel.md

# 仅导出已审核通过的章节
curl -b /tmp/cookies.txt "$MUMUAI_BASE_URL/api/refinement/project/{PROJECT_ID}/export?format=txt&only_approved=true" \
  -o novel_approved.txt
```

### 8.2 导出优化对比报告

```bash
# 导出所有章节的优化对比报告
curl -b /tmp/cookies.txt "$MUMUAI_BASE_URL/api/refinement/project/{PROJECT_ID}/export-diff?format=markdown" \
  -o diff_report.md
```

### 8.3 导出项目完整数据

```bash
# 导出项目JSON（包含角色、大纲、章节等）
curl -b /tmp/cookies.txt "$MUMUAI_BASE_URL/api/projects/{PROJECT_ID}/export" \
  -o project_backup.json
```

---

## 9. 自动化脚本

### 9.1 一键创建完整小说（MCP）

如果使用 Claude Desktop 或 Kiro，可以直接调用 MCP 工具：

```
novel_full_pipeline - 一键创建完整小说
```

### 9.2 Python自动化脚本

```bash
# 使用 novel_pipeline.py 自动化创建
python novel_pipeline.py \
  --title "龙霸星河" \
  --genre "星际科幻" \
  --chapters 100 \
  --words 10000
```

### 9.3 任务恢复脚本

```bash
# 查看所有项目状态
python auto_resume.py

# 恢复所有中断任务
python auto_resume.py --daemon

# 后台运行
nohup python auto_resume.py --daemon > resume.log 2>&1 &
```

### 9.4 完整自动化流程脚本

创建 `full_pipeline.sh`：

```bash
#!/bin/bash
# 完整自动化流程：生成 -> 优化 -> 验证 -> 导出

PROJECT_ID=$1
BASE_URL=${MUMUAI_BASE_URL:-http://localhost:8000}

echo "=== Phase 1: 检查生成状态 ==="
python auto_resume.py

echo "=== Phase 2: 等待生成完成 ==="
python auto_resume.py --daemon

echo "=== Phase 3: 启动二次优化 ==="
curl -b /tmp/cookies.txt -X POST "$BASE_URL/api/refinement/project/$PROJECT_ID/all" \
  -H "Content-Type: application/json" \
  -d '{"model": "opus"}'

echo "=== Phase 4: 等待优化完成 ==="
while true; do
  STATUS=$(curl -s -b /tmp/cookies.txt "$BASE_URL/api/refinement/project/$PROJECT_ID/status" | jq -r '.status')
  if [ "$STATUS" = "completed" ]; then
    echo "优化完成!"
    break
  fi
  echo "优化中... 状态: $STATUS"
  sleep 60
done

echo "=== Phase 5: 质量验证 ==="
curl -b /tmp/cookies.txt "$BASE_URL/api/duplicate/project/$PROJECT_ID/check-stream?max_chapters=100"

echo "=== Phase 6: 导出小说 ==="
curl -b /tmp/cookies.txt "$BASE_URL/api/refinement/project/$PROJECT_ID/export?format=txt" \
  -o "${PROJECT_ID}_novel.txt"

echo "=== 完成! ==="
echo "小说已导出到: ${PROJECT_ID}_novel.txt"
```

---

## 10. 故障排除

### 10.1 常见问题

**Q: 批量生成中断怎么办？**
```bash
python auto_resume.py --daemon
```

**Q: 如何查看生成日志？**
```bash
docker logs mumuainovel --tail 100
```

**Q: 优化任务失败怎么办？**
```bash
# 查看失败章节
curl -b /tmp/cookies.txt "$MUMUAI_BASE_URL/api/refinement/project/{PROJECT_ID}/chapters?status=failed"

# 重新优化失败章节
curl -b /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/refinement/chapter/{CHAPTER_ID}" \
  -d '{"model": "sonnet"}'  # 尝试换个模型
```

**Q: 如何取消正在进行的任务？**
```bash
curl -b /tmp/cookies.txt -X POST "$MUMUAI_BASE_URL/api/chapters/batch-generate/{BATCH_ID}/cancel"
```

**Q: Container重启后任务会继续吗？**
不会自动继续，需要运行 `python auto_resume.py` 恢复。

### 10.2 重试策略

| 重试次数 | 等待时间 | 说明 |
|----------|----------|------|
| 1-3 | 2, 4, 8秒 | 快速重试 |
| 4-6 | 30秒 | 中等等待 |
| 7-10 | 60秒 | 长等待 |

### 10.3 性能优化建议

1. **分批生成**：建议每次20-30章，避免单次任务过长
2. **错峰运行**：AI服务在非高峰时段响应更快
3. **模型选择**：网文用Sonnet更快，文学作品用Opus更好
4. **并发控制**：系统自动控制并发，无需手动调整

---

## 📊 API速查表

### 项目管理
| 功能 | 方法 | 端点 |
|------|------|------|
| 创建项目 | POST | /api/projects |
| 更新项目 | PUT | /api/projects/{id} |
| 查询项目 | GET | /api/projects |
| 导出项目 | GET | /api/projects/{id}/export |

### 内容管理
| 功能 | 方法 | 端点 |
|------|------|------|
| 创建角色 | POST | /api/characters |
| 创建大纲 | POST | /api/outlines |
| 展开大纲 | POST | /api/outlines/{id}/expand-stream |
| 批量生成 | POST | /api/chapters/project/{id}/batch-generate |
| 生成状态 | GET | /api/chapters/batch-generate/{batch_id}/status |

### 二次优化
| 功能 | 方法 | 端点 |
|------|------|------|
| 单章优化 | POST | /api/refinement/chapter/{id} |
| 批量优化 | POST | /api/refinement/project/{id}/all |
| 优化状态 | GET | /api/refinement/project/{id}/status |
| 优化对比 | GET | /api/refinement/chapter/{id}/diff |
| 回滚原版 | POST | /api/refinement/chapter/{id}/rollback |
| 导出小说 | GET | /api/refinement/project/{id}/export |

### 质量检测
| 功能 | 方法 | 端点 |
|------|------|------|
| 一致性检测 | POST | /api/consistency/chapter/{id}/check |
| 一致性检测(流式) | POST | /api/consistency/chapter/{id}/check-stream |
| 重复检测 | GET | /api/duplicate/project/{id}/check |
| 重复检测(流式) | GET | /api/duplicate/project/{id}/check-stream |
| 质量评分 | POST | /api/quality/chapter/{id}/score |

---

## 🔌 MCP工具速查

### 一键操作
```
novel_full_pipeline      - 一键创建完整小说
novel_resume_all         - 恢复所有中断任务
```

### 项目管理
```
novel_list_projects      - 列出项目
novel_create_project     - 创建项目
novel_delete_project     - 删除项目
novel_export_project     - 导出项目
```

### 内容生成
```
novel_create_characters_batch    - 批量创建角色
novel_create_outlines_batch      - 批量创建大纲
novel_batch_generate             - 提交批量生成
novel_check_progress             - 检查进度
```

### 质量检测
```
novel_check_quality      - 质量评分
novel_check_consistency  - 一致性检测
novel_check_duplicate    - 重复检测
```

---

*最后更新: 2026-01-07 | 版本: v1.11.0*
