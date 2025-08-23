#!/usr/bin/env python3
"""
测试发送队列中的文章
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.send_service import SendManager
from src.services.multi_rss_manager import MultiRSSManager

def test_send_queue():
    """测试发送队列"""
    print("=" * 60)
    print("📤 测试发送队列")
    print("=" * 60)
    
    try:
        # 创建发送管理器
        send_manager = SendManager()
        
        # 检查未发送文章
        print("🔍 检查缓存中的文章...")
        unsent_items = send_manager.multi_rss_manager.cache.get_unsent_items()
        print(f"未发送文章数量: {len(unsent_items)}")
        
        for i, item in enumerate(unsent_items, 1):
            print(f"\n文章 {i}:")
            print(f"  标题: {item.title[:60]}...")
            print(f"  来源: {item.source}")
            print(f"  发布时间: {item.pub_date}")
            print(f"  已发送: {item.sent}")
            print(f"  质量评分: {getattr(item, 'quality_score', '未评分')}")
            if hasattr(item, 'image_path') and item.image_path:
                print(f"  封面图片: {item.image_path}")
        
        if unsent_items:
            print(f"\n🚀 尝试发送文章...")
            
            # 尝试发送单篇文章
            result = send_manager.send_single_article()
            print(f"单篇发送结果: {result}")
            
            if not result:
                # 尝试发送批量文章
                print("单篇发送失败，尝试批量发送...")
                result = send_manager.send_batch_articles()
                print(f"批量发送结果: {result}")
        else:
            print("❌ 没有未发送的文章")
            
            # 尝试获取新文章
            print("\n🔄 尝试获取新文章...")
            multi_rss_manager = MultiRSSManager()
            items = multi_rss_manager.fetch_latest_items(since_minutes=60*24)  # 最近24小时
            print(f"获取到 {len(items)} 篇文章")
            
            if items:
                # 重新检查缓存
                unsent_items = send_manager.multi_rss_manager.cache.get_unsent_items()
                print(f"缓存中现有未发送文章: {len(unsent_items)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 开始测试发送队列...")
    
    result = test_send_queue()
    
    if result:
        print("\n✅ 测试完成")
    else:
        print("\n❌ 测试失败")
