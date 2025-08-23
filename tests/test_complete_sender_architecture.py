#!/usr/bin/env python3
"""
完整的发送器架构测试
测试所有发送器的功能和配置
"""

import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.integrations.send_service_manager import SendServiceManager
from src.core.config import Config

def test_complete_sender_architecture():
    """测试完整的发送器架构"""
    
    print("🔍 测试完整发送器架构...")
    print("=" * 60)
    
    # 显示当前配置
    print("📋 当前配置:")
    sender_configs = Config.get_sender_configs()
    enabled_senders = Config.get_enabled_senders()
    
    print(f"启用的发送器列表: {enabled_senders}")
    for name, config in sender_configs.items():
        status = "✅ 启用" if config['enabled'] else "❌ 禁用"
        print(f"  {name}: {status}")
    print()
    
    # 初始化发送服务管理器
    print("🚀 初始化发送服务管理器...")
    try:
        send_manager = SendServiceManager()
        print("✅ 发送服务管理器初始化成功")
        print(f"📊 已启用发送器: {', '.join(send_manager.get_enabled_senders())}")
    except Exception as e:
        print(f"❌ 发送服务管理器初始化失败: {e}")
        return False
    print()
    
    # 获取发送器信息
    print("📊 发送器详细信息:")
    sender_info = send_manager.get_sender_info()
    for name, info in sender_info.items():
        print(f"  {name}:")
        for key, value in info.items():
            print(f"    {key}: {value}")
        print()
    
    # 测试连接
    print("🔗 测试发送器连接:")
    connection_results = send_manager.test_all_connections()
    for name, success in connection_results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {name}: {status}")
    print()
    
    # 测试消息发送
    test_message = """📰 人工智能技术重大突破！🔥

最新研究表明，新一代AI模型在多个领域取得突破性进展：

✨ 自然语言理解能力显著提升
🚀 多模态处理技术实现新突破  
💡 推理和逻辑能力达到新高度
🌍 跨语言交流障碍进一步消除

这些技术进步将为教育、医疗、金融等行业带来革命性变化，预计未来3-5年内将实现大规模商业应用。

阅读原文：https://example.com/ai-breakthrough-2024

#人工智能 #科技突破 #技术创新"""
    
    print("📤 测试消息发送:")
    print("消息内容预览:")
    print("-" * 40)
    print(test_message[:200] + "..." if len(test_message) > 200 else test_message)
    print("-" * 40)
    
    try:
        send_results = send_manager.send_message(test_message)
        print("发送结果:")
        for sender_name, success in send_results.items():
            status = "✅ 成功" if success else "❌ 失败"
            print(f"  {sender_name}: {status}")
    except Exception as e:
        print(f"❌ 发送测试失败: {e}")
        return False
    print()
    
    # 测试特定发送器功能
    print("🎯 测试微信公众号HTML格式化:")
    if 'wechat_official' in sender_info:
        try:
            from src.integrations.wechat_official_sender import WeChatOfficialSender
            
            # 创建微信公众号发送器实例
            official_sender = WeChatOfficialSender({
                'enabled': False,
                'use_rich_formatting': True,
                'footer_text': '🎯 测试公众号 - 专注科技资讯',
                'author_name': '科技小助手'
            })
            
            # 测试HTML格式化
            html_content = official_sender._format_content(test_message)
            
            # 保存HTML预览文件
            preview_file = "complete_test_preview.html"
            with open(preview_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ HTML格式化成功，预览文件: {preview_file}")
            
        except Exception as e:
            print(f"❌ HTML格式化测试失败: {e}")
    else:
        print("⚠️  微信公众号发送器未配置，跳过HTML测试")
    
    print()
    print("🎉 完整发送器架构测试完成！")
    
    return True

def print_summary():
    """打印功能总结"""
    print("\n" + "=" * 60)
    print("📋 发送器架构功能总结")
    print("=" * 60)
    
    features = [
        "✅ 插件式发送器架构，支持多种发送方式",
        "✅ 微信即时消息发送（基于wxauto）",
        "✅ 小红书社交媒体发布框架",
        "✅ 微信公众号HTML文章发布",
        "✅ 丰富的HTML格式化和样式设计",
        "✅ 智能内容解析和结构化展示",
        "✅ 可配置的发送器开关和参数",
        "✅ 统一的发送管理和结果汇总",
        "✅ 连接测试和状态监控",
        "✅ 扩展友好的基类设计"
    ]
    
    for feature in features:
        print(feature)
    
    print("\n💡 下一步建议:")
    suggestions = [
        "🔧 完善小红书API集成（需要逆向工程或selenium）",
        "📱 完善微信公众号发布功能（草稿已支持）",
        "🎨 添加更多HTML模板和主题",
        "📊 增加发送统计和分析功能",
        "🔔 添加发送失败重试机制",
        "⚙️  支持更多平台（如钉钉、飞书等）"
    ]
    
    for suggestion in suggestions:
        print(suggestion)

if __name__ == "__main__":
    try:
        success = test_complete_sender_architecture()
        if success:
            print_summary()
        else:
            print("\n💥 测试失败，请检查配置和依赖。")
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
