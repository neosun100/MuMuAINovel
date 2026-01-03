# MuMuAINovel Docker 部署指南

## 快速开始

### 1. 使用 Docker Hub 镜像（推荐）

```bash
# 拉取镜像
docker pull neosun/mumuainovel:latest

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Key 等配置

# 启动服务
./start.sh
# 或
docker compose up -d
```

### 2. 访问服务

- Web UI: http://localhost:8000
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 三种访问模式

### 模式一：Web UI

访问 http://localhost:8000 使用完整的 Web 界面：
- 创建和管理小说项目
- AI 辅助生成大纲、角色、章节
- 角色关系可视化
- 多语言支持

### 模式二：REST API

所有功能都可通过 API 访问：

```bash
# 登录获取会话
curl -X POST http://localhost:8000/api/auth/local/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 获取项目列表
curl http://localhost:8000/api/projects \
  -H "Cookie: session_id=YOUR_SESSION_ID"
```

完整 API 文档: http://localhost:8000/docs

### 模式三：MCP 接口

支持 Model Context Protocol，可集成到 AI 助手：

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

详见 [MCP_GUIDE.md](MCP_GUIDE.md)

## 配置说明

### 必需配置

编辑 `.env` 文件：

```bash
# AI 服务（至少配置一个）
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1

# 本地登录账户
LOCAL_AUTH_USERNAME=admin
LOCAL_AUTH_PASSWORD=your_password

# 数据库密码
POSTGRES_PASSWORD=your_secure_password
```

### 端口配置

默认端口：
- 应用: 8000
- PostgreSQL: 5433

修改端口：
```bash
APP_PORT=8080
POSTGRES_PORT=5434
```

## 数据持久化

- `postgres_data`: PostgreSQL 数据
- `./logs`: 应用日志
- `/tmp/mumuainovel`: 临时文件

## 常用命令

```bash
# 启动
docker compose up -d

# 停止
docker compose down

# 查看日志
docker compose logs -f mumuainovel

# 重启
docker compose restart

# 更新镜像
docker compose pull
docker compose up -d
```

## 故障排除

### 服务无法启动

1. 检查端口占用：`ss -tlnp | grep 8000`
2. 查看日志：`docker compose logs mumuainovel`
3. 检查 .env 配置

### 数据库连接失败

1. 等待 PostgreSQL 完全启动
2. 检查 POSTGRES_PASSWORD 配置
3. 查看数据库日志：`docker compose logs postgres`

### API 调用失败

1. 确认服务健康：`curl http://localhost:8000/health`
2. 检查 API Key 配置
3. 查看应用日志
