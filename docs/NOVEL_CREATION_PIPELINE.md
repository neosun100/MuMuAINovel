# 小说全自动创建流程 (API Pipeline)

## 概述

本文档定义了从创意到100章完整小说的全自动化API流程。

## 用户输入模板

```yaml
# 小说创作需求
title: "小说标题"
genre: "类型（都市科幻/玄幻/历史穿越等）"
description: |
  故事简介（200-500字）
  包含：主角、背景、核心冲突、主题

# 主角设定
protagonist:
  name: "英文名 (中文名)"
  age: 38
  occupation: "职业"
  personality: "性格特点"
  background: "背景故事"

# 时代背景
setting:
  time: "时间"
  location: "地点"
  atmosphere: "氛围"
  rules: "世界规则"

# 故事方向
story_direction: |
  - 开篇：xxx
  - 发展：xxx
  - 高潮：xxx
  - 结局：xxx

# 特殊要求
requirements:
  - 真实人物（可选）
  - 神秘元素（可选）
  - 黑暗势力（可选）
  - 其他要求
```

## API执行流程

### Phase 1: 项目初始化

```bash
# Step 1: 登录获取Session
POST /api/auth/local/login
Body: {"username": "admin", "password": "xxx"}

# Step 2: 创建项目
POST /api/projects
Body: {
  "title": "小说标题",
  "genre": "类型",
  "description": "简介",
  "target_words": 1000000,
  "chapter_count": 100
}
Response: {"id": "PROJECT_ID", ...}
```

### Phase 2: 设置世界观

```bash
# 直接更新项目的世界观字段
# 注意：worldview字段不在API schema中，需要通过数据库或SQL更新

# 方式1: 通过SQL（推荐）
UPDATE projects SET 
  world_time_period = '时代背景',
  world_location = '地理设定',
  world_atmosphere = '社会氛围',
  world_rules = '核心规则',
  wizard_step = 1
WHERE id = 'PROJECT_ID';

# 方式2: 通过API更新部分字段
PUT /api/projects/{PROJECT_ID}
Body: {
  "world_time_period": "时代背景",
  "world_location": "地理设定",
  "world_atmosphere": "社会氛围",
  "world_rules": "核心规则"
}
```

### Phase 3: 批量创建角色

```bash
# 循环调用创建角色API
POST /api/characters
Body: {
  "project_id": "PROJECT_ID",
  "name": "角色名",
  "role_type": "protagonist|supporting|antagonist",
  "gender": "男|女",
  "age": "年龄",
  "personality": "性格描述",
  "background": "背景故事",
  "abilities": "能力（可选）",
  "goals": "目标（可选）",
  "relationships": "关系（可选）"
}

# 角色分类建议：
# - 主角家庭: 5-10人
# - 工作同事: 10-20人
# - 客户/合作伙伴: 10-15人
# - 反派/对手: 5-10人
# - 真实人物: 10-20人
# - 神秘角色: 5-10人
# - 配角: 20-50人
# 总计: 80-150人
```

### Phase 4: 批量创建大纲

```bash
# 循环调用创建大纲API
POST /api/outlines
Body: {
  "project_id": "PROJECT_ID",
  "title": "第N章 章节标题",
  "content": "章节内容概要（100-300字）",
  "order_index": N
}

# 大纲结构建议（100章）：
# - 第一卷 (1-10): 开篇/铺垫
# - 第二卷 (11-25): 发展/冲突
# - 第三卷 (26-50): 深入/转折
# - 第四卷 (51-75): 高潮/对决
# - 第五卷 (76-100): 结局/新篇
```

### Phase 5: 批量创建章节

```bash
# 循环调用创建章节API
POST /api/chapters
Body: {
  "project_id": "PROJECT_ID",
  "title": "第N章 章节标题",
  "summary": "章节摘要",
  "chapter_number": N,
  "outline_id": "对应大纲ID",
  "status": "pending"
}
```

### Phase 6: 提交批量生成

```bash
# 一次性提交100章生成任务
POST /api/chapters/project/{PROJECT_ID}/batch-generate
Body: {
  "start_chapter_number": 1,
  "count": 100,
  "target_word_count": 10000
}
Response: {"batch_id": "BATCH_ID", ...}
```

### Phase 7: 监控生成进度

```bash
# 查询章节生成状态
GET /api/chapters/project/{PROJECT_ID}?limit=200

# 解析响应，统计已生成章节数
# generated = items.filter(item => item.content && item.content.length > 100).length
```

## 完整执行脚本

见 `/home/neo/upload/MuMuAINovel/novel_pipeline.py`

## 注意事项

1. **角色设计**：角色要丰富多样，包含主角团、反派、配角、真实人物等
2. **大纲设计**：每章大纲100-300字，包含场景、人物、冲突、情感
3. **章节生成**：系统自动使用三段论（40%+40%+20%）生成每章内容
4. **上下文衔接**：RTCO框架自动处理章节间的上下文关联
5. **容错机制**：batch-generate内置重试机制，网络中断会自动恢复

## API速查表

| 功能 | 方法 | 端点 |
|------|------|------|
| 登录 | POST | /api/auth/local/login |
| 创建项目 | POST | /api/projects |
| 更新项目 | PUT | /api/projects/{id} |
| 创建角色 | POST | /api/characters |
| 查询角色 | GET | /api/characters/project/{id} |
| 创建大纲 | POST | /api/outlines |
| 查询大纲 | GET | /api/outlines/project/{id} |
| 创建章节 | POST | /api/chapters |
| 查询章节 | GET | /api/chapters/project/{id} |
| 批量生成 | POST | /api/chapters/project/{id}/batch-generate |
| 生成状态 | GET | /api/chapters/batch-generate/{batch_id}/status |
