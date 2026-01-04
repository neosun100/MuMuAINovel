# 预案01: 知识库集成方案

> 版本: v1.11 | 优先级: 🔴 P0 | **AI开发: 3-5天** | 人工审核: 0.5天

---

## 1. 目标与成功指标

### 1.1 核心目标
- 集成历史知识库，提升历史类小说准确性从 **60%→90%**
- 实现RAG检索增强生成，**自动注入**相关知识到章节生成
- 支持专业领域知识（科技/金融/医学/军事）

### 1.2 成功指标

| 指标 | 当前 | 目标 | 验证方法 |
|------|------|------|----------|
| 历史准确性 | 60% | 90% | AI评估+人工抽检 |
| 专业术语准确性 | 50% | 85% | 领域专家评审 |
| 知识检索响应时间 | - | <500ms | 性能测试 |
| 知识库覆盖率 | 0% | 80% | 数据统计 |

---

## 2. 方案对比

### 方案A: pgvector扩展 (推荐 ⭐)

**原理**: 利用现有PostgreSQL，添加pgvector扩展实现向量存储

```
优点:
✅ 无需新增服务，复用现有PostgreSQL
✅ 事务一致性，知识与业务数据同库
✅ 运维成本低，团队已熟悉PostgreSQL
✅ 成本最低，无额外服务器费用

缺点:
❌ 大规模(>1000万向量)性能下降
❌ 索引重建时间较长
❌ 高级向量功能有限

适用场景: 中小规模知识库(<500万条)
```

**架构图**:
```
┌─────────────────────────────────────────────────┐
│                 PostgreSQL 18                    │
├─────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ 业务数据表   │  │ 知识向量表 (pgvector)   │  │
│  │ - projects  │  │ - knowledge_entries     │  │
│  │ - chapters  │  │ - historical_figures    │  │
│  │ - characters│  │ - historical_events     │  │
│  └─────────────┘  └─────────────────────────┘  │
│                         │                       │
│                    HNSW索引                     │
└─────────────────────────────────────────────────┘
```

**成本估算**:
- 服务器: $0/月 (复用现有)
- 存储: +20GB SSD
- 一次性: $100 (嵌入生成API)

---

### 方案B: ChromaDB独立服务

**原理**: 部署独立的ChromaDB向量数据库服务

```
优点:
✅ 专为向量搜索优化
✅ 简单易用的Python API
✅ 项目已有ChromaDB集成经验
✅ 支持多种距离度量

缺点:
❌ 需要额外服务器资源
❌ 数据一致性需要额外处理
❌ 生产环境稳定性待验证

适用场景: 中等规模，快速原型
```

**架构图**:
```
┌─────────────────┐     ┌─────────────────┐
│   PostgreSQL    │     │    ChromaDB     │
│   (业务数据)    │     │   (向量数据)    │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
              ┌──────▼──────┐
              │ 知识检索服务 │
              └─────────────┘
```

**成本估算**:
- 服务器: +$50/月 (4核8G)
- 存储: 100GB SSD
- 一次性: $100 (嵌入生成)

---

### 方案C: Milvus企业级方案

**原理**: 部署Milvus分布式向量数据库

```
优点:
✅ 亿级向量支持
✅ 分布式架构，高可用
✅ 丰富的索引类型
✅ 企业级稳定性

缺点:
❌ 部署复杂，需要K8s
❌ 资源消耗大
❌ 学习曲线陡峭
❌ 成本较高

适用场景: 大规模生产环境
```

**成本估算**:
- 服务器: +$200/月 (集群)
- 运维: 需要专人
- 一次性: $100 (嵌入生成)

---

## 3. 推荐方案: pgvector (方案A)

### 3.1 选择理由

1. **与现有架构一致**: 项目已使用PostgreSQL，无需引入新技术栈
2. **成本最优**: 无额外服务器费用
3. **数据一致性**: 知识数据与业务数据同库，事务保证
4. **规模适中**: 历史知识库预计<100万条，pgvector完全胜任
5. **团队熟悉**: 降低学习和维护成本

### 3.2 技术实现

#### 3.2.1 数据库Schema

```sql
-- 启用pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 知识分类表
CREATE TABLE knowledge_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES knowledge_categories(id),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 知识条目表 (核心)
CREATE TABLE knowledge_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id INTEGER REFERENCES knowledge_categories(id),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(500),
    reliability FLOAT DEFAULT 0.8,
    time_period VARCHAR(100),
    tags JSONB,
    embedding vector(1536),  -- OpenAI ada-002维度
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 历史人物表
CREATE TABLE historical_figures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    aliases JSONB,  -- ["崇祯帝", "明思宗"]
    birth_year INTEGER,
    death_year INTEGER,
    dynasty VARCHAR(50),
    title VARCHAR(200),
    biography TEXT,
    personality TEXT,
    achievements JSONB,
    relationships JSONB,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 历史事件表
CREATE TABLE historical_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    year_start INTEGER,
    year_end INTEGER,
    dynasty VARCHAR(50),
    location VARCHAR(200),
    description TEXT,
    causes JSONB,
    consequences JSONB,
    key_figures JSONB,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 创建HNSW索引 (高性能近似搜索)
CREATE INDEX ON knowledge_entries 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE INDEX ON historical_figures 
    USING hnsw (embedding vector_cosine_ops);

CREATE INDEX ON historical_events 
    USING hnsw (embedding vector_cosine_ops);
```

#### 3.2.2 知识检索服务

```python
# backend/app/services/knowledge_service.py

from typing import List, Dict, Optional
from sqlalchemy import text
from sentence_transformers import SentenceTransformer

class KnowledgeService:
    """知识库检索服务 - 基于pgvector"""
    
    def __init__(self, db_session):
        self.db = db_session
        # 复用现有的embedding模型
        self.embedding_model = SentenceTransformer(
            'paraphrase-multilingual-MiniLM-L12-v2'
        )
    
    async def search_knowledge(
        self,
        query: str,
        category: str = None,
        time_period: str = None,
        top_k: int = 5
    ) -> List[Dict]:
        """语义搜索知识库"""
        # 生成查询向量
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # 构建SQL (pgvector余弦相似度)
        sql = """
        SELECT id, title, content, source, reliability,
               1 - (embedding <=> :embedding) as similarity
        FROM knowledge_entries
        WHERE 1=1
        """
        params = {"embedding": str(query_embedding)}
        
        if category:
            sql += " AND category_id = (SELECT id FROM knowledge_categories WHERE name = :category)"
            params["category"] = category
        if time_period:
            sql += " AND time_period = :time_period"
            params["time_period"] = time_period
        
        sql += " ORDER BY embedding <=> :embedding LIMIT :top_k"
        params["top_k"] = top_k
        
        result = await self.db.execute(text(sql), params)
        return [dict(row) for row in result.fetchall()]
    
    async def get_historical_context(
        self,
        dynasty: str,
        year: int = None,
        characters: List[str] = None
    ) -> Dict:
        """获取历史背景上下文 (用于章节生成)"""
        context = {
            "dynasty_info": await self._get_dynasty_info(dynasty),
            "period_events": [],
            "cultural_notes": [],
            "figure_info": []
        }
        
        # 获取时期事件
        if year:
            events = await self._search_events_by_year(dynasty, year)
            context["period_events"] = events[:5]
        
        # 获取涉及人物信息
        if characters:
            for name in characters:
                figure = await self._search_figure(name, dynasty)
                if figure:
                    context["figure_info"].append(figure)
        
        return context
    
    async def validate_historical_accuracy(
        self,
        content: str,
        dynasty: str,
        year: int = None
    ) -> Dict:
        """AI验证历史准确性 (自动化，无需人工)"""
        issues = []
        
        # 1. 提取内容中的实体
        entities = await self._extract_entities(content)
        
        # 2. 验证人物
        for person in entities.get("persons", []):
            figure = await self._search_figure(person, dynasty)
            if figure:
                # 检查生卒年
                if year and figure.get("death_year") and year > figure["death_year"]:
                    issues.append({
                        "type": "anachronism",
                        "entity": person,
                        "issue": f"{person}已于{figure['death_year']}年去世",
                        "suggestion": f"调整时间线或移除{person}"
                    })
        
        # 3. 验证物品/科技
        for item in entities.get("items", []):
            anachronism = await self._check_item_anachronism(item, dynasty, year)
            if anachronism:
                issues.append(anachronism)
        
        return {
            "is_accurate": len(issues) == 0,
            "accuracy_score": max(0, 1 - len(issues) * 0.1),
            "issues": issues,
            "auto_fix_available": len(issues) > 0
        }
    
    async def _extract_entities(self, content: str) -> Dict:
        """使用AI提取实体 (人物、地点、物品)"""
        # 调用现有AI服务
        prompt = f"""从以下文本中提取实体，返回JSON格式：
        {{
            "persons": ["人物1", "人物2"],
            "locations": ["地点1"],
            "items": ["物品1"],
            "events": ["事件1"]
        }}
        
        文本：{content[:2000]}
        """
        # 调用AI提取
        result = await self.ai_service.generate(prompt, max_tokens=500)
        return json.loads(result)
```

---

## 4. 数据准备方案

### 4.1 数据源与获取方式

| 数据源 | 内容 | 数据量 | 获取方式 | 可信度 |
|--------|------|--------|----------|--------|
| 维基百科API | 历史事件、人物 | ~50万条 | API爬取 | 高 |
| 中国历史年表 | 朝代、年号 | ~5000条 | 公开数据整理 | 高 |
| 百度百科 | 补充人物资料 | ~10万条 | API/爬取 | 中 |
| 历史地图数据 | 地名变迁 | ~2万条 | 公开数据 | 高 |
| 文化习俗资料 | 服饰、礼仪 | ~1万条 | 人工整理 | 高 |

### 4.2 数据处理Pipeline

```python
# scripts/import_knowledge.py

async def import_historical_data():
    """导入历史数据的完整流程"""
    
    # 阶段1: 导入朝代基础数据
    print("📚 导入朝代数据...")
    dynasties = load_json("data/dynasties.json")
    for d in dynasties:
        await db.execute(insert(KnowledgeCategory).values(
            name=d["name"],
            description=d["description"]
        ))
    
    # 阶段2: 导入历史人物 (批量嵌入)
    print("👤 导入历史人物...")
    figures = load_json("data/historical_figures.json")
    
    # 批量生成嵌入 (节省API调用)
    texts = [f"{f['name']} {f['biography'][:500]}" for f in figures]
    embeddings = embedding_model.encode(texts, batch_size=32, show_progress_bar=True)
    
    for i, figure in enumerate(figures):
        figure['embedding'] = embeddings[i].tolist()
        await db.execute(insert(HistoricalFigure).values(**figure))
    
    # 阶段3: 导入历史事件
    print("📅 导入历史事件...")
    events = load_json("data/historical_events.json")
    texts = [f"{e['name']} {e['description'][:500]}" for e in events]
    embeddings = embedding_model.encode(texts, batch_size=32)
    
    for i, event in enumerate(events):
        event['embedding'] = embeddings[i].tolist()
        await db.execute(insert(HistoricalEvent).values(**event))
    
    print("✅ 数据导入完成!")
```

### 4.3 数据格式示例

```json
// data/historical_figures.json
[
  {
    "name": "朱由检",
    "aliases": ["崇祯帝", "明思宗", "朱由检"],
    "birth_year": 1611,
    "death_year": 1644,
    "dynasty": "明朝",
    "title": "明朝第十六位皇帝",
    "biography": "朱由检（1611年2月6日－1644年4月25日），明朝末代皇帝。年号崇祯，在位十七年。即位后铲除魏忠贤阉党，勤于政事，但生性多疑，刚愎自用。面对内忧外患，最终于1644年李自成攻入北京时自缢于煤山。",
    "personality": "勤政、多疑、刚愎自用、节俭、急躁",
    "achievements": ["铲除魏忠贤", "整顿朝纲", "减免赋税"],
    "relationships": {
      "父亲": "明光宗朱常洛",
      "皇后": "周皇后",
      "重臣": ["袁崇焕", "孙承宗", "卢象升", "洪承畴"]
    }
  }
]
```

---

## 5. 集成到章节生成

### 5.1 修改章节生成流程

```python
# backend/app/services/chapter_generation_service.py

async def generate_chapter_with_knowledge(
    self,
    chapter: Chapter,
    project: Project
) -> str:
    """带知识增强的章节生成"""
    
    # 1. 判断是否需要知识增强
    if project.genre not in ["历史", "历史穿越", "架空历史"]:
        return await self.generate_chapter_normal(chapter, project)
    
    # 2. 获取历史背景上下文
    knowledge_context = await self.knowledge_service.get_historical_context(
        dynasty=project.world_time_period,
        year=getattr(chapter, 'story_year', None),
        characters=[c.name for c in chapter.involved_characters]
    )
    
    # 3. 格式化知识上下文
    knowledge_prompt = self._format_knowledge_context(knowledge_context)
    
    # 4. 构建增强提示词
    enhanced_prompt = f"""
【历史背景知识】
{knowledge_prompt}

---
基于以上历史背景，请创作以下章节。注意：
- 确保历史细节准确（人物、事件、时间）
- 使用符合时代的语言和称谓
- 避免出现时代错误（如明朝出现清朝物品）

{self.original_prompt}
"""
    
    # 5. 生成章节
    content = await self.ai_service.generate(enhanced_prompt)
    
    # 6. 自动验证准确性
    validation = await self.knowledge_service.validate_historical_accuracy(
        content=content,
        dynasty=project.world_time_period
    )
    
    # 7. 如果有问题，尝试自动修复
    if not validation["is_accurate"] and validation["auto_fix_available"]:
        content = await self._auto_fix_historical_issues(
            content, validation["issues"]
        )
    
    return content
```

---

## 6. API设计

### 6.1 新增API端点

```python
# backend/app/api/knowledge.py

@router.get("/knowledge/search")
async def search_knowledge(
    query: str,
    category: str = None,
    time_period: str = None,
    limit: int = 10
) -> List[KnowledgeEntry]:
    """搜索知识库"""

@router.get("/knowledge/figures")
async def search_figures(
    name: str = None,
    dynasty: str = None,
    limit: int = 10
) -> List[HistoricalFigure]:
    """搜索历史人物"""

@router.get("/knowledge/events")
async def search_events(
    keyword: str = None,
    dynasty: str = None,
    year_start: int = None,
    year_end: int = None
) -> List[HistoricalEvent]:
    """搜索历史事件"""

@router.post("/knowledge/validate")
async def validate_content(
    content: str,
    dynasty: str,
    year: int = None
) -> ValidationResult:
    """验证内容历史准确性"""

@router.get("/knowledge/context/{project_id}")
async def get_project_context(
    project_id: str,
    chapter_number: int = None
) -> KnowledgeContext:
    """获取项目相关知识上下文"""
```

### 6.2 MCP工具扩展

```python
# mcp_novel_server.py 新增工具

Tool(
    name="novel_search_knowledge",
    description="搜索知识库获取背景资料",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "category": {"type": "string", "enum": ["历史", "科技", "金融", "医学", "军事"]},
            "time_period": {"type": "string"}
        },
        "required": ["query"]
    }
),

Tool(
    name="novel_search_figure",
    description="搜索历史人物信息",
    inputSchema={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "dynasty": {"type": "string"}
        },
        "required": ["name"]
    }
),

Tool(
    name="novel_validate_history",
    description="验证内容的历史准确性（自动化）",
    inputSchema={
        "type": "object",
        "properties": {
            "content": {"type": "string"},
            "dynasty": {"type": "string"},
            "year": {"type": "integer"}
        },
        "required": ["content", "dynasty"]
    }
)
```

---

## 7. AI驱动实施计划

### 7.1 执行流程 (3-5天)

```
Day 1 (4小时):
├── AI: 生成pgvector Schema + 迁移脚本
├── AI: 生成KnowledgeService框架
└── 人工: 审核Schema设计

Day 2 (6小时):
├── AI: 实现知识检索服务
├── AI: 实现历史上下文获取
├── AI: 生成API端点
└── AI: 自动测试

Day 3 (4小时):
├── AI: 集成到章节生成流程
├── AI: 实现准确性验证
└── AI: 添加MCP工具

Day 4 (4小时):
├── AI: 数据导入脚本
├── AI: 批量嵌入生成
└── 人工: 集成测试

Day 5 (2小时):
├── AI: 文档更新
└── 人工: 最终审核+部署
```

### 7.2 AI Agent任务分配

| 任务 | Agent | 预计时间 |
|------|-------|----------|
| Schema设计 | Kiro | 30分钟 |
| 服务实现 | Claude | 2小时 |
| API开发 | Claude | 1小时 |
| 测试生成 | Claude | 30分钟 |
| 文档更新 | Claude | 30分钟 |

---

## 8. 风险与应对

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| 数据质量不佳 | 中 | 高 | 多源交叉验证、AI辅助清洗 |
| pgvector性能不足 | 低 | 中 | 优化索引参数、分表存储 |
| 嵌入API成本超支 | 中 | 低 | 使用本地模型、批量处理 |
| 知识过时 | 低 | 低 | 定期更新机制 |

---

## 9. 资源需求 (AI驱动模式)

### 9.1 时间
- AI开发: 3-5天
- 人工审核: 0.5天
- **总计: 4-5天** (vs 传统30天)

### 9.2 成本
- API调用 (开发期): $50
- 嵌入生成: $50 (一次性)
- 服务器: $0/月 (复用PostgreSQL)
- **总计: $100 一次性**

---

*最后更新: 2026-01-05*
