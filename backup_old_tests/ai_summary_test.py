#!/usr/bin/env python3
"""
使用模拟真实RSS数据的微信公众号测试
专注测试AI总结和微信发送功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.rss_service import RSSItem
from src.services.ai_service import Summarizer
from src.integrations.wechat_official_sender import WeChatOfficialSender
from datetime import datetime

def test_ai_summary_to_wechat():
    """测试AI总结到微信公众号的完整流程"""
    
    print("=" * 50)
    print("AI总结+微信公众号测试")
    print("=" * 50)
    
    try:
        # 1. 创建真实格式的RSS数据
        print("📰 创建测试RSS数据...")
        
        test_item = RSSItem(
            title="OpenAI发布GPT-5：AI能力再次突破",
            link="https://example.com/openai-gpt5-breakthrough",
            description="""
            OpenAI今日正式发布了最新的GPT-5模型，该模型在推理能力、多模态理解和代码生成方面都有显著提升。
            据OpenAI官方介绍，GPT-5相比GPT-4在数学推理能力上提升了40%，在复杂问题解决方面提升了35%。
            新模型还支持更长的上下文窗口，可以处理高达1000万token的输入。
            这一突破将为人工智能在教育、医疗、金融等领域的应用带来新的可能性。
            业内专家认为，GPT-5的发布标志着AI技术进入了一个新的阶段。
            """,
            published=datetime.now()
        )
        
        print(f"✅ 测试文章: {test_item.title}")
        
        # 2. AI总结
        print("🤖 进行AI总结...")
        summarizer = Summarizer()
        
        summary_content = summarizer.summarize_single_item(test_item)
        
        if not summary_content:
            print("❌ AI总结失败")
            return False
            
        print(f"✅ AI总结完成，内容长度: {len(summary_content)}")
        print("📄 总结内容:")
        print("-" * 50)
        print(summary_content)
        print("-" * 50)
        
        # 3. 发送到微信公众号
        print("📱 发送到微信公众号...")
        
        wechat_config = {
            'enabled': True,
            'app_id': os.getenv('WECHAT_OFFICIAL_APP_ID'),
            'app_secret': os.getenv('WECHAT_OFFICIAL_APP_SECRET'),
            'author_name': 'AI科技速递',
            'use_rich_formatting': False  # 使用简单格式化
        }
        
        sender = WeChatOfficialSender(wechat_config)
        
        # 更新条目的总结内容
        test_item.summary = summary_content
        test_item.content = summary_content
        
        # 明确设置没有本地图片
        def has_local_image():
            return False
        test_item.has_local_image = has_local_image
        
        # 发送（创建草稿）
        success = sender.send_message(
            message=summary_content,
            title=test_item.title,
            rss_item=test_item,
            type='draft'
        )
        
        if success:
            print("✅ 微信公众号草稿创建成功！")
            print("📱 请到微信公众号后台查看草稿")
            print("\n" + "=" * 50)
            print("🎉 AI总结+微信发送测试成功")
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
    
    test_ai_summary_to_wechat()
