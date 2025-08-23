#!/usr/bin/env python3
"""
最简单的微信公众号草稿测试
只使用必要字段
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.integrations.wechat_official_sender import WeChatOfficialSender
import requests
import time

def test_minimal_draft():
    """测试最基本的草稿创建"""
    
    print("=" * 50)
    print("最简微信公众号草稿测试")
    print("=" * 50)
    
    try:
        # 配置
        config = {
            'enabled': True,
            'app_id': os.getenv('WECHAT_OFFICIAL_APP_ID'),
            'app_secret': os.getenv('WECHAT_OFFICIAL_APP_SECRET'),
            'author_name': 'Bot',
            'use_rich_formatting': False
        }
        
        sender = WeChatOfficialSender(config)
        
        # 确保有access_token
        if not sender._ensure_access_token():
            print("❌ 无法获取access_token")
            return False
        
        # 上传封面图片
        print("📸 上传封面图片...")
        thumb_media_id = sender._upload_thumb_media("test_cover.jpg")
        if not thumb_media_id:
            print("❌ 封面图片上传失败")
            return False
        
        print(f"✅ 封面上传成功: {thumb_media_id}")
        
        # 直接调用微信API创建最简草稿
        print("📝 创建草稿...")
        
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={sender.access_token}"
        
        # 最简数据
        data = {
            "articles": [{
                "title": "测试标题",
                "content": "<p>这是一个测试内容</p>",
                "author": "Bot",
                "digest": "测试摘要",
                "thumb_media_id": thumb_media_id
            }]
        }
        
        print(f"📤 请求数据: {data}")
        
        response = requests.post(url, json=data, timeout=30)
        result = response.json()
        
        print(f"📥 响应结果: {result}")
        
        if 'errcode' in result and result['errcode'] != 0:
            print(f"❌ 草稿创建失败: {result}")
            return False
        
        if 'media_id' in result:
            print(f"✅ 草稿创建成功: {result['media_id']}")
            return True
        else:
            print(f"❌ 响应格式异常: {result}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    test_minimal_draft()
