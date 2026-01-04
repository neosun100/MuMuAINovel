#!/usr/bin/env python3
"""
自动恢复并继续所有中断的批量生成任务
用法: python auto_resume.py [--daemon]
  --daemon: 后台持续监控模式
"""

import requests
import time
import sys
import os
import argparse

BASE_URL = os.getenv("MUMUAI_BASE_URL", "http://localhost:8000")
USERNAME = os.getenv("MUMUAI_USERNAME", "admin")
PASSWORD = os.getenv("MUMUAI_PASSWORD", "admin123")
CHECK_INTERVAL = int(os.getenv("MUMUAI_CHECK_INTERVAL", "120"))

class TaskResumer:
    def __init__(self):
        self.session = requests.Session()
        
    def login(self) -> bool:
        try:
            resp = self.session.post(f"{BASE_URL}/api/auth/local/login",
                json={"username": USERNAME, "password": PASSWORD}, timeout=30)
            return resp.status_code == 200
        except:
            return False
    
    def get_all_projects(self):
        """获取所有项目"""
        try:
            resp = self.session.get(f"{BASE_URL}/api/projects", timeout=30)
            if resp.status_code == 200:
                return resp.json().get('items', [])
        except:
            pass
        return []
    
    def get_project_progress(self, project_id: str):
        """获取项目生成进度"""
        try:
            resp = self.session.get(
                f"{BASE_URL}/api/chapters/project/{project_id}?limit=200", 
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                items = data.get('items', [])
                total = data.get('total', 0)
                generated = len([c for c in items if c.get('content') and len(c['content']) > 100])
                last_chapter = max([c['chapter_number'] for c in items if c.get('content') and len(c['content']) > 100], default=0)
                return {
                    'total': total,
                    'generated': generated,
                    'last_chapter': last_chapter
                }
        except:
            pass
        return None
    
    def check_active_task(self, project_id: str) -> bool:
        """检查是否有活动的生成任务"""
        try:
            resp = self.session.get(
                f"{BASE_URL}/api/chapters/project/{project_id}/batch-generate/active",
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get('has_active_task', False)
        except:
            pass
        return False
    
    def submit_batch(self, project_id: str, start: int, count: int) -> bool:
        """提交批量生成任务"""
        try:
            resp = self.session.post(
                f"{BASE_URL}/api/chapters/project/{project_id}/batch-generate",
                json={
                    "start_chapter_number": start,
                    "count": count,
                    "target_word_count": 10000
                },
                timeout=60
            )
            if resp.status_code == 200:
                return True
            elif resp.status_code == 400:
                error = resp.json().get('detail', '')
                if '已有正在运行' in error:
                    return None  # 有任务在运行
        except:
            pass
        return False
    
    def resume_all(self):
        """恢复所有未完成的项目"""
        print(f"\n{'='*50}")
        print("🔄 检查并恢复未完成的任务")
        print(f"{'='*50}\n")
        
        if not self.login():
            print("❌ 登录失败")
            return
        
        projects = self.get_all_projects()
        print(f"📚 找到 {len(projects)} 个项目\n")
        
        resumed = 0
        for project in projects:
            project_id = project.get('id')
            title = project.get('title', '未知')
            
            progress = self.get_project_progress(project_id)
            if not progress:
                continue
            
            total = progress['total']
            generated = progress['generated']
            last_chapter = progress['last_chapter']
            
            if total == 0:
                continue
            
            if generated >= total:
                print(f"✅ {title}: 已完成 ({generated}/{total}章)")
                continue
            
            # 检查是否有活动任务
            if self.check_active_task(project_id):
                print(f"🟢 {title}: 正在生成中 ({generated}/{total}章)")
                continue
            
            # 需要恢复
            next_chapter = last_chapter + 1
            remaining = total - last_chapter
            
            print(f"⚠️ {title}: 中断于第{last_chapter}章 ({generated}/{total}章)")
            print(f"   → 尝试从第{next_chapter}章继续...")
            
            result = self.submit_batch(project_id, next_chapter, remaining)
            if result is True:
                print(f"   ✅ 已提交恢复任务: 第{next_chapter}-{total}章")
                resumed += 1
            elif result is None:
                print(f"   🟢 已有任务在运行")
            else:
                print(f"   ❌ 提交失败")
        
        print(f"\n{'='*50}")
        print(f"📊 恢复完成: {resumed} 个任务已重新提交")
        print(f"{'='*50}\n")
        return resumed
    
    def daemon_mode(self):
        """后台持续监控模式"""
        print("🔄 进入后台监控模式...")
        print(f"   检查间隔: {CHECK_INTERVAL}秒")
        print("   按 Ctrl+C 退出\n")
        
        while True:
            try:
                self.resume_all()
                
                # 检查是否全部完成
                if not self.login():
                    time.sleep(CHECK_INTERVAL)
                    continue
                
                projects = self.get_all_projects()
                all_done = True
                for project in projects:
                    progress = self.get_project_progress(project.get('id'))
                    if progress and progress['total'] > 0 and progress['generated'] < progress['total']:
                        all_done = False
                        break
                
                if all_done:
                    print("🎉 所有项目已完成！退出监控。")
                    break
                
                print(f"💤 等待 {CHECK_INTERVAL} 秒后再次检查...\n")
                time.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                print("\n👋 退出监控模式")
                break


def main():
    parser = argparse.ArgumentParser(description='自动恢复中断的批量生成任务')
    parser.add_argument('--daemon', action='store_true', help='后台持续监控模式')
    args = parser.parse_args()
    
    resumer = TaskResumer()
    
    if args.daemon:
        resumer.daemon_mode()
    else:
        resumer.resume_all()


if __name__ == "__main__":
    main()
