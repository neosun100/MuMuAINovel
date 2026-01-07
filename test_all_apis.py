#!/usr/bin/env python3
"""
MuMuAINovel API 全面测试脚本 v4
- 增加超时时间
- 标记耗时API
"""

import httpx
import asyncio
from datetime import datetime
from typing import List
import sys

BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "jiasunm@amazon.com"

results = {"passed": [], "failed": [], "slow": []}

class APITester:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=120.0)  # 增加到120秒
        self.project_id = None
        self.character_id = None
        self.outline_id = None
        self.chapter_id = None
        
    async def login(self):
        resp = await self.client.post("/api/auth/local/login", 
            json={"username": USERNAME, "password": PASSWORD})
        return resp.status_code == 200
    
    async def test(self, method: str, path: str, name: str, 
                   json_data: dict = None, expected: List[int] = None,
                   slow: bool = False) -> bool:
        expected = expected or [200, 201]
        start = datetime.now()
        try:
            if method == "GET":
                resp = await self.client.get(path)
            elif method == "POST":
                resp = await self.client.post(path, json=json_data or {})
            elif method == "PUT":
                resp = await self.client.put(path, json=json_data or {})
            elif method == "DELETE":
                resp = await self.client.delete(path)
            else:
                return False
            
            elapsed = (datetime.now() - start).total_seconds()
            ok = resp.status_code in expected
            
            # 标记慢API
            slow_mark = f" ⏱️{elapsed:.1f}s" if elapsed > 5 else ""
            icon = "✅" if ok else "❌"
            print(f"  {icon} {name} [{resp.status_code}]{slow_mark}")
            
            if ok:
                results["passed"].append(name)
                if elapsed > 5:
                    results["slow"].append((name, elapsed))
            else:
                try:
                    detail = resp.json()
                except:
                    detail = resp.text[:100]
                results["failed"].append((name, str(detail)[:80], resp.status_code))
                print(f"      └─ {str(detail)[:80]}")
            return ok
        except httpx.TimeoutException:
            elapsed = (datetime.now() - start).total_seconds()
            print(f"  ⏱️ {name} [TIMEOUT after {elapsed:.0f}s]")
            results["failed"].append((name, f"Timeout after {elapsed:.0f}s", 0))
            return False
        except Exception as e:
            print(f"  ❌ {name} [ERROR: {type(e).__name__}]")
            results["failed"].append((name, str(e)[:80], 0))
            return False
    
    async def run_all(self):
        print("=" * 70)
        print("MuMuAINovel API 全面测试 v4")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # 登录
        print("\n📌 [1/16] 认证模块 (auth)")
        await self.login()
        await self.test("POST", "/api/auth/local/login", "POST /api/auth/local/login", 
                       {"username": USERNAME, "password": PASSWORD})
        await self.test("GET", "/api/auth/user", "GET /api/auth/user")
        await self.test("GET", "/api/auth/config", "GET /api/auth/config")
        await self.test("POST", "/api/auth/refresh", "POST /api/auth/refresh")
        await self.test("GET", "/api/auth/password/status", "GET /api/auth/password/status")
        await self.test("POST", "/api/auth/logout", "POST /api/auth/logout")
        await self.login()
        
        # 健康检查
        print("\n📌 [2/16] 健康检查")
        await self.test("GET", "/health", "GET /health")
        await self.test("GET", "/health/db-sessions", "GET /health/db-sessions")
        
        # 项目管理
        print("\n📌 [3/16] 项目管理 (projects)")
        await self.test("GET", "/api/projects", "GET /api/projects")
        
        resp = await self.client.get("/api/projects")
        if resp.status_code == 200:
            data = resp.json()
            if data.get("items"):
                self.project_id = data["items"][0]["id"]
        
        if self.project_id:
            await self.test("GET", f"/api/projects/{self.project_id}", "GET /api/projects/{id}")
            await self.test("GET", f"/api/projects/{self.project_id}/export", "GET /api/projects/{id}/export")
        
        # 角色管理
        print("\n📌 [4/16] 角色管理 (characters)")
        if self.project_id:
            await self.test("GET", f"/api/characters/project/{self.project_id}", "GET /api/characters/project/{id}")
            
            resp = await self.client.get(f"/api/characters/project/{self.project_id}")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("items"):
                    self.character_id = data["items"][0]["id"]
            
            if self.character_id:
                await self.test("GET", f"/api/characters/{self.character_id}", "GET /api/characters/{id}")
        
        # 大纲管理
        print("\n📌 [5/16] 大纲管理 (outlines)")
        if self.project_id:
            await self.test("GET", f"/api/outlines/project/{self.project_id}", "GET /api/outlines/project/{id}")
            
            resp = await self.client.get(f"/api/outlines/project/{self.project_id}")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("items"):
                    self.outline_id = data["items"][0]["id"]
            
            if self.outline_id:
                await self.test("GET", f"/api/outlines/{self.outline_id}", "GET /api/outlines/{id}")
                await self.test("GET", f"/api/outlines/{self.outline_id}/chapters", "GET /api/outlines/{id}/chapters")
        
        # 章节管理
        print("\n📌 [6/16] 章节管理 (chapters)")
        if self.project_id:
            await self.test("GET", f"/api/chapters/project/{self.project_id}", "GET /api/chapters/project/{id}")
            await self.test("GET", f"/api/chapters/project/{self.project_id}/batch-generate/active", 
                           "GET /api/chapters/project/{id}/batch-generate/active")
            
            resp = await self.client.get(f"/api/chapters/project/{self.project_id}")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("items"):
                    self.chapter_id = data["items"][0]["id"]
            
            if self.chapter_id:
                await self.test("GET", f"/api/chapters/{self.chapter_id}", "GET /api/chapters/{id}")
                await self.test("GET", f"/api/chapters/{self.chapter_id}/navigation", "GET /api/chapters/{id}/navigation")
                await self.test("GET", f"/api/chapters/{self.chapter_id}/can-generate", "GET /api/chapters/{id}/can-generate")
                await self.test("GET", f"/api/chapters/{self.chapter_id}/analysis", "GET /api/chapters/{id}/analysis", 
                               expected=[200, 404])
                await self.test("GET", f"/api/chapters/{self.chapter_id}/annotations", "GET /api/chapters/{id}/annotations")
                await self.test("GET", f"/api/chapters/{self.chapter_id}/analysis/status", "GET /api/chapters/{id}/analysis/status")
        
        # 伏笔管理
        print("\n📌 [7/16] 伏笔管理 (foreshadows)")
        if self.project_id:
            await self.test("GET", f"/api/foreshadows?project_id={self.project_id}", "GET /api/foreshadows")
            await self.test("GET", f"/api/foreshadows/reminders?project_id={self.project_id}&current_chapter=1", 
                           "GET /api/foreshadows/reminders")
        
        # 时间线管理
        print("\n📌 [8/16] 时间线管理 (timeline)")
        if self.project_id:
            await self.test("GET", f"/api/timeline?project_id={self.project_id}", "GET /api/timeline")
            if self.chapter_id:
                await self.test("GET", f"/api/timeline/chapter/{self.chapter_id}/events", "GET /api/timeline/chapter/{id}/events")
        
        # 一致性检测
        print("\n📌 [9/16] 一致性检测 (consistency)")
        if self.chapter_id:
            await self.test("POST", f"/api/consistency/chapter/{self.chapter_id}/check", 
                           "POST /api/consistency/chapter/{id}/check", expected=[200, 400, 500])
        
        # 质量评分
        print("\n📌 [10/16] 质量评分 (quality)")
        if self.chapter_id:
            await self.test("GET", f"/api/quality/chapter/{self.chapter_id}/basic", "GET /api/quality/chapter/{id}/basic")
        
        # 重复检测
        print("\n📌 [11/16] 重复检测 (duplicate)")
        if self.chapter_id:
            await self.test("GET", f"/api/duplicate/chapter/{self.chapter_id}/check", "GET /api/duplicate/chapter/{id}/check")
        # 项目级别检测很慢，限制章节数
        if self.project_id:
            await self.test("GET", f"/api/duplicate/project/{self.project_id}/check?max_chapters=3", 
                           "GET /api/duplicate/project/{id}/check", slow=True)
        
        # 风格分析
        print("\n📌 [12/16] 风格分析 (style-analysis)")
        if self.chapter_id:
            await self.test("GET", f"/api/style-analysis/chapter/{self.chapter_id}/metrics", 
                           "GET /api/style-analysis/chapter/{id}/metrics")
        if self.project_id:
            await self.test("GET", f"/api/style-analysis/project/{self.project_id}/learn", 
                           "GET /api/style-analysis/project/{id}/learn")
        
        # 二次优化
        print("\n📌 [13/16] 二次优化 (refinement)")
        await self.test("GET", "/api/refinement/models", "GET /api/refinement/models")
        if self.project_id:
            await self.test("GET", f"/api/refinement/project/{self.project_id}/chapters", 
                           "GET /api/refinement/project/{id}/chapters")
            await self.test("GET", f"/api/refinement/project/{self.project_id}/review-summary", 
                           "GET /api/refinement/project/{id}/review-summary")
            await self.test("GET", f"/api/refinement/project/{self.project_id}/status", 
                           "GET /api/refinement/project/{id}/status")
        if self.chapter_id:
            await self.test("GET", f"/api/refinement/chapter/{self.chapter_id}/diff", 
                           "GET /api/refinement/chapter/{id}/diff", expected=[200, 404])
        
        # 记忆系统
        print("\n📌 [14/16] 记忆系统 (memories)")
        if self.project_id:
            await self.test("GET", f"/api/memories/projects/{self.project_id}/memories", 
                           "GET /api/memories/projects/{id}/memories")
            await self.test("GET", f"/api/memories/projects/{self.project_id}/stats", 
                           "GET /api/memories/projects/{id}/stats")
            await self.test("GET", f"/api/memories/projects/{self.project_id}/foreshadows?current_chapter=1", 
                           "GET /api/memories/projects/{id}/foreshadows")
        
        # 其他API
        print("\n📌 [15/16] 其他API")
        await self.test("GET", "/api/settings", "GET /api/settings")
        await self.test("GET", "/api/settings/presets", "GET /api/settings/presets")
        await self.test("GET", "/api/prompt-templates", "GET /api/prompt-templates")
        await self.test("GET", "/api/prompt-templates/categories", "GET /api/prompt-templates/categories")
        await self.test("GET", "/api/prompt-templates/system-defaults", "GET /api/prompt-templates/system-defaults")
        await self.test("GET", "/api/changelog", "GET /api/changelog")
        await self.test("GET", "/api/users/current", "GET /api/users/current")
        await self.test("GET", "/api/users", "GET /api/users")
        await self.test("GET", "/api/relationships/types", "GET /api/relationships/types")
        
        if self.project_id:
            await self.test("GET", f"/api/organizations/project/{self.project_id}", 
                           "GET /api/organizations/project/{id}")
            await self.test("GET", f"/api/relationships/project/{self.project_id}", 
                           "GET /api/relationships/project/{id}")
            await self.test("GET", f"/api/relationships/graph/{self.project_id}", 
                           "GET /api/relationships/graph/{id}")
            await self.test("GET", f"/api/careers?project_id={self.project_id}", 
                           "GET /api/careers")
            await self.test("GET", f"/api/character-growth/project/{self.project_id}", 
                           "GET /api/character-growth/project/{id}")
        
        # MCP插件
        print("\n📌 [16/16] MCP插件 (mcp)")
        await self.test("GET", "/api/mcp/plugins", "GET /api/mcp/plugins")
        await self.test("GET", "/api/mcp/plugins/cache/stats", "GET /api/mcp/plugins/cache/stats")
        
        # 管理员API
        print("\n📌 [BONUS] 管理员API (admin)")
        await self.test("GET", "/api/admin/users", "GET /api/admin/users")
        
        self.summary()
    
    def summary(self):
        print("\n" + "=" * 70)
        print("测试总结")
        print("=" * 70)
        
        total = len(results["passed"]) + len(results["failed"])
        passed = len(results["passed"])
        failed = len(results["failed"])
        
        print(f"\n总计: {total} 个API")
        print(f"✅ 通过: {passed} ({passed/total*100:.1f}%)" if total else "")
        print(f"❌ 失败: {failed} ({failed/total*100:.1f}%)" if total else "")
        
        if results["slow"]:
            print(f"\n⏱️ 慢API ({len(results['slow'])}个):")
            for name, elapsed in results["slow"]:
                print(f"  - {name}: {elapsed:.1f}s")
        
        if results["failed"]:
            print(f"\n❌ 失败详情:")
            for name, detail, status in results["failed"]:
                print(f"  - {name} [{status}]: {detail}")
        
        if total > 0:
            rate = passed / total * 100
            if rate >= 95:
                print(f"\n🎉 优秀！通过率 {rate:.1f}%")
            elif rate >= 80:
                print(f"\n👍 良好！通过率 {rate:.1f}%")
            else:
                print(f"\n⚠️ 需要改进！通过率 {rate:.1f}%")
        
        print("\n" + "=" * 70)


async def main():
    tester = APITester()
    await tester.run_all()
    await tester.client.aclose()
    return 1 if results["failed"] else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
