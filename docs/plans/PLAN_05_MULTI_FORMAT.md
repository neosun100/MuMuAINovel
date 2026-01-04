# 预案05: 多格式支持

> 版本: v1.16 | 优先级: 🟡 P1 | **AI开发: 3-5天** | 人工审核: 0.5天

---

## 1. 目标与成功指标

### 1.1 核心目标
- 支持影视剧本格式输出
- 支持互动小说/分支剧情
- 支持有声剧本格式
- 实现小说→剧本自动转换

### 1.2 成功指标

| 指标 | 当前 | 目标 |
|------|------|------|
| 支持格式数 | 1 | 4+ |
| 剧本格式合规率 | - | 95% |
| 互动小说分支完整性 | - | 90% |
| 转换保真度 | - | 85% |

---

## 2. 支持格式

### 2.1 影视剧本

```
格式规范:
- 场景标题 (INT./EXT. 地点 - 时间)
- 动作描述 (现在时态)
- 角色名 (居中大写)
- 对话 (角色名下方)
- 括号注释 (情绪/动作)
- 转场 (CUT TO: / FADE OUT:)
```

**输出示例**:
```
INT. 皇宫大殿 - 日

金碧辉煌的大殿内，文武百官分列两侧。

                    崇祯帝
            (沉声)
        朕已决定，即日起整顿朝纲。

大臣们面面相觑，殿内一片寂静。

                    魏忠贤
            (阴笑)
        陛下圣明。

                                        CUT TO:
```

### 2.2 互动小说

```json
{
  "scene_id": "chapter_1_scene_1",
  "content": "你站在皇宫门前，面前有两条路...",
  "choices": [
    {
      "text": "从正门进入",
      "next_scene": "chapter_1_scene_2a",
      "conditions": {"reputation": ">= 50"},
      "effects": {"reputation": "+10"}
    },
    {
      "text": "从侧门潜入",
      "next_scene": "chapter_1_scene_2b",
      "effects": {"stealth": "+5", "reputation": "-5"}
    }
  ]
}
```

### 2.3 有声剧本

```
【场景】皇宫大殿
【BGM】宫廷庄严曲 (渐入)
【音效】脚步声、衣袍摩擦声

【旁白】(低沉) 崇祯十七年，大明王朝风雨飘摇...

【崇祯帝】(威严) 朕已决定，即日起整顿朝纲。
【音效】群臣窃窃私语

【魏忠贤】(阴险) 陛下圣明。
【BGM】紧张悬疑曲 (渐入)
```

---

## 3. 技术实现

### 3.1 格式转换服务

```python
# backend/app/services/format_converter.py

class FormatConverter:
    """格式转换服务"""
    
    async def novel_to_screenplay(
        self,
        chapter_content: str,
        style: str = "movie"  # movie/tv/short
    ) -> str:
        """小说转影视剧本"""
        
        prompt = f"""将以下小说内容转换为标准{style}剧本格式：

【格式要求】
1. 场景标题: INT./EXT. 地点 - 时间
2. 动作描述: 现在时态，简洁有力
3. 角色名: 居中大写
4. 对话: 角色名下方，可加括号注释
5. 转场: CUT TO: / FADE OUT: 等

【小说内容】
{chapter_content}

请输出标准剧本格式：
"""
        return await self.ai.generate(prompt, max_tokens=len(chapter_content) * 2)
    
    async def novel_to_interactive(
        self,
        chapter_content: str,
        branch_points: int = 3
    ) -> Dict:
        """小说转互动小说"""
        
        prompt = f"""将以下小说内容转换为互动小说格式，设计{branch_points}个分支点：

【要求】
1. 识别关键决策点
2. 为每个决策设计2-3个选项
3. 每个选项有不同后果
4. 保持故事连贯性

【小说内容】
{chapter_content}

返回JSON格式的互动小说结构：
"""
        result = await self.ai.generate(prompt, max_tokens=3000)
        return json.loads(result)
    
    async def novel_to_audio_script(
        self,
        chapter_content: str
    ) -> str:
        """小说转有声剧本"""
        
        prompt = f"""将以下小说内容转换为有声剧本格式：

【格式要求】
1. 【场景】标注场景
2. 【BGM】标注背景音乐建议
3. 【音效】标注音效
4. 【角色名】(情绪) 对话内容
5. 【旁白】(语气) 旁白内容

【小说内容】
{chapter_content}

请输出有声剧本格式：
"""
        return await self.ai.generate(prompt, max_tokens=len(chapter_content) * 1.5)
```

### 3.2 互动小说引擎

```python
class InteractiveNovelEngine:
    """互动小说引擎"""
    
    async def create_interactive_novel(
        self,
        project_id: str,
        base_outline: List[Dict]
    ) -> Dict:
        """创建互动小说"""
        
        # 1. 分析大纲，识别分支点
        branch_points = await self._identify_branch_points(base_outline)
        
        # 2. 为每个分支点生成多条路线
        story_graph = {"nodes": [], "edges": []}
        
        for bp in branch_points:
            # 生成分支选项
            options = await self._generate_branch_options(bp)
            
            # 为每个选项生成后续内容
            for option in options:
                branch_content = await self._generate_branch_content(
                    branch_point=bp,
                    option=option,
                    context=story_graph
                )
                story_graph["nodes"].append(branch_content)
                story_graph["edges"].append({
                    "from": bp["id"],
                    "to": branch_content["id"],
                    "option": option
                })
        
        return story_graph
    
    async def export_to_twine(
        self,
        story_graph: Dict
    ) -> str:
        """导出为Twine格式"""
        
        twine_content = ":: StoryTitle\n互动小说\n\n"
        
        for node in story_graph["nodes"]:
            twine_content += f":: {node['id']}\n"
            twine_content += node["content"] + "\n\n"
            
            # 添加选项链接
            for edge in story_graph["edges"]:
                if edge["from"] == node["id"]:
                    twine_content += f"[[{edge['option']['text']}|{edge['to']}]]\n"
            
            twine_content += "\n"
        
        return twine_content
```

---

## 4. 数据模型

```python
class ScriptFormat(Base):
    """剧本格式表"""
    __tablename__ = "script_formats"
    
    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id"))
    chapter_id = Column(String(36), ForeignKey("chapters.id"))
    
    format_type = Column(String(50))  # screenplay/interactive/audio
    content = Column(Text)
    metadata = Column(JSON)  # 格式特定元数据
    
    created_at = Column(DateTime, default=func.now())


class InteractiveNode(Base):
    """互动小说节点表"""
    __tablename__ = "interactive_nodes"
    
    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id"))
    
    node_type = Column(String(50))  # scene/choice/ending
    content = Column(Text)
    choices = Column(JSON)  # [{"text": "选项", "next_node": "id", "conditions": {}, "effects": {}}]
    
    # 游戏化元素
    required_stats = Column(JSON)  # {"reputation": 50}
    stat_changes = Column(JSON)  # {"reputation": +10}
    
    created_at = Column(DateTime, default=func.now())
```

---

## 5. API设计

```python
@router.post("/format/convert")
async def convert_format(
    chapter_id: str,
    target_format: str,  # screenplay/interactive/audio
    options: Dict = None
) -> FormatConversionResult:
    """转换章节格式"""

@router.post("/interactive/create")
async def create_interactive_novel(
    project_id: str,
    branch_count: int = 3
) -> InteractiveNovel:
    """创建互动小说"""

@router.get("/interactive/{project_id}/export")
async def export_interactive(
    project_id: str,
    format: str = "twine"  # twine/ink/json
) -> str:
    """导出互动小说"""
```

---

## 6. AI驱动实施计划 (3-5天)

```
Day 1 (5小时):
├── AI: 实现影视剧本转换服务
├── AI: 实现有声剧本转换
└── 人工: 审核格式规范

Day 2 (5小时):
├── AI: 实现互动小说引擎
├── AI: 实现分支剧情生成
└── AI: 自动测试

Day 3 (4小时):
├── AI: 实现Twine/Ink导出
├── AI: 生成数据模型
└── AI: API开发

Day 4 (3小时):
├── AI: 添加MCP工具
├── AI: 更新文档
└── 人工: 最终审核

Day 5 (可选):
└── 优化和边缘情况处理
```

---

## 7. MCP工具

```python
Tool(
    name="novel_convert_format",
    description="转换章节为其他格式（剧本/互动/有声）",
    inputSchema={
        "type": "object",
        "properties": {
            "chapter_id": {"type": "string"},
            "target_format": {"type": "string", "enum": ["screenplay", "interactive", "audio"]}
        },
        "required": ["chapter_id", "target_format"]
    }
),

Tool(
    name="novel_create_interactive",
    description="创建互动小说版本",
    inputSchema={
        "type": "object",
        "properties": {
            "project_id": {"type": "string"},
            "branch_count": {"type": "integer", "default": 3}
        },
        "required": ["project_id"]
    }
)
```

---

## 8. 资源需求 (AI驱动模式)

- AI开发: 3-5天
- 人工审核: 0.5天
- API成本: $30
- **总计: 4-5天 + $30**

---

*最后更新: 2026-01-05*
