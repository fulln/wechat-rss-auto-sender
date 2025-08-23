#!/usr/bin/env python3
"""
调试发送队列问题 - 查看文章质量评分
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.send_service import SendManager
from src.core.config import Config

def debug_send_queue():
    """调试发送队列问题"""
    print("=" * 60)
    print("🔍 调试发送队列问题")
    print("=" * 60)
    
    try:
        # 创建发送管理器
        send_manager = SendManager()
        
        # 获取未发送的文章
        unsent_items = send_manager.multi_rss_manager.cache.get_unsent_items()
        
        print(f"📄 未发送文章总数: {len(unsent_items)}")
        print(f"📊 质量评分要求: {Config.MIN_QUALITY_SCORE}/10")
        print()
        
        if not unsent_items:
            print("❌ 缓存中没有未发送的文章")
            return
        
        # 显示文章详情
        print("📋 文章详情:")
        for i, article in enumerate(unsent_items, 1):
            print(f"\n{i}. {article.title[:60]}...")
            print(f"   来源: {article.source}")
            print(f"   链接: {article.link}")
            print(f"   已发送: {article.is_sent}")
            print(f"   质量评分: {article.quality_score}")
            print(f"   发布时间: {article.pub_date}")
            
        print("\n" + "=" * 60)
        print("🎯 质量评分分析")
        print("=" * 60)
        
        # 分析质量评分
        scored_count = 0
        unscored_count = 0
        qualified_count = 0
        
        for article in unsent_items:
            if article.quality_score is not None:
                scored_count += 1
                if article.quality_score >= Config.MIN_QUALITY_SCORE:
                    qualified_count += 1
                    print(f"✅ {article.title[:40]}... (评分: {article.quality_score}/10)")
                else:
                    print(f"❌ {article.title[:40]}... (评分: {article.quality_score}/10)")
            else:
                unscored_count += 1
                print(f"⭕ {article.title[:40]}... (未评分)")
        
        print(f"\n📈 统计结果:")
        print(f"   已评分文章: {scored_count}")
        print(f"   未评分文章: {unscored_count}")
        print(f"   达标文章: {qualified_count}")
        print(f"   不达标文章: {scored_count - qualified_count}")
        
        if qualified_count == 0:
            print(f"\n💡 建议:")
            print(f"   1. 降低质量评分要求 (当前: {Config.MIN_QUALITY_SCORE}/10)")
            print(f"   2. 或者等待AI评分完成")
            if unscored_count > 0:
                print(f"   3. 还有 {unscored_count} 篇文章需要评分")
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_send_queue()
