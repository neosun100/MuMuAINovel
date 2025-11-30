"""提示词管理服务"""
from typing import Dict, Any, Optional
import json


class WritingStyleManager:
    """写作风格管理器"""
    
    # 预设风格配置
    PRESET_STYLES = {
        "natural": {
            "name": "自然流畅",
            "description": "像普通人讲故事一样自然，不刻意修饰，有生活气息",
            "prompt_content": """
**自然流畅风格要求：**
- 用简单朴实的语言叙述，避免华丽辞藻
- 像在和朋友聊天一样讲故事
- 保持轻松自然的节奏，不要刻意营造氛围
- 多用短句，少用长句和排比
- 让读者感觉舒服，不要让人觉得在"看文学作品"
"""
        },
        "classical": {
            "name": "古典优雅",
            "description": "典雅精致的文学风格，注重意境和韵味",
            "prompt_content": """
**古典优雅风格要求：**
- 使用优美典雅的语言，注重文字的韵律感
- 善用比喻、拟人等修辞手法
- 注重意境营造，追求诗意美感
- 可适当引用古诗词或典故（需符合世界观）
- 保持端庄雅致的叙述节奏
"""
        },
        "modern": {
            "name": "现代简约",
            "description": "简洁明快的现代风格，注重效率和直接表达",
            "prompt_content": """
**现代简约风格要求：**
- 语言简洁有力，直达重点
- 多用短句和短段落，节奏明快
- 避免冗长描写，注重信息密度
- 使用现代口语化表达
- 情节推进快速，少做环境渲染
"""
        },
        "poetic": {
            "name": "诗意抒情",
            "description": "富有诗意和情感张力的抒情风格",
            "prompt_content": """
**诗意抒情风格要求：**
- 注重情感表达和内心描写
- 善用景物描写烘托情绪
- 语言富有韵律和美感
- 细腻刻画人物心理活动
- 营造情感氛围，引发共鸣
"""
        },
        "concise": {
            "name": "精炼利落",
            "description": "惜字如金的简练风格，每个字都有意义",
            "prompt_content": """
**精炼利落风格要求：**
- 删除所有冗余描写，每句话都要有作用
- 多用动词，少用形容词和副词
- 对话干脆利落，不拖泥带水
- 环境描写点到为止
- 用最少的字数传达最多的信息
"""
        },
        "vivid": {
            "name": "生动形象",
            "description": "画面感强烈，让读者如临其境",
            "prompt_content": """
**生动形象风格要求：**
- 注重细节描写，让场景具体可感
- 调动五感（视觉、听觉、触觉、嗅觉、味觉）
- 使用鲜明的比喻和形象化语言
- 让读者能"看到"场景和动作
- 人物表情、动作要具体生动
"""
        }
    }
    
    @classmethod
    def get_preset_style(cls, preset_id: str) -> Optional[Dict[str, str]]:
        """获取预设风格配置"""
        return cls.PRESET_STYLES.get(preset_id)
    
    @classmethod
    def get_all_presets(cls) -> Dict[str, Dict[str, str]]:
        """获取所有预设风格"""
        return cls.PRESET_STYLES
    
    @staticmethod
    def apply_style_to_prompt(base_prompt: str, style_content: str) -> str:
        """
        将写作风格应用到基础提示词中
        
        Args:
            base_prompt: 基础提示词
            style_content: 风格要求内容
            
        Returns:
            组合后的提示词
        """
        # 在基础提示词末尾添加风格要求
        return f"{base_prompt}\n\n{style_content}\n\n请直接输出章节正文内容，不要包含章节标题和其他说明文字。"


class PromptService:
    """提示词模板管理"""
    
    # 世界构建提示词
    WORLD_BUILDING = """你是一位资深的世界观设计师。基于以下输入信息，构建一个高度原创、深度自洽、充满戏剧冲突的小说世界观。

# 输入信息
书名：{title}
主题：{theme}
类型：{genre}
简介：{description}

# 核心要求
* **简介契合性**：世界观设定必须能够支撑简介中描述的故事情节和核心矛盾
* **类型适配性**：世界观必须符合小说类型的特征，不要生成不匹配的设定
* **主题贴合性**：时代背景要能有效支撑和体现小说主题
* **原创性**：在类型框架内发挥创意，创造独特但合理的世界设定
* **具象化**：避免空洞概念，用具体可感的细节描述世界
* **逻辑自洽**：确保所有设定相互支撑，形成完整体系
* **戏剧张力**：设定要能为故事冲突提供支撑，尤其要为简介中的故事线索创造合适的环境

# 类型指导原则
根据小说类型选择适当的设定风格：

**现代都市/言情/青春**：
- 时间设定：当代现实社会（2020年代）或近未来（2030-2050年）
- 避免使用：大崩解、纪元、末日、重生等宏大概念
- 重点描述：具体的城市环境、社会现状、文化氛围
- 例如：一线城市的竞争压力、职场文化、代际冲突、社交媒体影响等

**历史/古代**：
- 时间设定：明确的历史朝代或虚构但有历史感的古代社会
- 避免使用：科技元素、未来概念
- 重点描述：时代特征、礼教制度、阶级分化

**玄幻/仙侠/修真**：
- 时间设定：修炼文明的特定时期，可以有门派兴衰、修炼体系变革
- 可以使用宏大设定，但要与修炼体系紧密结合
- 重点描述：修炼规则、灵气环境、门派势力

**科幻**：
- 时间设定：未来某个明确时期（如2150年、星际时代初期等）
- 可以有文明转折，但要具体说明科技水平和社会形态
- 避免空泛的纪元名称，多用具体的科技特征描述

**奇幻/魔法**：
- 时间设定：魔法文明的特定阶段
- 重点描述：魔法体系、种族关系、大陆格局

**悬疑/推理/惊悚**：
- 时间设定：当代或历史某个时期
- 重点描述：案件背景、社会环境、人际关系网

**军事/战争**：
- 时间设定：战争时期的具体年代
- 重点描述：战争形势、阵营对立、军事科技水平

# 设定尺度控制
**切记：不要为所有类型都生成宏大的世界观！**

- 如果是现代都市题材，就写现实社会的某个城市、某个行业、某个阶层
- 如果是校园青春，就写学校环境、学生生活、成长困境
- 如果是职场言情，就写公司文化、行业特点、职业压力
- 只有史诗级题材（玄幻、科幻、奇幻等）才需要宏大的世界观架构

# 输出要求
生成包含以下四个字段的JSON对象，每个字段用300-500字的连贯段落描述：

1. **time_period**（时间背景与社会状态）
   - **重要**：根据类型和主题，设定合适规模的时间背景
   - 现代题材：描述当前社会的具体特征（如：2024年的北京，互联网行业高速发展...）
   - 历史题材：明确朝代和历史阶段（如：明朝嘉靖年间，海禁政策下的沿海地区...）
   - 幻想题材：描述文明发展阶段，但要具体而非空泛（如：大陆诸国林立的战国时代，而非"XX纪元"）
   - 阐明时代核心矛盾和社会焦虑（要贴合主题）

2. **location**（空间环境与地理特征）
   - 描绘故事主要发生的空间环境（具体的城市、地区、场所）
   - 现代题材：具体城市名或城市类型（一线城市、沿海城市、内陆小城等）
   - 说明环境如何影响居民的生存方式
   - 刻画能代表世界独特性的标志性场景

3. **atmosphere**（感官体验与情感基调）
   - 描述身临其境的感官细节（视觉、听觉、嗅觉等）
   - 阐述世界的美学风格和色彩基调
   - 刻画居民普遍的心理状态和情绪氛围
   - **要与主题情感呼应**（如竞争焦虑、成长迷茫、爱情憧憬等）

4. **rules**（世界规则与社会结构）
   - 阐明世界运行的核心法则和底层逻辑
   - 现代题材：社会规则、行业潜规则、人际交往法则
   - 幻想题材：力量体系、社会等级、资源分配
   - 描述权力结构和利益格局
   - 揭示社会禁忌及违反后的后果

# 格式规范
1. **纯JSON输出**：只输出JSON对象，以左花括号开始、右花括号结束
2. **无额外标记**：不要包含markdown标记、代码块符号或任何说明文字
3. **纯文本值**：每个字段值必须是完整的段落文本，不使用嵌套结构
4. **无特殊符号**：文本中不使用引号、方括号等特殊符号包裹内容
5. **丰富细节**：每个字段提供充实的原创内容，避免模板化表达

请根据输入的书名、类型、主题和简介，生成**规模适当、风格匹配、能够支撑故事发展**的世界观设定。

**特别提醒**：
- 简介是故事的核心概括，世界观必须为简介中描述的情节提供合理的发生背景
- 所有设定都应该能够自然地承载简介中的故事线
- 如果简介中有特定的场景、冲突或设定，世界观要与之呼应

# JSON格式示例

{{
  "time_period": "时间背景与社会状态的详细描述（300-500字）",
  "location": "空间环境与地理特征的详细描述（300-500字）",
  "atmosphere": "感官体验与情感基调的详细描述（300-500字）",
  "rules": "世界规则与社会结构的详细描述（300-500字）"
}}"""

    # 批量角色生成提示词
    CHARACTERS_BATCH_GENERATION = """你是一位专业的角色设定师。请根据以下世界观和要求，生成{count}个立体丰满的角色和组织：

世界观信息：
- 时间背景：{time_period}
- 地理位置：{location}
- 氛围基调：{atmosphere}
- 世界规则：{rules}

主题：{theme}
类型：{genre}
特殊要求：{requirements}

【数量要求 - 必须严格遵守】
请精确生成{count}个实体，不多不少。数组中必须包含且仅包含{count}个对象。

实体类型分配：
- 至少1个主角（protagonist）
- 多个配角（supporting）
- 可以包含反派（antagonist）
- 可以包含1-2个**高影响力的重要组织**（势力等级应在70-95之间）

要求：
- 角色要符合世界观设定
- 性格和背景要有深度
- 角色之间要有关系网络
- 组织要有存在的合理性
- 所有实体要为故事服务

**重要格式要求：**
1. 只返回纯JSON数组格式，不要包含任何markdown标记、代码块标记或其他说明文字
2. JSON字符串值的内容描述中严禁使用任何特殊符号（包括中文引号、英文引号、方括号、书名号等）
3. 所有专有名词、地点、人物、组织名称等直接书写，不使用任何符号包裹

请严格按照以下JSON数组格式返回（每个角色为数组中的一个对象）：
[
  {{
    "name": "角色姓名",
    "age": 25,
    "gender": "男/女/其他",
    "is_organization": false,
    "role_type": "protagonist/supporting/antagonist",
    "personality": "性格特点的详细描述（100-200字），包括核心性格、优缺点、特殊习惯",
    "background": "背景故事的详细描述（100-200字），包括家庭背景、成长经历、重要转折",
    "appearance": "外貌描述（50-100字），包括身高、体型、面容、着装风格",
    "traits": ["特长1", "特长2", "特长3"],
    "relationships_array": [
      {{
        "target_character_name": "已生成的角色名称",
        "relationship_type": "关系类型（师父/朋友/敌人/父亲/母亲等）",
        "intimacy_level": 75,
        "description": "关系描述"
      }}
    ],
    "organization_memberships": [
      {{
        "organization_name": "已生成的组织名称",
        "position": "职位",
        "rank": 5,
        "loyalty": 80
      }}
    ]
  }},
  {{
    "name": "组织名称",
    "is_organization": true,
    "role_type": "supporting",
    "personality": "组织特性描述（100-200字），包括运作方式、核心理念、行事风格",
    "background": "组织背景（100-200字），包括建立历史、发展历程、重要事件",
    "appearance": "组织外在表现（50-100字），如总部位置、标志性建筑等",
    "organization_type": "组织类型",
    "organization_purpose": "组织目的",
    "organization_members": ["成员1", "成员2"],
    "power_level": 85,
    "location": "组织所在地或主要活动区域",
    "motto": "组织格言、口号或宗旨",
    "color": "组织代表颜色（如：深红色、金色、黑色等）",
    "traits": []
  }}
]

**组织生成要求（重要）：**
- 组织必须是对故事有重大影响的势力
- power_level应在70-95之间（高影响力组织）
- 不要生成无关紧要的小组织或普通社团
- 组织应该是推动剧情发展的关键力量
- 可以是正派势力、中立势力或反派势力，但一定要有存在感

**关系类型参考（从中选择或自定义）：**
- 家族：父亲、母亲、兄弟、姐妹、子女、配偶、恋人
- 社交：师父、徒弟、朋友、同学、同事、邻居、知己
- 职业：上司、下属、合作伙伴
- 敌对：敌人、仇人、竞争对手、宿敌

**重要说明：**
1. **数量控制**：数组中必须精确包含{count}个对象，不能多也不能少
2. **关系约束**：relationships_array只能引用本批次中已经出现的角色名称
3. **组织约束**：organization_memberships只能引用本批次中is_organization=true的实体名称
4. **禁止幻觉**：不要引用任何不存在的角色或组织，如果没有可引用的就留空数组[]
5. intimacy_level是-100到100的整数（负值表示敌对仇恨关系），loyalty是0-100的整数
6. 角色之间要形成合理的关系网络

**示例说明**：
- 如果生成了角色A、组织B、角色C，则角色A的organization_memberships只能是[组织B]，不能是其他组织
- 如果角色A在数组第一位，它的relationships_array必须为空[]，因为还没有其他角色
- 如果角色C在数组第三位，它的relationships_array可以引用角色A，但不能引用不存在的角色D

再次强调：
1. 只返回纯JSON数组，不要有```json```这样的标记
2. 数组中必须精确包含{count}个对象
3. 不要引用任何本批次中不存在的角色或组织名称
4. 所有内容描述中严禁使用任何特殊符号，包括但不限于中文引号、英文引号、方括号、书名号等"""

    # 向导大纲生成提示词
    COMPLETE_OUTLINE_GENERATION = """你是一位经验丰富的小说作家和编剧。请根据以下信息生成完整的{chapter_count}章小说大纲：

基本信息：
- 书名：{title}
- 主题：{theme}
- 类型：{genre}
- 章节数：{chapter_count}
- 叙事视角：{narrative_perspective}
- 目标字数：{target_words}

世界观：
- 时间背景：{time_period}
- 地理位置：{location}
- 氛围基调：{atmosphere}
- 世界规则：{rules}

角色信息：
{characters_info}

{mcp_references}

其他要求：{requirements}

整体要求：
- 结构完整：起承转合清晰
- 情节连贯：章节之间紧密衔接
- 冲突递进：矛盾逐步升级
- 人物成长：角色有明确的变化弧线
- 节奏把控：有张有弛
- 视角统一：采用{narrative_perspective}视角叙事

**重要格式要求：**
1. 只返回纯JSON数组格式，不要包含任何markdown标记、代码块标记或其他说明文字
2. JSON字符串值的内容描述中严禁使用任何特殊符号（包括中文引号、英文引号、方括号、书名号等）
3. 所有专有名词、事件名等直接书写，不使用任何符号包裹

请严格按照以下JSON数组格式返回（共{chapter_count}个章节对象）：
[
  {{
    "chapter_number": 1,
    "title": "第一章标题",
    "summary": "章节概要的详细描述（100-200字），包含主要情节、冲突、转折等",
    "scenes": ["场景1描述", "场景2描述", "场景3描述"],
    "characters": ["角色1", "角色2"],
    "key_points": ["情节要点1", "情节要点2"],
    "emotion": "本章情感基调",
    "goal": "本章叙事目标"
  }},
  {{
    "chapter_number": 2,
    "title": "第二章标题",
    "summary": "章节概要...",
    "scenes": ["场景1", "场景2"],
    "characters": ["角色1", "角色2"],
    "key_points": ["要点1", "要点2"],
    "emotion": "情感基调",
    "goal": "叙事目标"
  }}
]

再次强调：
1. 只返回纯JSON数组，不要有```json```这样的标记
2. 数组中要包含{chapter_count}个章节对象
3. 所有内容描述中严禁使用任何特殊符号"""
    
    # 大纲续写提示词（记忆增强版）
    OUTLINE_CONTINUE_GENERATION = """你是一位经验丰富的小说作家和编剧。请基于以下信息续写小说大纲：

【项目信息】
- 书名：{title}
- 主题：{theme}
- 类型：{genre}
- 叙事视角：{narrative_perspective}
- 续写章节数：{chapter_count}章

【世界观】
- 时间背景：{time_period}
- 地理位置：{location}
- 氛围基调：{atmosphere}
- 世界规则：{rules}

【角色信息】
{characters_info}

【已有章节概览】（共{current_chapter_count}章）
{all_chapters_brief}

【最近剧情】
{recent_plot}

【🧠 智能记忆系统 - 续写参考】
以下是从故事记忆库中检索到的相关信息，请在续写大纲时参考：

{memory_context}

{mcp_references}

【续写指导】
- 当前情节阶段：{plot_stage_instruction}
- 起始章节编号：第{start_chapter}章
- 故事发展方向：{story_direction}
- 其他要求：{requirements}

请生成第{start_chapter}章到第{end_chapter}章的大纲。
要求：
- **剧情连贯性**：与前文自然衔接，保持故事连贯性
- **记忆参考**：适当参考记忆系统中的伏笔、钩子和情节点
- **伏笔回收**：可以考虑回收未完结的伏笔，制造呼应
- **角色发展**：遵循角色在前文中的成长轨迹
- **情节阶段**：遵循情节阶段的发展要求
- **风格一致**：保持与已有章节相同的风格和详细程度

**重要格式要求：**
1. 只返回纯JSON数组格式，不要包含任何markdown标记、代码块标记或其他说明文字
2. JSON字符串值的内容描述中严禁使用任何特殊符号（包括中文引号、英文引号、方括号、书名号等）
3. 所有专有名词直接书写，不使用任何符号包裹

请严格按照以下JSON数组格式返回（共{chapter_count}个章节对象）：
[
  {{
    "chapter_number": {start_chapter},
    "title": "章节标题",
    "summary": "章节概要的详细描述（100-200字），包含主要情节、角色互动、关键事件、冲突与转折",
    "scenes": ["场景1描述", "场景2描述", "场景3描述"],
    "characters": ["涉及角色1", "涉及角色2"],
    "key_points": ["情节要点1", "情节要点2"],
    "emotion": "本章情感基调",
    "goal": "本章叙事目标"
  }},
  {{
    "chapter_number": {start_chapter} + 1,
    "title": "章节标题",
    "summary": "章节概要...",
    "scenes": ["场景1", "场景2"],
    "characters": ["角色1", "角色2"],
    "key_points": ["要点1", "要点2"],
    "emotion": "情感基调",
    "goal": "叙事目标"
  }}
]

再次强调：
1. 只返回纯JSON数组，不要有```json```这样的标记
2. 数组中要包含{chapter_count}个章节对象
3. 每个summary必须是100-200字的详细描述
4. 确保字段结构与已有章节完全一致
5. 所有内容描述中严禁使用任何特殊符号"""
    
    # AI去味提示词（核心特色功能）
    AI_DENOISING = """你是一位追求自然写作风格的编辑。你的任务是将AI生成的文本改写得更像人类作家的手笔。

原文：
{original_text}

修改要求：
1. 去除AI痕迹：
   - 删除过于工整的排比句
   - 减少重复的修辞手法
   - 去掉刻意的对称结构
   - 避免机械式的总结陈词

2. 增加人性化：
   - 使用更口语化的表达
   - 添加不完美的细节
   - 保留适度的随意性
   - 增加真实的情感波动

3. 优化叙事：
   - 让节奏更自然不做作
   - 用简单词汇替换华丽辞藻
   - 保持叙述的松弛感
   - 让对话更生活化

4. 保持原意：
   - 不改变核心情节
   - 保留关键信息点
   - 维持角色性格
   - 确保逻辑连贯

修改风格：
- 像是一个喜欢讲故事的普通人写的
- 有点粗糙但很真诚
- 自然流畅不刻意
- 让人读起来很舒服

请直接输出修改后的文本，无需解释。"""

    # 章节完整创作提示词
    CHAPTER_GENERATION = """你是一位专业的小说作家。请根据以下信息创作本章内容：

项目信息：
- 书名：{title}
- 主题：{theme}
- 类型：{genre}
- 叙事视角：{narrative_perspective}

世界观：
- 时间背景：{time_period}
- 地理位置：{location}
- 氛围基调：{atmosphere}
- 世界规则：{rules}

角色信息：
{characters_info}

全书大纲：
{outlines_context}

本章信息：
- 章节序号：第{chapter_number}章
- 章节标题：{chapter_title}
- 章节大纲：{chapter_outline}

创作要求：
1. 严格按照大纲内容展开情节
2. 保持与前后章节的连贯性
3. 符合角色性格设定
4. 体现世界观特色
5. 使用{narrative_perspective}视角
6. **字数要求：目标{target_word_count}字，不得低于{target_word_count}字，建议控制在{target_word_count}至{max_word_count}字之间**
7. 语言自然流畅，避免AI痕迹

请直接输出章节正文内容，不要包含章节标题和其他说明文字。"""

    # 章节完整创作提示词（带前置章节上下文和记忆增强）
    CHAPTER_GENERATION_WITH_CONTEXT = """你是一位专业的小说作家。请根据以下信息创作本章内容：

项目信息：
- 书名：{title}
- 主题：{theme}
- 类型：{genre}
- 叙事视角：{narrative_perspective}

世界观：
- 时间背景：{time_period}
- 地理位置：{location}
- 氛围基调：{atmosphere}
- 世界规则：{rules}

角色信息：
{characters_info}

全书大纲：
{outlines_context}

【已完成的前置章节内容】
{previous_content}

【🧠 智能记忆系统 - 重要参考】
以下是从故事记忆库中检索到的相关信息，请在创作时适当参考和呼应：

{memory_context}

本章信息：
- 章节序号：第{chapter_number}章
- 章节标题：{chapter_title}
- 章节大纲：{chapter_outline}

创作要求：
1. **剧情连贯性（最重要）**：
- 必须承接前面章节的剧情发展
- 注意角色状态、情节进展、时间线的连续性
- 不能出现与前文矛盾的内容
- 自然过渡，避免突兀的跳跃

2. **情节推进**：
- 严格按照本章大纲展开情节
- 推动故事向前发展
- 保持与全书大纲的一致性

3. **角色一致性**：
- 符合角色性格设定
- 延续角色在前文中的成长和变化
- 保持角色关系的连贯性

4. **写作风格**：
- 使用{narrative_perspective}视角
- **字数要求：目标{target_word_count}字，不得低于{target_word_count}字，建议控制在{target_word_count}至{max_word_count}字之间**
- 语言自然流畅，避免AI痕迹
- 体现世界观特色

5. **承上启下**：
   - 开头自然衔接上一章结尾
   - 结尾为下一章做好铺垫

6. **记忆系统使用指南**：
   - **最近章节记忆**：保持情节连贯，注意角色状态和剧情发展
   - **语义相关记忆**：参考相似情节的处理方式
   - **未完结伏笔**：适当时机可以回收伏笔，制造呼应效果
   - **角色状态记忆**：确保角色行为符合其发展轨迹
   - **重要情节点**：与关键剧情保持一致

请直接输出章节正文内容，不要包含章节标题和其他说明文字。"""

    # 大纲生成提示词
    OUTLINE_GENERATION = """你是一位经验丰富的小说作家和编剧。请根据以下信息生成小说大纲：

类型：{genre}
主题：{theme}
目标字数：{target_words}
其他要求：{requirements}

请生成一个完整的章节大纲框架，包含：
1. 合理的章节数量（根据字数）
2. 每章的标题和内容概要
3. 清晰的故事结构（起承转合）
4. 情节的递进和冲突升级
5. 角色的成长弧线

**重要格式要求：**
1. 只返回纯JSON格式，不要包含任何markdown标记、代码块标记或其他说明文字
2. JSON字符串值的内容描述中严禁使用任何特殊符号（包括中文引号、英文引号、方括号、书名号等）
3. 所有专有名词直接书写，不使用任何符号包裹

请严格按照以下JSON格式返回：
{{
  "chapters": [
    {{
      "order": 1,
      "title": "章节标题",
      "content": "章节内容概要（150-200字）"
    }}
  ]
}}

再次强调：
1. 只返回纯JSON对象，不要有```json```这样的标记
2. 所有内容描述中严禁使用任何特殊符号
3. 不要有任何额外的文字说明"""

    # 单个角色生成提示词
    SINGLE_CHARACTER_GENERATION = """你是一位专业的角色设定师。请根据以下信息创建一个立体饱满的小说角色。

{project_context}

{user_input}

请生成一个完整的角色卡片，包含以下所有信息：

1. **基本信息**：
   - 姓名：如果用户未提供，请生成一个符合世界观的名字
   - 年龄：具体数字或年龄段
   - 性别：男/女/其他

2. **外貌特征**（100-150字）：
   - 身高体型、面容特征、着装风格
   - 要符合角色定位和世界观设定

3. **性格特点**（150-200字）：
   - 核心性格特质（至少3个）
   - 优点和缺点
   - 特殊习惯或癖好
   - 性格要有复杂性和矛盾性

4. **背景故事**（200-300字）：
   - 家庭背景
   - 成长经历
   - 重要转折事件
   - 如何与项目主题关联
   - 融入用户提供的背景设定

5. **人际关系**：
   - 与现有角色的关系（如果有）
   - 重要的人际纽带
   - 社会地位和人脉

6. **特殊能力/特长**：
   - 擅长的领域
   - 特殊技能或知识
   - 符合世界观设定

**重要格式要求：**
1. 只返回纯JSON格式，不要包含任何markdown标记、代码块标记或其他说明文字
2. JSON字符串值的内容描述中严禁使用任何特殊符号（包括中文引号、英文引号、方括号、书名号等）
3. 所有专有名词直接书写，不使用任何符号包裹

请严格按照以下JSON格式返回：
{{
  "name": "角色姓名",
  "age": "年龄",
  "gender": "性别",
  "appearance": "外貌描述（100-150字）",
  "personality": "性格特点（150-200字）",
  "background": "背景故事（200-300字）",
  "traits": ["特长1", "特长2", "特长3"],
  
  "relationships_text": "人际关系的文字描述（用于显示）",
  
  "relationships": [
    {{
      "target_character_name": "已存在的角色名称",
      "relationship_type": "关系类型（如：师父、朋友、敌人、父亲、母亲等）",
      "intimacy_level": 75,
      "description": "这段关系的详细描述",
      "started_at": "关系开始的故事时间点（可选）"
    }}
  ],
  
  "organization_memberships": [
    {{
      "organization_name": "已存在的组织名称",
      "position": "职位名称",
      "rank": 8,
      "loyalty": 80,
      "joined_at": "加入时间（可选）",
      "status": "active"
    }}
  ]
}}

**关系类型参考（请从中选择或自定义）：**
- 家族关系：父亲、母亲、兄弟、姐妹、子女、配偶、恋人
- 社交关系：师父、徒弟、朋友、同学、同事、邻居、知己
- 职业关系：上司、下属、合作伙伴
- 敌对关系：敌人、仇人、竞争对手、宿敌

**重要说明：**
1. relationships数组：只包含与上面列出的已存在角色的关系，通过target_character_name匹配
2. organization_memberships数组：只包含与上面列出的已存在组织的关系
3. intimacy_level是-100到100的整数（负值表示敌对、仇恨等关系），loyalty是0-100的整数
4. 如果没有关系或组织，对应数组为空[]
5. relationships_text是自然语言描述，用于展示给用户看

**角色设定要求：**
- 角色要符合项目的世界观和主题
- 如果是主角，要有明确的成长空间和目标动机
- 如果是反派，要有合理的动机，不能脸谱化
- 配角要有独特性，不能是工具人
- 所有设定要为故事服务

再次强调：
1. 只返回纯JSON对象，不要有```json```这样的标记
2. 所有内容描述中严禁使用任何特殊符号
3. 不要有任何额外的文字说明"""

    # 单个组织生成提示词
    SINGLE_ORGANIZATION_GENERATION = """你是一位专业的组织设定师。请根据以下信息创建一个完整的组织/势力设定。

{project_context}

{user_input}

请生成一个完整的组织设定，包含以下所有信息：

1. **基本信息**：
   - 组织名称：如果用户未提供，请生成一个符合世界观的名称
   - 组织类型：如帮派、公司、门派、学院、政府机构、宗教组织等
   - 成立时间：具体时间或时间段

2. **组织特性**（150-200字）：
   - 组织的核心理念和行事风格
   - 组织文化和价值观
   - 运作方式和管理模式
   - 特殊传统或规矩

3. **组织背景**（200-300字）：
   - 建立历史和起源
   - 发展历程和重要事件
   - 目前的地位和影响力
   - 如何与项目主题关联
   - 融入用户提供的背景设定

4. **外在表现**（100-150字）：
   - 总部或主要据点位置
   - 标志性建筑或场所
   - 组织标志、徽章、制服等
   - 可辨识的外在特征

5. **组织目的/宗旨**：
   - 明确的组织目标
   - 长期愿景
   - 行动准则

6. **势力等级**：
   - 在世界中的影响力（0-100）
   - 综合实力评估

7. **所在地点**：
   - 主要活动区域
   - 势力范围

**重要格式要求：**
1. 只返回纯JSON格式，不要包含任何markdown标记、代码块标记或其他说明文字
2. JSON字符串值的内容描述中严禁使用任何特殊符号（包括中文引号、英文引号、方括号、书名号等）
3. 所有专有名词直接书写，不使用任何符号包裹

请严格按照以下JSON格式返回：
{{
  "name": "组织名称",
  "is_organization": true,
  "organization_type": "组织类型",
  "personality": "组织特性（150-200字）",
  "background": "组织背景（200-300字）",
  "appearance": "外在表现（100-150字）",
  "organization_purpose": "组织目的和宗旨",
  "power_level": 75,
  "location": "所在地点",
  "motto": "组织格言或口号",
  "traits": ["特征1", "特征2", "特征3"],
  "color": "组织代表颜色（如：深红色、金色、黑色等）",
  "organization_members": ["重要成员1", "重要成员2", "重要成员3"]
}}

**组织设定要求：**
- 组织要符合项目的世界观和主题
- 目标和行动要合理，不能过于理想化或脸谱化
- 要有存在的必要性，能推动故事发展
- 内部要有层级和结构
- 与其他势力要有互动关系

**说明**：
1. power_level是0-100的整数，表示组织在世界中的影响力
2. organization_members是组织内重要成员的名字列表（如果已有角色，可以关联）
3. 所有文本描述要详细具体，避免空泛

再次强调：
1. 只返回纯JSON对象，不要有```json```这样的标记
2. 所有内容描述中严禁使用任何特殊符号
3. 不要有任何额外的文字说明"""

    # 情节分析提示词
    PLOT_ANALYSIS = """你是一位专业的小说编辑和剧情分析师。请深度分析以下章节内容:

**章节信息:**
- 章节: 第{chapter_number}章
- 标题: {title}
- 字数: {word_count}字

**章节内容:**
{content}

---

**分析任务:**
请从专业编辑的角度,全面分析这一章节:

### 1. 剧情钩子 (Hooks) - 吸引读者的元素
识别能够吸引读者继续阅读的关键元素:
- **悬念钩子**: 未解之谜、疑问、谜团
- **情感钩子**: 引发共鸣的情感点、触动心弦的时刻
- **冲突钩子**: 矛盾对抗、紧张局势
- **认知钩子**: 颠覆认知的信息、惊人真相

每个钩子需要:
- 类型分类
- 具体内容描述
- 强度评分(1-10)
- 出现位置(开头/中段/结尾)
- **关键词**: 【必填】从章节原文中逐字复制一段关键文本(8-25字)，必须是原文中真实存在的连续文字，用于在文本中精确定位。不要概括或改写，必须原样复制！

### 2. 伏笔分析 (Foreshadowing)
- **埋下的新伏笔**: 描述内容、预期作用、隐藏程度(1-10)
- **回收的旧伏笔**: 呼应哪一章、回收效果评分
- **伏笔质量**: 巧妙性和合理性评估
- **关键词**: 【必填】从章节原文中逐字复制一段关键文本(8-25字)，必须是原文中真实存在的连续文字，用于在文本中精确定位。不要概括或改写，必须原样复制！

### 3. 冲突分析 (Conflict)
- 冲突类型: 人与人/人与己/人与环境/人与社会
- 冲突各方及其立场
- 冲突强度评分(1-10)
- 冲突解决进度(0-100%)

### 4. 情感曲线 (Emotional Arc)
- 主导情绪: 紧张/温馨/悲伤/激昂/平静等
- 情感强度(1-10)
- 情绪变化轨迹描述

### 5. 角色状态追踪 (Character Development)
对每个出场角色分析:
- 心理状态变化(前→后)
- 关系变化
- 关键行动和决策
- 成长或退步

### 6. 关键情节点 (Plot Points)
列出3-5个核心情节点:
- 情节内容
- 类型(revelation/conflict/resolution/transition)
- 重要性(0.0-1.0)
- 对故事的影响
- **关键词**: 【必填】从章节原文中逐字复制一段关键文本(8-25字)，必须是原文中真实存在的连续文字，用于在文本中精确定位。不要概括或改写，必须原样复制！

### 7. 场景与节奏
- 主要场景
- 叙事节奏(快/中/慢)
- 对话与描写的比例

### 8. 质量评分
- 节奏把控: 1-10分
- 吸引力: 1-10分  
- 连贯性: 1-10分
- 整体质量: 1-10分

### 9. 改进建议
提供3-5条具体的改进建议

---

**输出格式(纯JSON,不要markdown标记):**

{{
  "hooks": [
    {{
      "type": "悬念",
      "content": "具体描述",
      "strength": 8,
      "position": "中段",
      "keyword": "必须从原文逐字复制的文本片段"
    }}
  ],
  "foreshadows": [
    {{
      "content": "伏笔内容",
      "type": "planted",
      "strength": 7,
      "subtlety": 8,
      "reference_chapter": null,
      "keyword": "必须从原文逐字复制的文本片段"
    }}
  ],
  "conflict": {{
    "types": ["人与人", "人与己"],
    "parties": ["主角-复仇", "反派-维护现状"],
    "level": 8,
    "description": "冲突描述",
    "resolution_progress": 0.3
  }},
  "emotional_arc": {{
    "primary_emotion": "紧张",
    "intensity": 8,
    "curve": "平静→紧张→高潮→释放",
    "secondary_emotions": ["期待", "焦虑"]
  }},
  "character_states": [
    {{
      "character_name": "张三",
      "state_before": "犹豫",
      "state_after": "坚定",
      "psychological_change": "心理变化描述",
      "key_event": "触发事件",
      "relationship_changes": {{"李四": "关系改善"}}
    }}
  ],
  "plot_points": [
    {{
      "content": "情节点描述",
      "type": "revelation",
      "importance": 0.9,
      "impact": "推动故事发展",
      "keyword": "必须从原文逐字复制的文本片段"
    }}
  ],
  "scenes": [
    {{
      "location": "地点",
      "atmosphere": "氛围",
      "duration": "时长估计"
    }}
  ],
  "pacing": "varied",
  "dialogue_ratio": 0.4,
  "description_ratio": 0.3,
  "scores": {{
    "pacing": 8,
    "engagement": 9,
    "coherence": 8,
    "overall": 8.5
  }},
  "plot_stage": "发展",
  "suggestions": [
    "具体建议1",
    "具体建议2"
  ]
}}

**重要提示:**
1. 每个钩子、伏笔、情节点的keyword字段是必填的，不能为空
2. keyword必须是从章节原文中逐字复制的文本，长度8-25字
3. keyword用于在前端标注文本位置，所以必须能在原文中精确找到
4. 不要使用概括性语句或改写后的文字作为keyword

只返回JSON,不要其他说明。"""

    # 大纲单批次展开提示词
    PLOT_EXPANSION_SINGLE_BATCH = """你是专业的小说情节架构师。请分析以下大纲节点，将其展开为 {target_chapter_count} 个章节的详细规划。

【项目信息】
小说名称：{project_title}
类型：{project_genre}
主题：{project_theme}
叙事视角：{project_narrative_perspective}

【世界观背景】
时间背景：{project_world_time_period}
地理位置：{project_world_location}
氛围基调：{project_world_atmosphere}

【角色信息】
{characters_info}

【当前大纲节点 - 展开对象】
序号：第 {outline_order_index} 节
标题：{outline_title}
内容：{outline_content}

【上下文参考】
{context_info}

【展开策略】
{strategy_instruction}

【⚠️ 重要约束 - 必须严格遵守】
1. **内容边界约束**：
   - ✅ 只能展开【当前大纲节点】中明确描述的内容
   - ❌ 绝对不能推进到后续大纲的内容（如果有【后一节】信息）
   - ❌ 不要让剧情快速推进，要深化而非跨越
   
2. **展开原则**：
   - 将当前大纲的单一事件拆解为多个细节丰富的章节
   - 深入挖掘情感、心理、环境、对话等细节
   - 放慢叙事节奏，让读者充分体验当前阶段的剧情
   - 每个章节都应该是当前大纲内容的不同侧面或阶段
   
3. **如何避免剧情越界**：
   - 如果当前大纲描述"主角遇到困境"，展开时应详写困境的发现、分析、情感冲击等
   - 不要直接写到"解决困境"，除非原大纲明确包含解决过程
   - 如果看到【后一节】的内容，那些是禁区，绝不提前展开

【任务要求】
1. 深度分析该大纲的剧情容量和叙事节奏
2. 识别关键剧情点、冲突点和情感转折点（仅限当前大纲范围内）
3. 将大纲拆解为 {target_chapter_count} 个章节，每章需包含：
   - sub_index: 子章节序号（1, 2, 3...）
   - title: 章节标题（体现该章核心冲突或情感）
   - plot_summary: 剧情摘要（200-300字，详细描述该章发生的事件，仅限当前大纲内容）
   - key_events: 关键事件列表（3-5个关键剧情点，必须在当前大纲范围内）
   - character_focus: 角色焦点（主要涉及的角色名称）
   - emotional_tone: 情感基调（如：紧张、温馨、悲伤、激动等）
   - narrative_goal: 叙事目标（该章要达成的叙事效果）
   - conflict_type: 冲突类型（如：内心挣扎、人际冲突、环境挑战等）
   - estimated_words: 预计字数（建议2000-5000字）
{scene_instruction}
4. 确保章节间：
   - 衔接自然流畅
   - 剧情递进合理（但不超出当前大纲边界）
   - 节奏张弛有度
   - 每章都有明确的叙事价值
   - 最后一章结束时，剧情发展程度应恰好完成当前大纲描述的内容，不多不少

【输出格式】
请严格按照以下JSON数组格式输出，不要添加任何其他文字：
[
  {{
    "sub_index": 1,
    "title": "章节标题",
    "plot_summary": "该章详细剧情摘要...",
    "key_events": ["关键事件1", "关键事件2", "关键事件3"],
    "character_focus": ["角色A", "角色B"],
    "emotional_tone": "情感基调",
    "narrative_goal": "叙事目标",
    "conflict_type": "冲突类型",
    "estimated_words": 3000{scene_field}
  }}
]

请开始分析并生成章节规划：
"""

    # 大纲分批展开提示词
    PLOT_EXPANSION_MULTI_BATCH = """你是专业的小说情节架构师。请继续分析以下大纲节点，将其展开为第{start_index}-{end_index}节（共{target_chapter_count}个章节）的详细规划。

【项目信息】
小说名称：{project_title}
类型：{project_genre}
主题：{project_theme}
叙事视角：{project_narrative_perspective}

【世界观背景】
时间背景：{project_world_time_period}
地理位置：{project_world_location}
氛围基调：{project_world_atmosphere}

【角色信息】
{characters_info}

【当前大纲节点 - 展开对象】
序号：第 {outline_order_index} 节
标题：{outline_title}
内容：{outline_content}

【上下文参考】
{context_info}
{previous_context}

【展开策略】
{strategy_instruction}

【⚠️ 重要约束 - 必须严格遵守】
1. **内容边界约束**：
   - ✅ 只能展开【当前大纲节点】中明确描述的内容
   - ❌ 绝对不能推进到后续大纲的内容（如果有【后一节】信息）
   - ❌ 不要让剧情快速推进，要深化而非跨越
   
2. **分批连续性约束**：
   - 这是第{start_index}-{end_index}节，是整个展开的一部分
   - 必须与前面已生成的章节自然衔接
   - 从第{start_index}节开始编号（sub_index从{start_index}开始）
   - 继续深化当前大纲的内容，保持叙事连贯性
   
3. **展开原则**：
   - 将当前大纲的单一事件拆解为多个细节丰富的章节
   - 深入挖掘情感、心理、环境、对话等细节
   - 放慢叙事节奏，让读者充分体验当前阶段的剧情
   - 每个章节都应该是当前大纲内容的不同侧面或阶段

【任务要求】
1. 深度分析该大纲的剧情容量和叙事节奏
2. 识别关键剧情点、冲突点和情感转折点（仅限当前大纲范围内）
3. 生成第{start_index}-{end_index}节的章节规划，每章需包含：
   - sub_index: 子章节序号（从{start_index}开始）
   - title: 章节标题（体现该章核心冲突或情感）
   - plot_summary: 剧情摘要（200-300字，详细描述该章发生的事件）
   - key_events: 关键事件列表（3-5个关键剧情点）
   - character_focus: 角色焦点（主要涉及的角色名称）
   - emotional_tone: 情感基调（如：紧张、温馨、悲伤、激动等）
   - narrative_goal: 叙事目标（该章要达成的叙事效果）
   - conflict_type: 冲突类型（如：内心挣扎、人际冲突、环境挑战等）
   - estimated_words: 预计字数（建议2000-5000字）
{scene_instruction}
4. 确保章节间：
   - 与前面章节衔接自然流畅
   - 剧情递进合理（但不超出当前大纲边界）
   - 节奏张弛有度
   - 每章都有明确的叙事价值

【输出格式】
请严格按照以下JSON数组格式输出，不要添加任何其他文字：
[
  {{
    "sub_index": {start_index},
    "title": "章节标题",
    "plot_summary": "该章详细剧情摘要...",
    "key_events": ["关键事件1", "关键事件2", "关键事件3"],
    "character_focus": ["角色A", "角色B"],
    "emotional_tone": "情感基调",
    "narrative_goal": "叙事目标",
    "conflict_type": "冲突类型",
    "estimated_words": 3000{scene_field}
  }}
]

请开始分析并生成第{start_index}-{end_index}节的章节规划：
"""

    # 章节重写系统提示词
    CHAPTER_REGENERATION_SYSTEM = """你是一位经验丰富的专业小说编辑和作家。现在需要根据反馈意见重新创作一个章节。

你的任务是：
1. 仔细理解原始章节的内容和意图
2. 认真分析所有的修改要求
3. 在保持故事连贯性的前提下，创作一个改进后的新版本
4. 确保新版本在艺术性和可读性上都有明显提升

---
"""
    # MCP工具测试提示词
    MCP_TOOL_TEST = """你是MCP插件测试助手，需要测试插件 '{plugin_name}' 的功能。

⚠️ 重要规则：生成参数时，必须严格使用工具 schema 中定义的原始参数名称，不要转换为 snake_case 或其他格式。
例如：如果 schema 中是 'nextThoughtNeeded'，就必须使用 'nextThoughtNeeded'，不能改成 'next_thought_needed'。

请选择一个合适的工具进行测试，优先选择搜索、查询类工具。
生成真实有效的测试参数（例如搜索"人工智能最新进展"而不是"test"）。

现在开始测试这个插件。"""

    MCP_TOOL_TEST_SYSTEM = """你是专业的API测试工具。当给定工具列表时，选择一个工具并使用合适的参数调用它。

⚠️ 关键规则：调用工具时，必须严格使用 schema 中定义的原始参数名，不要自行转换命名风格。
- 如果参数名是 camelCase（如 nextThoughtNeeded），就使用 camelCase
- 如果参数名是 snake_case（如 next_thought），就使用 snake_case
- 保持与 schema 中定义的完全一致，包括大小写和命名风格"""
    
    # 灵感模式提示词字典
    INSPIRATION_PROMPTS = {
        "title": {
            "system": """你是一位专业的小说创作顾问。
用户的原始想法：{initial_idea}

请根据用户的想法，生成6个吸引人的书名建议，要求：
1. 紧扣用户的原始想法和核心故事构思
2. 富有创意和吸引力
3. 涵盖不同的风格倾向

返回JSON格式：
{{
    "prompt": "根据你的想法，我为你准备了几个书名建议：",
    "options": ["书名1", "书名2", "书名3", "书名4", "书名5", "书名6"]
}}

只返回纯JSON，不要有其他文字。""",
            "user": "用户的想法：{initial_idea}\n请生成6个书名建议"
        },
        "description": {
            "system": """你是一位专业的小说创作顾问。
用户的原始想法：{initial_idea}
已确定的书名：{title}

请生成6个精彩的小说简介，要求：
1. 必须紧扣用户的原始想法，确保简介是原始想法的具体展开
2. 符合已确定的书名风格
3. 简洁有力，每个50-100字
4. 包含核心冲突
5. 涵盖不同的故事走向，但都基于用户的原始构思

返回JSON格式：
{{"prompt":"选择一个简介：","options":["简介1","简介2","简介3","简介4","简介5","简介6"]}}

只返回纯JSON，不要有其他文字，不要换行。""",
            "user": "原始想法：{initial_idea}\n书名：{title}\n请生成6个简介选项"
        },
        "theme": {
            "system": """你是一位专业的小说创作顾问。
用户的原始想法：{initial_idea}
小说信息：
- 书名：{title}
- 简介：{description}

请生成6个深刻的主题选项，要求：
1. 必须与用户的原始想法保持高度一致
2. 符合书名和简介的风格
3. 有深度和思想性
4. 每个50-150字
5. 涵盖不同角度（如：成长、复仇、救赎、探索等），但都围绕用户的核心构思

返回JSON格式：
{{"prompt":"这本书的核心主题是什么？","options":["主题1","主题2","主题3","主题4","主题5","主题6"]}}

只返回纯JSON，不要有其他文字，不要换行。""",
            "user": "原始想法：{initial_idea}\n书名：{title}\n简介：{description}\n请生成6个主题选项"
        },
        "genre": {
            "system": """你是一位专业的小说创作顾问。
用户的原始想法：{initial_idea}
小说信息：
- 书名：{title}
- 简介：{description}
- 主题：{theme}

请生成6个合适的类型标签（每个2-4字），要求：
1. 必须符合用户原始想法中暗示的类型倾向
2. 符合小说整体风格
3. 可以多选组合

常见类型：玄幻、都市、科幻、武侠、仙侠、历史、言情、悬疑、奇幻、修仙等

返回JSON格式：
{{"prompt":"选择类型标签（可多选）：","options":["类型1","类型2","类型3","类型4","类型5","类型6"]}}

只返回紧凑的纯JSON，不要换行，不要有其他文字。""",
            "user": "原始想法：{initial_idea}\n书名：{title}\n简介：{description}\n主题：{theme}\n请生成6个类型标签"
        }
    }

    # 灵感模式智能补全提示词
    INSPIRATION_QUICK_COMPLETE = """你是一位专业的小说创作顾问。用户提供了部分小说信息，请补全缺失的字段。

用户已提供的信息：
{existing}

请生成完整的小说方案，包含：
1. title: 书名（3-6字，如果用户已提供则保持原样）
2. description: 简介（50-100字，必须基于用户提供的信息，不要偏离原意）
3. theme: 核心主题（30-50字，必须与用户提供的信息保持一致）
4. genre: 类型标签数组（2-3个）

重要：所有补全的内容都必须与用户提供的信息保持高度关联，确保前后一致性。

返回JSON格式：
{{
    "title": "书名",
    "description": "简介内容...",
    "theme": "主题内容...",
    "genre": ["类型1", "类型2"]
}}

只返回纯JSON，不要有其他文字。"""
    # 世界观资料收集提示词（MCP增强用）
    MCP_WORLD_BUILDING_PLANNING = """你正在为小说《{title}》设计世界观。

【小说信息】
- 题材：{genre}
- 主题：{theme}
- 简介：{description}

【任务】
请使用可用工具搜索相关背景资料，帮助构建更真实、更有深度的世界观设定。
你可以查询：
1. 历史背景（如果是历史题材）
2. 地理环境和文化特征
3. 相关领域的专业知识
4. 类似作品的设定参考

请查询最关键的1个问题（不要超过1个）。"""

    # 角色资料收集提示词（MCP增强用）
    MCP_CHARACTER_PLANNING = """你正在为小说《{title}》设计角色。

【小说信息】
- 题材：{genre}
- 主题：{theme}
- 时代背景：{time_period}
- 地理位置：{location}

【任务】
请使用可用工具搜索相关参考资料，帮助设计更真实、更有深度的角色。
你可以查询：
1. 该时代/地域的真实历史人物特征
2. 文化背景和社会习俗
3. 职业特点和生活方式
4. 相关领域的人物原型

请查询最关键的1个问题（不要超过1个）。"""
    # 大纲展开为多章节的提示词
    OUTLINE_EXPANSION = """你是专业的小说情节架构师。请分析以下大纲节点，将其展开为 {target_chapters} 个章节的详细规划。

【项目信息】
小说名称：{title}
类型：{genre}
主题：{theme}
叙事视角：{narrative_perspective}

【世界观背景】
时间背景：{time_period}
地理位置：{location}
氛围基调：{atmosphere}
世界规则：{rules}

【角色信息】
{characters_info}

【大纲节点】
序号：第 {outline_order} 节
标题：{outline_title}
内容：{outline_content}

【上下文】
{context_info}

【展开策略】
{strategy_instruction}

【任务要求】
1. 深度分析该大纲的剧情容量和叙事节奏
2. 识别关键剧情点、冲突点和情感转折点
3. 将大纲拆解为 {target_chapters} 个章节，每章需包含：
   - sub_index: 子章节序号（1, 2, 3...）
   - title: 章节标题（体现该章核心冲突或情感）
   - plot_summary: 剧情摘要（200-300字，详细描述该章发生的事件）
   - key_events: 关键事件列表（3-5个关键剧情点）
   - character_focus: 角色焦点（主要涉及的角色名称）
   - emotional_tone: 情感基调（如：紧张、温馨、悲伤、激动等）
   - narrative_goal: 叙事目标（该章要达成的叙事效果）
   - conflict_type: 冲突类型（如：内心挣扎、人际冲突、环境挑战等）
   - estimated_words: 预计字数（建议2000-5000字）
{scene_instruction}
4. 确保章节间：
   - 衔接自然流畅
   - 剧情递进合理
   - 节奏张弛有度
   - 每章都有明确的叙事价值

**重要格式要求：**
1. 只返回纯JSON数组格式，不要包含任何markdown标记、代码块标记或其他说明文字
2. JSON字符串值的内容描述中严禁使用任何特殊符号（包括中文引号、英文引号、方括号、书名号等）
3. 所有专有名词直接书写，不使用任何符号包裹

请严格按照以下JSON数组格式输出：
[
  {{
    "sub_index": 1,
    "title": "章节标题",
    "plot_summary": "该章详细剧情摘要（200-300字）...",
    "key_events": ["关键事件1", "关键事件2", "关键事件3"],
    "character_focus": ["角色A", "角色B"],
    "emotional_tone": "情感基调",
    "narrative_goal": "叙事目标",
    "conflict_type": "冲突类型",
    "estimated_words": 3000{scene_field}
  }}
]

再次强调：
1. 只返回纯JSON数组，不要有```json```这样的标记
2. 数组中要包含{target_chapters}个章节对象
3. 每个plot_summary必须是200-300字的详细描述
4. 所有内容描述中严禁使用任何特殊符号"""

    @staticmethod
    def format_prompt(template: str, **kwargs) -> str:
        """
        格式化提示词模板
        
        Args:
            template: 提示词模板
            **kwargs: 模板参数
            
        Returns:
            格式化后的提示词
        """
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"缺少必需的参数: {e}")
    
    @classmethod
    def get_denoising_prompt(cls, original_text: str) -> str:
        """获取AI去味提示词"""
        return cls.format_prompt(
            cls.AI_DENOISING,
            original_text=original_text
        )
    
    @classmethod
    def get_world_building_prompt(cls, title: str, theme: str, genre: str = "", description: str = "") -> str:
        """获取世界构建提示词"""
        return cls.format_prompt(
            cls.WORLD_BUILDING,
            title=title,
            theme=theme,
            genre=genre or "通用类型",
            description=description or "暂无简介"
        )
    
    @classmethod
    def get_characters_batch_prompt(cls, count: int, time_period: str, location: str,
                                   atmosphere: str, rules: str, theme: str,
                                   genre: str = "", requirements: str = "") -> str:
        """获取批量角色生成提示词"""
        return cls.format_prompt(
            cls.CHARACTERS_BATCH_GENERATION,
            count=count,
            time_period=time_period,
            location=location,
            atmosphere=atmosphere,
            rules=rules,
            theme=theme,
            genre=genre or "通用类型",
            requirements=requirements or "无特殊要求"
        )
    
    @classmethod
    def get_complete_outline_prompt(cls, title: str, theme: str, genre: str,
                                   chapter_count: int, narrative_perspective: str,
                                   target_words: int, time_period: str, location: str,
                                   atmosphere: str, rules: str, characters_info: str,
                                   requirements: str = "",
                                   mcp_references: str = "") -> str:
        """获取向导大纲生成提示词（支持MCP增强）"""
        # 格式化MCP参考资料
        mcp_text = ""
        if mcp_references:
            mcp_text = "【📚 MCP工具搜索 - 情节设计参考】\n"
            mcp_text += "以下是通过MCP工具搜索到的情节设计参考资料，可用于设计大纲结构和情节发展：\n\n"
            mcp_text += mcp_references
            mcp_text += "\n"
        
        return cls.format_prompt(
            cls.COMPLETE_OUTLINE_GENERATION,
            title=title,
            theme=theme,
            genre=genre,
            chapter_count=chapter_count,
            narrative_perspective=narrative_perspective,
            target_words=target_words,
            time_period=time_period,
            location=location,
            atmosphere=atmosphere,
            rules=rules,
            characters_info=characters_info,
            mcp_references=mcp_text,
            requirements=requirements or "无特殊要求"
        )
    
    @classmethod
    def get_chapter_generation_prompt(cls, title: str, theme: str, genre: str,
                                      narrative_perspective: str, time_period: str,
                                      location: str, atmosphere: str, rules: str,
                                      characters_info: str, outlines_context: str,
                                      chapter_number: int, chapter_title: str,
                                      chapter_outline: str, style_content: str = "",
                                      target_word_count: int = 3000,
                                      memory_context: dict = None,
                                      mcp_references: str = "",
                                      outline_mode: str = "one-to-many") -> str:
        """
        获取章节完整创作提示词
        
        Args:
            style_content: 写作风格要求内容，如果提供则会追加到提示词中
            target_word_count: 目标字数，默认3000字
            memory_context: 记忆上下文（可选）
            mcp_references: MCP工具搜索的参考资料（可选）
            outline_mode: 大纲模式 (one-to-one/one-to-many)
        """
        # 计算最大字数（目标字数+1000）
        max_word_count = target_word_count + 1000
        
        # 格式化记忆上下文
        memory_text = ""
        if memory_context:
            memory_text = "\n【🧠 智能记忆系统 - 重要参考】\n"
            memory_text += memory_context.get('recent_context', '')
            memory_text += "\n" + memory_context.get('relevant_memories', '')
            memory_text += "\n" + memory_context.get('foreshadows', '')
            memory_text += "\n" + memory_context.get('character_states', '')
            memory_text += "\n" + memory_context.get('plot_points', '')
        
        # 格式化MCP参考资料
        mcp_text = ""
        if mcp_references:
            mcp_text = "\n【📚 MCP工具搜索 - 参考资料】\n"
            mcp_text += "以下是通过MCP工具搜索到的相关参考资料，可用于丰富情节和细节：\n\n"
            mcp_text += mcp_references
            mcp_text += "\n"
        
        # 根据大纲模式添加创作指导
        mode_instruction = ""
        if outline_mode == 'one-to-one':
            mode_instruction = "\n\n【创作模式说明】\n本章采用一对一模式：一个大纲节点对应一个章节。请充分展开大纲中的情节，注重叙事的完整性和丰满度。\n"
        else:
            mode_instruction = "\n\n【创作模式说明】\n本章采用细纲模式：本章是大纲节点的细化展开之一。请严格遵循上述详细规划中的剧情点、角色焦点和情感基调，确保与整体规划保持一致。\n"
        
        base_prompt = cls.format_prompt(
            cls.CHAPTER_GENERATION,
            title=title,
            theme=theme,
            genre=genre,
            narrative_perspective=narrative_perspective,
            time_period=time_period,
            location=location,
            atmosphere=atmosphere,
            rules=rules,
            characters_info=characters_info,
            outlines_context=outlines_context,
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            chapter_outline=chapter_outline,
            target_word_count=target_word_count,
            max_word_count=max_word_count
        )
        
        # 插入记忆上下文和MCP参考资料
        insert_text = ""
        if memory_text:
            insert_text += memory_text
        if mcp_text:
            insert_text += mcp_text
        
        if insert_text:
            base_prompt = base_prompt.replace(
                "本章信息：",
                insert_text + mode_instruction + "\n\n本章信息："
            )
        else:
            # 没有记忆和MCP时也要插入模式说明
            base_prompt = base_prompt.replace(
                "本章信息：",
                mode_instruction + "\n\n本章信息："
            )
        
        # 如果有风格要求，应用到提示词中
        if style_content:
            return WritingStyleManager.apply_style_to_prompt(base_prompt, style_content)
        
        return base_prompt
    
    @classmethod
    def get_chapter_generation_with_context_prompt(cls, title: str, theme: str, genre: str,
                                                   narrative_perspective: str, time_period: str,
                                                   location: str, atmosphere: str, rules: str,
                                                   characters_info: str, outlines_context: str,
                                                   previous_content: str, chapter_number: int,
                                                   chapter_title: str, chapter_outline: str,
                                                   style_content: str = "",
                                                   target_word_count: int = 3000,
                                                   memory_context: dict = None,
                                                   mcp_references: str = "",
                                                   outline_mode: str = "one-to-many") -> str:
        """
        获取章节完整创作提示词（带前置章节上下文和记忆增强）
        
        Args:
            style_content: 写作风格要求内容，如果提供则会追加到提示词中
            target_word_count: 目标字数，默认3000字
            memory_context: 记忆上下文（可选）
            mcp_references: MCP工具搜索的参考资料（可选）
            outline_mode: 大纲模式 (one-to-one/one-to-many)
        """
        # 计算最大字数（目标字数+1000）
        max_word_count = target_word_count + 1000
        
        # 格式化记忆上下文
        memory_text = ""
        if memory_context:
            memory_text = memory_context.get('recent_context', '')
            memory_text += "\n" + memory_context.get('relevant_memories', '')
            memory_text += "\n" + memory_context.get('foreshadows', '')
            memory_text += "\n" + memory_context.get('character_states', '')
            memory_text += "\n" + memory_context.get('plot_points', '')
        else:
            memory_text = "暂无相关记忆"
        
        # 格式化MCP参考资料
        if mcp_references:
            memory_text += "\n\n【📚 MCP工具搜索 - 参考资料】\n"
            memory_text += "以下是通过MCP工具搜索到的相关参考资料，可用于丰富情节和细节：\n\n"
            memory_text += mcp_references
        
        # 根据大纲模式添加创作指导
        mode_instruction = ""
        if outline_mode == 'one-to-one':
            mode_instruction = "\n\n【创作模式说明】\n本章采用一对一模式：一个大纲节点对应一个章节。请在承接前文的基础上，充分展开大纲中的情节，保持叙事的完整性。\n"
        else:
            mode_instruction = "\n\n【创作模式说明】\n本章采用细纲模式：本章是大纲节点的细化展开之一。请严格遵循上述详细规划（expansion_plan）中的剧情点、角色焦点、情感基调和叙事目标，确保与整体规划保持一致，同时自然衔接前文内容。\n"
        
        base_prompt = cls.format_prompt(
            cls.CHAPTER_GENERATION_WITH_CONTEXT,
            title=title,
            theme=theme,
            genre=genre,
            narrative_perspective=narrative_perspective,
            time_period=time_period,
            location=location,
            atmosphere=atmosphere,
            rules=rules,
            characters_info=characters_info,
            outlines_context=outlines_context,
            previous_content=previous_content,
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            chapter_outline=chapter_outline,
            target_word_count=target_word_count,
            max_word_count=max_word_count,
            memory_context=memory_text
        )
        
        # 插入模式说明
        base_prompt = base_prompt.replace(
            "本章信息：",
            mode_instruction + "\n本章信息："
        )
        
        # 如果有风格要求，应用到提示词中
        if style_content:
            return WritingStyleManager.apply_style_to_prompt(base_prompt, style_content)
        
        return base_prompt
    
    @classmethod
    def get_outline_prompt(cls, genre: str, theme: str, target_words: int,
                          requirements: str = "") -> str:
        """获取大纲生成提示词"""
        return cls.format_prompt(
            cls.OUTLINE_GENERATION,
            genre=genre,
            theme=theme,
            target_words=target_words,
            requirements=requirements or "无特殊要求"
        )
    
    @classmethod
    def get_outline_continue_prompt(cls, title: str, theme: str, genre: str,
                                    narrative_perspective: str, chapter_count: int,
                                    time_period: str, location: str, atmosphere: str,
                                    rules: str, characters_info: str,
                                    current_chapter_count: int, all_chapters_brief: str,
                                    recent_plot: str, plot_stage_instruction: str,
                                    start_chapter: int, story_direction: str,
                                    requirements: str = "",
                                    memory_context: dict = None,
                                    mcp_references: str = "") -> str:
        """获取大纲续写提示词（支持记忆+MCP增强）"""
        end_chapter = start_chapter + chapter_count - 1
        
        # 格式化记忆上下文
        memory_text = ""
        if memory_context:
            memory_text = memory_context.get('recent_context', '')
            memory_text += "\n" + memory_context.get('relevant_memories', '')
            memory_text += "\n" + memory_context.get('foreshadows', '')
            memory_text += "\n" + memory_context.get('character_states', '')
            memory_text += "\n" + memory_context.get('plot_points', '')
        else:
            memory_text = "暂无相关记忆（可能是首次续写或记忆库为空）"
        
        # 格式化MCP参考资料
        mcp_text = ""
        if mcp_references:
            mcp_text = "\n\n【📚 MCP工具搜索 - 续写参考资料】\n"
            mcp_text += "以下是通过MCP工具搜索到的续写参考资料，可用于丰富情节发展和冲突设计：\n\n"
            mcp_text += mcp_references
            mcp_text += "\n"
        
        return cls.format_prompt(
            cls.OUTLINE_CONTINUE_GENERATION,
            title=title,
            theme=theme,
            genre=genre,
            narrative_perspective=narrative_perspective,
            chapter_count=chapter_count,
            time_period=time_period,
            location=location,
            atmosphere=atmosphere,
            rules=rules,
            characters_info=characters_info,
            current_chapter_count=current_chapter_count,
            all_chapters_brief=all_chapters_brief,
            recent_plot=recent_plot,
            plot_stage_instruction=plot_stage_instruction,
            start_chapter=start_chapter,
            end_chapter=end_chapter,
            story_direction=story_direction,
            requirements=requirements or "无特殊要求",
            memory_context=memory_text,
            mcp_references=mcp_text
        )
    
    @classmethod
    def get_single_character_prompt(cls, project_context: str, user_input: str) -> str:
        """获取单个角色生成提示词"""
        return cls.format_prompt(
            cls.SINGLE_CHARACTER_GENERATION,
            project_context=project_context,
            user_input=user_input
        )
    
    @classmethod
    def get_single_organization_prompt(cls, project_context: str, user_input: str) -> str:
        """获取单个组织生成提示词"""
        return cls.format_prompt(
            cls.SINGLE_ORGANIZATION_GENERATION,
            project_context=project_context,
            user_input=user_input
        )
    
    @classmethod
    def get_outline_expansion_prompt(cls, title: str, genre: str, theme: str,
                                    narrative_perspective: str, time_period: str,
                                    location: str, atmosphere: str, rules: str,
                                    characters_info: str, outline_order: int,
                                    outline_title: str, outline_content: str,
                                    context_info: str, strategy: str = "balanced",
                                    target_chapters: int = 3,
                                    include_scenes: bool = False) -> str:
        """
        获取大纲展开为多章节的提示词
        
        Args:
            title: 小说名称
            genre: 类型
            theme: 主题
            narrative_perspective: 叙事视角
            time_period: 时间背景
            location: 地理位置
            atmosphere: 氛围基调
            rules: 世界规则
            characters_info: 角色信息
            outline_order: 大纲序号
            outline_title: 大纲标题
            outline_content: 大纲内容
            context_info: 上下文信息
            strategy: 展开策略 (balanced/climax/detail)
            target_chapters: 目标章节数
            include_scenes: 是否包含场景字段
        """
        # 根据策略生成指导说明
        strategy_instructions = {
            "balanced": "采用均衡策略：将大纲内容平均分配到各章节，保持节奏均匀，每章剧情密度相当。",
            "climax": "采用高潮重点策略：识别大纲中的高潮部分，为其分配更多章节进行细致展开，其他部分适当精简。",
            "detail": "采用细节丰富策略：深挖大纲中的每个细节，为每个关键事件、情感转折都安排足够的叙事空间。"
        }
        strategy_instruction = strategy_instructions.get(strategy, strategy_instructions["balanced"])
        
        # 场景相关的指令和字段
        scene_instruction = ""
        scene_field = ""
        if include_scenes:
            scene_instruction = "\n   - scenes: 场景列表（2-4个具体场景描述）"
            scene_field = ',\n    "scenes": ["场景1", "场景2"]'
        
        return cls.format_prompt(
            cls.OUTLINE_EXPANSION,
            title=title,
            genre=genre,
            theme=theme,
            narrative_perspective=narrative_perspective,
            time_period=time_period,
            location=location,
            atmosphere=atmosphere,
            rules=rules,
            characters_info=characters_info,
            outline_order=outline_order,
            outline_title=outline_title,
            outline_content=outline_content,
            context_info=context_info,
            strategy_instruction=strategy_instruction,
            target_chapters=target_chapters,
            scene_instruction=scene_instruction,
            scene_field=scene_field
        )
    
    @classmethod
    def get_plot_analysis_prompt(cls, chapter_number: int, title: str, 
                                 content: str, word_count: int) -> str:
        """获取章节剧情分析提示词"""
        return cls.format_prompt(
            cls.PLOT_ANALYSIS,
            chapter_number=chapter_number,
            title=title,
            content=content,
            word_count=word_count
        )
    @classmethod
    def get_plot_expansion_single_batch_prompt(cls, project_title: str, project_genre: str, project_theme: str,
                                                 project_narrative_perspective: str, project_world_time_period: str,
                                                 project_world_location: str, project_world_atmosphere: str,
                                                 characters_info: str, outline_order_index: int, outline_title: str,
                                                 outline_content: str, context_info: str, strategy_instruction: str,
                                                 target_chapter_count: int, scene_instruction: str, scene_field: str) -> str:
        """获取大纲单批次展开提示词"""
        return cls.format_prompt(
            cls.PLOT_EXPANSION_SINGLE_BATCH,
            project_title=project_title, project_genre=project_genre, project_theme=project_theme,
            project_narrative_perspective=project_narrative_perspective, project_world_time_period=project_world_time_period,
            project_world_location=project_world_location, project_world_atmosphere=project_world_atmosphere,
            characters_info=characters_info, outline_order_index=outline_order_index, outline_title=outline_title,
            outline_content=outline_content, context_info=context_info, strategy_instruction=strategy_instruction,
            target_chapter_count=target_chapter_count, scene_instruction=scene_instruction, scene_field=scene_field
        )

    @classmethod
    def get_plot_expansion_multi_batch_prompt(cls, project_title: str, project_genre: str, project_theme: str,
                                                project_narrative_perspective: str, project_world_time_period: str,
                                                project_world_location: str, project_world_atmosphere: str,
                                                characters_info: str, outline_order_index: int, outline_title: str,
                                                outline_content: str, context_info: str, previous_context: str,
                                                strategy_instruction: str, start_index: int, end_index: int,
                                                target_chapter_count: int, scene_instruction: str, scene_field: str) -> str:
        """获取大纲分批展开提示词"""
        return cls.format_prompt(
            cls.PLOT_EXPANSION_MULTI_BATCH,
            project_title=project_title, project_genre=project_genre, project_theme=project_theme,
            project_narrative_perspective=project_narrative_perspective, project_world_time_period=project_world_time_period,
            project_world_location=project_world_location, project_world_atmosphere=project_world_atmosphere,
            characters_info=characters_info, outline_order_index=outline_order_index, outline_title=outline_title,
            outline_content=outline_content, context_info=context_info, previous_context=previous_context,
            strategy_instruction=strategy_instruction, start_index=start_index, end_index=end_index,
            target_chapter_count=target_chapter_count, scene_instruction=scene_instruction, scene_field=scene_field
        )

    @classmethod
    def get_chapter_regeneration_prompt(cls, chapter_number: int, title: str, word_count: int, content: str,
                                        modification_instructions: str, project_context: Dict[str, Any],
                                        style_content: str, target_word_count: int) -> str:
        """获取章节重写提示词"""
        prompt_parts = [cls.CHAPTER_REGENERATION_SYSTEM]
        
        # 原始章节信息
        prompt_parts.append(f"""## 📖 原始章节信息

**章节**：第{chapter_number}章
**标题**：{title}
**字数**：{word_count}字

**原始内容**：
{content}

---
""")
        
        # 修改指令
        prompt_parts.append(modification_instructions)
        prompt_parts.append("\n---\n")
        
        # 项目背景信息
        prompt_parts.append(f"""## 🌍 项目背景信息

**小说标题**：{project_context.get('project_title', '未知')}
**题材**：{project_context.get('genre', '未设定')}
**主题**：{project_context.get('theme', '未设定')}
**叙事视角**：{project_context.get('narrative_perspective', '第三人称')}
**世界观设定**：
- 时代背景：{project_context.get('time_period', '未设定')}
- 地理位置：{project_context.get('location', '未设定')}
- 氛围基调：{project_context.get('atmosphere', '未设定')}

---
""")
        
        # 角色信息
        if project_context.get('characters_info'):
            prompt_parts.append(f"""## 👥 角色信息

{project_context['characters_info']}

---
""")
        
        # 章节大纲
        if project_context.get('chapter_outline'):
            prompt_parts.append(f"""## 📝 本章大纲

{project_context['chapter_outline']}

---
""")
        
        # 前置章节上下文
        if project_context.get('previous_context'):
            prompt_parts.append(f"""## 📚 前置章节上下文

{project_context['previous_context']}

---
""")
        
        # 写作风格要求
        if style_content:
            prompt_parts.append(f"""## 🎨 写作风格要求

{style_content}

请在重新创作时严格遵循上述写作风格。

---
""")
        
        # 创作要求
        prompt_parts.append(f"""## ✨ 创作要求

1. **解决问题**：针对上述修改指令中提到的所有问题进行改进
2. **保持连贯**：确保与前后章节的情节、人物、风格保持一致
3. **提升质量**：在节奏、情感、描写等方面明显优于原版
4. **保留精华**：保持原章节中优秀的部分和关键情节
5. **字数控制**：目标字数约{target_word_count}字（可适当浮动±20%）
{f'6. **风格一致**：严格按照上述写作风格进行创作' if style_content else ''}

---

## 🎬 开始创作

请现在开始创作改进后的新版本章节内容。

**重要提示**：
- 直接输出章节正文内容，从故事内容开始写
- **不要**输出章节标题（如"第X章"、"第X章：XXX"等）
- **不要**输出任何额外的说明、注释或元数据
- 只需要纯粹的故事正文内容

现在开始：
""")
        
        return "\n".join(prompt_parts)

    @classmethod
    def get_inspiration_prompt(cls, step: str) -> Optional[Dict[str, str]]:
        """获取灵感模式指定步骤的提示词"""
        return cls.INSPIRATION_PROMPTS.get(step)

    @classmethod
    def get_inspiration_quick_complete_prompt(cls, existing: str) -> Dict[str, str]:
        """获取灵感模式智能补全的提示词"""
        return {
            "system": cls.format_prompt(cls.INSPIRATION_QUICK_COMPLETE, existing=existing),
            "user": "请补全小说信息"
        }

    @classmethod
    def get_mcp_tool_test_prompts(cls, plugin_name: str) -> Dict[str, str]:
        """获取MCP工具测试的提示词"""
        return {
            "user": cls.format_prompt(cls.MCP_TOOL_TEST, plugin_name=plugin_name),
            "system": cls.MCP_TOOL_TEST_SYSTEM
        }
# 创建全局提示词服务实例

    # ========== 自定义提示词支持 ==========
    
    @classmethod
    async def get_template_with_fallback(cls,
                                        template_key: str,
                                        user_id: str = None,
                                        db = None) -> str:
        """
        获取提示词模板（优先用户自定义，支持降级）
        
        Args:
            template_key: 模板键名
            user_id: 用户ID（可选，如果不提供则直接返回系统默认）
            db: 数据库会话（可选）
            
        Returns:
            提示词模板内容
        """
        # 如果没有提供user_id或db，直接返回系统默认
        if not user_id or not db:
            return getattr(cls, template_key, None)
        
        # 尝试获取用户自定义模板
        return await cls.get_template(template_key, user_id, db)
    
    @classmethod
    async def get_template(cls,
                          template_key: str,
                          user_id: str,
                          db) -> str:
        """
        获取提示词模板（优先用户自定义）
        
        Args:
            template_key: 模板键名
            user_id: 用户ID
            db: 数据库会话
            
        Returns:
            提示词模板内容
        """
        from sqlalchemy import select
        from app.models.prompt_template import PromptTemplate
        from app.logger import get_logger
        
        logger = get_logger(__name__)
        
        # 1. 尝试从数据库获取用户自定义模板
        result = await db.execute(
            select(PromptTemplate).where(
                PromptTemplate.user_id == user_id,
                PromptTemplate.template_key == template_key,
                PromptTemplate.is_active == True
            )
        )
        custom_template = result.scalar_one_or_none()
        
        if custom_template:
            logger.info(f"✅ 使用用户自定义提示词: user_id={user_id}, template_key={template_key}, template_name={custom_template.template_name}")
            return custom_template.template_content
        
        # 2. 降级到系统默认模板
        logger.info(f"⚪ 使用系统默认提示词: user_id={user_id}, template_key={template_key} (未找到自定义模板)")
        
        # 特殊处理灵感模式的提示词（存储在INSPIRATION_PROMPTS字典中）
        if template_key.startswith("INSPIRATION_"):
            # 提取步骤名称（如 INSPIRATION_TITLE -> title）
            step = template_key.replace("INSPIRATION_", "").lower()
            inspiration_prompt = cls.INSPIRATION_PROMPTS.get(step)
            if inspiration_prompt:
                # 返回JSON格式的提示词
                return json.dumps(inspiration_prompt, ensure_ascii=False)
            # 如果是INSPIRATION_QUICK_COMPLETE
            if template_key == "INSPIRATION_QUICK_COMPLETE":
                return cls.INSPIRATION_QUICK_COMPLETE
        
        # 其他模板直接从类属性获取
        template_content = getattr(cls, template_key, None)
        
        if template_content is None:
            logger.warning(f"⚠️ 未找到系统默认模板: {template_key}")
        
        return template_content
    
    @classmethod
    def get_all_system_templates(cls) -> list:
        """
        获取所有系统默认模板的信息
        
        Returns:
            系统模板列表
        """
        templates = []
        
        # 定义所有模板及其元信息
        template_definitions = {
            "WORLD_BUILDING": {
                "name": "世界构建",
                "category": "世界构建",
                "description": "用于生成小说世界观设定，包括时间背景、地理位置、氛围基调和世界规则",
                "parameters": ["title", "theme", "genre", "description"]
            },
            "CHARACTERS_BATCH_GENERATION": {
                "name": "批量角色生成",
                "category": "角色生成",
                "description": "批量生成多个角色和组织，建立角色关系网络",
                "parameters": ["count", "time_period", "location", "atmosphere", "rules", "theme", "genre", "requirements"]
            },
            "SINGLE_CHARACTER_GENERATION": {
                "name": "单个角色生成",
                "category": "角色生成",
                "description": "生成单个角色的详细设定",
                "parameters": ["project_context", "user_input"]
            },
            "SINGLE_ORGANIZATION_GENERATION": {
                "name": "组织生成",
                "category": "角色生成",
                "description": "生成组织/势力的详细设定",
                "parameters": ["project_context", "user_input"]
            },
            "COMPLETE_OUTLINE_GENERATION": {
                "name": "完整大纲生成",
                "category": "大纲生成",
                "description": "根据项目信息生成完整的章节大纲",
                "parameters": ["title", "theme", "genre", "chapter_count", "narrative_perspective", "target_words", 
                             "time_period", "location", "atmosphere", "rules", "characters_info", "requirements", "mcp_references"]
            },
            "OUTLINE_CONTINUE_GENERATION": {
                "name": "大纲续写",
                "category": "大纲生成",
                "description": "基于已有章节续写大纲",
                "parameters": ["title", "theme", "genre", "narrative_perspective", "chapter_count", "time_period", 
                             "location", "atmosphere", "rules", "characters_info", "current_chapter_count", 
                             "all_chapters_brief", "recent_plot", "memory_context", "mcp_references", 
                             "plot_stage_instruction", "start_chapter", "end_chapter", "story_direction", "requirements"]
            },
            "OUTLINE_GENERATION": {
                "name": "基础大纲生成",
                "category": "大纲生成",
                "description": "生成基础章节大纲框架",
                "parameters": ["genre", "theme", "target_words", "requirements"]
            },
            "OUTLINE_EXPANSION": {
                "name": "大纲展开",
                "category": "大纲生成",
                "description": "将单个大纲节点展开为多个章节",
                "parameters": ["title", "genre", "theme", "narrative_perspective", "time_period", "location", 
                             "atmosphere", "rules", "characters_info", "outline_order", "outline_title", 
                             "outline_content", "context_info", "strategy_instruction", "target_chapters", 
                             "scene_instruction", "scene_field"]
            },
            "CHAPTER_GENERATION": {
                "name": "章节创作",
                "category": "章节创作",
                "description": "根据大纲创作章节内容",
                "parameters": ["title", "theme", "genre", "narrative_perspective", "time_period", "location", 
                             "atmosphere", "rules", "characters_info", "outlines_context", "chapter_number", 
                             "chapter_title", "chapter_outline", "target_word_count", "max_word_count"]
            },
            "CHAPTER_GENERATION_WITH_CONTEXT": {
                "name": "章节创作（带上下文）",
                "category": "章节创作",
                "description": "基于前置章节内容创作新章节",
                "parameters": ["title", "theme", "genre", "narrative_perspective", "time_period", "location", 
                             "atmosphere", "rules", "characters_info", "outlines_context", "previous_content", 
                             "memory_context", "chapter_number", "chapter_title", "chapter_outline", 
                             "target_word_count", "max_word_count"]
            },
            "CHAPTER_REGENERATION_SYSTEM": {
                "name": "章节重写系统提示",
                "category": "章节重写",
                "description": "用于章节重写的系统提示词",
                "parameters": ["chapter_number", "title", "word_count", "content", "modification_instructions", 
                             "project_context", "style_content", "target_word_count"]
            },
            "AI_DENOISING": {
                "name": "AI去味",
                "category": "辅助功能",
                "description": "将AI生成的文本改写得更自然",
                "parameters": ["original_text"]
            },
            "PLOT_ANALYSIS": {
                "name": "情节分析",
                "category": "情节分析",
                "description": "深度分析章节的剧情、钩子、伏笔等",
                "parameters": ["chapter_number", "title", "content", "word_count"]
            },
            "PLOT_EXPANSION_SINGLE_BATCH": {
                "name": "大纲单批次展开",
                "category": "情节展开",
                "description": "将大纲节点展开为详细章节规划（单批次）",
                "parameters": ["project_title", "project_genre", "project_theme", "project_narrative_perspective", 
                             "project_world_time_period", "project_world_location", "project_world_atmosphere", 
                             "characters_info", "outline_order_index", "outline_title", "outline_content", 
                             "context_info", "strategy_instruction", "target_chapter_count", "scene_instruction", "scene_field"]
            },
            "PLOT_EXPANSION_MULTI_BATCH": {
                "name": "大纲分批展开",
                "category": "情节展开",
                "description": "将大纲节点展开为详细章节规划（分批）",
                "parameters": ["project_title", "project_genre", "project_theme", "project_narrative_perspective", 
                             "project_world_time_period", "project_world_location", "project_world_atmosphere", 
                             "characters_info", "outline_order_index", "outline_title", "outline_content", 
                             "context_info", "previous_context", "strategy_instruction", "start_index", 
                             "end_index", "target_chapter_count", "scene_instruction", "scene_field"]
            },
            "MCP_TOOL_TEST": {
                "name": "MCP工具测试",
                "category": "MCP测试",
                "description": "用于测试MCP插件功能",
                "parameters": ["plugin_name"]
            },
            "MCP_WORLD_BUILDING_PLANNING": {
                "name": "MCP世界观规划",
                "category": "MCP增强",
                "description": "使用MCP工具搜索资料辅助世界观设计",
                "parameters": ["title", "genre", "theme", "description"]
            },
            "MCP_CHARACTER_PLANNING": {
                "name": "MCP角色规划",
                "category": "MCP增强",
                "description": "使用MCP工具搜索资料辅助角色设计",
                "parameters": ["title", "genre", "theme", "time_period", "location"]
            }
        }
        
        for key, info in template_definitions.items():
            template_content = getattr(cls, key, None)
            if template_content:
                templates.append({
                    "template_key": key,
                    "template_name": info["name"],
                    "category": info["category"],
                    "description": info["description"],
                    "parameters": info["parameters"],
                    "content": template_content
                })
        
        return templates
    
    @classmethod
    def get_system_template_info(cls, template_key: str) -> dict:
        """
        获取指定系统模板的信息
        
        Args:
            template_key: 模板键名
            
        Returns:
            模板信息字典
        """
        all_templates = cls.get_all_system_templates()
        for template in all_templates:
            if template["template_key"] == template_key:
                return template
        return None
prompt_service = PromptService()