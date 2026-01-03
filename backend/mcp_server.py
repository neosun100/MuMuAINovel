"""
MuMuAINovel MCP 服务器
提供小说创作相关的 MCP 工具接口
"""
import os
import sys
import asyncio
import httpx
from typing import Optional, Dict, Any, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 配置
API_BASE_URL = os.getenv("MUMUAI_API_URL", "http://localhost:8000")
API_TIMEOUT = int(os.getenv("MUMUAI_API_TIMEOUT", "60"))

# 创建 MCP 服务器
server = Server("mumuainovel")

# HTTP 客户端
http_client: Optional[httpx.AsyncClient] = None


async def get_client() -> httpx.AsyncClient:
    """获取 HTTP 客户端"""
    global http_client
    if http_client is None:
        http_client = httpx.AsyncClient(
            base_url=API_BASE_URL,
            timeout=API_TIMEOUT
        )
    return http_client


async def api_call(method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
    """调用 API"""
    client = await get_client()
    try:
        if method.upper() == "GET":
            resp = await client.get(endpoint, params=kwargs.get("params"))
        elif method.upper() == "POST":
            resp = await client.post(endpoint, json=kwargs.get("json"))
        elif method.upper() == "PUT":
            resp = await client.put(endpoint, json=kwargs.get("json"))
        elif method.upper() == "DELETE":
            resp = await client.delete(endpoint)
        else:
            raise ValueError(f"不支持的方法: {method}")
        
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"API 错误: {e.response.status_code}", "detail": e.response.text}
    except Exception as e:
        return {"error": str(e)}


@server.list_tools()
async def list_tools() -> List[Tool]:
    """列出所有可用工具"""
    return [
        Tool(
            name="health_check",
            description="检查 MuMuAINovel 服务健康状态",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_projects",
            description="获取用户的小说项目列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "用户会话 ID（登录后获取）"
                    }
                },
                "required": ["session_id"]
            }
        ),
        Tool(
            name="get_project",
            description="获取指定小说项目的详细信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "用户会话 ID"},
                    "project_id": {"type": "integer", "description": "项目 ID"}
                },
                "required": ["session_id", "project_id"]
            }
        ),
        Tool(
            name="list_chapters",
            description="获取小说项目的章节列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "用户会话 ID"},
                    "project_id": {"type": "integer", "description": "项目 ID"}
                },
                "required": ["session_id", "project_id"]
            }
        ),
        Tool(
            name="get_chapter",
            description="获取指定章节的内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "用户会话 ID"},
                    "chapter_id": {"type": "integer", "description": "章节 ID"}
                },
                "required": ["session_id", "chapter_id"]
            }
        ),
        Tool(
            name="list_characters",
            description="获取小说项目的角色列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "用户会话 ID"},
                    "project_id": {"type": "integer", "description": "项目 ID"}
                },
                "required": ["session_id", "project_id"]
            }
        ),
        Tool(
            name="get_outline",
            description="获取小说项目的大纲",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "用户会话 ID"},
                    "project_id": {"type": "integer", "description": "项目 ID"}
                },
                "required": ["session_id", "project_id"]
            }
        ),
        Tool(
            name="generate_inspiration",
            description="生成创作灵感和点子",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "用户会话 ID"},
                    "genre": {"type": "string", "description": "小说类型（如：玄幻、都市、科幻）"},
                    "keywords": {"type": "string", "description": "关键词（可选）"},
                    "count": {"type": "integer", "description": "生成数量，默认 3", "default": 3}
                },
                "required": ["session_id", "genre"]
            }
        ),
        Tool(
            name="local_login",
            description="使用本地账户登录获取会话 ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "用户名"},
                    "password": {"type": "string", "description": "密码"}
                },
                "required": ["username", "password"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """执行工具调用"""
    try:
        result = await _execute_tool(name, arguments)
        import json
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"错误: {str(e)}")]


async def _execute_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """执行具体工具"""
    session_id = args.get("session_id")
    headers = {"Cookie": f"session_id={session_id}"} if session_id else {}
    
    if name == "health_check":
        return await api_call("GET", "/health")
    
    elif name == "local_login":
        return await api_call("POST", "/api/auth/local/login", json={
            "username": args["username"],
            "password": args["password"]
        })
    
    elif name == "list_projects":
        client = await get_client()
        resp = await client.get("/api/projects", headers=headers)
        return resp.json()
    
    elif name == "get_project":
        client = await get_client()
        resp = await client.get(f"/api/projects/{args['project_id']}", headers=headers)
        return resp.json()
    
    elif name == "list_chapters":
        client = await get_client()
        resp = await client.get(f"/api/projects/{args['project_id']}/chapters", headers=headers)
        return resp.json()
    
    elif name == "get_chapter":
        client = await get_client()
        resp = await client.get(f"/api/chapters/{args['chapter_id']}", headers=headers)
        return resp.json()
    
    elif name == "list_characters":
        client = await get_client()
        resp = await client.get(f"/api/projects/{args['project_id']}/characters", headers=headers)
        return resp.json()
    
    elif name == "get_outline":
        client = await get_client()
        resp = await client.get(f"/api/projects/{args['project_id']}/outline", headers=headers)
        return resp.json()
    
    elif name == "generate_inspiration":
        client = await get_client()
        resp = await client.post("/api/inspiration/generate", headers=headers, json={
            "genre": args["genre"],
            "keywords": args.get("keywords", ""),
            "count": args.get("count", 3)
        })
        return resp.json()
    
    else:
        return {"error": f"未知工具: {name}"}


async def main():
    """主函数"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
