#!/usr/bin/env python3
"""
MuMuAINovel MCP Server
让AI助手（如Claude、Kiro）通过MCP协议直接创作小说

安装: pip install mcp httpx
运行: python mcp_novel_server.py
"""

import os
import json
import asyncio
import httpx
from typing import Optional, List, Dict, Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 配置
BASE_URL = os.getenv("MUMUAI_BASE_URL", "http://localhost:8000")
USERNAME = os.getenv("MUMUAI_USERNAME", "admin")
PASSWORD = os.getenv("MUMUAI_PASSWORD", "admin123")

server = Server("mumuai-novel")

class NovelClient:
    """MuMuAINovel API客户端"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=60.0)
        self.logged_in = False
    
    async def login(self) -> bool:
        """登录获取Session"""
        if self.logged_in:
            return True
        try:
            resp = await self.client.post("/api/auth/local/login", 
                json={"username": USERNAME, "password": PASSWORD})
            if resp.status_code == 200:
                self.logged_in = True
                return True
        except Exception as e:
            print(f"Login error: {e}")
        return False
    
    async def request(self, method: str, path: str, **kwargs) -> Dict:
        """发送API请求"""
        await self.login()
        resp = await getattr(self.client, method)(path, **kwargs)
        if resp.status_code == 200:
            return resp.json()
        return {"error": resp.text, "status": resp.status_code}

client = NovelClient()

# ============ MCP Tools ============

@server.list_tools()
async def list_tools() -> List[Tool]:
    """列出所有可用工具"""
    return [
        Tool(
            name="novel_list_projects",
            description="列出所有小说项目",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="novel_get_project",
            description="获取项目详情",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "项目ID"}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="novel_create_project",
            description="创建新小说项目",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "小说标题"},
                    "genre": {"type": "string", "description": "类型（都市科幻/玄幻/历史穿越等）"},
                    "description": {"type": "string", "description": "故事简介"}
                },
                "required": ["title", "genre", "description"]
            }
        ),
        Tool(
            name="novel_set_worldview",
            description="设置小说世界观",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "项目ID"},
                    "time_period": {"type": "string", "description": "时代背景"},
                    "location": {"type": "string", "description": "地理设定"},
                    "atmosphere": {"type": "string", "description": "社会氛围"},
                    "rules": {"type": "string", "description": "核心规则"}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="novel_create_character",
            description="创建角色",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "项目ID"},
                    "name": {"type": "string", "description": "角色名"},
                    "role_type": {"type": "string", "enum": ["protagonist", "supporting", "antagonist"], "description": "角色类型"},
                    "personality": {"type": "string", "description": "性格描述"},
                    "background": {"type": "string", "description": "背景故事"}
                },
                "required": ["project_id", "name", "role_type"]
            }
        ),
        Tool(
            name="novel_create_characters_batch",
            description="批量创建多个角色",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "项目ID"},
                    "characters": {
                        "type": "array",
                        "description": "角色列表",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "role_type": {"type": "string"},
                                "personality": {"type": "string"},
                                "background": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["project_id", "characters"]
            }
        ),
        Tool(
            name="novel_list_characters",
            description="获取项目的所有角色",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "项目ID"}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="novel_create_outline",
            description="创建章节大纲",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "项目ID"},
                    "chapter_number": {"type": "integer", "description": "章节序号"},
                    "title": {"type": "string", "description": "章节标题"},
                    "content": {"type": "string", "description": "章节概要（100-300字）"}
                },
                "required": ["project_id", "chapter_number", "title", "content"]
            }
        ),
        Tool(
            name="novel_create_outlines_batch",
            description="批量创建多个章节大纲",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "项目ID"},
                    "outlines": {
                        "type": "array",
                        "description": "大纲列表",
                        "items": {
                            "type": "object",
                            "properties": {
                                "chapter_number": {"type": "integer"},
                                "title": {"type": "string"},
                                "content": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["project_id", "outlines"]
            }
        ),
        Tool(
            name="novel_list_outlines",
            description="获取项目的所有大纲",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "项目ID"}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="novel_create_chapters_from_outlines",
            description="从大纲创建所有章节（空壳）",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "项目ID"}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="novel_batch_generate",
            description="提交批量生成任务，自动生成章节内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "项目ID"},
                    "start_chapter": {"type": "integer", "description": "起始章节", "default": 1},
                    "count": {"type": "integer", "description": "生成数量", "default": 100},
                    "target_words": {"type": "integer", "description": "每章字数", "default": 10000}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="novel_check_progress",
            description="检查项目生成进度",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "项目ID"}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="novel_resume_all",
            description="恢复所有中断的生成任务",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="novel_get_chapter",
            description="获取章节内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "chapter_id": {"type": "string", "description": "章节ID"}
                },
                "required": ["chapter_id"]
            }
        ),
        Tool(
            name="novel_full_pipeline",
            description="一键创建完整小说（项目+世界观+角色+大纲+章节+生成）",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "小说标题"},
                    "genre": {"type": "string", "description": "类型"},
                    "description": {"type": "string", "description": "故事简介"},
                    "worldview": {
                        "type": "object",
                        "description": "世界观设定",
                        "properties": {
                            "time_period": {"type": "string"},
                            "location": {"type": "string"},
                            "atmosphere": {"type": "string"},
                            "rules": {"type": "string"}
                        }
                    },
                    "characters": {"type": "array", "description": "角色列表"},
                    "outlines": {"type": "array", "description": "大纲列表（100章）"},
                    "target_words": {"type": "integer", "default": 10000}
                },
                "required": ["title", "genre", "description", "characters", "outlines"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """执行工具调用"""
    
    try:
        if name == "novel_list_projects":
            result = await client.request("get", "/api/projects")
            projects = result.get("items", [])
            summary = [f"📚 {p['title']} (ID: {p['id'][:8]}...)" for p in projects]
            return [TextContent(type="text", text=f"找到 {len(projects)} 个项目:\n" + "\n".join(summary))]
        
        elif name == "novel_get_project":
            result = await client.request("get", f"/api/projects/{arguments['project_id']}")
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "novel_create_project":
            result = await client.request("post", "/api/projects", json={
                "title": arguments["title"],
                "genre": arguments["genre"],
                "description": arguments["description"],
                "target_words": 1000000,
                "chapter_count": 100
            })
            return [TextContent(type="text", text=f"✅ 项目创建成功\nID: {result.get('id')}\n标题: {result.get('title')}")]
        
        elif name == "novel_set_worldview":
            data = {}
            if arguments.get("time_period"): data["world_time_period"] = arguments["time_period"]
            if arguments.get("location"): data["world_location"] = arguments["location"]
            if arguments.get("atmosphere"): data["world_atmosphere"] = arguments["atmosphere"]
            if arguments.get("rules"): data["world_rules"] = arguments["rules"]
            result = await client.request("put", f"/api/projects/{arguments['project_id']}", json=data)
            return [TextContent(type="text", text=f"✅ 世界观设置成功")]
        
        elif name == "novel_create_character":
            result = await client.request("post", "/api/characters", json={
                "project_id": arguments["project_id"],
                "name": arguments["name"],
                "role_type": arguments["role_type"],
                "personality": arguments.get("personality", ""),
                "background": arguments.get("background", "")
            })
            return [TextContent(type="text", text=f"✅ 角色创建成功: {result.get('name')}")]
        
        elif name == "novel_create_characters_batch":
            success = 0
            for char in arguments["characters"]:
                result = await client.request("post", "/api/characters", json={
                    "project_id": arguments["project_id"],
                    **char
                })
                if "id" in result:
                    success += 1
            return [TextContent(type="text", text=f"✅ 批量创建角色完成: {success}/{len(arguments['characters'])}")]
        
        elif name == "novel_list_characters":
            result = await client.request("get", f"/api/characters/project/{arguments['project_id']}?limit=200")
            chars = result.get("items", [])
            return [TextContent(type="text", text=f"共 {len(chars)} 个角色")]
        
        elif name == "novel_create_outline":
            result = await client.request("post", "/api/outlines", json={
                "project_id": arguments["project_id"],
                "title": f"第{arguments['chapter_number']}章 {arguments['title']}",
                "content": arguments["content"],
                "order_index": arguments["chapter_number"]
            })
            return [TextContent(type="text", text=f"✅ 大纲创建成功: 第{arguments['chapter_number']}章")]
        
        elif name == "novel_create_outlines_batch":
            success = 0
            for outline in arguments["outlines"]:
                result = await client.request("post", "/api/outlines", json={
                    "project_id": arguments["project_id"],
                    "title": f"第{outline['chapter_number']}章 {outline['title']}",
                    "content": outline["content"],
                    "order_index": outline["chapter_number"]
                })
                if "id" in result:
                    success += 1
            return [TextContent(type="text", text=f"✅ 批量创建大纲完成: {success}/{len(arguments['outlines'])}")]
        
        elif name == "novel_list_outlines":
            result = await client.request("get", f"/api/outlines/project/{arguments['project_id']}?limit=200")
            outlines = result.get("items", [])
            return [TextContent(type="text", text=f"共 {len(outlines)} 个大纲")]
        
        elif name == "novel_create_chapters_from_outlines":
            # 获取所有大纲
            outlines_resp = await client.request("get", f"/api/outlines/project/{arguments['project_id']}?limit=200")
            outlines = sorted(outlines_resp.get("items", []), key=lambda x: x.get("order_index", 0))
            
            success = 0
            for outline in outlines:
                result = await client.request("post", "/api/chapters", json={
                    "project_id": arguments["project_id"],
                    "title": outline["title"],
                    "summary": outline.get("content", "")[:500],
                    "chapter_number": outline.get("order_index", 0),
                    "outline_id": outline["id"],
                    "status": "pending"
                })
                if "id" in result:
                    success += 1
            return [TextContent(type="text", text=f"✅ 从大纲创建章节完成: {success}/{len(outlines)}")]
        
        elif name == "novel_batch_generate":
            result = await client.request("post", 
                f"/api/chapters/project/{arguments['project_id']}/batch-generate",
                json={
                    "start_chapter_number": arguments.get("start_chapter", 1),
                    "count": arguments.get("count", 100),
                    "target_word_count": arguments.get("target_words", 10000)
                })
            if "batch_id" in result:
                return [TextContent(type="text", text=f"✅ 批量生成任务已提交\nBatch ID: {result['batch_id']}\n后台正在生成中...")]
            return [TextContent(type="text", text=f"❌ 提交失败: {result}")]
        
        elif name == "novel_check_progress":
            chapters = await client.request("get", f"/api/chapters/project/{arguments['project_id']}?limit=200")
            items = chapters.get("items", [])
            total = chapters.get("total", 0)
            generated = len([c for c in items if c.get("content") and len(c["content"]) > 100])
            
            active = await client.request("get", f"/api/chapters/project/{arguments['project_id']}/batch-generate/active")
            status = "🟢 生成中" if active.get("has_active_task") else "⏸️ 空闲"
            
            return [TextContent(type="text", text=f"📊 进度: {generated}/{total}章\n状态: {status}")]
        
        elif name == "novel_resume_all":
            projects = await client.request("get", "/api/projects")
            resumed = 0
            for proj in projects.get("items", []):
                pid = proj["id"]
                chapters = await client.request("get", f"/api/chapters/project/{pid}?limit=200")
                items = chapters.get("items", [])
                total = chapters.get("total", 0)
                if total == 0:
                    continue
                generated = len([c for c in items if c.get("content") and len(c["content"]) > 100])
                if generated >= total:
                    continue
                
                active = await client.request("get", f"/api/chapters/project/{pid}/batch-generate/active")
                if active.get("has_active_task"):
                    continue
                
                # 需要恢复
                last = max([c["chapter_number"] for c in items if c.get("content") and len(c["content"]) > 100], default=0)
                result = await client.request("post", f"/api/chapters/project/{pid}/batch-generate",
                    json={"start_chapter_number": last + 1, "count": total - last, "target_word_count": 10000})
                if "batch_id" in result:
                    resumed += 1
            
            return [TextContent(type="text", text=f"✅ 恢复完成: {resumed} 个任务已重新提交")]
        
        elif name == "novel_get_chapter":
            result = await client.request("get", f"/api/chapters/{arguments['chapter_id']}")
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "novel_full_pipeline":
            steps = []
            
            # 1. 创建项目
            proj = await client.request("post", "/api/projects", json={
                "title": arguments["title"],
                "genre": arguments["genre"],
                "description": arguments["description"],
                "target_words": 1000000,
                "chapter_count": 100
            })
            project_id = proj.get("id")
            steps.append(f"✅ 项目创建成功: {project_id[:8]}...")
            
            # 2. 设置世界观
            if arguments.get("worldview"):
                wv = arguments["worldview"]
                await client.request("put", f"/api/projects/{project_id}", json={
                    "world_time_period": wv.get("time_period", ""),
                    "world_location": wv.get("location", ""),
                    "world_atmosphere": wv.get("atmosphere", ""),
                    "world_rules": wv.get("rules", "")
                })
                steps.append("✅ 世界观设置成功")
            
            # 3. 创建角色
            char_success = 0
            for char in arguments.get("characters", []):
                result = await client.request("post", "/api/characters", json={
                    "project_id": project_id,
                    **char
                })
                if "id" in result:
                    char_success += 1
            steps.append(f"✅ 角色创建完成: {char_success}个")
            
            # 4. 创建大纲
            outline_success = 0
            for outline in arguments.get("outlines", []):
                result = await client.request("post", "/api/outlines", json={
                    "project_id": project_id,
                    "title": f"第{outline['chapter_number']}章 {outline['title']}",
                    "content": outline["content"],
                    "order_index": outline["chapter_number"]
                })
                if "id" in result:
                    outline_success += 1
            steps.append(f"✅ 大纲创建完成: {outline_success}章")
            
            # 5. 创建章节
            outlines_resp = await client.request("get", f"/api/outlines/project/{project_id}?limit=200")
            outlines = sorted(outlines_resp.get("items", []), key=lambda x: x.get("order_index", 0))
            chapter_success = 0
            for outline in outlines:
                result = await client.request("post", "/api/chapters", json={
                    "project_id": project_id,
                    "title": outline["title"],
                    "summary": outline.get("content", "")[:500],
                    "chapter_number": outline.get("order_index", 0),
                    "outline_id": outline["id"],
                    "status": "pending"
                })
                if "id" in result:
                    chapter_success += 1
            steps.append(f"✅ 章节创建完成: {chapter_success}章")
            
            # 6. 提交批量生成
            batch = await client.request("post", f"/api/chapters/project/{project_id}/batch-generate",
                json={
                    "start_chapter_number": 1,
                    "count": len(outlines),
                    "target_word_count": arguments.get("target_words", 10000)
                })
            if "batch_id" in batch:
                steps.append(f"✅ 批量生成已提交: {batch['batch_id'][:8]}...")
            
            return [TextContent(type="text", text=f"🎉 小说创建Pipeline完成!\n\nProject ID: {project_id}\n\n" + "\n".join(steps))]
        
        else:
            return [TextContent(type="text", text=f"❌ 未知工具: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"❌ 错误: {str(e)}")]


async def main():
    """启动MCP服务器"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
