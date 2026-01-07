#!/usr/bin/env python3
"""测试流式 API - 重复检测和一致性检测（使用 Cookie 认证）"""
import httpx
import asyncio
import json
import os
import sys

BASE_URL = os.getenv("MUMUAI_BASE_URL", "http://localhost:8000")
USERNAME = os.getenv("MUMUAI_USERNAME", "admin")
PASSWORD = os.getenv("MUMUAI_PASSWORD", "admin123")

async def login() -> httpx.Cookies:
    """登录获取 cookies"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/api/auth/local/login",
            json={"username": USERNAME, "password": PASSWORD}
        )
        if resp.status_code == 200 and resp.json().get("success"):
            print(f"  用户: {resp.json()['user']['username']}")
            return resp.cookies
        print(f"❌ 登录失败: {resp.status_code} - {resp.text}")
        sys.exit(1)

async def get_test_data(cookies: httpx.Cookies) -> tuple:
    """获取测试用的项目ID和章节ID"""
    async with httpx.AsyncClient(cookies=cookies) as client:
        # 获取项目
        resp = await client.get(f"{BASE_URL}/api/projects")
        if resp.status_code != 200:
            print(f"❌ 获取项目失败: {resp.status_code}")
            return None, None
        
        data = resp.json()
        # 支持两种格式: 直接数组 或 {total, items}
        projects = data.get("items", data) if isinstance(data, dict) else data
        if not projects:
            print("❌ 无可用项目")
            return None, None
        
        project_id = projects[0]["id"]
        project_title = projects[0].get("title", "未知")
        print(f"  项目: {project_title} ({project_id[:8]}...)")
        
        # 获取章节
        resp = await client.get(f"{BASE_URL}/api/chapters/project/{project_id}")
        if resp.status_code != 200:
            print(f"❌ 获取章节失败: {resp.status_code}")
            return project_id, None
        
        ch_data = resp.json()
        chapters = ch_data.get("items", ch_data) if isinstance(ch_data, dict) else ch_data
        chapters_with_content = [c for c in chapters if c.get("content")]
        
        if not chapters_with_content:
            print("❌ 无已完成章节")
            return project_id, None
        
        # 选择第2章或更后的章节（有前置章节可检测情节连贯性）
        target_chapter = None
        for c in chapters_with_content:
            if c.get("chapter_number", 0) >= 2:
                target_chapter = c
                break
        if not target_chapter:
            target_chapter = chapters_with_content[0]
        
        print(f"  章节: 第{target_chapter['chapter_number']}章 ({target_chapter['id'][:8]}...)")
        print(f"  已完成章节数: {len(chapters_with_content)}")
        
        return project_id, target_chapter["id"]

async def test_duplicate_stream(cookies: httpx.Cookies, project_id: str):
    """测试重复检测流式 API"""
    print("\n" + "="*60)
    print("📋 测试: GET /api/duplicate/project/{id}/check-stream")
    print("="*60)
    
    url = f"{BASE_URL}/api/duplicate/project/{project_id}/check-stream?max_chapters=5"
    
    event_count = 0
    start_time = asyncio.get_event_loop().time()
    last_event = None
    
    try:
        async with httpx.AsyncClient(cookies=cookies, timeout=120) as client:
            async with client.stream("GET", url) as resp:
                if resp.status_code != 200:
                    print(f"❌ 请求失败: {resp.status_code}")
                    content = await resp.aread()
                    print(f"   响应: {content.decode()[:200]}")
                    return False
                
                print(f"✅ 连接成功，接收流式数据...")
                
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            print(f"\n✅ 流结束标记收到")
                            break
                        
                        event_count += 1
                        try:
                            event = json.loads(data)
                            last_event = event
                            event_type = event.get("type", "unknown")
                            
                            if event_type == "progress":
                                phase = event.get("phase", "")
                                current = event.get("current", 0)
                                total = event.get("total", 0)
                                print(f"  📊 进度: {phase} {current}/{total}    ", end="\r")
                            elif event_type == "internal":
                                ch = event.get("chapter_number", "?")
                                count = event.get("count", 0)
                                print(f"\n  🔍 章节{ch}内部重复: {count}处")
                            elif event_type == "cross":
                                ch1 = event.get("chapter1", {}).get("number", "?")
                                ch2 = event.get("chapter2", {}).get("number", "?")
                                count = event.get("count", 0)
                                print(f"\n  🔗 章节{ch1}-{ch2}间重复: {count}处")
                            elif event_type == "complete":
                                print(f"\n  ✅ 完成! 检查{event.get('chapters_checked', 0)}章, 共{event.get('total_issues', 0)}个问题")
                            elif event_type == "error":
                                print(f"\n  ❌ 错误: {event.get('message', '')}")
                                return False
                        except json.JSONDecodeError:
                            pass
        
        elapsed = asyncio.get_event_loop().time() - start_time
        print(f"\n📈 统计: 收到 {event_count} 个事件, 耗时 {elapsed:.1f}s")
        
        # 验证是否收到完成事件
        if last_event and last_event.get("type") == "complete":
            return True
        return event_count > 0
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_consistency_stream(cookies: httpx.Cookies, chapter_id: str):
    """测试一致性检测流式 API"""
    print("\n" + "="*60)
    print("📋 测试: POST /api/consistency/chapter/{id}/check-stream")
    print("="*60)
    
    url = f"{BASE_URL}/api/consistency/chapter/{chapter_id}/check-stream"
    
    event_count = 0
    start_time = asyncio.get_event_loop().time()
    last_event = None
    
    try:
        async with httpx.AsyncClient(cookies=cookies, timeout=120) as client:
            async with client.stream("POST", url) as resp:
                if resp.status_code != 200:
                    print(f"❌ 请求失败: {resp.status_code}")
                    content = await resp.aread()
                    print(f"   响应: {content.decode()[:200]}")
                    return False
                
                print(f"✅ 连接成功，接收流式数据...")
                
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            print(f"\n✅ 流结束标记收到")
                            break
                        
                        event_count += 1
                        try:
                            event = json.loads(data)
                            last_event = event
                            event_type = event.get("type", "unknown")
                            
                            if event_type == "start":
                                ch = event.get("chapter_number", "?")
                                print(f"  🚀 开始检测章节 {ch}")
                            elif event_type == "progress":
                                step = event.get("step", "")
                                msg = event.get("message", "")
                                print(f"  📊 {step}: {msg}")
                            elif event_type == "character_result":
                                score = event.get("data", {}).get("score", "?")
                                issues = len(event.get("data", {}).get("issues", []))
                                print(f"  🎭 角色一致性: {score}分, {issues}个问题")
                            elif event_type == "plot_result":
                                score = event.get("data", {}).get("score", "?")
                                issues = len(event.get("data", {}).get("issues", []))
                                print(f"  📖 情节连贯性: {score}分, {issues}个问题")
                            elif event_type == "complete":
                                overall = event.get("overall_score", "?")
                                print(f"  ✅ 完成! 综合评分: {overall}")
                            elif event_type == "error":
                                print(f"  ❌ 错误: {event.get('message', '')}")
                                return False
                        except json.JSONDecodeError:
                            pass
        
        elapsed = asyncio.get_event_loop().time() - start_time
        print(f"\n📈 统计: 收到 {event_count} 个事件, 耗时 {elapsed:.1f}s")
        
        # 验证是否收到完成事件
        if last_event and last_event.get("type") == "complete":
            return True
        return event_count > 0
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🚀 流式 API 测试")
    print("="*60)
    
    # 登录
    print("🔐 登录中...")
    cookies = await login()
    print(f"✅ 登录成功")
    
    # 获取测试数据
    print("\n📦 获取测试数据...")
    project_id, chapter_id = await get_test_data(cookies)
    
    if not project_id:
        print("\n❌ 无法获取测试数据，请先创建项目和章节")
        return 1
    
    results = []
    
    # 测试重复检测流式 API
    result = await test_duplicate_stream(cookies, project_id)
    results.append(("重复检测流式API", result))
    
    # 测试一致性检测流式 API
    if chapter_id:
        result = await test_consistency_stream(cookies, chapter_id)
        results.append(("一致性检测流式API", result))
    else:
        print("\n⚠️ 跳过一致性检测测试（无可用章节）")
    
    # 汇总
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
    
    all_passed = all(r[1] for r in results)
    print(f"\n{'✅ 全部测试通过!' if all_passed else '❌ 存在失败测试'}")
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
