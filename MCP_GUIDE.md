# MuMuAINovel MCP 使用指南

## 概述

MuMuAINovel 提供 MCP (Model Context Protocol) 接口，允许 AI 助手直接调用小说创作相关功能。

## 配置方法

### Claude Desktop / Cursor 配置

在 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "mumuainovel": {
      "command": "python",
      "args": ["/path/to/MuMuAINovel/backend/mcp_server.py"],
      "env": {
        "MUMUAI_API_URL": "http://localhost:8000",
        "MUMUAI_API_TIMEOUT": "60"
      }
    }
  }
}
```

### Docker 环境配置

如果 MuMuAINovel 运行在 Docker 中：

```json
{
  "mcpServers": {
    "mumuainovel": {
      "command": "docker",
      "args": ["exec", "-i", "mumuainovel", "python", "/app/mcp_server.py"],
      "env": {
        "MUMUAI_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

## 可用工具

### 1. health_check
检查服务健康状态

```json
{
  "name": "health_check",
  "arguments": {}
}
```

### 2. local_login
本地账户登录，获取会话 ID

```json
{
  "name": "local_login",
  "arguments": {
    "username": "admin",
    "password": "admin123"
  }
}
```

返回示例：
```json
{
  "session_id": "abc123...",
  "user": {
    "id": 1,
    "username": "admin"
  }
}
```

### 3. list_projects
获取用户的小说项目列表

```json
{
  "name": "list_projects",
  "arguments": {
    "session_id": "your_session_id"
  }
}
```

### 4. get_project
获取指定项目详情

```json
{
  "name": "get_project",
  "arguments": {
    "session_id": "your_session_id",
    "project_id": 1
  }
}
```

### 5. list_chapters
获取项目的章节列表

```json
{
  "name": "list_chapters",
  "arguments": {
    "session_id": "your_session_id",
    "project_id": 1
  }
}
```

### 6. get_chapter
获取指定章节内容

```json
{
  "name": "get_chapter",
  "arguments": {
    "session_id": "your_session_id",
    "chapter_id": 1
  }
}
```

### 7. list_characters
获取项目的角色列表

```json
{
  "name": "list_characters",
  "arguments": {
    "session_id": "your_session_id",
    "project_id": 1
  }
}
```

### 8. get_outline
获取项目大纲

```json
{
  "name": "get_outline",
  "arguments": {
    "session_id": "your_session_id",
    "project_id": 1
  }
}
```

### 9. generate_inspiration
生成创作灵感

```json
{
  "name": "generate_inspiration",
  "arguments": {
    "session_id": "your_session_id",
    "genre": "玄幻",
    "keywords": "修仙 逆袭",
    "count": 3
  }
}
```

## 使用流程

1. 首先调用 `local_login` 获取 `session_id`
2. 使用 `session_id` 调用其他工具
3. 会话有效期为 2 小时（可配置）

## 与 API 的区别

| 特性 | MCP | REST API |
|------|-----|----------|
| 协议 | stdio/SSE | HTTP |
| 认证 | session_id 参数 | Cookie |
| 适用场景 | AI 助手集成 | Web/移动应用 |
| 实时性 | 同步调用 | 支持流式 |

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| MUMUAI_API_URL | API 服务地址 | http://localhost:8000 |
| MUMUAI_API_TIMEOUT | 请求超时（秒） | 60 |

## 故障排除

### 连接失败
- 确保 MuMuAINovel 服务已启动
- 检查 `MUMUAI_API_URL` 配置是否正确
- 检查防火墙设置

### 认证失败
- 确保 `session_id` 有效
- 会话可能已过期，重新登录获取新的 session_id

### 超时
- 增加 `MUMUAI_API_TIMEOUT` 值
- 检查网络连接
