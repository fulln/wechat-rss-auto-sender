#!/usr/bin/env python3
"""
测试微信公众号HTML格式化功能
"""

import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.integrations.wechat_official_sender import WeChatOfficialSender

def test_html_formatting():
    """测试HTML格式化功能"""
    
    # 创建微信公众号发送器实例（不需要真实配置）
    sender = WeChatOfficialSender({
        'enabled': False,  # 不启用真实发送
        'app_id': 'test',
        'app_secret': 'test'
    })
    
    # 测试消息内容
    test_message = """📰 OpenAI推出升级版GPT-4 Turbo模型，人工智能再进化！💡

新一代GPT-4 Turbo在推理能力、代码生成和多语言支持方面实现重大突破✨响应速度提升50%，信息准确度提高40%，上下文理解能力显著增强，并配备更完善的安全防护机制🚀

这不仅意味着更流畅的AI对话体验，更将推动教育、科研、创意产业等多个领域的智能化变革。企业可获得更精准的数据分析，开发者能快速生成优质代码，语言学习者将拥有更强大的跨语言交流助手🌍

• 响应速度提升50%，处理效率显著优化
• 多语言支持覆盖全球主要语言
• 代码生成准确率达到新高度
• 安全防护机制全面升级

阅读原文：https://example.com/test-article

#人工智能 #GPT4Turbo #科技创新"""
    
    print("🔍 测试微信公众号HTML格式化...")
    print("=" * 60)
    
    # 测试解析消息结构
    sections = sender._parse_message_sections(test_message)
    print("📋 解析的消息结构:")
    print(f"  标题: {sections['title']}")
    print(f"  要点数量: {len(sections['highlights'])}")
    print(f"  标签: {sections['tags']}")
    print(f"  链接: {sections['link']}")
    print()
    
    # 测试HTML格式化
    html_content = sender._format_content(test_message)
    
    print("📝 生成的HTML内容:")
    print("=" * 60)
    print(html_content)
    print("=" * 60)
    
    # 保存到文件用于预览
    output_file = "wechat_official_preview.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML内容已保存到: {output_file}")
    print("💡 可以用浏览器打开该文件预览效果")
    
    return True

if __name__ == "__main__":
    try:
        success = test_html_formatting()
        if success:
            print("\n🎉 HTML格式化测试完成！")
        else:
            print("\n💥 测试失败。")
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
