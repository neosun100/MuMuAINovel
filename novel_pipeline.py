#!/usr/bin/env python3
"""
小说全自动创建Pipeline
用法: python novel_pipeline.py config.yaml
"""

import requests
import json
import time
import sys
import os
import yaml
from typing import List, Dict, Optional

# ============ 配置 ============
BASE_URL = os.getenv("MUMUAI_BASE_URL", "http://localhost:8000")
USERNAME = os.getenv("MUMUAI_USERNAME", "admin")
PASSWORD = os.getenv("MUMUAI_PASSWORD", "admin123")

class NovelPipeline:
    def __init__(self):
        self.session = requests.Session()
        self.project_id = None
        
    def login(self) -> bool:
        """Step 1: 登录"""
        print("\n" + "="*50)
        print("Phase 1: 登录系统")
        print("="*50)
        resp = self.session.post(f"{BASE_URL}/api/auth/local/login",
            json={"username": USERNAME, "password": PASSWORD})
        if resp.status_code == 200:
            print("✅ 登录成功")
            return True
        print(f"❌ 登录失败: {resp.text}")
        return False
    
    def create_project(self, title: str, genre: str, description: str) -> Optional[str]:
        """Step 2: 创建项目"""
        print("\n" + "="*50)
        print("Phase 2: 创建项目")
        print("="*50)
        resp = self.session.post(f"{BASE_URL}/api/projects", json={
            "title": title,
            "genre": genre,
            "description": description,
            "target_words": 1000000,
            "chapter_count": 100
        })
        if resp.status_code == 200:
            self.project_id = resp.json()['id']
            print(f"✅ 项目创建成功: {title}")
            print(f"   Project ID: {self.project_id}")
            return self.project_id
        print(f"❌ 创建失败: {resp.text}")
        return None
    
    def set_worldview(self, time_period: str, location: str, atmosphere: str, rules: str) -> bool:
        """Step 3: 设置世界观"""
        print("\n" + "="*50)
        print("Phase 3: 设置世界观")
        print("="*50)
        resp = self.session.put(f"{BASE_URL}/api/projects/{self.project_id}", json={
            "world_time_period": time_period,
            "world_location": location,
            "world_atmosphere": atmosphere,
            "world_rules": rules
        })
        if resp.status_code == 200:
            print("✅ 世界观设置成功")
            print(f"   时代: {time_period[:50]}...")
            print(f"   地点: {location[:50]}...")
            return True
        print(f"❌ 设置失败: {resp.text}")
        return False
    
    def create_characters(self, characters: List[Dict]) -> int:
        """Step 4: 批量创建角色"""
        print("\n" + "="*50)
        print(f"Phase 4: 创建角色 ({len(characters)}个)")
        print("="*50)
        success = 0
        for i, char in enumerate(characters):
            char['project_id'] = self.project_id
            resp = self.session.post(f"{BASE_URL}/api/characters", json=char)
            if resp.status_code == 200:
                success += 1
                if success <= 5 or success % 20 == 0:
                    print(f"  ✅ [{success:03d}/{len(characters)}] {char['name']}")
            else:
                print(f"  ❌ {char['name']} 失败")
        print(f"\n📊 角色创建完成: {success}/{len(characters)}")
        return success
    
    def create_outlines(self, outlines: List[Dict]) -> int:
        """Step 5: 批量创建大纲"""
        print("\n" + "="*50)
        print(f"Phase 5: 创建大纲 ({len(outlines)}章)")
        print("="*50)
        success = 0
        for i, outline in enumerate(outlines):
            chapter_num = outline.get('chapter_number', i+1)
            title = outline.get('title', f'第{chapter_num}章')
            content = outline.get('content', '')
            
            resp = self.session.post(f"{BASE_URL}/api/outlines", json={
                'project_id': self.project_id,
                'title': f'第{chapter_num}章 {title}',
                'content': content,
                'order_index': chapter_num
            })
            if resp.status_code == 200:
                success += 1
                if success <= 5 or success % 20 == 0:
                    print(f"  ✅ [{success:03d}/{len(outlines)}] 第{chapter_num}章: {title[:20]}")
            else:
                print(f"  ❌ 第{chapter_num}章失败")
        print(f"\n📊 大纲创建完成: {success}/{len(outlines)}")
        return success
    
    def create_chapters(self) -> int:
        """Step 6: 从大纲创建章节"""
        print("\n" + "="*50)
        print("Phase 6: 创建章节")
        print("="*50)
        
        # 获取所有大纲
        resp = self.session.get(f"{BASE_URL}/api/outlines/project/{self.project_id}?limit=200")
        outlines = resp.json().get('items', [])
        print(f"获取到 {len(outlines)} 个大纲")
        
        success = 0
        for outline in sorted(outlines, key=lambda x: x.get('order_index', 0)):
            order = outline.get('order_index', 0)
            title = outline.get('title', f'第{order}章')
            content = outline.get('content', '')
            
            resp = self.session.post(f"{BASE_URL}/api/chapters", json={
                'project_id': self.project_id,
                'title': title,
                'summary': content[:500] if content else '',
                'chapter_number': order,
                'outline_id': outline.get('id'),
                'status': 'pending'
            })
            if resp.status_code == 200:
                success += 1
                if success <= 5 or success % 20 == 0:
                    print(f"  ✅ [{success:03d}/{len(outlines)}] {title[:30]}")
        
        print(f"\n📊 章节创建完成: {success}/{len(outlines)}")
        return success
    
    def batch_generate(self, start: int = 1, count: int = 100, target_words: int = 10000) -> Optional[str]:
        """Step 7: 提交批量生成"""
        print("\n" + "="*50)
        print(f"Phase 7: 提交批量生成 (第{start}-{start+count-1}章)")
        print("="*50)
        
        resp = self.session.post(
            f"{BASE_URL}/api/chapters/project/{self.project_id}/batch-generate",
            json={
                "start_chapter_number": start,
                "count": count,
                "target_word_count": target_words
            }
        )
        if resp.status_code == 200:
            data = resp.json()
            batch_id = data.get('batch_id')
            print(f"✅ 批量生成已提交")
            print(f"   Batch ID: {batch_id}")
            print(f"   章节数: {data.get('chapters_to_generate', [])[:3]}...")
            return batch_id
        print(f"❌ 提交失败: {resp.text}")
        return None
    
    def check_progress(self) -> Dict:
        """检查生成进度"""
        resp = self.session.get(f"{BASE_URL}/api/chapters/project/{self.project_id}?limit=200")
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('items', [])
            generated = [c for c in items if c.get('content') and len(c['content']) > 100]
            total_words = sum(c.get('word_count', 0) for c in generated)
            return {
                'total': data.get('total', 0),
                'generated': len(generated),
                'total_words': total_words
            }
        return {'total': 0, 'generated': 0, 'total_words': 0}
    
    def monitor(self, interval: int = 60):
        """监控生成进度"""
        print("\n" + "="*50)
        print("Phase 8: 监控生成进度")
        print("="*50)
        
        while True:
            progress = self.check_progress()
            generated = progress['generated']
            total = progress['total']
            words = progress['total_words']
            
            print(f"  📊 进度: {generated}/{total}章 | 总字数: {words:,}")
            
            if generated >= total and total > 0:
                print(f"\n🎉 全部完成！共{generated}章，{words:,}字")
                break
            
            time.sleep(interval)


def load_config(config_file: str) -> Dict:
    """加载配置文件"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    if len(sys.argv) < 2:
        print("用法: python novel_pipeline.py config.yaml")
        print("或者直接运行使用默认配置")
        # 使用默认配置演示
        run_demo()
        return
    
    config = load_config(sys.argv[1])
    pipeline = NovelPipeline()
    
    # 执行Pipeline
    if not pipeline.login():
        return
    
    if not pipeline.create_project(
        config['title'],
        config['genre'],
        config['description']
    ):
        return
    
    pipeline.set_worldview(
        config['setting']['time'],
        config['setting']['location'],
        config['setting']['atmosphere'],
        config['setting']['rules']
    )
    
    pipeline.create_characters(config['characters'])
    pipeline.create_outlines(config['outlines'])
    pipeline.create_chapters()
    pipeline.batch_generate()
    
    print("\n" + "="*50)
    print("🚀 Pipeline执行完成！")
    print("="*50)
    print(f"项目ID: {pipeline.project_id}")
    print("后台正在生成章节内容，可使用以下命令监控进度:")
    print(f"  python novel_pipeline.py --monitor {pipeline.project_id}")


def run_demo():
    """演示模式"""
    print("="*50)
    print("小说创建Pipeline - 演示模式")
    print("="*50)
    print("""
使用方法:

1. 创建配置文件 (config.yaml):
   
   title: "我的小说"
   genre: "都市科幻"
   description: "故事简介..."
   setting:
     time: "2026年"
     location: "香港"
     atmosphere: "紧张刺激"
     rules: "AI与人类共存"
   characters:
     - name: "主角"
       role_type: "protagonist"
       personality: "性格描述"
       background: "背景故事"
   outlines:
     - chapter_number: 1
       title: "开篇"
       content: "章节概要..."

2. 运行Pipeline:
   python novel_pipeline.py config.yaml

3. 监控进度:
   python novel_pipeline.py --monitor PROJECT_ID
""")


if __name__ == "__main__":
    main()
