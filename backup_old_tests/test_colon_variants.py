#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.integrations.wechat_official_sender import WeChatOfficialSender
import requests

def test_colon_variants():
    """测试不同冒号的标题"""
    
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
    
    # 测试不同版本的标题
    titles = [
        "OpenAI发布GPT-5：AI能力再次突破",  # 全角冒号 (U+FF1A)
        "OpenAI发布GPT-5:AI能力再次突破",   # 半角冒号 (U+003A)
        "OpenAI发布GPT-5 AI能力再次突破",   # 空格替代
        "OpenAI发布GPT-5-AI能力再次突破",   # 短横线替代
    ]
    
    for title in titles:
        print(f"\n测试标题: '{title}'")
        print(f"标题长度: {len(title)}")
        
        # 检查冒号字符
        if '：' in title:
            print("包含全角冒号 (U+FF1A)")
        elif ':' in title:
            print("包含半角冒号 (U+003A)")
        else:
            print("不包含冒号")
        
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
    
    test_colon_variants()
