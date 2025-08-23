#!/usr/bin/env python3
"""
简单的微信公众号草稿创建测试
不使用封面图片，专注测试草稿创建功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.integrations.wechat_official_sender import WeChatOfficialSender
from src.services.rss_service import RSSItem
from datetime import datetime

def test_simple_draft_creation():
    """测试简单的草稿创建（不使用封面图片）"""
    
    # 配置
    config = {
        'enabled': True,
        'app_id': os.getenv('WECHAT_OFFICIAL_APP_ID'),
        'app_secret': os.getenv('WECHAT_OFFICIAL_APP_SECRET'),
        'author_name': 'RSS助手',
        'use_rich_formatting': True
    }
    
    sender = WeChatOfficialSender(config)
    
    # 创建简单的测试文章
    test_item = RSSItem(
        title="简单测试",
        link="https://example.com/simple-test",
        description="这是一个简单的微信公众号草稿测试。",
        published=datetime.now()
    )
    
    # 添加简单的内容
    test_item.content = f"""
    <h2>微信公众号草稿测试</h2>
    <p>这是一个测试文章，用于验证微信公众号草稿创建功能。</p>
    <p>测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    """
    
    test_item.summary = "这是一个简单的微信公众号草稿测试。"
    
    # 明确设置没有本地图片
    def has_local_image():
        return False
    
    test_item.has_local_image = has_local_image
    
    # 创建消息
    message = f"""📰 {test_item.title}

✨ 核心要点：
{test_item.summary}

🔗 阅读原文：{test_item.link}
"""
    
    print("🔍 开始测试微信公众号草稿创建...")
    
    try:
        # 发送消息
        result = sender.send_message(message, rss_item=test_item)
        
        if result:
            print("✅ 草稿创建成功！请到微信公众号后台查看")
            return True
        else:
            print("❌ 草稿创建失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("微信公众号简单草稿创建测试")
    print("=" * 50)
    
    success = test_simple_draft_creation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试成功：草稿已创建")
    else:
        print("❌ 测试失败：请检查配置和日志")
    print("=" * 50)
