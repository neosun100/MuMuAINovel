# 预案06: 多语言支持

> 版本: v1.26 | 优先级: 🟢 P2 | **AI开发: 2-3天** | 人工审核: 0.5天

---

## 1. 目标与成功指标

### 1.1 核心目标
- 支持多语言小说创作（中/英/日/韩）
- 实现高质量文学翻译
- 文化本地化适配

### 1.2 成功指标

| 指标 | 当前 | 目标 |
|------|------|------|
| 支持语言数 | 1 | 4+ |
| 翻译质量评分 | - | 4.0/5.0 |
| 文化适配准确率 | - | 85% |

---

## 2. 支持语言

| 语言 | 代码 | 优先级 | 特殊处理 |
|------|------|--------|----------|
| 简体中文 | zh-CN | 已支持 | - |
| 英语 | en | 高 | 文化转换 |
| 日语 | ja | 中 | 敬语系统 |
| 韩语 | ko | 中 | 敬语系统 |
| 繁体中文 | zh-TW | 低 | 用词转换 |

---

## 3. 技术实现

### 3.1 多语言生成服务

```python
class MultilingualService:
    """多语言生成服务"""
    
    LANGUAGE_CONFIGS = {
        "zh-CN": {
            "name": "简体中文",
            "prompt_template": "请用简体中文创作...",
            "style_guide": "现代白话文，流畅自然"
        },
        "en": {
            "name": "English",
            "prompt_template": "Please write in English...",
            "style_guide": "Modern literary English, engaging narrative"
        },
        "ja": {
            "name": "日本語",
            "prompt_template": "日本語で書いてください...",
            "style_guide": "現代日本語、敬語を適切に使用"
        },
        "ko": {
            "name": "한국어",
            "prompt_template": "한국어로 작성해 주세요...",
            "style_guide": "현대 한국어, 적절한 존댓말 사용"
        }
    }
    
    async def generate_in_language(
        self,
        content_prompt: str,
        target_language: str,
        style: str = None
    ) -> str:
        """指定语言生成内容"""
        
        config = self.LANGUAGE_CONFIGS[target_language]
        
        prompt = f"""
{config['prompt_template']}

【风格要求】
{style or config['style_guide']}

【内容要求】
{content_prompt}
"""
        return await self.ai.generate(prompt)
    
    async def translate_novel(
        self,
        content: str,
        source_lang: str,
        target_lang: str,
        preserve_style: bool = True
    ) -> str:
        """文学翻译"""
        
        prompt = f"""将以下{self.LANGUAGE_CONFIGS[source_lang]['name']}小说内容翻译为{self.LANGUAGE_CONFIGS[target_lang]['name']}：

【翻译要求】
1. 保持文学性和可读性
2. 适当进行文化本地化
3. 保留原文的情感和氛围
4. 人名地名采用音译+注释
5. {"保持原文写作风格" if preserve_style else "适应目标语言习惯"}

【原文】
{content}

【译文】
"""
        return await self.ai.generate(prompt, max_tokens=len(content) * 2)
```

### 3.2 文化适配服务

```python
class CulturalAdaptationService:
    """文化适配服务"""
    
    async def adapt_content(
        self,
        content: str,
        source_culture: str,
        target_culture: str
    ) -> str:
        """文化适配"""
        
        prompt = f"""对以下内容进行文化适配，从{source_culture}文化转换为{target_culture}文化：

【适配要求】
1. 替换文化特定的比喻和典故
2. 调整不适合目标文化的内容
3. 保持故事核心不变
4. 标注重大改动

【原内容】
{content}

【适配后】
"""
        return await self.ai.generate(prompt)
    
    async def check_cultural_sensitivity(
        self,
        content: str,
        target_culture: str
    ) -> Dict:
        """检查文化敏感性"""
        
        prompt = f"""检查以下内容在{target_culture}文化中是否存在敏感问题：

【内容】
{content[:3000]}

返回JSON：
{{
    "has_issues": true/false,
    "issues": [
        {{"content": "问题内容", "reason": "原因", "suggestion": "建议"}}
    ]
}}
"""
        result = await self.ai.generate(prompt, max_tokens=500)
        return json.loads(result)
```

---

## 4. 数据模型

```python
class ProjectTranslation(Base):
    """项目翻译表"""
    __tablename__ = "project_translations"
    
    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id"))
    language = Column(String(10))  # en/ja/ko
    
    # 翻译后的项目信息
    title = Column(String(500))
    description = Column(Text)
    
    # 翻译状态
    status = Column(String(20))  # pending/in_progress/completed
    progress = Column(Float, default=0)  # 0-1
    
    created_at = Column(DateTime, default=func.now())


class ChapterTranslation(Base):
    """章节翻译表"""
    __tablename__ = "chapter_translations"
    
    id = Column(String(36), primary_key=True)
    chapter_id = Column(String(36), ForeignKey("chapters.id"))
    language = Column(String(10))
    
    title = Column(String(500))
    content = Column(Text)
    
    # 翻译质量
    quality_score = Column(Float)
    reviewed = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=func.now())
```

---

## 5. AI驱动实施计划 (2-3天)

```
Day 1 (5小时):
├── AI: 实现多语言生成服务
├── AI: 实现翻译服务
└── 人工: 审核语言配置

Day 2 (5小时):
├── AI: 实现文化适配服务
├── AI: 生成数据模型
├── AI: API开发
└── AI: 自动测试

Day 3 (3小时):
├── AI: 添加MCP工具
├── AI: 更新文档
└── 人工: 最终审核
```

---

## 6. API设计

```python
@router.post("/translate/project/{project_id}")
async def translate_project(
    project_id: str,
    target_language: str,
    options: TranslationOptions = None
) -> TranslationTask:
    """翻译整个项目"""

@router.post("/translate/chapter/{chapter_id}")
async def translate_chapter(
    chapter_id: str,
    target_language: str
) -> ChapterTranslation:
    """翻译单个章节"""

@router.post("/generate/multilingual")
async def generate_multilingual(
    project_id: str,
    languages: List[str],
    chapter_number: int
) -> Dict[str, str]:
    """同时生成多语言版本"""
```

---

## 6. 实施计划 (7周)

| 阶段 | 时间 | 任务 |
|------|------|------|
| 阶段1 | 第1-2周 | 多语言生成服务 |
| 阶段2 | 第3-4周 | 翻译服务 |
| 阶段3 | 第5-6周 | 文化适配 |
| 阶段4 | 第7周 | 测试、优化 |

---

## 7. MCP工具

```python
Tool(
    name="novel_translate",
    description="翻译小说内容",
    inputSchema={
        "type": "object",
        "properties": {
            "content": {"type": "string"},
            "source_lang": {"type": "string"},
            "target_lang": {"type": "string", "enum": ["en", "ja", "ko", "zh-TW"]}
        },
        "required": ["content", "target_lang"]
    }
),

Tool(
    name="novel_generate_multilingual",
    description="生成多语言版本",
    inputSchema={
        "type": "object",
        "properties": {
            "project_id": {"type": "string"},
            "languages": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["project_id", "languages"]
    }
)
```

---

## 8. 资源需求 (AI驱动模式)

- AI开发: 2-3天
- 人工审核: 0.5天
- API成本: $50 (翻译调用)
- **总计: 3天 + $50**

---

*最后更新: 2026-01-05*
