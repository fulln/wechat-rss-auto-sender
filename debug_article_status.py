#!/usr/bin/env python3
"""
调试脚本：追踪文章状态变化
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.multi_rss_manager import MultiRSSManager
from src.services.send_service import SendManager
from src.core.utils import setup_logger

logger = setup_logger(__name__)

def debug_article_status():
    """调试文章状态"""
    print("=" * 80)
    print("📊 调试文章状态变化")
    print("=" * 80)
    
    # 创建管理器
    manager = MultiRSSManager()
    send_manager = SendManager()
    
    print("\n🔍 步骤1: 检查当前缓存状态")
    unsent_items = manager.cache.get_unsent_items()
    print(f"当前未发送文章数: {len(unsent_items)}")
    
    for i, item in enumerate(unsent_items[:3]):
        print(f"  文章 {i+1}: {item.title[:40]}...")
        print(f"    sent_status: {item.sent_status}")
        print(f"    excluded: {item.excluded_from_sending}")
        print(f"    quality_score: {item.quality_score}")
        print(f"    send_attempts: {item.send_attempts}")
        print(f"    is_sendable(): {item.is_sendable()}")
        print()
    
    print("\n🎯 步骤2: 模拟选择文章过程")
    selected_articles = send_manager.select_articles_to_send()
    print(f"选择的文章数量: {len(selected_articles)}")
    
    print("\n🔄 步骤3: 再次检查缓存状态")
    unsent_items_after = manager.cache.get_unsent_items()
    print(f"选择后未发送文章数: {len(unsent_items_after)}")
    
    print("\n📊 步骤4: 对比前后状态")
    if len(unsent_items) != len(unsent_items_after):
        print(f"⚠️ 文章数量变化: {len(unsent_items)} -> {len(unsent_items_after)}")
        
        # 找出被移除的文章
        before_ids = {item.link for item in unsent_items}
        after_ids = {item.link for item in unsent_items_after}
        removed_ids = before_ids - after_ids
        
        if removed_ids:
            print(f"❌ 被移除的文章: {len(removed_ids)}")
            for item in unsent_items:
                if item.link in removed_ids:
                    print(f"  - {item.title[:40]}...")
                    print(f"    原因: excluded={item.excluded_from_sending}, reason={item.exclusion_reason}")
                    print(f"    质量分: {item.quality_score}")
    else:
        print("✅ 文章数量未变化")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    debug_article_status()
