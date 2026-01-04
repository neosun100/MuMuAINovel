# 预案07: 自主创作Agent系统

> 版本: v2.0 | 优先级: 🟢 P2 | **AI开发: 5-7天** | 人工审核: 1天

---

## 1. 目标与成功指标

### 1.1 核心目标
- 实现完全自主的小说创作Agent
- 用户只需提供创意种子，Agent自动完成全部创作
- 自动搜索资料、设计角色、规划大纲、生成内容、质量检测、自我修复

### 1.2 成功指标

| 指标 | 当前 | 目标 |
|------|------|------|
| 人工干预次数 | 多次 | 0-1次 |
| 创作完成率 | 80% | 98% |
| 质量达标率 | 70% | 90% |
| 平均创作时间 | 15小时 | 10小时 |

---

## 2. 方案对比

### 方案A: LangGraph工作流 (推荐 ⭐)

**原理**: 使用LangGraph构建状态图工作流

```
优点:
✅ 状态管理清晰
✅ 支持循环和条件分支
✅ 易于调试和监控
✅ 与LangChain生态兼容

缺点:
❌ 学习曲线
❌ 需要重构部分代码

适用场景: 复杂工作流，需要精细控制
```

### 方案B: CrewAI多Agent协作

**原理**: 多个专业Agent协作完成任务

```
优点:
✅ 角色分工明确
✅ 易于理解和扩展
✅ 支持人类介入

缺点:
❌ Agent间协调复杂
❌ 成本较高（多次AI调用）

适用场景: 需要多专业协作
```

### 方案C: 自定义Agent框架

**原理**: 基于现有代码构建轻量级Agent

```
优点:
✅ 完全可控
✅ 与现有系统深度集成
✅ 无额外依赖

缺点:
❌ 开发工作量大
❌ 需要自己处理状态管理

适用场景: 特定需求，深度定制
```

---

## 3. 推荐方案: LangGraph工作流 (方案A)

### 3.1 Agent架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                     自主创作Agent系统                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    协调Agent (Orchestrator)                  │   │
│  │  - 任务分解                                                  │   │
│  │  - 进度监控                                                  │   │
│  │  - 异常处理                                                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│         ┌────────────────────┼────────────────────┐                │
│         ▼                    ▼                    ▼                │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐          │
│  │ 研究Agent   │     │ 创作Agent   │     │ 评估Agent   │          │
│  │ - 搜索资料  │     │ - 设计角色  │     │ - 质量检测  │          │
│  │ - 知识整理  │     │ - 规划大纲  │     │ - 一致性检查│          │
│  │ - 背景构建  │     │ - 生成内容  │     │ - 逻辑验证  │          │
│  └─────────────┘     └─────────────┘     └─────────────┘          │
│         │                    │                    │                │
│         └────────────────────┼────────────────────┘                │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    修复Agent (Fixer)                         │   │
│  │  - 自动修复问题                                              │   │
│  │  - 重新生成不合格内容                                        │   │
│  │  - 优化润色                                                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 LangGraph工作流定义

```python
# backend/app/agents/novel_agent.py

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional

class NovelCreationState(TypedDict):
    """创作状态"""
    # 输入
    user_input: str  # 用户创意种子
    
    # 研究阶段
    research_results: Optional[List[dict]]
    background_info: Optional[str]
    
    # 设计阶段
    project_id: Optional[str]
    characters: Optional[List[dict]]
    outlines: Optional[List[dict]]
    worldview: Optional[dict]
    
    # 生成阶段
    chapters_generated: int
    current_chapter: int
    generation_errors: List[dict]
    
    # 评估阶段
    quality_issues: List[dict]
    consistency_issues: List[dict]
    
    # 修复阶段
    fix_attempts: int
    
    # 状态
    status: str  # researching/designing/generating/evaluating/fixing/completed/failed
    error_message: Optional[str]


def create_novel_agent():
    """创建小说创作Agent"""
    
    workflow = StateGraph(NovelCreationState)
    
    # 添加节点
    workflow.add_node("research", research_node)
    workflow.add_node("design", design_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("evaluate", evaluate_node)
    workflow.add_node("fix", fix_node)
    
    # 添加边
    workflow.add_edge("research", "design")
    workflow.add_edge("design", "generate")
    workflow.add_edge("generate", "evaluate")
    
    # 条件边
    workflow.add_conditional_edges(
        "evaluate",
        should_fix,
        {
            "fix": "fix",
            "continue": "generate",
            "complete": END
        }
    )
    
    workflow.add_conditional_edges(
        "fix",
        check_fix_result,
        {
            "retry": "generate",
            "give_up": END
        }
    )
    
    # 设置入口
    workflow.set_entry_point("research")
    
    return workflow.compile()


async def research_node(state: NovelCreationState) -> NovelCreationState:
    """研究节点 - 搜索和整理背景资料"""
    
    user_input = state["user_input"]
    
    # 1. 解析用户输入，提取关键词
    keywords = await extract_keywords(user_input)
    
    # 2. 搜索相关资料
    search_results = []
    for keyword in keywords:
        results = await web_search(keyword)
        search_results.extend(results)
    
    # 3. 整理背景信息
    background = await summarize_research(search_results, user_input)
    
    return {
        **state,
        "research_results": search_results,
        "background_info": background,
        "status": "designing"
    }


async def design_node(state: NovelCreationState) -> NovelCreationState:
    """设计节点 - 创建项目、角色、大纲"""
    
    # 1. 创建项目
    project = await create_project(
        user_input=state["user_input"],
        background=state["background_info"]
    )
    
    # 2. 设计世界观
    worldview = await design_worldview(
        user_input=state["user_input"],
        background=state["background_info"]
    )
    await update_project_worldview(project.id, worldview)
    
    # 3. 设计角色 (80-150个)
    characters = await design_characters(
        user_input=state["user_input"],
        worldview=worldview,
        count=100
    )
    await batch_create_characters(project.id, characters)
    
    # 4. 设计大纲 (100章)
    outlines = await design_outlines(
        user_input=state["user_input"],
        worldview=worldview,
        characters=characters,
        count=100
    )
    await batch_create_outlines(project.id, outlines)
    
    # 5. 创建章节记录
    await create_chapters_from_outlines(project.id)
    
    return {
        **state,
        "project_id": project.id,
        "characters": characters,
        "outlines": outlines,
        "worldview": worldview,
        "chapters_generated": 0,
        "current_chapter": 1,
        "status": "generating"
    }


async def generate_node(state: NovelCreationState) -> NovelCreationState:
    """生成节点 - 批量生成章节"""
    
    project_id = state["project_id"]
    current = state["current_chapter"]
    
    # 每次生成10章
    batch_size = 10
    end_chapter = min(current + batch_size - 1, 100)
    
    # 提交批量生成
    batch_result = await batch_generate(
        project_id=project_id,
        start_chapter=current,
        count=end_chapter - current + 1,
        target_word_count=10000
    )
    
    # 等待完成
    await wait_for_batch_completion(batch_result["batch_id"])
    
    return {
        **state,
        "chapters_generated": end_chapter,
        "current_chapter": end_chapter + 1,
        "status": "evaluating"
    }


async def evaluate_node(state: NovelCreationState) -> NovelCreationState:
    """评估节点 - 检查质量和一致性"""
    
    project_id = state["project_id"]
    start = state["chapters_generated"] - 9  # 检查最近10章
    end = state["chapters_generated"]
    
    quality_issues = []
    consistency_issues = []
    
    for chapter_num in range(start, end + 1):
        chapter = await get_chapter(project_id, chapter_num)
        
        # 质量检测
        quality = await check_quality(chapter.id)
        if quality["grade"] in ["C", "D"]:
            quality_issues.append({
                "chapter": chapter_num,
                "grade": quality["grade"],
                "issues": quality["issues"]
            })
        
        # 一致性检测
        consistency = await check_consistency(chapter.id)
        if not consistency["is_consistent"]:
            consistency_issues.append({
                "chapter": chapter_num,
                "issues": consistency["issues"]
            })
    
    return {
        **state,
        "quality_issues": quality_issues,
        "consistency_issues": consistency_issues,
        "status": "evaluated"
    }


async def fix_node(state: NovelCreationState) -> NovelCreationState:
    """修复节点 - 自动修复问题"""
    
    project_id = state["project_id"]
    fix_attempts = state.get("fix_attempts", 0) + 1
    
    # 修复质量问题
    for issue in state["quality_issues"]:
        chapter = await get_chapter(project_id, issue["chapter"])
        fixed_content = await auto_fix_quality(chapter, issue["issues"])
        await update_chapter_content(chapter.id, fixed_content)
    
    # 修复一致性问题
    for issue in state["consistency_issues"]:
        chapter = await get_chapter(project_id, issue["chapter"])
        fixed_content = await auto_fix_consistency(chapter, issue["issues"])
        await update_chapter_content(chapter.id, fixed_content)
    
    return {
        **state,
        "fix_attempts": fix_attempts,
        "quality_issues": [],
        "consistency_issues": [],
        "status": "fixed"
    }


def should_fix(state: NovelCreationState) -> str:
    """判断是否需要修复"""
    
    has_issues = len(state["quality_issues"]) > 0 or len(state["consistency_issues"]) > 0
    all_generated = state["chapters_generated"] >= 100
    
    if has_issues and state.get("fix_attempts", 0) < 3:
        return "fix"
    elif not all_generated:
        return "continue"
    else:
        return "complete"


def check_fix_result(state: NovelCreationState) -> str:
    """检查修复结果"""
    
    if state.get("fix_attempts", 0) >= 3:
        return "give_up"
    return "retry"
```

### 3.3 Agent调用接口

```python
# backend/app/api/agent.py

@router.post("/agent/create-novel")
async def create_novel_with_agent(
    user_input: str,
    options: AgentOptions = None
) -> AgentTask:
    """使用Agent创建小说"""
    
    # 创建Agent实例
    agent = create_novel_agent()
    
    # 初始化状态
    initial_state = NovelCreationState(
        user_input=user_input,
        status="researching",
        chapters_generated=0,
        current_chapter=1,
        generation_errors=[],
        quality_issues=[],
        consistency_issues=[],
        fix_attempts=0
    )
    
    # 异步执行
    task_id = await start_agent_task(agent, initial_state)
    
    return AgentTask(
        task_id=task_id,
        status="started",
        estimated_time="10-15小时"
    )


@router.get("/agent/status/{task_id}")
async def get_agent_status(task_id: str) -> AgentStatus:
    """获取Agent任务状态"""
    
    state = await get_agent_state(task_id)
    
    return AgentStatus(
        task_id=task_id,
        status=state["status"],
        progress=state["chapters_generated"] / 100,
        current_phase=state["status"],
        project_id=state.get("project_id"),
        errors=state.get("generation_errors", [])
    )
```

---

## 4. MCP工具

```python
Tool(
    name="novel_auto_create",
    description="全自动创建小说（Agent模式）",
    inputSchema={
        "type": "object",
        "properties": {
            "creative_seed": {
                "type": "string",
                "description": "创意种子：标题、类型、主角、背景等"
            },
            "target_chapters": {
                "type": "integer",
                "default": 100
            },
            "target_words_per_chapter": {
                "type": "integer",
                "default": 10000
            }
        },
        "required": ["creative_seed"]
    }
),

Tool(
    name="novel_agent_status",
    description="查询Agent任务状态",
    inputSchema={
        "type": "object",
        "properties": {
            "task_id": {"type": "string"}
        },
        "required": ["task_id"]
    }
)
```

---

## 5. AI驱动实施计划 (5-7天)

```
Day 1 (6小时):
├── AI: 安装LangGraph依赖
├── AI: 设计状态机架构
├── AI: 实现基础工作流框架
└── 人工: 审核架构设计

Day 2 (6小时):
├── AI: 实现研究Agent节点
├── AI: 实现设计Agent节点
└── AI: 自动测试

Day 3 (6小时):
├── AI: 实现生成Agent节点
├── AI: 实现评估Agent节点
└── AI: 集成测试

Day 4 (5小时):
├── AI: 实现修复Agent节点
├── AI: 实现条件边逻辑
└── AI: 端到端测试

Day 5 (4小时):
├── AI: 实现API接口
├── AI: 添加MCP工具
└── AI: 异步任务管理

Day 6 (3小时):
├── AI: 更新文档
├── AI: 性能优化
└── 人工: 审核

Day 7 (可选):
└── 边缘情况处理+压力测试
```

---

## 6. 资源需求 (AI驱动模式)

- AI开发: 5-7天
- 人工审核: 1天
- API成本: $100 (开发期多次调用)
- 服务器: +$100/月 (Agent运行)
- **总计: 6-8天 + $100 + $100/月**

---

## 7. 风险与应对

| 风险 | 概率 | 应对 |
|------|------|------|
| Agent陷入循环 | 中 | 设置最大迭代次数 |
| 成本失控 | 中 | 设置预算上限 |
| 质量不稳定 | 中 | 多轮评估+人工兜底 |

---

*最后更新: 2026-01-05*
