# MuMuAINovel MCP Server 使用指南

## 概述

MCP (Model Context Protocol) 让AI助手（Claude、Kiro等）可以直接调用MuMuAINovel的API来创作小说。

## 安装

```bash
# 安装依赖
pip install mcp httpx

# 或使用 requirements
pip install -r requirements-mcp.txt
```

## 配置

### 1. 环境变量

```bash
export MUMUAI_BASE_URL=http://localhost:8000
export MUMUAI_USERNAME=admin
export MUMUAI_PASSWORD=your_password
```

### 2. Claude Desktop 配置

编辑 `~/.config/claude/claude_desktop_config.json` (Linux) 或 `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "mumuai-novel": {
      "command": "python",
      "args": ["/home/neo/upload/MuMuAINovel/mcp_novel_server.py"],
      "env": {
        "MUMUAI_BASE_URL": "http://localhost:8000",
        "MUMUAI_USERNAME": "admin",
        "MUMUAI_PASSWORD": "your_password"
      }
    }
  }
}
```

### 3. Kiro CLI 配置

编辑 `~/.kiro/mcp.json`:

```json
{
  "mcpServers": {
    "mumuai-novel": {
      "command": "python",
      "args": ["/home/neo/upload/MuMuAINovel/mcp_novel_server.py"],
      "env": {
        "MUMUAI_BASE_URL": "http://localhost:8000",
        "MUMUAI_USERNAME": "admin",
        "MUMUAI_PASSWORD": "your_password"
      }
    }
  }
}
```

## 可用工具

| 工具名 | 说明 |
|--------|------|
| `novel_list_projects` | 列出所有小说项目 |
| `novel_get_project` | 获取项目详情 |
| `novel_create_project` | 创建新项目 |
| `novel_set_worldview` | 设置世界观 |
| `novel_create_character` | 创建单个角色 |
| `novel_create_characters_batch` | 批量创建角色 |
| `novel_list_characters` | 获取角色列表 |
| `novel_create_outline` | 创建单个大纲 |
| `novel_create_outlines_batch` | 批量创建大纲 |
| `novel_list_outlines` | 获取大纲列表 |
| `novel_create_chapters_from_outlines` | 从大纲创建章节 |
| `novel_batch_generate` | 提交批量生成任务 |
| `novel_check_progress` | 检查生成进度 |
| `novel_resume_all` | 恢复所有中断任务 |
| `novel_get_chapter` | 获取章节内容 |
| `novel_full_pipeline` | 一键创建完整小说 |

## 使用示例

### 示例1: 查看项目列表

```
用户: 列出所有小说项目
AI: [调用 novel_list_projects]
```

### 示例2: 检查进度

```
用户: 检查盗火者的悲歌的进度
AI: [调用 novel_check_progress, project_id="43a8d273-..."]
```

### 示例3: 一键创建小说

```
用户: 帮我创建一部小说《星际霸主》，科幻类型，主角Jack Chen是边境矿工...

AI: [调用 novel_full_pipeline]
参数:
{
  "title": "星际霸主",
  "genre": "星际科幻",
  "description": "边境矿工Jack Chen意外获得远古文明遗产...",
  "worldview": {
    "time_period": "银河纪元3000年",
    "location": "银河系边境星域",
    "atmosphere": "星际殖民时代",
    "rules": "超光速航行、能量武器、AI辅助"
  },
  "characters": [
    {"name": "Jack Chen", "role_type": "protagonist", "personality": "坚韧不拔", "background": "边境矿工"},
    ...
  ],
  "outlines": [
    {"chapter_number": 1, "title": "边境矿工", "content": "Jack在边境星球挖矿..."},
    ...
  ]
}
```

### 示例4: 恢复中断任务

```
用户: 恢复所有中断的生成任务
AI: [调用 novel_resume_all]
```

## 完整工作流

1. **用户提供创意** → AI设计角色和大纲
2. **AI调用 `novel_full_pipeline`** → 自动创建项目、角色、大纲、章节
3. **后台自动生成** → 100章×10000字
4. **用户查询进度** → AI调用 `novel_check_progress`
5. **完成** → 100万字小说生成完毕

## 注意事项

1. 确保MuMuAINovel服务已启动 (`docker-compose up -d`)
2. 确保环境变量配置正确
3. 批量生成是异步的，提交后后台自动执行
4. 使用 `novel_resume_all` 可恢复容器重启后中断的任务

## 故障排除

### MCP连接失败
```bash
# 检查服务是否运行
curl http://localhost:8000/api/auth/config

# 测试MCP服务器
python mcp_novel_server.py
```

### 登录失败
```bash
# 检查环境变量
echo $MUMUAI_USERNAME
echo $MUMUAI_PASSWORD

# 测试登录
curl -X POST http://localhost:8000/api/auth/local/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```
