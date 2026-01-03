#!/bin/bash
# ==========================================
# MuMuAINovel 一键启动脚本
# ==========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}🚀 MuMuAINovel 启动脚本${NC}"
echo -e "${BLUE}================================================${NC}"

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装，请先安装 Docker${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker 环境检查通过${NC}"

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️ .env 文件不存在，从模板创建...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 请编辑 .env 文件配置 API Key 等信息${NC}"
fi

# 检查端口占用
APP_PORT=${APP_PORT:-8000}
POSTGRES_PORT=${POSTGRES_PORT:-5433}

check_port() {
    local port=$1
    if ss -tlnp 2>/dev/null | grep -q ":${port} " || netstat -tlnp 2>/dev/null | grep -q ":${port} "; then
        return 0  # 端口被占用
    fi
    return 1  # 端口空闲
}

if check_port $APP_PORT; then
    echo -e "${RED}❌ 端口 $APP_PORT 已被占用，请修改 .env 中的 APP_PORT${NC}"
    exit 1
fi

if check_port $POSTGRES_PORT; then
    echo -e "${YELLOW}⚠️ 端口 $POSTGRES_PORT 已被占用，尝试使用其他端口...${NC}"
    for port in 5434 5435 5436 5437; do
        if ! check_port $port; then
            export POSTGRES_PORT=$port
            echo -e "${GREEN}✅ 使用 PostgreSQL 端口: $port${NC}"
            break
        fi
    done
fi

echo -e "${GREEN}✅ 端口检查通过 (APP: $APP_PORT, PostgreSQL: $POSTGRES_PORT)${NC}"

# 启动服务
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}🐳 启动 Docker 服务...${NC}"
echo -e "${BLUE}================================================${NC}"

# 使用 docker compose 或 docker-compose
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

$COMPOSE_CMD up -d

# 等待服务启动
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 5

# 检查服务状态
if $COMPOSE_CMD ps | grep -q "Up"; then
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}🎉 MuMuAINovel 启动成功！${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo ""
    echo -e "${BLUE}📱 访问地址:${NC}"
    echo -e "   Web UI:     http://0.0.0.0:${APP_PORT}"
    echo -e "   API 文档:   http://0.0.0.0:${APP_PORT}/docs"
    echo -e "   健康检查:   http://0.0.0.0:${APP_PORT}/health"
    echo ""
    echo -e "${BLUE}📋 常用命令:${NC}"
    echo -e "   查看日志:   $COMPOSE_CMD logs -f"
    echo -e "   停止服务:   $COMPOSE_CMD down"
    echo -e "   重启服务:   $COMPOSE_CMD restart"
    echo ""
else
    echo -e "${RED}❌ 服务启动失败，请检查日志:${NC}"
    $COMPOSE_CMD logs --tail=50
    exit 1
fi
