# 小说自动化生成最佳实践指南

## 版本信息
- **版本**: v1.0.0
- **更新日期**: 2026-01-04
- **目标**: 实现从用户输入到100章完整小说的全自动化生成

---

## 一、整体流程概览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        小说自动化生成完整流程                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  【第一阶段：手动准备】 ← 用户参与                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. 用户提供：书名 + 类型 + 核心设定 + 主要角色概念                      │   │
│  │ 2. AI生成：完整项目设定文档（世界观、角色、大纲框架）                    │   │
│  │ 3. 用户确认/调整设定                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓                                              │
│  【第二阶段：半自动创建】 ← AI执行，用户监督                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 4. 创建项目 (API)                                                      │   │
│  │ 5. 批量创建角色 (API) - 100-150个角色                                  │   │
│  │ 6. 批量创建大纲 (API) - 100个大纲                                      │   │
│  │ 7. 展开大纲创建章节记录 (API) - 100个章节                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓                                              │
│  【第三阶段：全自动生成】 ← 后台无人值守                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 8. 提交batch-generate任务 (每次20章，共5次)                            │   │
│  │ 9. 后台自动：                                                          │   │
│  │    - 三段论生成每章内容 (10000-20000字/章)                             │   │
│  │    - 自动生成章节摘要                                                  │   │
│  │    - RTCO上下文框架保证章节连贯                                        │   │
│  │    - 分层递减上下文利用150个角色信息                                   │   │
│  │ 10. 循环直到100章全部完成                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↓                                              │
│  【最终输出】                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 100章完整小说，总计100-200万字                                         │   │
│  │ 每章10000-20000字，有完整悬念结尾                                      │   │
│  │ 章节间高度连贯，角色行为一致                                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 二、手动准备阶段（用户输入）

### 2.1 用户需要提供的最小信息

```yaml
# 用户输入模板
书名: "龙霸星河"
类型: "星际科幻/军事战争/热血爽文"
字数规划: "100章，每章15000-20000字"

核心设定:
  背景: "小兵传奇续集，统一宇宙15年后"
  主要冲突: "异宇宙入侵 + 帝国内部危机"
  
主角信息:
  - 姓名: 唐龙
    身份: 宇宙皇帝
    性格: 痞气、护短、热血
    
关键配角:
  - 星零（皇后，AI生命体）
  - 唐天（儿子，新一代主角）
  - 暗龙（反派，唐龙的兄弟）
  
写作风格: "轻松幽默，战斗热血，情感细腻"
```

### 2.2 AI生成完整设定文档

基于用户输入，AI自动生成：

1. **项目设定.md** - 完整的故事框架
2. **角色设定.md** - 150个角色的详细设定
3. **世界观设定.md** - 科技、势力、地理等
4. **章节大纲.md** - 100章的大纲框架

---

## 三、API调用流程（半自动）

### 3.1 创建项目

```bash
# API: POST /api/projects
curl -X POST "http://localhost:8000/api/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "龙霸星河",
    "description": "小兵传奇续集，统一宇宙15年后的新冒险",
    "genre": "星际科幻",
    "target_words": 2000000,
    "outline_mode": "one-to-many",
    "narrative_perspective": "第三人称",
    "writing_style": "轻松幽默，战斗热血"
  }'
```

**关键参数**：
- `outline_mode: "one-to-many"` - 一对多模式，每个大纲对应一个章节

### 3.2 批量创建角色（150个）

```python
# 角色创建脚本示例
characters = [
    # 主角阵营
    {"name": "唐龙", "role_type": "protagonist", "personality": "痞气、护短、热血", 
     "background": "从小兵成长为宇宙皇帝，统治宇宙15年"},
    {"name": "星零", "role_type": "supporting", "personality": "温柔、智慧、忠诚",
     "background": "AI皇后，帝国内务总管"},
    # ... 继续添加148个角色
]

for char in characters:
    char["project_id"] = PROJECT_ID
    requests.post(f"{BASE_URL}/api/characters", json=char)
```

**角色分类建议**：
- 主角阵营：20-30个
- 反派阵营：20-30个
- 中立势力：20-30个
- 配角/龙套：70-80个

### 3.3 批量创建大纲（100个）

```python
# 大纲创建脚本示例
outlines = [
    {"order": 1, "title": "帝国十五年", 
     "content": "唐龙视察帝国，展现繁荣景象，暗示隐患"},
    {"order": 2, "title": "皇子成年",
     "content": "唐天18岁成年礼，展现新一代实力"},
    # ... 继续添加98个大纲
]

for outline in outlines:
    outline["project_id"] = PROJECT_ID
    requests.post(f"{BASE_URL}/api/outlines", json=outline)
```

### 3.4 展开大纲创建章节记录

```python
# 为每个大纲创建章节记录
for outline in outlines:
    requests.post(
        f"{BASE_URL}/api/outlines/{outline['id']}/expand-stream",
        json={
            "target_chapter_count": 1,
            "auto_create_chapters": True
        }
    )
```

**作用**：
- 创建空的章节记录
- AI自动生成章节标题
- 生成expansion_plan（详细的章节规划）

---

## 四、全自动生成阶段

### 4.1 提交batch-generate任务

```bash
# 第1批：第1-20章
curl -X POST "http://localhost:8000/api/chapters/project/{project_id}/batch-generate" \
  -H "Content-Type: application/json" \
  -d '{
    "start_chapter_number": 1,
    "count": 20,
    "target_word_count": 10000,
    "enable_analysis": false
  }'

# 第2批：第21-40章（等第1批完成后）
# 第3批：第41-60章
# 第4批：第61-80章
# 第5批：第81-100章
```

### 4.2 后台自动执行的流程

```
每章生成流程：
┌─────────────────────────────────────────────────────────────────────┐
│ 1. 构建上下文 (ChapterContextBuilder)                                │
│    - 获取本章大纲和expansion_plan                                    │
│    - 获取本章涉及的角色信息（从150个角色中筛选）                       │
│    - 构建分层递减摘要（远期/中期/近期）                               │
│    - 获取上一章结尾6000-10000字                                      │
│    - 获取伏笔上下文和风格指南                                        │
├─────────────────────────────────────────────────────────────────────┤
│ 2. 三段论生成                                                        │
│    - 第1段：4000字，开头+情节发展                                    │
│    - 第2段：4000字，继续发展                                         │
│    - 第3段：2000字，高潮+悬念结尾                                    │
├─────────────────────────────────────────────────────────────────────┤
│ 3. 结尾检查                                                          │
│    - 确保以完整句子结尾                                              │
│    - 必要时补充结尾                                                  │
├─────────────────────────────────────────────────────────────────────┤
│ 4. 保存章节                                                          │
│    - 合并三段内容                                                    │
│    - 更新字数统计                                                    │
├─────────────────────────────────────────────────────────────────────┤
│ 5. 生成摘要                                                          │
│    - AI生成600-800字摘要                                             │
│    - 供后续章节的上下文使用                                          │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.3 角色信息如何被使用

```
角色使用机制：
┌─────────────────────────────────────────────────────────────────────┐
│ 1. 大纲展开时                                                        │
│    - AI分析大纲内容，识别涉及的角色                                  │
│    - 生成expansion_plan时包含character_focus字段                     │
│    - 例如：["唐龙", "星零", "暗龙"]                                  │
├─────────────────────────────────────────────────────────────────────┤
│ 2. 章节生成时                                                        │
│    - 从expansion_plan提取character_focus                             │
│    - 从150个角色中查询这些角色的详细信息                             │
│    - 将角色信息注入到生成Prompt中                                    │
├─────────────────────────────────────────────────────────────────────┤
│ 3. 上下文构建时                                                      │
│    - 分层摘要中包含角色行为记录                                      │
│    - 确保角色行为在章节间保持一致                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 五、关键技术保障

### 5.1 章节连贯性保障（RTCO框架）

```
RTCO (Real-Time Context Optimization) 上下文框架：

章节序号    上下文策略
─────────────────────────────────────
第 1 章     仅大纲 + 角色
第 2-10 章  上章结尾 6000 字 + 涉及角色
第 11-30 章 上章结尾 8000 字 + 分层摘要 + 相关记忆
第 31-50 章 上章结尾 10000 字 + 分层摘要 + 故事骨架
第 51+ 章   上章结尾 10000 字 + 完整分层摘要 + 智能记忆
```

### 5.2 分层递减上下文

```
以第51章为例：

┌─ 远期摘要（第1-25章）：每10章合并，约3600字
├─ 中期摘要（第26-40章）：每5章合并，约4500字
├─ 近期详情（第41-50章）：每章独立摘要，约12000字
├─ 直接上文（第50章结尾）：完整保留10000字
└─ 总计：约40000字上下文，充分利用100K token窗口
```

### 5.3 三段论生成策略

```
目标10000字的分段：
┌─────────────────────────────────────────────────────────────────────┐
│ 第1段 (40%): 约4000字                                                │
│ - 输入：完整Prompt（大纲+角色+上下文）                               │
│ - 输出：开头+情节发展                                                │
│ - 要求：不要结尾，留发展空间                                         │
├─────────────────────────────────────────────────────────────────────┤
│ 第2段 (40%): 约4000字                                                │
│ - 输入：核心上下文 + 第1段全部内容                                   │
│ - 输出：继续发展情节                                                 │
│ - 要求：不要结尾，后面还有                                           │
├─────────────────────────────────────────────────────────────────────┤
│ 第3段 (20%): 约2000字                                                │
│ - 输入：核心上下文 + 第1段+第2段全部内容                             │
│ - 输出：高潮+悬念结尾                                                │
│ - 要求：必须有完整包袱，吸引读者继续                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 六、一键自动化脚本

### 6.1 完整自动化脚本

```python
#!/usr/bin/env python3
"""
小说全自动生成脚本
使用方法：python auto_generate_novel.py
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "your_password"

class NovelGenerator:
    def __init__(self):
        self.session = requests.Session()
        self.project_id = None
        
    def login(self):
        """登录获取session"""
        resp = self.session.post(
            f"{BASE_URL}/api/auth/local/login",
            json={"username": USERNAME, "password": PASSWORD}
        )
        return resp.status_code == 200
    
    def create_project(self, title, description, genre):
        """创建项目"""
        resp = self.session.post(
            f"{BASE_URL}/api/projects",
            json={
                "title": title,
                "description": description,
                "genre": genre,
                "target_words": 2000000,
                "outline_mode": "one-to-many"
            }
        )
        if resp.status_code == 200:
            self.project_id = resp.json()["id"]
            return True
        return False
    
    def create_characters(self, characters):
        """批量创建角色"""
        created = 0
        for char in characters:
            char["project_id"] = self.project_id
            resp = self.session.post(f"{BASE_URL}/api/characters", json=char)
            if resp.status_code == 200:
                created += 1
        print(f"创建角色: {created}/{len(characters)}")
        return created
    
    def create_outlines(self, outlines):
        """批量创建大纲"""
        created = 0
        for outline in outlines:
            outline["project_id"] = self.project_id
            resp = self.session.post(f"{BASE_URL}/api/outlines", json=outline)
            if resp.status_code == 200:
                created += 1
        print(f"创建大纲: {created}/{len(outlines)}")
        return created
    
    def expand_outlines(self):
        """展开所有大纲创建章节记录"""
        resp = self.session.get(
            f"{BASE_URL}/api/outlines",
            params={"project_id": self.project_id}
        )
        outlines = resp.json()
        
        for outline in outlines:
            self.session.post(
                f"{BASE_URL}/api/outlines/{outline['id']}/expand-stream",
                json={"target_chapter_count": 1, "auto_create_chapters": True}
            )
            time.sleep(1)  # 避免请求过快
        
        print(f"展开大纲: {len(outlines)}个")
    
    def batch_generate(self, start, count=20, target_words=10000):
        """提交批量生成任务"""
        resp = self.session.post(
            f"{BASE_URL}/api/chapters/project/{self.project_id}/batch-generate",
            json={
                "start_chapter_number": start,
                "count": count,
                "target_word_count": target_words,
                "enable_analysis": False
            }
        )
        if resp.status_code == 200:
            data = resp.json()
            print(f"提交生成任务: 第{start}-{start+count-1}章")
            print(f"  批次ID: {data.get('batch_id')}")
            print(f"  预计时间: {data.get('estimated_minutes')}分钟")
            return data.get('batch_id')
        return None
    
    def check_status(self):
        """检查生成状态"""
        resp = self.session.get(
            f"{BASE_URL}/api/chapters/project/{self.project_id}/active-task"
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    
    def wait_for_completion(self, batch_id, check_interval=60):
        """等待批次完成"""
        while True:
            status = self.check_status()
            if not status or status.get("status") != "running":
                print("批次完成或无活动任务")
                return True
            
            print(f"进度: 第{status.get('current_chapter')}章, "
                  f"已完成{status.get('completed_count')}/{status.get('total_count')}")
            time.sleep(check_interval)
    
    def generate_all(self):
        """生成全部100章"""
        # 分5批生成
        for batch in range(5):
            start = batch * 20 + 1
            batch_id = self.batch_generate(start, 20, 10000)
            if batch_id:
                self.wait_for_completion(batch_id)
            time.sleep(10)  # 批次间隔
        
        print("全部100章生成完成！")


def main():
    # 从文件加载角色和大纲
    with open("characters.json", "r") as f:
        characters = json.load(f)
    with open("outlines.json", "r") as f:
        outlines = json.load(f)
    
    generator = NovelGenerator()
    
    # 1. 登录
    if not generator.login():
        print("登录失败")
        return
    
    # 2. 创建项目
    generator.create_project(
        title="龙霸星河",
        description="小兵传奇续集",
        genre="星际科幻"
    )
    
    # 3. 创建角色
    generator.create_characters(characters)
    
    # 4. 创建大纲
    generator.create_outlines(outlines)
    
    # 5. 展开大纲
    generator.expand_outlines()
    
    # 6. 全自动生成
    generator.generate_all()


if __name__ == "__main__":
    main()
```

---

## 七、监控与恢复

### 7.1 检查生成状态

```bash
# 检查活动任务
curl -s "http://localhost:8000/api/chapters/project/{project_id}/active-task"

# 检查已生成章节
curl -s "http://localhost:8000/api/chapters/project/{project_id}?limit=100" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); \
  print(f'已生成: {len([c for c in d[\"items\"] if c[\"content\"]])}章')"
```

### 7.2 断点续传

如果生成中断，可以从断点继续：

```bash
# 查看最后生成的章节
curl -s "http://localhost:8000/api/chapters/project/{project_id}?limit=100" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); \
  last=max([c['chapter_number'] for c in d['items'] if c['content']], default=0); \
  print(f'最后生成: 第{last}章，从第{last+1}章继续')"

# 从断点继续
curl -X POST "http://localhost:8000/api/chapters/project/{project_id}/batch-generate" \
  -d '{"start_chapter_number": 断点章节号, "count": 20, "target_word_count": 10000}'
```

---

## 八、预期效果

### 8.1 生成质量

| 指标 | 预期值 |
|------|--------|
| 每章字数 | 10,000-20,000字 |
| 结尾完整率 | >95% |
| 有悬念结尾 | >90% |
| 角色一致性 | 高（通过分层上下文保障） |
| 情节连贯性 | 高（通过RTCO框架保障） |

### 8.2 时间预估

| 阶段 | 时间 |
|------|------|
| 手动准备（用户输入+AI生成设定） | 1-2小时 |
| 半自动创建（项目+角色+大纲+章节） | 30分钟 |
| 全自动生成（100章） | 10-15小时 |
| **总计** | **约12-18小时** |

### 8.3 成本预估

以Claude 3.5 Sonnet为例：
- 每章约消耗50K input tokens + 20K output tokens
- 100章约消耗7M tokens
- 成本约 $20-30

---

## 九、常见问题

### Q1: 角色信息会被后续章节使用吗？

**是的**。系统通过以下机制确保角色信息被使用：
1. 大纲展开时，AI识别涉及的角色并记录在expansion_plan
2. 章节生成时，从数据库查询这些角色的详细信息
3. 角色信息被注入到生成Prompt中
4. 分层摘要中包含角色行为记录，确保一致性

### Q2: 如何保证章节间连贯？

通过**RTCO框架**和**分层递减上下文**：
1. 每章生成时获取上一章结尾6000-10000字
2. 构建分层摘要（远期/中期/近期）
3. 自动生成章节摘要供后续使用
4. 伏笔系统追踪未回收的线索

### Q3: 生成中断怎么办？

系统支持**断点续传**：
1. 查询最后生成的章节号
2. 从下一章开始重新提交batch-generate
3. 已生成的章节不会丢失

### Q4: 如何调整生成质量？

可以调整以下参数：
- `target_word_count`: 目标字数（建议10000-15000）
- AI模型选择：Claude 3.5 Sonnet效果最佳
- `temperature`: 0.7-0.8之间平衡创意和一致性

---

## 十、总结

### 手动部分（需要用户参与）

1. **提供核心设定**：书名、类型、主角、核心冲突
2. **确认AI生成的设定文档**
3. **启动生成任务**

### 自动部分（后台无人值守）

1. **角色创建**：批量API调用
2. **大纲创建**：批量API调用
3. **章节记录创建**：expand-stream API
4. **内容生成**：batch-generate API
   - 三段论生成
   - 自动摘要
   - RTCO上下文
   - 分层递减上下文
5. **循环生成**：直到100章完成

### 最终交付

- 100章完整小说
- 每章10000-20000字
- 总计100-200万字
- 章节连贯，角色一致
- 每章有悬念结尾

---

*文档版本: v1.0.0*
*最后更新: 2026-01-04*
