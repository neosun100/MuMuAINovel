# Kiro 全自动小说生成工作流

## 概述

本文档定义了 Kiro 与用户的标准交互流程，实现从创意到100章完整小说的全自动生成。

## 用户只需提供

```
1. 小说标题
2. 类型/题材（玄幻、科幻、历史、都市等）
3. 核心创意（1-3句话描述核心卖点）
4. 主角设定（姓名、性格、初始状态）
5. 故事背景（时代、世界观概要）
6. 特殊要求（可选：参考作品、风格偏好、禁忌内容）
```

## Kiro 自动执行流程

### Phase 1: 项目初始化 (Kiro 执行)

```
步骤1: 创建项目
  POST /api/projects
  - title, genre, description, target_words(1000000)

步骤2: 生成世界观
  POST /api/projects/{id}/generate-worldview
  - 基于用户提供的背景自动扩展

步骤3: 生成职业体系（如适用）
  POST /api/professions/project/{id}/generate
  
步骤4: 生成角色（150个）
  POST /api/characters/project/{id}/batch
  - 分批创建：主角团、反派、配角、势力代表等
  
步骤5: 生成大纲（100章）
  POST /api/outlines/project/{id}/batch-generate
  - count: 100
  
步骤6: 创建章节框架
  POST /api/chapters/project/{id}/batch-create
  - 基于大纲创建100个章节占位
```

### Phase 2: 章节生成 (后台自动)

```
步骤7: 提交批量生成
  POST /api/chapters/project/{id}/batch-generate
  - start_chapter_number: 1
  - count: 100
  - target_word_count: 10000

步骤8: 监控与重试
  - 每60秒检查进度
  - 检测卡住自动重新提交
  - 直到100章全部完成
```

## 章节生成最佳实践

### RTCO 上下文框架
- 第1章：仅大纲 + 角色
- 第2-10章：上章结尾300字 + 涉及角色
- 第11-50章：上章结尾500字 + 相关记忆3条
- 第51+章：上章结尾500字 + 故事骨架 + 智能记忆5条

### 三段论生成策略
每章10000字目标，分三段生成：
- 第一段：4000字（40%）- 承接上章，展开新情节
- 第二段：4000字（40%）- 发展冲突，推进剧情
- 第三段：2000字（20%）- 高潮/转折，设置悬念

### 容错机制
- API调用失败：最多重试5次，间隔递增
- 生成中断：自动从断点续传
- 网络超时：60秒超时，自动重连
- JSON解析错误：记录日志，跳过重试

## 当前项目状态

### 崇祯大帝（终极版）
- Project ID: `7cf21fed-567b-4f48-b0ee-f9458c02a8d7`
- 状态: 生成中 (42/100章)
- Batch ID: `9e7b28f7-e601-401e-aa14-c0f5226c3c1d`
- 待生成: 43-100章

### 龙霸星河
- Project ID: `61ee2c8d-b445-4406-bfaa-8527cdc6a97b`
- 状态: 生成中 (12/100章)
- Batch ID: `cc26ffbf-11da-46a0-9309-157f06385c2d`
- 待生成: 13-100章

## 新项目启动模板

当用户说"帮我创建一部新小说"时，Kiro 应询问：

```
请提供以下信息：

1. **标题**：小说名称
2. **类型**：玄幻/科幻/历史/都市/其他
3. **核心创意**：一句话描述最大卖点
4. **主角**：姓名、性格特点、初始身份
5. **背景**：故事发生的时代/世界
6. **参考**（可选）：类似的作品风格

示例：
- 标题：《星际霸主》
- 类型：科幻
- 核心创意：普通矿工意外获得远古文明遗产，逐步统一银河系
- 主角：李云，沉稳内敛，边境星球矿工
- 背景：银河纪元3000年，人类已殖民千万星球
```

## 质量保证检查点

生成完成后，Kiro 应自动检查：
1. 章节连贯性（前后章节衔接）
2. 角色一致性（性格、能力不矛盾）
3. 伏笔回收（已埋伏笔是否回收）
4. 字数达标（每章≥8000字）

## 命令速查

```bash
# 检查项目进度
curl -b cookies.txt "http://localhost:8000/api/chapters/project/{PROJECT_ID}?limit=200" | \
  jq '{generated: [.items[] | select(.content | length > 100)] | length, total: .total}'

# 提交批量生成
curl -b cookies.txt -X POST "http://localhost:8000/api/chapters/project/{PROJECT_ID}/batch-generate" \
  -H "Content-Type: application/json" \
  -d '{"start_chapter_number": N, "count": 100, "target_word_count": 10000}'

# 查看最新章节
curl -b cookies.txt "http://localhost:8000/api/chapters/project/{PROJECT_ID}?limit=5&sort=-chapter_number" | \
  jq '.items[] | {chapter: .chapter_number, title: .title, words: .word_count}'
```
