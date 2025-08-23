#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.integrations.wechat_official_sender import WeChatOfficialSender
import requests

def test_author_lengths():
    """测试不同作者名称长度"""
    
    config = {
        'enabled': True,
        'app_id': os.getenv('WECHAT_OFFICIAL_APP_ID'),
        'app_secret': os.getenv('WECHAT_OFFICIAL_APP_SECRET'),
        'author_name': 'Bot',
        'use_rich_formatting': False
    }
    
    sender = WeChatOfficialSender(config)
    
    if not sender._ensure_access_token():
        print("无法获取access_token")
        return
    
    # 上传封面
    thumb_media_id = sender._upload_thumb_media("test_cover.jpg")
    if not thumb_media_id:
        print("封面上传失败")
        return
    
    # 测试不同长度的作者名称
    authors_to_test = [
        "",               # 空字符串
        "Bot",           # 短英文
        "小助手",         # 短中文
        "AI科技速递",     # 原始作者名
        "RSS智能助手",    # 稍长中文
        "智能科技资讯助手", # 更长中文
    ]
    
    for author in authors_to_test:
        print(f"\n测试作者: '{author}' (长度: {len(author)})")
        
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={sender.access_token}"
        
        data = {
            "articles": [{
                "title": "测试标题",
                "content": "<p>测试内容</p>",
                "author": author,
                "thumb_media_id": thumb_media_id
            }]
        }
        
        try:
            response = requests.post(url, json=data, timeout=30)
            result = response.json()
            
            if 'errcode' in result and result['errcode'] != 0:
                print(f"❌ 失败: {result}")
            elif 'media_id' in result:
                print(f"✅ 成功: {result['media_id']}")
            else:
                print(f"❓ 异常响应: {result}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    test_author_lengths()
