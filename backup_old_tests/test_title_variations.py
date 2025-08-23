#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.integrations.wechat_official_sender import WeChatOfficialSender
import requests

def test_title_variations():
    """测试不同标题的草稿创建"""
    
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
    
    # 测试不同的标题
    titles_to_test = [
        "Test Title",  # 简单英文
        "测试标题",     # 简单中文
        "OpenAI发布GPT-5",  # 去掉冒号后的部分
        "AI能力再次突破",   # 标题的后半部分
        "OpenAI发布GPT-5AI能力再次突破",  # 去掉冒号和空格
    ]
    
    for title in titles_to_test:
        print(f"\n测试标题: '{title}' (长度: {len(title)})")
        
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={sender.access_token}"
        
        data = {
            "articles": [{
                "title": title,
                "content": "<p>测试内容</p>",
                "author": "Bot",
                "digest": "测试摘要",
                "thumb_media_id": thumb_media_id
            }]
        }
        
        try:
            response = requests.post(url, json=data, timeout=30)
            result = response.json()
            
            if 'errcode' in result and result['errcode'] != 0:
                print(f"失败: {result}")
            elif 'media_id' in result:
                print(f"成功: {result['media_id']}")
            else:
                print(f"异常响应: {result}")
                
        except Exception as e:
            print(f"异常: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    test_title_variations()
