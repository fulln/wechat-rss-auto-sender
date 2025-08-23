#!/usr/bin/env python3
"""
测试微信公众号永久素材上传和文章发布的真实API调用
注意：需要配置正确的微信公众号凭据和IP白名单
"""

import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.integrations.wechat_official_sender import WeChatOfficialSender
from src.core.config import Config
from src.services.rss_service import RSSItem
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_wechat_official_real():
    """测试微信公众号真实API功能"""
    
    # 1. 初始化配置和发送器
    config = Config()
    
    if not config.WECHAT_OFFICIAL_APP_ID or not config.WECHAT_OFFICIAL_APP_SECRET:
        print("❌ 微信公众号配置不完整，请检查.env文件")
        print("需要配置：")
        print("- WECHAT_OFFICIAL_APP_ID")
        print("- WECHAT_OFFICIAL_APP_SECRET")
        print("- WECHAT_OFFICIAL_SENDER_ENABLED=true")
        return False
    
    sender = WeChatOfficialSender(config)
    
    # 2. 测试获取访问令牌
    print("🔍 测试获取访问令牌...")
    try:
        access_token = sender._get_access_token()
        if access_token:
            print(f"✅ 访问令牌获取成功: {access_token[:20]}...")
        else:
            print("❌ 访问令牌获取失败")
            return False
    except Exception as e:
        print(f"❌ 访问令牌获取异常: {e}")
        return False
    
    # 3. 创建测试RSS项目
    test_rss_item = RSSItem(
        guid="test-wechat-official-permanent-media",
        title="微信公众号永久素材测试",
        link="https://example.com/test",
        description="这是一个测试微信公众号永久素材上传功能的文章。",
        content="""
        <h1>微信公众号永久素材测试</h1>
        <p>本文用于测试微信公众号API的永久素材上传功能。</p>
        <p>永久素材的优势：</p>
        <ul>
            <li>素材不会过期</li>
            <li>可以重复使用</li>
            <li>管理更方便</li>
        </ul>
        <p>测试时间：{}</p>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        pub_date=datetime.now(),
        author="RSS自动发送器",
        image_url=None
    )
    
    # 4. 测试内容格式化
    print("🔍 测试内容格式化...")
    try:
        formatted_content = sender._format_content_for_wechat(test_rss_item)
        print(f"✅ 内容格式化成功，长度: {len(formatted_content)} 字符")
        
        # 显示格式化内容的前200个字符
        print(f"内容预览: {formatted_content[:200]}...")
    except Exception as e:
        print(f"❌ 内容格式化失败: {e}")
        return False
    
    # 5. 测试发送到微信公众号（创建草稿）
    print("🔍 测试发送到微信公众号...")
    try:
        result = sender.send(test_rss_item)
        if result:
            print("✅ 微信公众号测试成功！")
            print("文章已创建为草稿，请到微信公众号后台查看")
            return True
        else:
            print("❌ 微信公众号测试失败")
            return False
    except Exception as e:
        print(f"❌ 微信公众号测试异常: {e}")
        # 如果是IP白名单问题，给出提示
        if "ip not allow" in str(e).lower():
            print("\n💡 可能是IP白名单问题，请在微信公众号后台添加当前服务器IP到白名单：")
            print("   微信公众平台 -> 开发 -> 基本配置 -> IP白名单")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("微信公众号永久素材上传功能测试")
    print("=" * 60)
    
    success = test_wechat_official_real()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 测试完成：所有功能正常")
    else:
        print("❌ 测试失败：请检查配置和网络连接")
    print("=" * 60)
