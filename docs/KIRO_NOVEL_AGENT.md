# Kiro 小说创作Agent工作流

## 交互模式

用户只需提供以下信息，Kiro自动完成全部创作流程：

```
我想创作一部小说：
- 标题：《xxx》
- 类型：都市科幻/玄幻/历史穿越/...
- 主角：名字、职业、性格
- 背景：时代、地点、核心冲突
- 方向：开篇→发展→高潮→结局的大致走向
- 特殊要求：真实人物、神秘元素、黑暗势力等
```

## Kiro执行流程

### Step 1: 信息收集与搜索
```
1. 解析用户输入，提取关键信息
2. 使用web_search搜索相关背景资料：
   - 行业背景（科技/金融/历史等）
   - 真实人物信息
   - 时代特征
   - 专业术语
3. 整合搜索结果，丰富世界观设定
```

### Step 2: 项目创建 (API)
```bash
POST /api/projects
{
  "title": "小说标题",
  "genre": "类型",
  "description": "基于用户输入+搜索结果的完整描述",
  "target_words": 1000000,
  "chapter_count": 100
}
```

### Step 3: 世界观设置 (API/SQL)
```bash
PUT /api/projects/{id}
{
  "world_time_period": "时代背景（含搜索到的真实信息）",
  "world_location": "地理设定",
  "world_atmosphere": "社会氛围",
  "world_rules": "核心规则/隐喻"
}
```

### Step 4: 角色设计与创建 (API)
```
Kiro根据故事需要设计角色：
- 主角家庭 (5-10人)
- 工作/社交圈 (15-25人)
- 反派/对手 (5-15人)
- 真实人物 (10-20人，如用户要求)
- 神秘角色 (5-10人)
- 配角 (20-50人)

每个角色调用:
POST /api/characters
{
  "project_id": "xxx",
  "name": "英文名 (中文名)",
  "role_type": "protagonist|supporting|antagonist",
  "personality": "性格描述",
  "background": "背景故事"
}
```

### Step 5: 大纲设计与创建 (API)
```
Kiro设计100章完整大纲：
- 第一卷 (1-10): 开篇/铺垫
- 第二卷 (11-25): 发展/冲突
- 第三卷 (26-50): 深入/转折
- 第四卷 (51-75): 高潮/对决
- 第五卷 (76-100): 结局/新篇

每章调用:
POST /api/outlines
{
  "project_id": "xxx",
  "title": "第N章 章节标题",
  "content": "章节概要（100-300字）",
  "order_index": N
}
```

### Step 6: 章节创建 (API)
```
遍历大纲，创建对应章节:
POST /api/chapters
{
  "project_id": "xxx",
  "title": "第N章 章节标题",
  "summary": "章节摘要",
  "chapter_number": N,
  "outline_id": "大纲ID",
  "status": "pending"
}
```

### Step 7: 批量生成 (API)
```bash
POST /api/chapters/project/{id}/batch-generate
{
  "start_chapter_number": 1,
  "count": 100,
  "target_word_count": 10000
}
```

### Step 8: 进度监控
```
定期查询生成进度:
GET /api/chapters/project/{id}?limit=200

解析响应，报告进度:
- 已生成章节数
- 总字数
- 预计完成时间
```

## 示例对话

**用户**:
> 帮我创作一部小说，标题《星际霸主》，科幻类型。主角叫Jack Chen，是一个边境星球的矿工，意外获得远古文明遗产。背景是银河纪元3000年，人类已殖民千万星球。我希望有真实的科技大佬出现，比如Elon Musk的后代。

**Kiro**:
> 好的，让我开始创作《星际霸主》：
> 
> 1. 🔍 搜索科幻背景资料...
> 2. 📚 创建项目...
> 3. 🌍 设置世界观...
> 4. 👥 创建角色（预计120个）...
>    - ✅ Jack Chen (主角)
>    - ✅ Elon Musk III (马斯克后代)
>    - ...
> 5. 📝 创建大纲（100章）...
>    - ✅ 第1章: 边境矿工
>    - ✅ 第2章: 神秘遗迹
>    - ...
> 6. 📖 创建章节...
> 7. 🚀 提交批量生成...
> 
> ✅ 全部准备完成！
> - Project ID: xxx
> - Batch ID: xxx
> - 预计生成时间: 10-15小时
> - 目标字数: 100万字

## 关键API清单

| 步骤 | API | 说明 |
|------|-----|------|
| 登录 | POST /api/auth/local/login | 获取Session |
| 创建项目 | POST /api/projects | 返回project_id |
| 更新世界观 | PUT /api/projects/{id} | 设置背景 |
| 创建角色 | POST /api/characters | 循环调用 |
| 创建大纲 | POST /api/outlines | 循环调用 |
| 创建章节 | POST /api/chapters | 循环调用 |
| 批量生成 | POST /api/chapters/project/{id}/batch-generate | 一次提交 |
| 查询进度 | GET /api/chapters/project/{id} | 监控状态 |

## 质量保证

1. **角色丰富度**: 至少80个角色，覆盖各类型
2. **大纲完整性**: 100章，每章有明确的场景、人物、冲突
3. **章节生成**: 每章10000字，三段论结构
4. **上下文衔接**: RTCO框架自动处理
5. **容错机制**: 网络中断自动重试

## 文件位置

- 流程文档: `/docs/NOVEL_CREATION_PIPELINE.md`
- Pipeline脚本: `/novel_pipeline.py`
- 本文档: `/docs/KIRO_NOVEL_AGENT.md`
