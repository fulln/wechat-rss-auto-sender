#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.integrations.wechat_official_sender import WeChatOfficialSender
import json

def test_utf8_encoding():
    """测试UTF-8编码处理"""
    
    config = {
        'enabled': True,
        'app_id': os.getenv('WECHAT_OFFICIAL_APP_ID'),
        'app_secret': os.getenv('WECHAT_OFFICIAL_APP_SECRET'),
        'author_name': 'RSS Bot',  # 使用英文作者名
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
    
    # 测试中文标题和内容
    chinese_title = "OpenAI发布GPT-5:AI能力再次突破"
    chinese_content = """
    <div>
        <p style="font-size: 16px; line-height: 1.6; color: #333;">
            🤖【GPT-5震撼发布！AI能力全面突破】💡<br><br>
            这是一个测试中文内容的草稿。<br>
            包含中文字符：人工智能、机器学习、深度学习<br>
            以及各种表情符号：🚀🎯💡🔍
        </p>
    </div>
    """
    
    print(f"测试标题: {chinese_title}")
    print(f"测试内容长度: {len(chinese_content)}")
    
    # 直接调用草稿创建
    success = sender._create_draft_v2(chinese_title, chinese_content, thumb_media_id)
    
    if success:
        print("✅ UTF-8编码草稿创建成功！")
        return True
    else:
        print("❌ UTF-8编码草稿创建失败")
        return False

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    test_utf8_encoding()
