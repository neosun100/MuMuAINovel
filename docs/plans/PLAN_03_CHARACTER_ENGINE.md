# 预案03: 角色一致性引擎

> 版本: v1.12 | 优先级: 🔴 P0 | **AI开发: 2-4天** | 人工审核: 0.5天

---

## 1. 目标与成功指标

### 1.1 核心目标
- 建立角色性格模型，确保行为一致性 **80%→95%**
- 实现对话风格一致性检测
- 自动检测并修复角色行为偏差
- 追踪角色成长轨迹

### 1.2 成功指标

| 指标 | 当前 | 目标 | 验证方法 |
|------|------|------|----------|
| 角色行为一致性 | 80% | 95% | AI评估 |
| 对话风格一致性 | 75% | 90% | 风格分析 |
| 性格偏差检测率 | 50% | 90% | 自动检测 |
| 自动修复成功率 | - | 80% | 统计 |

---

## 2. 方案对比

### 方案A: 性格向量模型 (推荐 ⭐)

**原理**: 为每个角色构建多维性格向量，生成时作为约束

```
优点:
✅ 数学化表示，可量化比较
✅ 易于检测偏差
✅ 可自动修复
✅ 与现有系统兼容

缺点:
❌ 需要设计合适的维度
❌ 初始化需要AI分析

适用场景: 大规模角色管理
```

### 方案B: 角色档案+Few-shot

**原理**: 为每个角色维护详细档案，生成时提供示例

```
优点:
✅ 实现简单
✅ 灵活性高
✅ 无需复杂模型

缺点:
❌ 上下文消耗大
❌ 难以量化检测

适用场景: 角色数量较少
```

### 方案C: 微调专属模型

**原理**: 为重要角色微调专属语言模型

```
优点:
✅ 一致性最高
✅ 生成质量好

缺点:
❌ 成本极高
❌ 不适合大量角色
❌ 维护困难

适用场景: 极少数核心角色
```

---

## 3. 推荐方案: 性格向量模型 (方案A)

### 3.1 性格维度设计

基于心理学模型，设计10维性格向量：

```python
# 性格维度定义
PERSONALITY_DIMENSIONS = {
    # 大五人格 (Big Five)
    "openness": "开放性 (0=保守, 1=开放)",
    "conscientiousness": "尽责性 (0=随性, 1=严谨)",
    "extraversion": "外向性 (0=内向, 1=外向)",
    "agreeableness": "宜人性 (0=对抗, 1=合作)",
    "neuroticism": "神经质 (0=稳定, 1=敏感)",
    
    # 扩展维度
    "intelligence": "智力表现 (0=普通, 1=聪慧)",
    "morality": "道德倾向 (0=邪恶, 1=正义)",
    "courage": "勇气 (0=怯懦, 1=勇敢)",
    "humor": "幽默感 (0=严肃, 1=幽默)",
    "ambition": "野心 (0=安于现状, 1=野心勃勃)"
}
```

### 3.2 数据模型

```python
# backend/app/models/character_personality.py

class CharacterPersonality(Base):
    """角色性格模型"""
    __tablename__ = "character_personalities"
    
    id = Column(String(36), primary_key=True)
    character_id = Column(String(36), ForeignKey("characters.id"), unique=True)
    project_id = Column(String(36), ForeignKey("projects.id"))
    
    # 性格向量 (10维)
    openness = Column(Float, default=0.5)
    conscientiousness = Column(Float, default=0.5)
    extraversion = Column(Float, default=0.5)
    agreeableness = Column(Float, default=0.5)
    neuroticism = Column(Float, default=0.5)
    intelligence = Column(Float, default=0.5)
    morality = Column(Float, default=0.5)
    courage = Column(Float, default=0.5)
    humor = Column(Float, default=0.5)
    ambition = Column(Float, default=0.5)
    
    # 对话风格
    speech_style = Column(JSON)  # {"正式度": 0.7, "用词复杂度": 0.6, "口头禅": ["..."], "语气词": ["..."]}
    
    # 行为模式
    behavior_patterns = Column(JSON)  # {"压力下": "冷静分析", "面对敌人": "直接对抗", ...}
    
    # 禁忌行为 (绝对不会做的事)
    forbidden_behaviors = Column(JSON)  # ["背叛朋友", "伤害无辜", ...]
    
    # 典型行为 (经常做的事)
    typical_behaviors = Column(JSON)  # ["保护弱者", "追求真相", ...]
    
    # 成长轨迹
    growth_history = Column(JSON)  # [{"chapter": 10, "dimension": "courage", "change": +0.1, "reason": "..."}]
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def to_vector(self) -> List[float]:
        """转换为向量"""
        return [
            self.openness, self.conscientiousness, self.extraversion,
            self.agreeableness, self.neuroticism, self.intelligence,
            self.morality, self.courage, self.humor, self.ambition
        ]
    
    def similarity(self, other: 'CharacterPersonality') -> float:
        """计算性格相似度"""
        v1 = np.array(self.to_vector())
        v2 = np.array(other.to_vector())
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
```

### 3.3 角色一致性服务

```python
# backend/app/services/character_consistency_service.py

class CharacterConsistencyService:
    """角色一致性引擎"""
    
    def __init__(self, db_session, ai_service):
        self.db = db_session
        self.ai = ai_service
    
    async def initialize_personality(
        self,
        character: Character
    ) -> CharacterPersonality:
        """从角色描述初始化性格模型（自动化）"""
        
        prompt = f"""分析以下角色，生成性格向量（每个维度0-1）：

角色名: {character.name}
角色类型: {character.role_type}
性格描述: {character.personality}
背景故事: {character.background}

返回JSON格式：
{{
    "openness": 0.7,
    "conscientiousness": 0.8,
    "extraversion": 0.4,
    "agreeableness": 0.6,
    "neuroticism": 0.3,
    "intelligence": 0.8,
    "morality": 0.9,
    "courage": 0.7,
    "humor": 0.3,
    "ambition": 0.6,
    "speech_style": {{
        "正式度": 0.7,
        "用词复杂度": 0.6,
        "口头禅": ["确实", "有意思"],
        "语气词": ["嗯", "啊"]
    }},
    "behavior_patterns": {{
        "压力下": "冷静分析",
        "面对敌人": "智取为主",
        "面对朋友": "真诚相待"
    }},
    "forbidden_behaviors": ["背叛朋友", "伤害无辜"],
    "typical_behaviors": ["保护弱者", "追求真相"]
}}
"""
        
        result = await self.ai.generate(prompt, max_tokens=1000)
        data = json.loads(result)
        
        personality = CharacterPersonality(
            character_id=character.id,
            project_id=character.project_id,
            **data
        )
        
        self.db.add(personality)
        await self.db.commit()
        
        return personality
    
    async def check_behavior_consistency(
        self,
        character_id: str,
        behavior_description: str,
        context: str = None
    ) -> Dict:
        """检查行为是否符合角色性格（自动化）"""
        
        personality = await self._get_personality(character_id)
        character = await self._get_character(character_id)
        
        # 1. 检查是否为禁忌行为
        for forbidden in personality.forbidden_behaviors or []:
            if await self._is_similar_behavior(behavior_description, forbidden):
                return {
                    "is_consistent": False,
                    "confidence": 0.95,
                    "issue": f"行为违反角色禁忌: {forbidden}",
                    "suggestion": f"修改为符合{character.name}性格的行为"
                }
        
        # 2. AI评估行为一致性
        prompt = f"""评估以下行为是否符合角色性格：

角色: {character.name}
性格向量: {personality.to_vector()}
性格描述: {character.personality}
行为模式: {personality.behavior_patterns}

待评估行为: {behavior_description}
上下文: {context or '无'}

返回JSON：
{{
    "is_consistent": true/false,
    "confidence": 0.0-1.0,
    "analysis": "分析说明",
    "suggestion": "如果不一致，建议如何修改"
}}
"""
        
        result = await self.ai.generate(prompt, max_tokens=500)
        return json.loads(result)
    
    async def check_dialogue_consistency(
        self,
        character_id: str,
        dialogue: str
    ) -> Dict:
        """检查对话是否符合角色说话风格（自动化）"""
        
        personality = await self._get_personality(character_id)
        character = await self._get_character(character_id)
        
        prompt = f"""评估以下对话是否符合角色说话风格：

角色: {character.name}
说话风格: {personality.speech_style}
性格: {character.personality}

待评估对话: "{dialogue}"

返回JSON：
{{
    "is_consistent": true/false,
    "confidence": 0.0-1.0,
    "issues": ["问题1", "问题2"],
    "corrected_dialogue": "修正后的对话（如果需要）"
}}
"""
        
        result = await self.ai.generate(prompt, max_tokens=500)
        return json.loads(result)
    
    async def auto_fix_inconsistency(
        self,
        content: str,
        character_id: str,
        issues: List[Dict]
    ) -> str:
        """自动修复不一致内容"""
        
        personality = await self._get_personality(character_id)
        character = await self._get_character(character_id)
        
        prompt = f"""修复以下内容中的角色不一致问题：

角色: {character.name}
性格: {character.personality}
性格向量: {personality.to_vector()}
行为模式: {personality.behavior_patterns}
说话风格: {personality.speech_style}

原内容:
{content}

需要修复的问题:
{json.dumps(issues, ensure_ascii=False)}

请输出修复后的完整内容，保持故事连贯性：
"""
        
        fixed_content = await self.ai.generate(prompt, max_tokens=len(content) * 2)
        return fixed_content
    
    async def record_character_growth(
        self,
        character_id: str,
        chapter_number: int,
        dimension: str,
        change: float,
        reason: str
    ):
        """记录角色成长（性格变化）"""
        
        personality = await self._get_personality(character_id)
        
        # 更新性格维度
        current_value = getattr(personality, dimension)
        new_value = max(0, min(1, current_value + change))
        setattr(personality, dimension, new_value)
        
        # 记录成长历史
        growth_history = personality.growth_history or []
        growth_history.append({
            "chapter": chapter_number,
            "dimension": dimension,
            "old_value": current_value,
            "new_value": new_value,
            "change": change,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        personality.growth_history = growth_history
        
        await self.db.commit()
```

### 3.4 集成到章节生成

```python
# 修改章节生成流程

async def generate_chapter_with_consistency(
    self,
    chapter: Chapter,
    project: Project
) -> str:
    """带角色一致性检查的章节生成"""
    
    # 1. 获取涉及角色的性格约束
    character_constraints = []
    for char in chapter.involved_characters:
        personality = await self.consistency_service.get_personality(char.id)
        if personality:
            character_constraints.append({
                "name": char.name,
                "personality_vector": personality.to_vector(),
                "speech_style": personality.speech_style,
                "behavior_patterns": personality.behavior_patterns,
                "forbidden_behaviors": personality.forbidden_behaviors
            })
    
    # 2. 构建带约束的提示词
    constraint_prompt = self._format_character_constraints(character_constraints)
    
    enhanced_prompt = f"""
【角色性格约束】
{constraint_prompt}

请严格按照以上角色性格生成内容，确保：
1. 每个角色的行为符合其性格向量
2. 对话风格符合角色说话习惯
3. 不出现角色禁忌行为

{self.original_prompt}
"""
    
    # 3. 生成章节
    content = await self.ai_service.generate(enhanced_prompt)
    
    # 4. 自动检查一致性
    for char in chapter.involved_characters:
        # 提取该角色的行为和对话
        char_content = self._extract_character_content(content, char.name)
        
        # 检查行为一致性
        behavior_check = await self.consistency_service.check_behavior_consistency(
            character_id=char.id,
            behavior_description=char_content["behaviors"],
            context=chapter.summary
        )
        
        # 检查对话一致性
        for dialogue in char_content["dialogues"]:
            dialogue_check = await self.consistency_service.check_dialogue_consistency(
                character_id=char.id,
                dialogue=dialogue
            )
            
            # 如果不一致，自动修复
            if not dialogue_check["is_consistent"]:
                content = content.replace(
                    dialogue,
                    dialogue_check["corrected_dialogue"]
                )
    
    return content
```

---

## 4. AI驱动实施计划 (2-4天)

```
Day 1 (5小时):
├── AI: 设计性格维度体系
├── AI: 生成CharacterPersonality模型
├── AI: 生成迁移脚本
└── 人工: 审核设计

Day 2 (5小时):
├── AI: 实现性格初始化服务
├── AI: 实现一致性检测服务
├── AI: 实现对话风格检测
└── AI: 自动测试

Day 3 (4小时):
├── AI: 实现自动修复功能
├── AI: 集成到生成流程
├── AI: 添加MCP工具
└── AI: 为现有角色批量生成性格

Day 4 (2小时):
├── AI: 更新文档
└── 人工: 最终审核+部署
```

---

## 5. MCP工具扩展

```python
Tool(
    name="novel_get_character_personality",
    description="获取角色性格模型",
    inputSchema={
        "type": "object",
        "properties": {
            "character_id": {"type": "string"}
        },
        "required": ["character_id"]
    }
),

Tool(
    name="novel_check_consistency",
    description="检查内容的角色一致性",
    inputSchema={
        "type": "object",
        "properties": {
            "content": {"type": "string"},
            "character_ids": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["content", "character_ids"]
    }
),

Tool(
    name="novel_fix_inconsistency",
    description="自动修复角色不一致问题",
    inputSchema={
        "type": "object",
        "properties": {
            "content": {"type": "string"},
            "character_id": {"type": "string"},
            "issues": {"type": "array"}
        },
        "required": ["content", "character_id", "issues"]
    }
)
```

---

## 6. 资源需求 (AI驱动模式)

- AI开发: 2-4天
- 人工审核: 0.5天
- API成本: $40
- 服务器: 无额外需求
- **总计: 3-4天 + $40**

---

*最后更新: 2026-01-05*
