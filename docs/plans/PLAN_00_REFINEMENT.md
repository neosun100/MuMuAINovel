# 预案00: 章节二次优化系统 (Post-Generation Refinement)

> 版本: v2.1.0 | 优先级: 🔴 **TOP 1** | AI开发: 2-3天

---

## 0. 模型配置

### 0.1 LiteLLM 端点配置

```bash
# .env 文件配置

# 二次优化专用模型配置
REFINEMENT_API_BASE=https://litellm.aws.xin/v1/chat/completions
REFINEMENT_API_KEY=sk-y7wOGZxhZTgstCwsov2EzUXEzU

# 可选模型（二选一）
# 模型1: Claude Opus 4.5 (最高质量，推荐历史类小说)
REFINEMENT_MODEL=bedrock/anthropic.claude-opus-4-5-20251101-v1:0-64k-thinking

# 模型2: Claude Sonnet 4.5 (性价比高，速度更快)
# REFINEMENT_MODEL=bedrock/anthropic.claude-sonnet-4.5-20250929-v1:0-64k-1M-thinking
```

### 0.2 模型选择开关

```python
# backend/app/core/config.py

class RefinementConfig:
    """二次优化配置"""
    
    # API配置
    API_BASE: str = os.getenv("REFINEMENT_API_BASE", "https://litellm.aws.xin/v1/chat/completions")
    API_KEY: str = os.getenv("REFINEMENT_API_KEY", "")
    
    # 可用模型
    AVAILABLE_MODELS = {
        "opus": "bedrock/anthropic.claude-opus-4-5-20251101-v1:0-64k-thinking",
        "sonnet": "bedrock/anthropic.claude-sonnet-4.5-20250929-v1:0-64k-1M-thinking"
    }
    
    # 默认模型（可通过环境变量或API参数覆盖）
    DEFAULT_MODEL: str = os.getenv("REFINEMENT_MODEL", AVAILABLE_MODELS["opus"])
    
    @classmethod
    def get_model(cls, model_key: str = None) -> str:
        """
        获取模型名称
        
        Args:
            model_key: "opus" 或 "sonnet"，不传则使用默认
        """
        if model_key and model_key in cls.AVAILABLE_MODELS:
            return cls.AVAILABLE_MODELS[model_key]
        return cls.DEFAULT_MODEL
```

### 0.3 API调用方式

```python
# 使用 LiteLLM 端点调用

import httpx

async def call_refinement_model(prompt: str, model: str = None) -> str:
    """调用二次优化模型"""
    
    config = RefinementConfig()
    actual_model = config.get_model(model)
    
    async with httpx.AsyncClient(timeout=300) as client:
        response = await client.post(
            config.API_BASE,
            headers={
                "Authorization": f"Bearer {config.API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": actual_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 8000,
                "temperature": 0.3
            }
        )
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
```

---

## 1. 核心理念

### 1.1 问题分析

当前生成的100章存在以下问题：
- ❌ 部分历史细节不准确
- ❌ 偶尔出现章节末尾的"总结性文字"
- ❌ 角色行为偶有不一致
- ❌ 文笔可进一步提升
- ❌ 部分内容重复或冗余

### 1.2 解决方案

```
第一阶段: 批量生成 (已完成)
    ↓
第二阶段: 系统性二次优化 ← 本预案（三段论）
    ↓
最终输出: 高质量100章小说
```

### 1.3 核心原则

1. **串行优化**: 第N章优化时，第N-1章必须是已优化版本
2. **三段论**: 每章分3段优化，避免一次性输出导致遗漏/质量下降
3. **完整上下文**: 每段优化都携带完整固定上下文 + 已优化段落
4. **模型可选**: 支持指定高质量模型（o1/o3/claude-opus）
5. **自动化流程**: 无需人工干预，自动完成100章

---

## 1.5 原文保留机制

### 1.5.1 设计原则

**核心需求**: 优化后原文必须保留，支持对比和回滚

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         章节内容版本管理                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  优化前:                                                                    │
│    Chapter.content = "原始生成的内容..."                                    │
│    Chapter.is_refined = False                                               │
│                                                                             │
│  优化过程:                                                                  │
│    1. 创建 ChapterRefinement 记录                                           │
│    2. 备份: Chapter.content → ChapterRefinement.original_content            │
│    3. 三段论优化，保存每段原文和优化结果                                    │
│    4. 合并优化结果 → ChapterRefinement.refined_content                      │
│                                                                             │
│  优化后:                                                                    │
│    Chapter.content = "优化后的内容..."  ← 替换为优化版                      │
│    Chapter.is_refined = True            ← 标记已优化                        │
│    Chapter.refined_at = 2026-01-05      ← 优化时间                          │
│    Chapter.refinement_id = "xxx"        ← 关联优化记录                      │
│                                                                             │
│  数据保留:                                                                  │
│    ChapterRefinement.original_content = "原始内容"  ← 永久保留              │
│    ChapterRefinement.refined_content = "优化内容"                           │
│    ChapterRefinement.segment1_original = "原始第1段"                        │
│    ChapterRefinement.segment1_refined = "优化第1段"                         │
│    ... (第2、3段同理)                                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.5.2 Chapter 表扩展

```python
# 在 Chapter 模型中添加字段

class Chapter(Base):
    # ... 现有字段 ...
    
    # 新增：优化状态
    is_refined = Column(Boolean, default=False, index=True)  # 是否已优化
    refined_at = Column(DateTime, nullable=True)              # 优化时间
    refinement_id = Column(String(36), nullable=True)         # 关联优化记录ID
    refinement_model = Column(String(100), nullable=True)     # 使用的优化模型
```

### 1.5.3 UI 显示

```
章节列表显示:
┌────────────────────────────────────────────────────────────┐
│ 第1章  崇祯登基        12,345字   ✅ 已优化 (opus)         │
│ 第2章  朝堂风云        11,890字   ✅ 已优化 (opus)         │
│ 第3章  边关告急        10,567字   🔄 优化中 (第2段)        │
│ 第4章  调兵遣将        12,100字   ⏳ 待优化                │
│ ...                                                        │
└────────────────────────────────────────────────────────────┘

章节详情页:
┌────────────────────────────────────────────────────────────┐
│ 第1章 崇祯登基                                             │
│                                                            │
│ [当前版本] [查看原文] [对比视图] [回滚原文]                │
│                                                            │
│ 状态: ✅ 已优化                                            │
│ 优化时间: 2026-01-05 10:30                                 │
│ 使用模型: claude-opus-4.5                                  │
│ 原文字数: 12,000 → 优化后: 12,345 (+2.9%)                  │
│                                                            │
│ [内容区域...]                                              │
└────────────────────────────────────────────────────────────┘
```

### 1.5.4 回滚功能

```python
# API: 回滚到原文
@router.post("/refinement/chapter/{chapter_id}/rollback")
async def rollback_to_original(chapter_id: str):
    """将章节内容回滚到优化前的原文"""
    
    # 1. 获取优化记录
    refinement = await get_refinement_by_chapter(chapter_id)
    if not refinement:
        raise HTTPException(404, "未找到优化记录")
    
    # 2. 恢复原文
    chapter = await get_chapter(chapter_id)
    chapter.content = refinement.original_content
    chapter.is_refined = False
    chapter.refined_at = None
    
    await db.commit()
    
    return {"status": "rolled_back", "word_count": len(refinement.original_content)}
```

---

## 2. 三段论优化流程

### 2.1 为什么需要三段论

**问题**: 一次性让模型优化1万-1.8万字，风险很大：
- 模型可能遗漏段落
- 后半部分质量下降
- 结尾草草收场
- 字数严重缩水

**解决方案**: 将原文分成3段（40%/40%/20%），逐段优化，每段携带：
- 完整固定上下文（背景、角色、骨架、上章、大纲）
- 已优化的前面段落（确保衔接）
- 后续段落摘要（让模型知道走向）

### 2.2 单章优化完整流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    单章二次优化完整流程（三段论）                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  输入: 第N章原文 (12000字) + 第N-1章优化版 + 项目上下文                      │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│  第1段优化 (40%)                                                            │
│  ═══════════════════════════════════════════════════════════════════════   │
│  输入 (~32K tokens):                                                        │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │ [固定上下文 11.5K字]                                             │     │
│    │   • 项目背景/世界观 (2K)                                         │     │
│    │   • 涉及角色档案 (1K)                                            │     │
│    │   • 故事骨架/前情摘要 (3K)                                       │     │
│    │   • 上一章(N-1)优化版结尾 (5K)                                   │     │
│    │   • 本章大纲 (0.5K)                                              │     │
│    ├─────────────────────────────────────────────────────────────────┤     │
│    │ [本段内容]                                                       │     │
│    │   • 原文第1段 (4.8K) ← 待优化                                    │     │
│    │   • 原文第2-3段摘要 (0.5K) ← 让模型知道后续走向                  │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│  输出: 优化后第1段 (~4.8K字)                                                │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│  第2段优化 (40%)                                                            │
│  ═══════════════════════════════════════════════════════════════════════   │
│  输入 (~40K tokens):                                                        │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │ [固定上下文 11.5K字] ← 完整重复                                  │     │
│    ├─────────────────────────────────────────────────────────────────┤     │
│    │ [已优化内容]                                                     │     │
│    │   • 优化后第1段完整 (4.8K) ← 确保衔接                            │     │
│    ├─────────────────────────────────────────────────────────────────┤     │
│    │ [本段内容]                                                       │     │
│    │   • 原文第2段 (4.8K) ← 待优化                                    │     │
│    │   • 原文第3段摘要 (0.3K)                                         │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│  输出: 优化后第2段 (~4.8K字)                                                │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│  第3段优化 (20%) - 结尾段特殊处理                                           │
│  ═══════════════════════════════════════════════════════════════════════   │
│  输入 (~43K tokens):                                                        │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │ [固定上下文 11.5K字] ← 完整重复                                  │     │
│    ├─────────────────────────────────────────────────────────────────┤     │
│    │ [已优化内容]                                                     │     │
│    │   • 优化后第1段完整 (4.8K)                                       │     │
│    │   • 优化后第2段完整 (4.8K)                                       │     │
│    ├─────────────────────────────────────────────────────────────────┤     │
│    │ [本段内容]                                                       │     │
│    │   • 原文第3段 (2.4K) ← 待优化                                    │     │
│    │   • ⚠️ 特殊指令: 悬念结尾，绝对禁止总结                          │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│  输出: 优化后第3段 (~2.4K字)                                                │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│  合并 & 后处理                                                              │
│  ═══════════════════════════════════════════════════════════════════════   │
│  优化后第1段 + 优化后第2段 + 优化后第3段 = 完整优化章节 (~12K字)            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 100章串行优化流程

```
第1章: [固定上下文] + [原文三段] → 三段论优化 → 保存优化版
   ↓
第2章: [固定上下文] + [第1章优化版结尾] + [原文三段] → 三段论优化
   ↓
第3章: [固定上下文] + [第2章优化版结尾] + [原文三段] → 三段论优化
   ↓
...
   ↓
第100章: 完成全部优化
```

---

## 3. 模型选择机制

### 3.1 优先级规则

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           模型选择优先级（从高到低）                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. 调用时指定 model 参数 (最高优先级)                                       │
│     └─ novel_refine_chapter(chapter_id="xxx", model="o1")                  │
│     └─ POST /api/refinement/chapter/xxx {"model": "o1"}                    │
│                                                                             │
│  2. 环境变量 REFINEMENT_MODEL                                               │
│     └─ export REFINEMENT_MODEL=claude-3.5-sonnet                           │
│     └─ 适合批量优化时统一指定高质量模型                                      │
│                                                                             │
│  3. 项目默认模型 (project.default_model)                                    │
│     └─ 项目设置中配置的默认AI模型                                           │
│     └─ 如果项目用 gpt-4o 生成，优化时也默认用 gpt-4o                        │
│                                                                             │
│  4. 系统默认模型 (DEFAULT_MODEL)                                            │
│     └─ .env 中配置的系统默认模型                                            │
│     └─ 兜底选项                                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 推荐模型配置

| 场景 | 推荐模型 | 原因 | 单章成本 |
|------|---------|------|---------|
| 历史类小说 | o1 / o3 | 推理能力强，事实准确 | $2.93 |
| 文学性强 | claude-3.5-opus | 文笔优美 | $2.50 |
| 成本敏感 | gpt-4o | 性价比高 | $0.80 |
| 最高质量 | o3 | 最强推理 | $8.00 |

### 3.3 代码实现

```python
def _get_model(
    self,
    specified_model: str = None,
    project: Project = None
) -> str:
    """
    获取优化模型
    优先级: 指定 > 环境变量 > 项目默认 > 系统默认
    """
    # 1. 调用时指定
    if specified_model:
        return specified_model
    
    # 2. 环境变量
    env_model = os.getenv("REFINEMENT_MODEL")
    if env_model:
        return env_model
    
    # 3. 项目默认模型
    if project and project.default_model:
        return project.default_model
    
    # 4. 系统默认模型
    return os.getenv("DEFAULT_MODEL", "gpt-4o")
```

---

## 4. 成本估算

### 4.1 详细计算

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        三段论真实成本计算 (o1模型)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  第1段:                                                                     │
│    输入: 固定上下文11.5K + 原文段1(4.8K) + 摘要(0.5K) = 16.8K字 ≈ 32K tokens│
│    输出: 优化后段1 ≈ 4.8K字 ≈ 8K tokens                                     │
│    成本: 32K×$15/M + 8K×$60/M = $0.48 + $0.48 = $0.96                      │
│                                                                             │
│  第2段:                                                                     │
│    输入: 固定上下文11.5K + 优化段1(4.8K) + 原文段2(4.8K) + 摘要(0.3K)       │
│         = 21.4K字 ≈ 40K tokens                                              │
│    输出: 优化后段2 ≈ 4.8K字 ≈ 8K tokens                                     │
│    成本: 40K×$15/M + 8K×$60/M = $0.60 + $0.48 = $1.08                      │
│                                                                             │
│  第3段:                                                                     │
│    输入: 固定上下文11.5K + 优化段1(4.8K) + 优化段2(4.8K) + 原文段3(2.4K)    │
│         = 23.5K字 ≈ 43K tokens                                              │
│    输出: 优化后段3 ≈ 2.4K字 ≈ 4K tokens                                     │
│    成本: 43K×$15/M + 4K×$60/M = $0.65 + $0.24 = $0.89                      │
│                                                                             │
│  ───────────────────────────────────────────────────────────────────────   │
│  单章总计: $0.96 + $1.08 + $0.89 = $2.93                                    │
│  100章总计: $293                                                            │
│  加上重试(~10%): ~$320                                                      │
│  开发测试: ~$30                                                             │
│  总预算: ~$350                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 方案对比

| 方案 | 输入tokens | 输出tokens | 单章成本 | 100章成本 | 质量 | 风险 |
|------|-----------|-----------|---------|----------|------|------|
| 一次性优化 | 43K | 20K | $1.85 | $185 | 中 | 高 |
| **三段论** | 115K | 20K | $2.93 | $293 | **高** | **低** |
| 差异 | +168% | 0% | +58% | +$108 | ↑↑ | ↓↓ |

**结论**: 用 +$108 换取显著质量提升和风险降低，值得。

---

## 5. 提示词设计（核心中的核心）

> ⚠️ 提示词是二次优化质量的关键，需要精心设计

### 5.1 提示词设计原则

1. **明确角色定位**: 资深小说编辑，而非作者
2. **强调"优化"而非"重写"**: 保持原意，提升质量
3. **具体化优化方向**: 历史准确性、文笔、细节、衔接
4. **明确禁止事项**: 总结性文字、改变情节、字数大幅变化
5. **分段特殊处理**: 结尾段有额外要求

### 5.2 第1段优化提示词

```python
SEGMENT1_PROMPT_TEMPLATE = """# 角色设定
你是一位资深小说编辑，专门负责长篇历史小说的深度优化工作。你的任务是在保持原文核心情节和风格的基础上，提升文章质量。

# 当前任务
优化《{project_title}》第{chapter_number}章《{chapter_title}》的【第1部分】（约占全章40%）

---

# 背景信息

## 小说基本信息
{background}

## 本章涉及的主要角色
{characters}

## 前情摘要（故事骨架）
{story_skeleton}

## 上一章结尾（第{prev_chapter_number}章优化版）
{previous_chapter_ending}

## 本章大纲
{outline}

---

# 待优化内容

## 原文第1部分（{segment1_word_count}字）
{segment1_content}

## 后续内容摘要（供参考，确保连贯）
第2部分开头：{segment2_summary}
第3部分开头：{segment3_summary}

---

# 优化要求

## 1. 修正错误（最重要）
- 修正任何历史事实错误（年代、人物、事件、官职、地名等）
- 修正时间线矛盾（与前文不符的时间描述）
- 修正角色行为不一致（性格、能力、立场与设定不符）
- 修正逻辑漏洞（因果关系、空间移动等）

## 2. 提升文笔
- 优化句式结构，避免重复单调
- 丰富环境描写（视觉、听觉、嗅觉、触觉）
- 增强动作描写的画面感
- 优化对话的自然度和个性化
- 增强情感表达的细腻度

## 3. 保持连贯
- 确保与上一章结尾自然衔接（语气、情绪、场景）
- 保持角色性格一致
- 保持叙事风格统一（第三人称、过去时等）

## 4. 字数控制
- 原文约{segment1_word_count}字
- 优化后应在{min_words}-{max_words}字（±10%）
- 不要大幅删减或扩充

## 5. 绝对禁止
- ❌ 不要改变核心情节走向
- ❌ 不要添加原文没有的重要情节
- ❌ 不要改变人物关系
- ❌ 这是第1部分，后面还有内容，不要写成结尾的感觉
- ❌ 不要添加任何说明、注释、点评
- ❌ 不要输出"优化后："等前缀

---

# 输出要求
直接输出优化后的第1部分内容，保持原有的段落结构。
"""
```

### 5.3 第2段优化提示词

```python
SEGMENT2_PROMPT_TEMPLATE = """# 角色设定
你是一位资深小说编辑，正在继续优化《{project_title}》第{chapter_number}章《{chapter_title}》。

# 当前任务
优化【第2部分】（约占全章40%），确保与已优化的第1部分自然衔接。

---

# 背景信息

## 小说基本信息
{background}

## 本章涉及的主要角色
{characters}

## 前情摘要（故事骨架）
{story_skeleton}

## 上一章结尾（第{prev_chapter_number}章优化版）
{previous_chapter_ending}

## 本章大纲
{outline}

---

# 已完成内容

## 已优化的第1部分（{segment1_refined_word_count}字）
{segment1_refined}

---

# 待优化内容

## 原文第2部分（{segment2_word_count}字）
{segment2_content}

## 后续内容摘要
第3部分开头：{segment3_summary}

---

# 优化要求

## 1. 衔接第1部分
- 语气、节奏与第1部分保持一致
- 情节发展自然承接
- 不要重复第1部分已经描述的内容

## 2. 修正错误
- 历史事实、时间线、角色行为、逻辑漏洞

## 3. 提升文笔
- 句式、环境描写、动作描写、对话、情感

## 4. 字数控制
- 原文约{segment2_word_count}字
- 优化后应在{min_words}-{max_words}字（±10%）

## 5. 绝对禁止
- ❌ 不要改变核心情节
- ❌ 这是第2部分，后面还有结尾，不要写成结尾的感觉
- ❌ 不要添加任何说明、注释
- ❌ 不要与第1部分内容重复

---

# 输出要求
直接输出优化后的第2部分内容。
"""
```

### 5.4 第3段优化提示词（结尾段，特殊处理）

```python
SEGMENT3_PROMPT_TEMPLATE = """# 角色设定
你是一位资深小说编辑，正在完成《{project_title}》第{chapter_number}章《{chapter_title}》的最后优化。

# 当前任务
优化【结尾部分】（约占全章20%），这是本章的收尾，需要特别注意结尾处理。

---

# 背景信息

## 小说基本信息
{background}

## 本章涉及的主要角色
{characters}

## 前情摘要（故事骨架）
{story_skeleton}

## 上一章结尾（第{prev_chapter_number}章优化版）
{previous_chapter_ending}

## 本章大纲
{outline}

---

# 已完成内容

## 已优化的第1部分
{segment1_refined}

## 已优化的第2部分
{segment2_refined}

---

# 待优化内容

## 原文结尾部分（{segment3_word_count}字）
{segment3_content}

---

# 优化要求

## 1. 衔接前文
- 与第2部分自然衔接
- 情节发展符合逻辑
- 不要重复前面已描述的内容

## 2. 修正错误
- 历史事实、时间线、角色行为、逻辑漏洞

## 3. 提升文笔
- 句式、环境描写、动作描写、对话、情感

## 4. ⚠️ 结尾处理（极其重要）

### 必须做到：
- ✅ 以悬念结尾（留下未解决的问题或冲突）
- ✅ 或以情感高点结尾（强烈的情感冲击）
- ✅ 或以转折结尾（意外的发展）
- ✅ 让读者产生"想继续看下一章"的欲望

### 绝对禁止：
- ❌ 禁止出现"本章讲述了..."、"至此..."等总结性文字
- ❌ 禁止出现"欲知后事如何，请看下回分解"
- ❌ 禁止出现"综上所述"、"总而言之"、"总之"
- ❌ 禁止出现"（本章完）"、"（未完待续）"
- ❌ 禁止对本章内容进行任何形式的回顾或总结
- ❌ 禁止使用"这一天"、"这一夜"等收束性时间词作为结尾

### 好的结尾示例：
- "城门缓缓关闭，崇祯望着远去的背影，眼中闪过一丝复杂的神色。"
- "就在此时，一名信使飞马而来，高喊道：'八百里加急！'"
- "他不知道的是，此刻的辽东，一场更大的风暴正在酝酿。"

## 5. 字数控制
- 原文约{segment3_word_count}字
- 优化后应在{min_words}-{max_words}字（±10%）

---

# 输出要求
直接输出优化后的结尾部分内容。记住：以悬念、高潮或转折结尾，绝对不要总结！
"""
```

### 5.5 提示词变量说明

| 变量 | 来源 | 说明 |
|------|------|------|
| `{project_title}` | Project.title | 小说标题 |
| `{chapter_number}` | Chapter.chapter_number | 章节号 |
| `{chapter_title}` | Chapter.title | 章节标题 |
| `{background}` | 构建函数 | 项目背景+世界观 |
| `{characters}` | 构建函数 | 本章涉及角色 |
| `{story_skeleton}` | 构建函数 | 前情摘要 |
| `{previous_chapter_ending}` | 上章优化版 | 上章结尾5000字 |
| `{outline}` | Outline.content | 本章大纲 |
| `{segment1_content}` | 分段函数 | 原文第1段 |
| `{segment1_refined}` | 优化结果 | 优化后第1段 |
| `{segment2_summary}` | 摘要函数 | 第2段前200字 |
| `{min_words}` | 计算 | 原字数×0.9 |
| `{max_words}` | 计算 | 原字数×1.1 |

---

## 6. 数据模型

### 6.1 ChapterRefinement 表

```python
# backend/app/models/refinement.py

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base

class ChapterRefinement(Base):
    """章节优化记录表"""
    __tablename__ = "chapter_refinements"
    
    id = Column(String(36), primary_key=True)
    chapter_id = Column(String(36), ForeignKey("chapters.id"), index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), index=True)
    chapter_number = Column(Integer)
    
    # 版本管理
    version = Column(Integer, default=1)
    
    # 原始内容
    original_content = Column(Text)
    original_word_count = Column(Integer)
    
    # 三段分段结果
    segment1_original = Column(Text)
    segment1_refined = Column(Text)
    segment1_word_count = Column(Integer)
    
    segment2_original = Column(Text)
    segment2_refined = Column(Text)
    segment2_word_count = Column(Integer)
    
    segment3_original = Column(Text)
    segment3_refined = Column(Text)
    segment3_word_count = Column(Integer)
    
    # 最终合并内容
    refined_content = Column(Text)
    refined_word_count = Column(Integer)
    
    # 模型信息
    model_used = Column(String(50))
    
    # 状态: pending / segment1 / segment2 / segment3 / merging / completed / failed
    status = Column(String(20), default="pending", index=True)
    current_segment = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # 时间
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime, nullable=True)
```

### 6.2 数据库迁移

```python
# alembic/versions/xxxx_add_chapter_refinement.py

def upgrade():
    op.create_table(
        'chapter_refinements',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('chapter_id', sa.String(36), sa.ForeignKey('chapters.id')),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id')),
        sa.Column('chapter_number', sa.Integer),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('original_content', sa.Text),
        sa.Column('original_word_count', sa.Integer),
        sa.Column('segment1_original', sa.Text),
        sa.Column('segment1_refined', sa.Text),
        sa.Column('segment1_word_count', sa.Integer),
        sa.Column('segment2_original', sa.Text),
        sa.Column('segment2_refined', sa.Text),
        sa.Column('segment2_word_count', sa.Integer),
        sa.Column('segment3_original', sa.Text),
        sa.Column('segment3_refined', sa.Text),
        sa.Column('segment3_word_count', sa.Integer),
        sa.Column('refined_content', sa.Text),
        sa.Column('refined_word_count', sa.Integer),
        sa.Column('model_used', sa.String(50)),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('current_segment', sa.Integer, default=0),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime, nullable=True),
    )
    op.create_index('ix_chapter_refinements_chapter_id', 'chapter_refinements', ['chapter_id'])
    op.create_index('ix_chapter_refinements_project_id', 'chapter_refinements', ['project_id'])
    op.create_index('ix_chapter_refinements_status', 'chapter_refinements', ['status'])

def downgrade():
    op.drop_table('chapter_refinements')
```

---

## 7. 核心服务实现

### 7.1 分段工具函数

```python
# backend/app/services/refinement_service.py

from typing import List, Dict

def split_chapter_for_refinement(content: str) -> List[Dict]:
    """
    将章节分成3段用于优化
    分段比例: 40% / 40% / 20%
    在段落边界处切分，不破坏句子
    """
    total_length = len(content)
    
    # 目标切分点
    target_seg1_end = int(total_length * 0.4)
    target_seg2_end = int(total_length * 0.8)
    
    # 在段落边界处切分
    seg1_end = _find_best_split_point(content, target_seg1_end)
    seg2_end = _find_best_split_point(content, target_seg2_end)
    
    return [
        {
            "segment": 1,
            "content": content[:seg1_end].strip(),
            "word_count": len(content[:seg1_end].strip()),
            "is_ending": False
        },
        {
            "segment": 2,
            "content": content[seg1_end:seg2_end].strip(),
            "word_count": len(content[seg1_end:seg2_end].strip()),
            "is_ending": False
        },
        {
            "segment": 3,
            "content": content[seg2_end:].strip(),
            "word_count": len(content[seg2_end:].strip()),
            "is_ending": True
        }
    ]


def _find_best_split_point(content: str, target: int, search_range: int = 500) -> int:
    """
    在目标位置附近找最佳切分点
    优先级: 双换行 > 单换行 > 句号
    """
    start = max(0, target - search_range)
    end = min(len(content), target + search_range)
    search_area = content[start:end]
    
    # 优先找双换行（段落边界）
    pos = search_area.rfind('\n\n')
    if pos != -1:
        return start + pos + 2
    
    # 其次找单换行
    pos = search_area.rfind('\n')
    if pos != -1:
        return start + pos + 1
    
    # 最后找句号
    for punct in ['。', '！', '？', '.', '!', '?']:
        pos = search_area.rfind(punct)
        if pos != -1:
            return start + pos + 1
    
    return target


def generate_segment_summary(content: str, max_chars: int = 200) -> str:
    """生成段落摘要，让模型知道后续走向"""
    summary = content[:max_chars]
    
    # 在句子边界截断
    for punct in ['。', '！', '？', '.', '!', '?']:
        last_punct = summary.rfind(punct)
        if last_punct > max_chars * 0.5:
            summary = summary[:last_punct + 1]
            break
    
    return summary + "..."
```

### 7.2 核心优化服务

```python
# backend/app/services/refinement_service.py

import os
import uuid
from datetime import datetime
from typing import Dict, Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refinement import ChapterRefinement
from app.models.chapter import Chapter
from app.models.project import Project


class ChapterRefinementService:
    """章节二次优化服务 - 三段论实现"""
    
    def __init__(self, db: AsyncSession, ai_service):
        self.db = db
        self.ai = ai_service
    
    # ==================== 模型选择 ====================
    
    def _get_model(
        self,
        specified_model: str = None,
        project: Project = None
    ) -> str:
        """
        获取优化模型
        优先级: 指定 > 环境变量 > 项目默认 > 系统默认
        """
        if specified_model:
            return specified_model
        
        env_model = os.getenv("REFINEMENT_MODEL")
        if env_model:
            return env_model
        
        if project and project.default_model:
            return project.default_model
        
        return os.getenv("DEFAULT_MODEL", "gpt-4o")
    
    # ==================== 单章优化（三段论） ====================
    
    async def refine_chapter(
        self,
        chapter_id: str,
        previous_refined_content: str = None,
        model: str = None
    ) -> Dict:
        """
        优化单个章节（三段论）
        
        Args:
            chapter_id: 章节ID
            previous_refined_content: 上一章优化后的内容（用于衔接）
            model: 指定模型（可选）
        
        Returns:
            优化结果
        """
        # 1. 获取章节和项目
        chapter = await self._get_chapter(chapter_id)
        project = await self._get_project(chapter.project_id)
        
        # 2. 确定使用的模型
        actual_model = self._get_model(model, project)
        
        # 3. 构建固定上下文（三段共用）
        fixed_context = await self._build_fixed_context(
            chapter=chapter,
            project=project,
            previous_refined=previous_refined_content
        )
        
        # 4. 分段
        segments = split_chapter_for_refinement(chapter.content)
        
        # 5. 创建优化记录
        refinement = await self._create_refinement_record(
            chapter=chapter,
            segments=segments,
            model=actual_model
        )
        
        # 6. 逐段优化
        refined_segments = []
        
        try:
            for i, seg in enumerate(segments):
                # 更新状态
                await self._update_status(refinement.id, f"segment{i+1}", i+1)
                
                # 优化当前段
                refined = await self._refine_single_segment(
                    segment_index=i,
                    segment_content=seg["content"],
                    fixed_context=fixed_context,
                    chapter=chapter,
                    refined_segments=refined_segments,
                    remaining_segments=segments[i+1:],
                    model=actual_model
                )
                
                # 保存段落结果
                refined_segments.append(refined)
                await self._save_segment_result(
                    refinement_id=refinement.id,
                    segment_num=i+1,
                    original=seg["content"],
                    refined=refined
                )
            
            # 7. 合并
            await self._update_status(refinement.id, "merging", 3)
            final_content = "\n\n".join(refined_segments)
            
            # 8. 后处理
            final_content = self._post_process(final_content)
            
            # 9. 保存最终结果
            await self._save_final_result(refinement.id, final_content)
            
            # 10. 更新章节内容
            await self._update_chapter_content(chapter_id, final_content)
            
            return {
                "chapter_id": chapter_id,
                "chapter_number": chapter.chapter_number,
                "original_words": len(chapter.content),
                "refined_words": len(final_content),
                "model_used": actual_model,
                "segments_processed": 3,
                "status": "completed"
            }
            
        except Exception as e:
            await self._mark_failed(refinement.id, str(e))
            raise
    
    # ==================== 单段优化 ====================
    
    async def _refine_single_segment(
        self,
        segment_index: int,
        segment_content: str,
        fixed_context: Dict,
        chapter: Chapter,
        refined_segments: List[str],
        remaining_segments: List[Dict],
        model: str
    ) -> str:
        """优化单个段落"""
        
        # 构建提示词
        if segment_index == 0:
            prompt = self._build_segment1_prompt(
                fixed_context=fixed_context,
                chapter=chapter,
                segment_content=segment_content,
                remaining_segments=remaining_segments
            )
        elif segment_index == 1:
            prompt = self._build_segment2_prompt(
                fixed_context=fixed_context,
                chapter=chapter,
                segment1_refined=refined_segments[0],
                segment_content=segment_content,
                remaining_segments=remaining_segments
            )
        else:
            prompt = self._build_segment3_prompt(
                fixed_context=fixed_context,
                chapter=chapter,
                segment1_refined=refined_segments[0],
                segment2_refined=refined_segments[1],
                segment_content=segment_content
            )
        
        # 调用模型
        result = await self.ai.generate(
            prompt=prompt,
            model=model,
            max_tokens=8000,
            temperature=0.3
        )
        
        return self._clean_output(result)
    
    # ==================== 批量优化 ====================
    
    async def refine_all_chapters(
        self,
        project_id: str,
        start_chapter: int = 1,
        end_chapter: int = 100,
        model: str = None
    ) -> AsyncGenerator[Dict, None]:
        """
        串行优化所有章节
        第N章优化时使用第N-1章的优化版作为上下文
        """
        previous_refined = None
        
        for chapter_num in range(start_chapter, end_chapter + 1):
            chapter = await self._get_chapter_by_number(project_id, chapter_num)
            
            if not chapter:
                yield {
                    "chapter": chapter_num,
                    "status": "skipped",
                    "reason": "not found"
                }
                continue
            
            try:
                result = await self.refine_chapter(
                    chapter_id=chapter.id,
                    previous_refined_content=previous_refined,
                    model=model
                )
                
                # 更新 previous_refined 为当前优化后的内容
                previous_refined = await self._get_refined_content(chapter.id)
                
                yield {
                    "chapter": chapter_num,
                    "status": "completed",
                    **result
                }
                
            except Exception as e:
                yield {
                    "chapter": chapter_num,
                    "status": "failed",
                    "error": str(e)
                }
                # 失败时使用原文作为 previous
                previous_refined = chapter.content
    
    # ==================== 上下文构建 ====================
    
    async def _build_fixed_context(
        self,
        chapter: Chapter,
        project: Project,
        previous_refined: str = None
    ) -> Dict:
        """构建固定上下文（三段共用）"""
        
        context = {}
        
        # 1. 项目背景 (~2000字)
        context["background"] = f"""【小说信息】
标题: {project.title}
类型: {project.genre}
简介: {project.description}

【世界观】
时代: {project.world_time_period or '未设定'}
地点: {project.world_location or '未设定'}
氛围: {project.world_atmosphere or '未设定'}
规则: {project.world_rules or '未设定'}
"""
        
        # 2. 涉及角色 (~1000字)
        involved_chars = await self._get_involved_characters(chapter)
        context["characters"] = self._format_characters(involved_chars)
        
        # 3. 故事骨架 (~3000字)
        if chapter.chapter_number > 1:
            summaries = await self._get_chapter_summaries(
                project_id=project.id,
                end_chapter=chapter.chapter_number - 1
            )
            context["story_skeleton"] = self._format_summaries(summaries)
        else:
            context["story_skeleton"] = "（第一章，无前文）"
        
        # 4. 上一章优化版结尾 (~5000字)
        if previous_refined:
            context["previous_chapter"] = previous_refined[-5000:] if len(previous_refined) > 5000 else previous_refined
            context["prev_chapter_number"] = chapter.chapter_number - 1
        else:
            context["previous_chapter"] = "（第一章，无前文）"
            context["prev_chapter_number"] = 0
        
        # 5. 本章大纲
        outline = await self._get_outline(chapter.outline_id)
        context["outline"] = outline.content if outline else "（无大纲）"
        
        return context
    
    # ==================== 后处理 ====================
    
    def _post_process(self, content: str) -> str:
        """后处理：清理格式问题"""
        import re
        
        # 移除可能的前缀
        prefixes = [
            "优化后：", "优化后的内容：", "以下是优化后的内容：",
            "【优化后】", "---", "```"
        ]
        for prefix in prefixes:
            if content.startswith(prefix):
                content = content[len(prefix):].strip()
        
        # 移除可能的后缀总结
        patterns = [
            r'\n\n【本章总结】.*$',
            r'\n\n本章讲述了.*$',
            r'\n\n---\n.*$',
            r'\n\n综上所述.*$',
        ]
        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        return content.strip()
    
    def _clean_output(self, output: str) -> str:
        """清理单段输出"""
        # 移除可能的markdown代码块
        if output.startswith("```"):
            lines = output.split("\n")
            output = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        
        return output.strip()
```


---

## 8. API 接口

### 8.1 接口定义

```python
# backend/app/api/refinement.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.services.refinement_service import ChapterRefinementService
from app.schemas.refinement import (
    RefinementRequest,
    RefinementResult,
    BatchRefinementRequest,
    RefinementStatus
)

router = APIRouter(prefix="/api/refinement", tags=["refinement"])


@router.post("/chapter/{chapter_id}", response_model=RefinementResult)
async def refine_single_chapter(
    chapter_id: str,
    request: RefinementRequest = None,
    db: AsyncSession = Depends(get_db),
    ai_service = Depends(get_ai_service)
):
    """
    优化单个章节（三段论）
    
    - 可选指定模型，不指定则使用默认模型
    - 返回优化结果
    """
    service = ChapterRefinementService(db, ai_service)
    
    model = request.model if request else None
    
    result = await service.refine_chapter(
        chapter_id=chapter_id,
        model=model
    )
    
    return result


@router.post("/project/{project_id}/all")
async def refine_all_chapters(
    project_id: str,
    request: BatchRefinementRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    ai_service = Depends(get_ai_service)
):
    """
    批量优化所有章节（后台任务）
    
    - 串行处理，第N章使用第N-1章优化版作为上下文
    - 可选指定模型
    - 返回任务ID，通过 /status 接口查询进度
    """
    service = ChapterRefinementService(db, ai_service)
    
    # 创建后台任务
    task_id = str(uuid.uuid4())
    
    background_tasks.add_task(
        _run_batch_refinement,
        service=service,
        project_id=project_id,
        start_chapter=request.start_chapter or 1,
        end_chapter=request.end_chapter or 100,
        model=request.model,
        task_id=task_id
    )
    
    return {
        "task_id": task_id,
        "status": "started",
        "message": f"开始优化第{request.start_chapter or 1}-{request.end_chapter or 100}章"
    }


@router.get("/project/{project_id}/status", response_model=RefinementStatus)
async def get_refinement_status(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取优化进度
    
    返回:
    - total: 总章节数
    - completed: 已完成数
    - failed: 失败数
    - current_chapter: 当前处理章节
    - current_segment: 当前处理段落 (1/2/3)
    """
    # 查询优化记录
    result = await db.execute(
        select(ChapterRefinement)
        .where(ChapterRefinement.project_id == project_id)
        .order_by(ChapterRefinement.chapter_number.desc())
    )
    refinements = result.scalars().all()
    
    completed = sum(1 for r in refinements if r.status == "completed")
    failed = sum(1 for r in refinements if r.status == "failed")
    
    # 找当前处理中的
    processing = next((r for r in refinements if r.status not in ["completed", "failed"]), None)
    
    return {
        "total": len(refinements),
        "completed": completed,
        "failed": failed,
        "current_chapter": processing.chapter_number if processing else None,
        "current_segment": processing.current_segment if processing else None,
        "status": "processing" if processing else ("completed" if completed > 0 else "idle")
    }


@router.get("/chapter/{chapter_id}/diff")
async def get_refinement_diff(
    chapter_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取优化前后对比
    
    返回原文和优化后内容，以及各段落对比
    """
    result = await db.execute(
        select(ChapterRefinement)
        .where(ChapterRefinement.chapter_id == chapter_id)
        .order_by(ChapterRefinement.version.desc())
        .limit(1)
    )
    refinement = result.scalar_one_or_none()
    
    if not refinement:
        raise HTTPException(404, "未找到优化记录")
    
    return {
        "chapter_id": chapter_id,
        "version": refinement.version,
        "model_used": refinement.model_used,
        "original_word_count": refinement.original_word_count,
        "refined_word_count": refinement.refined_word_count,
        "segments": [
            {
                "segment": 1,
                "original": refinement.segment1_original,
                "refined": refinement.segment1_refined
            },
            {
                "segment": 2,
                "original": refinement.segment2_original,
                "refined": refinement.segment2_refined
            },
            {
                "segment": 3,
                "original": refinement.segment3_original,
                "refined": refinement.segment3_refined
            }
        ],
        "status": refinement.status
    }
```

### 8.2 Schemas

```python
# backend/app/schemas/refinement.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class RefinementRequest(BaseModel):
    model: Optional[str] = None  # 可选指定模型


class BatchRefinementRequest(BaseModel):
    start_chapter: Optional[int] = 1
    end_chapter: Optional[int] = 100
    model: Optional[str] = None  # 可选指定模型


class RefinementResult(BaseModel):
    chapter_id: str
    chapter_number: int
    original_words: int
    refined_words: int
    model_used: str
    segments_processed: int
    status: str


class RefinementStatus(BaseModel):
    total: int
    completed: int
    failed: int
    current_chapter: Optional[int]
    current_segment: Optional[int]
    status: str  # idle / processing / completed


class SegmentDiff(BaseModel):
    segment: int
    original: str
    refined: str


class RefinementDiff(BaseModel):
    chapter_id: str
    version: int
    model_used: str
    original_word_count: int
    refined_word_count: int
    segments: List[SegmentDiff]
    status: str
```

---

## 9. MCP 工具

### 9.1 工具定义

```python
# mcp_novel_server.py 中添加

# ==================== 二次优化工具 ====================

Tool(
    name="novel_refine_chapter",
    description="""优化单个章节（三段论）
    
使用高质量模型对已生成的章节进行深度优化：
- 修正历史/事实错误
- 提升文笔质量
- 删除总结性文字
- 确保与上下文衔接

可选指定模型（o1/o3/claude-3.5-opus等），不指定则使用项目默认模型。
""",
    inputSchema={
        "type": "object",
        "properties": {
            "chapter_id": {
                "type": "string",
                "description": "章节ID"
            },
            "model": {
                "type": "string",
                "description": "可选：指定优化模型（如 o1, o3, claude-3.5-opus）",
                "enum": ["o1", "o3", "gpt-4o", "claude-3.5-sonnet", "claude-3.5-opus"]
            }
        },
        "required": ["chapter_id"]
    }
),

Tool(
    name="novel_refine_all",
    description="""串行优化项目所有章节（三段论）
    
批量优化指定范围的章节：
- 串行处理，第N章优化时使用第N-1章的优化版作为上下文
- 每章分3段优化，确保质量
- 可选指定模型

注意：这是一个耗时操作，100章约需5-8小时。
""",
    inputSchema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "string",
                "description": "项目ID"
            },
            "start_chapter": {
                "type": "integer",
                "description": "起始章节号（默认1）",
                "default": 1
            },
            "end_chapter": {
                "type": "integer",
                "description": "结束章节号（默认100）",
                "default": 100
            },
            "model": {
                "type": "string",
                "description": "可选：指定优化模型"
            }
        },
        "required": ["project_id"]
    }
),

Tool(
    name="novel_refine_status",
    description="""查询优化进度
    
返回：
- 总章节数、已完成数、失败数
- 当前处理的章节和段落
- 整体状态
""",
    inputSchema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "string",
                "description": "项目ID"
            }
        },
        "required": ["project_id"]
    }
)
```

### 9.2 工具处理函数

```python
# mcp_novel_server.py 中添加处理逻辑

async def handle_novel_refine_chapter(arguments: dict) -> str:
    """处理单章优化"""
    chapter_id = arguments["chapter_id"]
    model = arguments.get("model")
    
    url = f"{BASE_URL}/api/refinement/chapter/{chapter_id}"
    payload = {"model": model} if model else {}
    
    async with httpx.AsyncClient(timeout=600) as client:  # 10分钟超时
        response = await client.post(url, json=payload, headers=get_headers())
        
        if response.status_code == 200:
            result = response.json()
            return f"""✅ 章节优化完成

章节: 第{result['chapter_number']}章
原文字数: {result['original_words']}
优化后字数: {result['refined_words']}
使用模型: {result['model_used']}
处理段数: {result['segments_processed']}
"""
        else:
            return f"❌ 优化失败: {response.text}"


async def handle_novel_refine_all(arguments: dict) -> str:
    """处理批量优化"""
    project_id = arguments["project_id"]
    start = arguments.get("start_chapter", 1)
    end = arguments.get("end_chapter", 100)
    model = arguments.get("model")
    
    url = f"{BASE_URL}/api/refinement/project/{project_id}/all"
    payload = {
        "start_chapter": start,
        "end_chapter": end,
        "model": model
    }
    
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, json=payload, headers=get_headers())
        
        if response.status_code == 200:
            result = response.json()
            return f"""✅ 批量优化任务已启动

任务ID: {result['task_id']}
范围: 第{start}-{end}章
使用模型: {model or '项目默认'}

使用 novel_refine_status 查询进度。
预计耗时: {(end - start + 1) * 3}分钟（每章约3分钟）
"""
        else:
            return f"❌ 启动失败: {response.text}"


async def handle_novel_refine_status(arguments: dict) -> str:
    """处理进度查询"""
    project_id = arguments["project_id"]
    
    url = f"{BASE_URL}/api/refinement/project/{project_id}/status"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=get_headers())
        
        if response.status_code == 200:
            s = response.json()
            
            progress = ""
            if s["current_chapter"]:
                progress = f"\n当前: 第{s['current_chapter']}章 第{s['current_segment']}段"
            
            return f"""📊 优化进度

状态: {s['status']}
总计: {s['total']}章
完成: {s['completed']}章
失败: {s['failed']}章{progress}

完成率: {s['completed']/s['total']*100:.1f}%
"""
        else:
            return f"❌ 查询失败: {response.text}"
```

---

## 10. 质量保证

### 10.1 段落验证

```python
def _validate_segment_output(
    self,
    output: str,
    original_segment: Dict,
    segment_index: int
) -> bool:
    """验证段落输出质量"""
    
    original_len = len(original_segment["content"])
    output_len = len(output)
    
    # 1. 字数检查: ±20%（单段允许更大波动）
    if output_len < original_len * 0.8 or output_len > original_len * 1.2:
        return False
    
    # 2. 结尾段特殊检查
    if original_segment["is_ending"]:
        summary_patterns = [
            "本章讲述", "本章介绍", "综上所述", 
            "总而言之", "至此", "欲知后事"
        ]
        for pattern in summary_patterns:
            if pattern in output[-300:]:
                return False
    
    # 3. 非结尾段不应有结尾感
    if not original_segment["is_ending"]:
        ending_patterns = ["全文完", "（完）", "THE END"]
        for pattern in ending_patterns:
            if pattern in output[-100:]:
                return False
    
    return True
```

### 10.2 段落重试

```python
async def _refine_segment_with_retry(
    self,
    segment_index: int,
    segment: Dict,
    context: Dict,
    chapter: Chapter,
    refined_segments: List[str],
    remaining_segments: List[Dict],
    model: str,
    max_retries: int = 3
) -> str:
    """单段优化，支持重试"""
    
    for attempt in range(max_retries):
        try:
            result = await self._refine_single_segment(
                segment_index=segment_index,
                segment_content=segment["content"],
                fixed_context=context,
                chapter=chapter,
                refined_segments=refined_segments,
                remaining_segments=remaining_segments,
                model=model
            )
            
            # 验证输出
            if self._validate_segment_output(result, segment, segment_index):
                return result
            
            logger.warning(f"段落{segment_index+1}验证失败，重试 {attempt+1}/{max_retries}")
            
        except Exception as e:
            logger.error(f"段落{segment_index+1}优化失败: {e}")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
    
    raise Exception(f"段落{segment_index+1}优化失败，已重试{max_retries}次")
```

---

## 11. 实施计划

### 11.0 自动触发机制

```python
# 批量生成完成后自动触发二次优化

# 方式1: 在批量生成API中添加参数
@router.post("/chapters/project/{project_id}/batch-generate")
async def batch_generate_chapters(
    project_id: str,
    request: BatchGenerateRequest,
    background_tasks: BackgroundTasks
):
    # ... 现有生成逻辑 ...
    
    # 新增：生成完成后自动触发优化
    if request.auto_refine:
        background_tasks.add_task(
            auto_refine_after_generation,
            project_id=project_id,
            model=request.refine_model or "opus"  # 默认用opus
        )
    
    return result


async def auto_refine_after_generation(project_id: str, model: str):
    """生成完成后自动触发二次优化"""
    
    # 等待所有章节生成完成
    while True:
        status = await get_generation_status(project_id)
        if status["pending"] == 0:
            break
        await asyncio.sleep(60)  # 每分钟检查一次
    
    # 启动二次优化
    service = ChapterRefinementService(db, ai_service)
    async for result in service.refine_all_chapters(
        project_id=project_id,
        model=model
    ):
        logger.info(f"优化进度: {result}")


# 方式2: 独立的自动优化脚本
# auto_refine.py

async def main():
    """自动优化脚本 - 可作为定时任务运行"""
    
    # 查找所有已完成生成但未优化的项目
    projects = await find_projects_need_refinement()
    
    for project in projects:
        logger.info(f"开始优化项目: {project.title}")
        
        service = ChapterRefinementService(db, ai_service)
        async for result in service.refine_all_chapters(
            project_id=project.id,
            model="opus"
        ):
            logger.info(f"第{result['chapter']}章: {result['status']}")
        
        logger.info(f"项目 {project.title} 优化完成")


if __name__ == "__main__":
    asyncio.run(main())
```

### 11.1 文件清单

```
backend/app/
├── core/
│   └── config.py                      # 添加 RefinementConfig 类
├── models/
│   ├── chapter.py                     # 添加 is_refined, refined_at 等字段
│   └── refinement.py                  # 新增 ChapterRefinement 模型
├── services/
│   └── refinement_service.py          # 核心优化服务（三段论）
├── api/
│   └── refinement.py                  # API 接口（含回滚）
└── schemas/
    └── refinement.py                  # Pydantic schemas

mcp_novel_server.py                    # 添加3个MCP工具

alembic/versions/
├── xxxx_add_chapter_refinement.py     # 新增优化记录表
└── xxxx_add_chapter_refined_fields.py # Chapter表添加字段

scripts/
└── auto_refine.py                     # 自动优化脚本
```

### 11.2 开发时间线

```
Day 1 (5小时):
├── 创建 refinement.py 数据模型
├── 创建数据库迁移
├── 实现 split_chapter_for_refinement 分段函数
├── 实现 _build_fixed_context 上下文构建
└── 实现三段提示词模板

Day 2 (5小时):
├── 实现 refine_chapter 单章优化（三段论）
├── 实现 refine_all_chapters 批量优化
├── 实现 API 接口
├── 实现 MCP 工具
└── 单元测试

Day 3 (3小时):
├── 集成测试（优化1-3章验证）
├── 提示词调优
├── 文档更新
└── 部署上线
```

### 11.3 使用示例

```bash
# 1. 优化单章（使用默认模型）
curl -X POST "$BASE_URL/api/refinement/chapter/{CHAPTER_ID}"

# 2. 优化单章（指定o1模型）
curl -X POST "$BASE_URL/api/refinement/chapter/{CHAPTER_ID}" \
  -H "Content-Type: application/json" \
  -d '{"model": "o1"}'

# 3. 批量优化（指定模型）
curl -X POST "$BASE_URL/api/refinement/project/{PROJECT_ID}/all" \
  -H "Content-Type: application/json" \
  -d '{"start_chapter": 1, "end_chapter": 100, "model": "o1"}'

# 4. 查询进度
curl "$BASE_URL/api/refinement/project/{PROJECT_ID}/status"

# 5. 查看优化对比
curl "$BASE_URL/api/refinement/chapter/{CHAPTER_ID}/diff"
```

---

## 12. 资源需求汇总

| 项目 | 数值 |
|------|------|
| AI开发时间 | 2-3天 |
| 人工审核 | 0.5天 |
| API成本(开发测试) | $30 |
| API成本(100章优化,o1) | $293 |
| 重试预留(10%) | $30 |
| **总计** | **3天 + $350** |

---

## 13. 预期效果

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| 历史准确性 | 60% | 85%+ |
| 文笔质量 | B级 | A级 |
| 章节完整性 | 90% | 99% |
| 角色一致性 | 80% | 90%+ |
| 无总结性文字 | 85% | 100% |

---

*最后更新: 2026-01-05*
*版本: v2.0.0*
*优先级: 🔴 TOP 1 - 立即实施*
