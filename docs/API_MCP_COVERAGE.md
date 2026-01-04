# API 与 MCP 功能覆盖清单

## 概述

MuMuAINovel 提供 **160个 REST API** 和 **33个 MCP 工具**，覆盖小说创作的完整流程。

---

## MCP 工具清单 (33个)

### 项目管理 (6个)

| 工具 | 说明 | 对应API |
|------|------|---------|
| `novel_list_projects` | 列出所有项目 | GET /api/projects |
| `novel_get_project` | 获取项目详情 | GET /api/projects/{id} |
| `novel_create_project` | 创建新项目 | POST /api/projects |
| `novel_set_worldview` | 设置世界观 | PUT /api/projects/{id} |
| `novel_delete_project` | 删除项目 | DELETE /api/projects/{id} |
| `novel_export_project` | 导出项目 | GET /api/projects/{id}/export |

### 角色管理 (5个)

| 工具 | 说明 | 对应API |
|------|------|---------|
| `novel_list_characters` | 获取角色列表 | GET /api/characters/project/{id} |
| `novel_create_character` | 创建单个角色 | POST /api/characters |
| `novel_create_characters_batch` | 批量创建角色 | POST /api/characters (循环) |
| `novel_update_character` | 更新角色 | PUT /api/characters/{id} |
| `novel_delete_character` | 删除角色 | DELETE /api/characters/{id} |

### 大纲管理 (5个)

| 工具 | 说明 | 对应API |
|------|------|---------|
| `novel_list_outlines` | 获取大纲列表 | GET /api/outlines/project/{id} |
| `novel_create_outline` | 创建单个大纲 | POST /api/outlines |
| `novel_create_outlines_batch` | 批量创建大纲 | POST /api/outlines (循环) |
| `novel_update_outline` | 更新大纲 | PUT /api/outlines/{id} |
| `novel_delete_outline` | 删除大纲 | DELETE /api/outlines/{id} |

### 章节管理 (5个)

| 工具 | 说明 | 对应API |
|------|------|---------|
| `novel_list_chapters` | 获取章节列表 | GET /api/chapters/project/{id} |
| `novel_get_chapter` | 获取章节内容 | GET /api/chapters/{id} |
| `novel_create_chapters_from_outlines` | 从大纲创建章节 | POST /api/chapters (循环) |
| `novel_update_chapter` | 更新章节 | PUT /api/chapters/{id} |
| `novel_delete_chapter` | 删除章节 | DELETE /api/chapters/{id} |

### 批量生成 (4个)

| 工具 | 说明 | 对应API |
|------|------|---------|
| `novel_batch_generate` | 提交批量生成 | POST /api/chapters/project/{id}/batch-generate |
| `novel_check_progress` | 检查生成进度 | GET /api/chapters/project/{id} + .../active |
| `novel_cancel_generation` | 取消生成任务 | POST /api/chapters/batch-generate/{id}/cancel |
| `novel_resume_all` | 恢复所有中断任务 | (组合多个API) |

### 高级功能 (7个)

| 工具 | 说明 | 对应API |
|------|------|---------|
| `novel_check_quality` | 章节质量评分 | GET /api/quality/chapter/{id}/basic |
| `novel_check_consistency` | 一致性检测 | GET /api/consistency/chapter/{id}/check |
| `novel_check_duplicate` | 重复内容检测 | GET /api/duplicate/chapter/{id}/check |
| `novel_list_foreshadows` | 获取伏笔列表 | GET /api/foreshadows |
| `novel_create_foreshadow` | 创建伏笔 | POST /api/foreshadows |
| `novel_get_timeline` | 获取时间线 | GET /api/timeline |
| `novel_analyze_style` | 风格分析 | POST /api/style-analysis/project/{id}/learn |

### 一键Pipeline (1个)

| 工具 | 说明 |
|------|------|
| `novel_full_pipeline` | 一键创建完整小说（项目+世界观+角色+大纲+章节+生成） |

---

## API 分类统计 (160个)

| 模块 | API数量 | MCP覆盖 | 说明 |
|------|---------|---------|------|
| Auth | 8 | 内部使用 | 登录/OAuth/会话 |
| Projects | 12 | ✅ 6个 | 项目CRUD |
| Characters | 18 | ✅ 5个 | 角色管理 |
| Outlines | 15 | ✅ 5个 | 大纲管理 |
| Chapters | 25 | ✅ 5个 | 章节管理 |
| Batch Generate | 4 | ✅ 4个 | 批量生成 |
| Quality | 2 | ✅ 1个 | 质量评分 |
| Consistency | 4 | ✅ 1个 | 一致性检测 |
| Duplicate | 2 | ✅ 1个 | 重复检测 |
| Foreshadows | 10 | ✅ 2个 | 伏笔管理 |
| Timeline | 6 | ✅ 1个 | 时间线 |
| Style Analysis | 4 | ✅ 1个 | 风格分析 |
| Character Growth | 6 | ❌ | UI专用 |
| Organizations | 8 | ❌ | UI专用 |
| Relationships | 6 | ❌ | UI专用 |
| Memories | 8 | ❌ | 内部使用 |
| Writing Styles | 8 | ❌ | UI专用 |
| Careers | 10 | ❌ | UI专用 |
| Admin | 6 | ❌ | 管理员专用 |
| Settings | 10 | ❌ | UI专用 |
| Others | 6 | ❌ | 系统/健康检查 |

---

## 核心场景覆盖

### ✅ 完全覆盖的场景

| 场景 | 方式 |
|------|------|
| 创建新小说（一键） | `novel_full_pipeline` |
| 分步创建小说 | 组合多个工具 |
| 查看所有项目 | `novel_list_projects` |
| 检查生成进度 | `novel_check_progress` |
| 恢复中断任务 | `novel_resume_all` |
| 取消生成任务 | `novel_cancel_generation` |
| 导出项目数据 | `novel_export_project` |
| 质量检测 | `novel_check_quality` |
| 一致性检测 | `novel_check_consistency` |
| 重复检测 | `novel_check_duplicate` |
| 伏笔管理 | `novel_list/create_foreshadow` |
| 时间线查看 | `novel_get_timeline` |
| 风格分析 | `novel_analyze_style` |
| CRUD操作 | 各模块的增删改查工具 |

### ❌ 未覆盖的场景（UI专用）

| 场景 | 原因 |
|------|------|
| OAuth登录 | Web UI专用 |
| 用户管理 | 管理员Web UI |
| 组织架构图 | 可视化功能 |
| 角色关系图 | 可视化功能 |
| 写作风格预设 | UI配置功能 |
| 职业系统 | 游戏化功能 |
| 提示词模板 | 高级配置 |

---

## 使用建议

### 新手用户
直接使用 `novel_full_pipeline` 一键创建小说

### 进阶用户
分步使用各工具，精细控制每个环节

### 监控任务
使用 `novel_check_progress` 和 `novel_resume_all`

### 质量保证
使用 `novel_check_quality`、`novel_check_consistency`、`novel_check_duplicate`

---

*最后更新: 2026-01-05*
