#!/usr/bin/env python3
"""
真实RSS数据的微信公众号测试
使用实际的RSS获取和AI总结
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.rss_service import RSSFetcher
from src.services.ai_service import Summarizer
from src.integrations.wechat_official_sender import WeChatOfficialSender
from src.core.config import Config
from datetime import datetime

def test_real_rss_to_wechat():
    """测试完整的RSS到微信公众号流程"""
    
    print("=" * 50)
    print("真实RSS数据微信公众号测试")
    print("=" * 50)
    
    try:
        # 1. 获取RSS数据
        print("🔍 获取RSS数据...")
        rss_fetcher = RSSFetcher()
        
        # 获取最新的RSS条目
        items = rss_fetcher.fetch_latest_items(since_minutes=60)  # 获取最近1小时的内容
        
        if not items:
            print("❌ 没有获取到RSS数据")
            return False
            
        print(f"✅ 获取到 {len(items)} 条RSS数据")
        
        # 2. AI总结
        print("🤖 进行AI总结...")
        summarizer = Summarizer()
        
        # 对第一条进行单独总结
        first_item = items[0]
        print(f"📰 处理文章: {first_item.title}")
        
        summary_content = summarizer.summarize_single_item(first_item)
        
        if not summary_content:
            print("❌ AI总结失败")
            return False
            
        print(f"✅ AI总结完成，内容长度: {len(summary_content)}")
        print(f"📄 总结预览: {summary_content[:200]}...")
        
        # 3. 发送到微信公众号
        print("📱 发送到微信公众号...")
        
        wechat_config = {
            'enabled': True,
            'app_id': os.getenv('WECHAT_OFFICIAL_APP_ID'),
            'app_secret': os.getenv('WECHAT_OFFICIAL_APP_SECRET'),
            'author_name': 'RSS智能助手',
            'use_rich_formatting': True
        }
        
        sender = WeChatOfficialSender(wechat_config)
        
        # 更新条目的总结内容
        first_item.summary = summary_content
        first_item.content = summary_content
        
        # 发送（创建草稿）
        success = sender.send_message(first_item)
        
        if success:
            print("✅ 微信公众号草稿创建成功！")
            print("📱 请到微信公众号后台查看草稿")
            print("\n" + "=" * 50)
            print("🎉 完整流程测试成功")
            print("=" * 50)
            return True
        else:
            print("❌ 微信公众号草稿创建失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    test_real_rss_to_wechat()
