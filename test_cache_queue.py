#!/usr/bin/env python3
"""
测试文章缓存和发送队列
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.multi_rss_manager import MultiRSSManager
from src.services.send_service import SendManager
from src.core.config import Config

def test_cache_and_queue():
    """测试缓存和发送队列"""
    print("=" * 60)
    print("🔍 测试文章缓存和发送队列")
    print("=" * 60)
    
    try:
        # 1. 强制获取新文章
        print("1. 获取最新文章...")
        manager = MultiRSSManager()
        items = manager.fetch_latest_items(since_minutes=24*60)  # 最近24小时
        print(f"   获取到 {len(items)} 篇文章")
        
        if items:
            print("\n📄 文章列表:")
            for i, item in enumerate(items[:3], 1):  # 只显示前3篇
                print(f"   {i}. {item.title[:50]}...")
                print(f"      来源: {getattr(item, 'source_name', '未知')}")
                print(f"      已发送: {item.sent_status}")
                print(f"      质量评分: {item.quality_score}")
        
        # 2. 检查缓存中的文章
        print(f"\n2. 检查缓存状态...")
        cache = manager.cache
        if cache:
            unsent_items = cache.get_unsent_items()
            print(f"   缓存中未发送文章: {len(unsent_items)}")
            
            if unsent_items:
                print("\n📋 缓存中的未发送文章:")
                for i, item in enumerate(unsent_items[:3], 1):
                    print(f"   {i}. {item.title[:50]}...")
                    print(f"      已发送: {item.sent_status}")
                    print(f"      质量评分: {item.quality_score}")
        else:
            print("   ❌ 无法访问缓存")
        
        # 3. 测试发送服务
        print(f"\n3. 测试发送服务...")
        send_manager = SendManager()
        
        # 降低质量要求进行测试
        original_score = Config.MIN_QUALITY_SCORE
        Config.MIN_QUALITY_SCORE = 5  # 临时降低到5分
        
        articles_to_send = send_manager.select_articles_to_send(max_count=1)
        print(f"   选择发送的文章数: {len(articles_to_send)}")
        
        # 恢复原始配置
        Config.MIN_QUALITY_SCORE = original_score
        
        if articles_to_send:
            article = articles_to_send[0]
            print(f"   准备发送: {article.title[:50]}...")
            print(f"   质量评分: {article.quality_score}/10")
        
        # 4. 分析问题
        print(f"\n4. 问题分析:")
        print(f"   当前质量要求: {Config.MIN_QUALITY_SCORE}/10")
        print(f"   缓存文章数: {len(unsent_items) if 'unsent_items' in locals() else '未知'}")
        print(f"   可发送文章数: {len(articles_to_send)}")
        
        if len(unsent_items if 'unsent_items' in locals() else []) > 0 and len(articles_to_send) == 0:
            print(f"\n💡 建议: 文章质量评分可能不够高，考虑:")
            print(f"   1. 降低 MIN_QUALITY_SCORE (当前: {Config.MIN_QUALITY_SCORE})")
            print(f"   2. 检查AI评分服务是否正常工作")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cache_and_queue()
