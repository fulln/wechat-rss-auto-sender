#!/usr/bin/env python3
"""
调试版本的草稿创建测试
"""

import sys
import os
import logging

# 设置调试日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.integrations.wechat_official_sender import WeChatOfficialSender
from src.services.rss_service import RSSItem
from datetime import datetime

def test_debug_draft_creation():
    """调试草稿创建"""
    
    # 配置
    config = {
        'enabled': True,
        'app_id': os.getenv('WECHAT_OFFICIAL_APP_ID'),
        'app_secret': os.getenv('WECHAT_OFFICIAL_APP_SECRET'),
        'author_name': 'RSS助手',
        'use_rich_formatting': True
    }
    
    sender = WeChatOfficialSender(config)
    
    # 创建测试文章
    test_item = RSSItem(
        title="调试测试",
        link="https://example.com/debug-test",
        description="调试草稿创建。",
        published=datetime.now()
    )
    
    test_item.summary = "调试草稿创建。"
    
    # 明确设置没有本地图片
    def has_local_image():
        return False
    
    test_item.has_local_image = has_local_image
    
    message = f"📰 {test_item.title}\n\n✨ 核心要点：\n{test_item.summary}\n\n🔗 阅读原文：{test_item.link}"
    
    print("🔍 开始调试草稿创建...")
    print(f"测试消息: {message}")
    
    try:
        result = sender.send_message(message, rss_item=test_item)
        
        if result:
            print("✅ 草稿创建成功！")
            return True
        else:
            print("❌ 草稿创建失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

if __name__ == "__main__":
    test_debug_draft_creation()
