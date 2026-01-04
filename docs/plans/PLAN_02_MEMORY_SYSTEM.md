# 预案02: 全局记忆系统升级

> 版本: v1.11 | 优先级: 🔴 P0 | **AI开发: 2-3天** | 人工审核: 0.5天

---

## 1. 目标与成功指标

### 1.1 核心目标
- 实现跨100章的**长期记忆存储**和检索
- 追踪角色状态变化（位置、情绪、关系）
- 追踪物品/道具的流转
- 追踪未解决的冲突和伏笔

### 1.2 成功指标

| 指标 | 当前 | 目标 | 验证方法 |
|------|------|------|----------|
| 记忆检索准确率 | 70% | 95% | 自动化测试 |
| 跨章节一致性 | 75% | 95% | AI评估 |
| 记忆检索延迟 | 2s | <500ms | 性能测试 |
| 伏笔回收率 | 60% | 90% | 统计分析 |

---

## 2. 现状分析

### 2.1 现有系统

项目已有基于ChromaDB的记忆系统：
- `memory_service.py`: 向量记忆服务
- `StoryMemory`模型: 存储故事片段
- `PlotAnalysis`模型: 剧情分析

### 2.2 现有问题

1. **记忆衰减不智能**: 简单的时间衰减，未考虑重要性
2. **状态追踪缺失**: 无法追踪角色位置、物品流转
3. **伏笔管理分散**: 伏笔与记忆系统未深度整合
4. **检索效率低**: 大量记忆时检索变慢

---

## 3. 方案对比

### 方案A: 增强现有ChromaDB (推荐 ⭐)

**原理**: 在现有ChromaDB基础上增强，添加状态追踪层

```
优点:
✅ 复用现有代码，改动最小
✅ 团队已熟悉ChromaDB
✅ 无需新增服务
✅ 开发周期短

缺点:
❌ ChromaDB生产稳定性一般
❌ 复杂查询能力有限

适用场景: 快速迭代，中等规模
```

### 方案B: 迁移到pgvector统一存储

**原理**: 将记忆系统迁移到PostgreSQL+pgvector

```
优点:
✅ 与知识库统一存储
✅ 事务一致性
✅ 复杂查询支持
✅ 运维简单

缺点:
❌ 需要迁移现有数据
❌ 改动较大

适用场景: 长期稳定运行
```

### 方案C: 混合架构

**原理**: PostgreSQL存储结构化状态，ChromaDB存储向量

```
优点:
✅ 各取所长
✅ 灵活性高

缺点:
❌ 架构复杂
❌ 数据同步问题

适用场景: 大规模复杂需求
```

---

## 4. 推荐方案: 增强现有系统 (方案A)

### 4.1 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                      增强记忆系统架构                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    记忆管理器                            │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐             │   │
│  │  │ 事件记忆  │ │ 状态追踪  │ │ 伏笔管理  │             │   │
│  │  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘             │   │
│  └────────┼─────────────┼─────────────┼─────────────────────┘   │
│           │             │             │                         │
│           ▼             ▼             ▼                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   存储层                                 │   │
│  │  ┌───────────────┐  ┌───────────────┐                   │   │
│  │  │   ChromaDB    │  │  PostgreSQL   │                   │   │
│  │  │  (向量记忆)   │  │  (状态数据)   │                   │   │
│  │  └───────────────┘  └───────────────┘                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 新增数据模型

```python
# backend/app/models/character_state.py

class CharacterState(Base):
    """角色状态追踪表"""
    __tablename__ = "character_states"
    
    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id"))
    character_id = Column(String(36), ForeignKey("characters.id"))
    chapter_id = Column(String(36), ForeignKey("chapters.id"))
    chapter_number = Column(Integer, index=True)
    
    # 位置状态
    location = Column(String(200))
    location_detail = Column(Text)
    
    # 情绪状态
    emotion = Column(String(50))  # 喜/怒/哀/惧/惊/思
    emotion_intensity = Column(Float)  # 0-1
    emotion_cause = Column(Text)
    
    # 关系变化
    relationship_changes = Column(JSON)  # {"角色B": {"变化": "敌对→中立", "原因": "..."}}
    
    # 能力/属性变化
    ability_changes = Column(JSON)  # {"武力": "+10", "智力": "-5"}
    
    # 持有物品
    inventory = Column(JSON)  # ["物品1", "物品2"]
    inventory_changes = Column(JSON)  # {"获得": ["物品A"], "失去": ["物品B"]}
    
    created_at = Column(DateTime, default=func.now())


class ItemTracking(Base):
    """物品追踪表"""
    __tablename__ = "item_tracking"
    
    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id"))
    item_name = Column(String(200), index=True)
    item_type = Column(String(50))  # 武器/道具/信物/文件
    description = Column(Text)
    
    # 当前持有者
    current_holder = Column(String(36), ForeignKey("characters.id"))
    
    # 流转历史
    transfer_history = Column(JSON)  # [{"from": "A", "to": "B", "chapter": 5, "reason": "..."}]
    
    # 重要性
    importance = Column(Float, default=0.5)
    is_plot_device = Column(Boolean, default=False)  # 是否为关键道具
    
    created_at = Column(DateTime, default=func.now())


class UnresolvedConflict(Base):
    """未解决冲突追踪表"""
    __tablename__ = "unresolved_conflicts"
    
    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id"))
    
    # 冲突信息
    conflict_type = Column(String(50))  # 人物冲突/势力冲突/内心冲突
    description = Column(Text)
    parties = Column(JSON)  # ["角色A", "角色B"] 或 ["势力A", "势力B"]
    
    # 状态
    status = Column(String(20), default="active")  # active/resolved/abandoned
    introduced_chapter = Column(Integer)
    resolved_chapter = Column(Integer, nullable=True)
    resolution = Column(Text, nullable=True)
    
    # 重要性
    importance = Column(Float, default=0.5)
    
    created_at = Column(DateTime, default=func.now())
```

### 4.3 增强记忆服务

```python
# backend/app/services/enhanced_memory_service.py

class EnhancedMemoryService:
    """增强记忆服务 - 整合事件记忆、状态追踪、伏笔管理"""
    
    def __init__(self, db_session, chroma_client):
        self.db = db_session
        self.memory_service = MemoryService()  # 现有服务
        
    async def record_chapter_memory(
        self,
        chapter: Chapter,
        content: str
    ) -> Dict:
        """章节生成后自动记录记忆（全自动化）"""
        
        # 1. AI分析章节内容
        analysis = await self._analyze_chapter_content(content)
        
        # 2. 记录事件记忆 (复用现有)
        for event in analysis["events"]:
            await self.memory_service.add_memory(
                project_id=chapter.project_id,
                chapter_id=chapter.id,
                memory_type="plot_point",
                content=event["description"],
                importance=event["importance"]
            )
        
        # 3. 更新角色状态
        for char_state in analysis["character_states"]:
            await self._update_character_state(
                chapter=chapter,
                character_name=char_state["name"],
                state=char_state
            )
        
        # 4. 追踪物品流转
        for item_change in analysis["item_changes"]:
            await self._track_item(
                project_id=chapter.project_id,
                chapter_number=chapter.chapter_number,
                item=item_change
            )
        
        # 5. 记录新冲突/解决旧冲突
        for conflict in analysis["conflicts"]:
            if conflict["status"] == "new":
                await self._add_conflict(chapter, conflict)
            elif conflict["status"] == "resolved":
                await self._resolve_conflict(chapter, conflict)
        
        # 6. 更新伏笔状态
        for foreshadow in analysis["foreshadows"]:
            await self._update_foreshadow(chapter, foreshadow)
        
        return {"status": "success", "analysis": analysis}
    
    async def get_chapter_context(
        self,
        project_id: str,
        chapter_number: int,
        involved_characters: List[str]
    ) -> Dict:
        """获取章节生成所需的记忆上下文"""
        
        context = {
            # 1. 相关事件记忆 (语义检索)
            "relevant_memories": await self.memory_service.search_memories(
                project_id=project_id,
                query=f"第{chapter_number}章相关情节",
                top_k=10
            ),
            
            # 2. 涉及角色的当前状态
            "character_states": await self._get_character_states(
                project_id=project_id,
                character_names=involved_characters,
                as_of_chapter=chapter_number - 1
            ),
            
            # 3. 活跃物品
            "active_items": await self._get_active_items(
                project_id=project_id,
                holders=involved_characters
            ),
            
            # 4. 未解决冲突
            "unresolved_conflicts": await self._get_unresolved_conflicts(
                project_id=project_id,
                as_of_chapter=chapter_number - 1
            ),
            
            # 5. 待回收伏笔
            "pending_foreshadows": await self._get_pending_foreshadows(
                project_id=project_id,
                chapter_number=chapter_number
            )
        }
        
        return context
    
    async def _analyze_chapter_content(self, content: str) -> Dict:
        """AI分析章节内容，提取结构化信息"""
        
        prompt = f"""分析以下章节内容，提取结构化信息。返回JSON格式：

{{
    "events": [
        {{"description": "事件描述", "importance": 0.8, "type": "plot_point"}}
    ],
    "character_states": [
        {{
            "name": "角色名",
            "location": "当前位置",
            "emotion": "情绪",
            "emotion_intensity": 0.7,
            "relationship_changes": {{"角色B": "关系变化描述"}},
            "inventory_changes": {{"获得": [], "失去": []}}
        }}
    ],
    "item_changes": [
        {{"item": "物品名", "from": "角色A", "to": "角色B", "reason": "原因"}}
    ],
    "conflicts": [
        {{"description": "冲突描述", "parties": ["A", "B"], "status": "new/resolved"}}
    ],
    "foreshadows": [
        {{"content": "伏笔内容", "status": "planted/resolved"}}
    ]
}}

章节内容：
{content[:5000]}
"""
        
        result = await self.ai_service.generate(prompt, max_tokens=2000)
        return json.loads(result)
```

### 4.4 智能记忆衰减

```python
class MemoryDecayStrategy:
    """智能记忆衰减策略"""
    
    @staticmethod
    def calculate_relevance(
        memory: StoryMemory,
        current_chapter: int,
        query_context: str = None
    ) -> float:
        """计算记忆相关性分数"""
        
        # 基础分数 = 重要性
        score = memory.importance_score
        
        # 时间衰减 (章节距离)
        chapter_distance = current_chapter - memory.story_timeline
        if chapter_distance <= 5:
            time_factor = 1.0  # 最近5章不衰减
        elif chapter_distance <= 20:
            time_factor = 0.8  # 5-20章轻微衰减
        elif chapter_distance <= 50:
            time_factor = 0.5  # 20-50章中等衰减
        else:
            time_factor = 0.3  # 50章以上大幅衰减
        
        # 重要性加成 (重要事件不衰减)
        if memory.importance_score >= 0.9:
            time_factor = max(time_factor, 0.8)  # 重要事件最低保持0.8
        
        # 伏笔加成 (未回收伏笔不衰减)
        if memory.is_foreshadow == 1:  # 已埋下未回收
            time_factor = 1.0
        
        # 语义相关性 (如果有查询上下文)
        semantic_factor = 1.0
        if query_context:
            # 计算语义相似度
            semantic_factor = calculate_similarity(memory.content, query_context)
        
        return score * time_factor * semantic_factor
```

---

## 5. AI驱动实施计划 (2-3天)

```
Day 1 (5小时):
├── AI: 生成数据模型 (CharacterState, ItemTracking, UnresolvedConflict)
├── AI: 生成迁移脚本
├── AI: 实现状态追踪服务
└── 人工: 审核设计

Day 2 (5小时):
├── AI: 实现EnhancedMemoryService
├── AI: 实现AI内容分析
├── AI: 实现智能衰减策略
└── AI: 集成到章节生成

Day 3 (3小时):
├── AI: 生成测试用例
├── AI: 自动测试+修复
├── AI: 更新文档
└── 人工: 最终审核
```

---

## 6. MCP工具扩展

```python
Tool(
    name="novel_get_character_state",
    description="获取角色当前状态（位置、情绪、关系）",
    inputSchema={
        "type": "object",
        "properties": {
            "project_id": {"type": "string"},
            "character_name": {"type": "string"},
            "as_of_chapter": {"type": "integer"}
        },
        "required": ["project_id", "character_name"]
    }
),

Tool(
    name="novel_track_item",
    description="追踪物品流转历史",
    inputSchema={
        "type": "object",
        "properties": {
            "project_id": {"type": "string"},
            "item_name": {"type": "string"}
        },
        "required": ["project_id", "item_name"]
    }
),

Tool(
    name="novel_list_conflicts",
    description="列出未解决的冲突",
    inputSchema={
        "type": "object",
        "properties": {
            "project_id": {"type": "string"},
            "status": {"type": "string", "enum": ["active", "resolved", "all"]}
        },
        "required": ["project_id"]
    }
)
```

---

## 7. 资源需求 (AI驱动模式)

- AI开发: 2-3天
- 人工审核: 0.5天
- API成本: $30
- 服务器: 无额外需求
- **总计: 3天 + $30**

---

*最后更新: 2026-01-05*
