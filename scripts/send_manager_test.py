#!/usr/bin/env python3
"""
发送管理器测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.send_manager import SendManager
from src.rss_fetcher import RSSFetcher
from src.utils import setup_logger

logger = setup_logger(__name__)

def test_send_manager():
    """测试发送管理器功能"""
    print("=== 发送管理器功能测试 ===\n")
    
    try:
        # 创建发送管理器
        send_manager = SendManager()
        
        # 1. 获取发送状态
        print("📊 当前发送状态:")
        status = send_manager.get_send_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # 2. 获取待发送文章
        print(f"\n📝 获取待发送文章:")
        articles = send_manager.select_articles_to_send()
        print(f"待发送文章数: {len(articles)}")
        
        if articles:
            print("文章列表:")
            for i, article in enumerate(articles, 1):
                print(f"  {i}. {article.title}")
                print(f"     发送状态: {'已发送' if article.sent_status else '未发送'}")
                if article.sent_time:
                    print(f"     发送时间: {article.sent_time}")
        
        # 3. 检查发送时机
        print(f"\n⏰ 发送时机检查:")
        can_send = send_manager.can_send_now()
        print(f"当前可以发送: {can_send}")
        
        if not can_send:
            next_time = send_manager.get_next_send_time()
            print(f"下次发送时间: {next_time}")
        
        # 4. 模拟发送（如果有文章且可以发送）
        if articles and can_send:
            print(f"\n🚀 模拟发送过程:")
            print("注意：这是模拟发送，不会真正发送微信消息")
            
            # 这里可以选择是否真的发送
            choice = input("是否真的发送到微信？(y/N): ").strip().lower()
            
            if choice == 'y':
                sent_count = send_manager.process_pending_articles()
                print(f"实际发送了 {sent_count} 篇文章")
            else:
                print("跳过实际发送")
        
        print("\n✅ 发送管理器测试完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 发送管理器测试失败: {e}")
        return False

if __name__ == "__main__":
    test_send_manager()
