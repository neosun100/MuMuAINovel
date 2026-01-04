# 预案04: 情节逻辑验证系统

> 版本: v1.13 | 优先级: 🟡 P1 | **AI开发: 2-3天** | 人工审核: 0.5天

---

## 1. 目标与成功指标

### 1.1 核心目标
- 自动检测情节逻辑漏洞（因果关系、时间线、空间逻辑）
- 检测角色能力边界违规
- 自动生成修复建议
- 构建情节因果图谱

### 1.2 成功指标

| 指标 | 当前 | 目标 | 验证方法 |
|------|------|------|----------|
| 逻辑漏洞检测率 | 40% | 85% | AI评估 |
| 时间线冲突检测 | 50% | 95% | 自动检测 |
| 空间逻辑错误检测 | 30% | 80% | 自动检测 |
| 自动修复建议采纳率 | - | 70% | 统计 |

---

## 2. 核心功能

### 2.1 因果关系检测

```python
class CausalityChecker:
    """因果关系检测器"""
    
    async def check_causality(
        self,
        event: str,
        preceding_events: List[str],
        chapter_context: str
    ) -> Dict:
        """检查事件的因果合理性"""
        
        prompt = f"""分析以下事件的因果关系是否合理：

当前事件: {event}

前置事件:
{chr(10).join(f'- {e}' for e in preceding_events)}

章节上下文:
{chapter_context[:2000]}

返回JSON：
{{
    "is_logical": true/false,
    "confidence": 0.0-1.0,
    "missing_causes": ["缺失的前置条件1", "缺失的前置条件2"],
    "contradictions": ["矛盾点1", "矛盾点2"],
    "suggestions": ["修复建议1", "修复建议2"]
}}
"""
        result = await self.ai.generate(prompt, max_tokens=500)
        return json.loads(result)
```

### 2.2 时间线冲突检测

```python
class TimelineChecker:
    """时间线冲突检测器"""
    
    async def check_timeline(
        self,
        project_id: str,
        chapter_number: int,
        events: List[Dict]
    ) -> Dict:
        """检测时间线冲突"""
        
        # 获取已有时间线
        existing_timeline = await self._get_timeline(project_id)
        
        conflicts = []
        for event in events:
            # 检查时间顺序
            if event.get("time"):
                for existing in existing_timeline:
                    if self._is_time_conflict(event, existing):
                        conflicts.append({
                            "type": "time_order",
                            "event": event["description"],
                            "conflict_with": existing["description"],
                            "issue": f"事件时间顺序冲突"
                        })
            
            # 检查持续时间合理性
            if event.get("duration"):
                if not self._is_duration_reasonable(event):
                    conflicts.append({
                        "type": "duration",
                        "event": event["description"],
                        "issue": "事件持续时间不合理"
                    })
        
        return {
            "has_conflicts": len(conflicts) > 0,
            "conflicts": conflicts,
            "suggestions": await self._generate_fix_suggestions(conflicts)
        }
```

### 2.3 空间逻辑检测

```python
class SpatialChecker:
    """空间逻辑检测器"""
    
    async def check_spatial_logic(
        self,
        chapter_content: str,
        character_locations: Dict[str, str]
    ) -> Dict:
        """检测空间逻辑错误"""
        
        prompt = f"""检测以下内容中的空间逻辑错误：

内容:
{chapter_content[:3000]}

角色当前位置:
{json.dumps(character_locations, ensure_ascii=False)}

检查：
1. 角色是否能在短时间内到达新位置
2. 角色是否同时出现在两个地方
3. 场景描述是否与位置一致

返回JSON：
{{
    "has_errors": true/false,
    "errors": [
        {{
            "type": "teleportation/simultaneous/inconsistent",
            "character": "角色名",
            "description": "错误描述",
            "location1": "位置1",
            "location2": "位置2"
        }}
    ],
    "suggestions": ["修复建议"]
}}
"""
        result = await self.ai.generate(prompt, max_tokens=500)
        return json.loads(result)
```

### 2.4 能力边界检测

```python
class AbilityChecker:
    """角色能力边界检测器"""
    
    async def check_ability_bounds(
        self,
        character_id: str,
        action: str,
        context: str
    ) -> Dict:
        """检测角色行为是否超出能力范围"""
        
        character = await self._get_character(character_id)
        
        prompt = f"""检测角色行为是否超出能力范围：

角色: {character.name}
能力描述: {character.abilities}
背景: {character.background}

待检测行为: {action}
上下文: {context}

返回JSON：
{{
    "is_within_bounds": true/false,
    "confidence": 0.0-1.0,
    "issue": "如果超出范围，说明原因",
    "suggestion": "修复建议"
}}
"""
        result = await self.ai.generate(prompt, max_tokens=300)
        return json.loads(result)
```

---

## 3. 情节因果图谱

### 3.1 数据模型

```python
class PlotCausalGraph(Base):
    """情节因果图谱"""
    __tablename__ = "plot_causal_graphs"
    
    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id"))
    
    # 节点（事件）
    event_id = Column(String(36))
    event_description = Column(Text)
    event_chapter = Column(Integer)
    event_type = Column(String(50))  # action/decision/revelation/consequence
    
    # 边（因果关系）
    causes = Column(JSON)  # [{"event_id": "xxx", "relation": "直接导致/间接影响"}]
    effects = Column(JSON)  # [{"event_id": "xxx", "relation": "..."}]
    
    # 重要性
    importance = Column(Float, default=0.5)
    is_key_plot_point = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=func.now())
```

### 3.2 图谱构建服务

```python
class PlotGraphService:
    """情节图谱服务"""
    
    async def build_causal_graph(
        self,
        project_id: str,
        chapter_range: Tuple[int, int] = None
    ) -> Dict:
        """构建情节因果图谱"""
        
        # 获取章节内容
        chapters = await self._get_chapters(project_id, chapter_range)
        
        # AI分析每章的关键事件和因果关系
        all_events = []
        for chapter in chapters:
            events = await self._extract_events(chapter)
            all_events.extend(events)
        
        # 构建因果关系
        for event in all_events:
            causes = await self._find_causes(event, all_events)
            effects = await self._find_effects(event, all_events)
            
            await self._save_graph_node(
                project_id=project_id,
                event=event,
                causes=causes,
                effects=effects
            )
        
        return {
            "total_events": len(all_events),
            "key_plot_points": len([e for e in all_events if e["is_key"]]),
            "graph_built": True
        }
    
    async def detect_plot_holes(
        self,
        project_id: str
    ) -> List[Dict]:
        """检测情节漏洞"""
        
        graph = await self._load_graph(project_id)
        holes = []
        
        # 1. 检测悬空事件（无因无果）
        for node in graph.nodes:
            if not node.causes and not node.effects and node.importance > 0.5:
                holes.append({
                    "type": "orphan_event",
                    "event": node.event_description,
                    "chapter": node.event_chapter,
                    "suggestion": "为此事件添加前因或后果"
                })
        
        # 2. 检测断裂的因果链
        for node in graph.nodes:
            if node.is_key_plot_point and not node.effects:
                holes.append({
                    "type": "broken_chain",
                    "event": node.event_description,
                    "chapter": node.event_chapter,
                    "suggestion": "关键情节点缺少后续发展"
                })
        
        return holes
```

---

## 4. 集成到生成流程

```python
async def generate_chapter_with_logic_check(
    self,
    chapter: Chapter,
    project: Project
) -> str:
    """带逻辑检查的章节生成"""
    
    # 1. 生成章节
    content = await self.generate_chapter(chapter, project)
    
    # 2. 提取事件
    events = await self.logic_service.extract_events(content)
    
    # 3. 检查因果关系
    for event in events:
        causality = await self.causality_checker.check_causality(
            event=event["description"],
            preceding_events=await self._get_preceding_events(chapter),
            chapter_context=content
        )
        if not causality["is_logical"]:
            # 自动修复
            content = await self._fix_causality_issue(
                content, event, causality
            )
    
    # 4. 检查时间线
    timeline_check = await self.timeline_checker.check_timeline(
        project_id=project.id,
        chapter_number=chapter.chapter_number,
        events=events
    )
    if timeline_check["has_conflicts"]:
        content = await self._fix_timeline_issues(
            content, timeline_check["conflicts"]
        )
    
    # 5. 检查空间逻辑
    spatial_check = await self.spatial_checker.check_spatial_logic(
        chapter_content=content,
        character_locations=await self._get_character_locations(chapter)
    )
    if spatial_check["has_errors"]:
        content = await self._fix_spatial_issues(
            content, spatial_check["errors"]
        )
    
    # 6. 更新因果图谱
    await self.plot_graph_service.update_graph(
        project_id=project.id,
        chapter_number=chapter.chapter_number,
        events=events
    )
    
    return content
```

---

## 5. AI驱动实施计划 (2-3天)

```
Day 1 (5小时):
├── AI: 实现因果关系检测器
├── AI: 实现时间线冲突检测
├── AI: 实现空间逻辑检测
└── 人工: 审核设计

Day 2 (5小时):
├── AI: 实现能力边界检测
├── AI: 实现情节图谱服务
├── AI: 集成到生成流程
└── AI: 自动测试

Day 3 (3小时):
├── AI: 添加MCP工具
├── AI: 更新文档
└── 人工: 最终审核
```

---

## 6. MCP工具

```python
Tool(
    name="novel_check_logic",
    description="检查章节的情节逻辑",
    inputSchema={
        "type": "object",
        "properties": {
            "chapter_id": {"type": "string"},
            "check_types": {
                "type": "array",
                "items": {"type": "string", "enum": ["causality", "timeline", "spatial", "ability"]}
            }
        },
        "required": ["chapter_id"]
    }
),

Tool(
    name="novel_get_plot_graph",
    description="获取情节因果图谱",
    inputSchema={
        "type": "object",
        "properties": {
            "project_id": {"type": "string"},
            "chapter_range": {"type": "array", "items": {"type": "integer"}}
        },
        "required": ["project_id"]
    }
),

Tool(
    name="novel_detect_plot_holes",
    description="检测情节漏洞",
    inputSchema={
        "type": "object",
        "properties": {
            "project_id": {"type": "string"}
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
- **总计: 3天 + $30**

---

*最后更新: 2026-01-05*
