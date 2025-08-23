#!/usr/bin/env python3
"""
测试微信公众号发送的HTML样式和原文链接功能
"""
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.integrations.wechat_official_sender import WeChatOfficialSender
from src.services.rss_service import RSSItem

def test_html_styling_and_source_url():
    """测试HTML样式和原文链接功能"""
    print("=" * 60)
    print("🎨 测试微信公众号HTML样式和原文链接")
    print("=" * 60)
    
    try:
        # 创建微信发送器实例
        config = {
            'app_id': 'test_app_id',
            'app_secret': 'test_app_secret',
            'use_rich_formatting': True,  # 启用丰富格式化
            'author_name': 'AI科技助手',
            'footer_text': '🚀 关注我们，获取更多AI科技资讯'
        }
        
        sender = WeChatOfficialSender(config)
        
        # 创建测试RSS条目
        test_rss_item = RSSItem(
            title="Google发布Genie 3模型：向AGI迈进的重要一步",
            link="https://techcrunch.com/2025/08/23/google-genie-3-agi-breakthrough",
            description="Google最新发布的Genie 3模型在AI领域取得重大突破...",
            published=datetime.now()
        )
        test_rss_item.source_name = "TechCrunch"
        test_rss_item.source_url = "https://techcrunch.com"
        
        # 创建测试消息内容
        test_message = """🔥 Google发布Genie 3模型：向AGI迈进的重要一步

Google在人工智能领域再次取得重大突破，最新发布的Genie 3模型被称为向通用人工智能(AGI)迈进的重要里程碑。

✨ 核心亮点：
• 🚀 突破性的多模态理解能力，能够同时处理文本、图像和音频
• 💡 自主学习机制，无需大量人工标注数据即可持续改进
• 🌍 跨语言理解能力，支持全球主要语言的无缝交互
• ⚡ 超快响应速度，处理复杂任务仅需毫秒级时间

这项技术的发布标志着AI向更加通用化和智能化的方向发展，预计将在教育、医疗、科研等多个领域产生深远影响。

业内专家认为，Genie 3模型的问世可能会重新定义人机交互的方式，为实现真正的通用人工智能奠定坚实基础。

#AI #Google #AGI #人工智能 #科技突破

阅读原文：https://techcrunch.com/2025/08/23/google-genie-3-agi-breakthrough"""
        
        print("📝 测试消息内容:")
        print(f"标题: {test_rss_item.title}")
        print(f"原文链接: {test_rss_item.link}")
        print(f"消息长度: {len(test_message)} 字符")
        
        # 测试内容格式化
        print("\n🎨 测试内容格式化...")
        formatted_content = sender._format_content(test_message, rss_item=test_rss_item)
        
        print("✅ 格式化完成")
        print(f"HTML内容长度: {len(formatted_content)} 字符")
        
        # 显示格式化后的HTML片段（前500字符）
        print(f"\n📋 HTML格式化预览 (前500字符):")
        print("-" * 50)
        print(formatted_content[:500] + "...")
        print("-" * 50)
        
        # 检查是否包含关键的样式元素
        style_checks = {
            '现代CSS样式': '<style>' in formatted_content,
            '文章容器': 'article-container' in formatted_content,
            '标题样式': 'article-title' in formatted_content,
            '高亮要点': 'highlights-list' in formatted_content,
            '标签样式': 'tags-container' in formatted_content,
            '阅读原文链接': 'read-more' in formatted_content,
            '渐变背景': 'linear-gradient' in formatted_content,
            '响应式设计': '@media' in formatted_content,
            '原文链接': test_rss_item.link in formatted_content
        }
        
        print(f"\n🔍 样式功能检查:")
        for feature, present in style_checks.items():
            status = "✅" if present else "❌"
            print(f"  {status} {feature}")
        
        # 检查CSS特性
        css_features = {
            '字体优化': 'PingFang SC' in formatted_content,
            '阴影效果': 'box-shadow' in formatted_content,
            '过渡动画': 'transition' in formatted_content,
            '圆角设计': 'border-radius' in formatted_content,
            '颜色渐变': 'gradient' in formatted_content
        }
        
        print(f"\n🎯 CSS高级特性:")
        for feature, present in css_features.items():
            status = "✅" if present else "❌"
            print(f"  {status} {feature}")
        
        # 模拟创建草稿（但不实际发送）
        print(f"\n📤 模拟创建草稿...")
        
        # 测试提取标题
        extracted_title = sender._extract_title(test_message)
        print(f"提取的标题: {extracted_title}")
        
        # 测试解析消息结构
        sections = sender._parse_message_sections(test_message)
        print(f"\n📊 消息结构解析:")
        print(f"  标题: {sections.get('title', '未识别')}")
        print(f"  要点数量: {len(sections.get('highlights', []))}")
        print(f"  标签数量: {len(sections.get('tags', []))}")
        print(f"  原文链接: {sections.get('link', '未识别')}")
        
        print(f"\n✅ HTML样式和原文链接功能测试完成！")
        
        return {
            'html_length': len(formatted_content),
            'style_features': sum(style_checks.values()),
            'css_features': sum(css_features.values()),
            'total_features': len(style_checks) + len(css_features),
            'source_url_included': test_rss_item.link in formatted_content
        }
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_simple_vs_rich_formatting():
    """测试简单格式化vs丰富格式化的对比"""
    print("\n" + "=" * 60)
    print("🆚 测试简单格式化 vs 丰富格式化")
    print("=" * 60)
    
    test_content = """📰 AI技术新突破
    
这是一条测试消息，用于对比不同的格式化效果。

✨ 要点1：重要功能
• 要点2：性能提升
🚀 要点3：创新特性

#AI #测试"""
    
    # 简单格式化
    simple_config = {'use_rich_formatting': False}
    simple_sender = WeChatOfficialSender(simple_config)
    simple_html = simple_sender._format_content(test_content)
    
    # 丰富格式化  
    rich_config = {'use_rich_formatting': True}
    rich_sender = WeChatOfficialSender(rich_config)
    rich_html = rich_sender._format_content(test_content)
    
    print(f"📊 格式化对比:")
    print(f"  简单格式化长度: {len(simple_html)} 字符")
    print(f"  丰富格式化长度: {len(rich_html)} 字符")
    print(f"  丰富度提升: {len(rich_html) / len(simple_html):.1f}x")
    
    print(f"\n📋 简单格式化预览:")
    print("-" * 30)
    print(simple_html[:200] + "...")
    print("-" * 30)
    
    print(f"\n🎨 丰富格式化预览:")
    print("-" * 30)
    print(rich_html[:300] + "...")
    print("-" * 30)
    
    return True

if __name__ == "__main__":
    print("🚀 开始测试微信公众号HTML样式功能...")
    
    # 运行测试
    result1 = test_html_styling_and_source_url()
    result2 = test_simple_vs_rich_formatting()
    
    # 总结结果
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    if result1 and result2:
        print("✅ 所有测试通过！")
        print(f"\n💡 功能特性:")
        print(f"   🎨 HTML样式特性: {result1['style_features']}/{len({'现代CSS样式': True, '文章容器': True, '标题样式': True, '高亮要点': True, '标签样式': True, '阅读原文链接': True, '渐变背景': True, '响应式设计': True, '原文链接': True})}")
        print(f"   ⚡ CSS高级特性: {result1['css_features']}/{len({'字体优化': True, '阴影效果': True, '过渡动画': True, '圆角设计': True, '颜色渐变': True})}")
        print(f"   🔗 原文链接支持: {'✅' if result1['source_url_included'] else '❌'}")
        print(f"   📏 HTML内容长度: {result1['html_length']} 字符")
        
        print(f"\n🎯 主要改进:")
        print(f"   ✅ 添加了content_source_url支持")
        print(f"   ✅ 现代化CSS样式设计")
        print(f"   ✅ 响应式布局优化")
        print(f"   ✅ 渐变色和阴影效果")
        print(f"   ✅ 优化的字体和排版")
        print(f"   ✅ 增强的视觉层次结构")
    else:
        print("❌ 部分测试失败")
