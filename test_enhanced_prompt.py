#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的微信公众号prompt和评分系统
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.ai_service import Summarizer
from src.services.rss_service import RSSItem
from datetime import datetime

def test_enhanced_wechat_official_prompt():
    """测试增强的微信公众号prompt"""
    print("🧪 测试增强的微信公众号prompt...")
    
    # 创建模拟的RSS条目
    test_articles = [
        {
            "title": "OpenAI Introduces GPT-4 Turbo with Vision Capabilities",
            "description": "OpenAI has released GPT-4 Turbo, a more efficient version of GPT-4 that can process images and text with improved performance and reduced costs. The model features a 128k context window and knowledge cutoff of April 2024.",
            "link": "https://example.com/gpt4-turbo"
        },
        {
            "title": "Meta发布新一代VR头显Quest 3，配备混合现实功能",
            "description": "Meta公司今日正式发布Quest 3 VR头显，这款设备搭载了最新的Snapdragon XR2处理器，支持高分辨率显示和先进的混合现实功能，预计将重新定义VR体验。售价499美元起。",
            "link": "https://example.com/quest3"
        }
    ]
    
    summarizer = Summarizer()
    
    for i, article_data in enumerate(test_articles, 1):
        print(f"\n{'='*60}")
        print(f"测试文章 {i}: {article_data['title'][:50]}...")
        print('='*60)
        
        # 创建RSS条目
        rss_item = RSSItem(
            title=article_data['title'],
            link=article_data['link'],
            description=article_data['description'],
            published=datetime.now()
        )
        
        print("📰 原始文章信息:")
        print(f"标题: {rss_item.title}")
        print(f"描述: {rss_item.description}")
        print(f"链接: {rss_item.link}")
        
        try:
            # 生成微信公众号内容
            summary = summarizer.summarize_single_item(rss_item, sender_type="wechat_official")
            
            print(f"\n🎯 生成的微信公众号文章:")
            print("-" * 40)
            print(summary)
            print("-" * 40)
            
            # 测试评分和标签提取
            score = summarizer.get_article_engagement_score(summary)
            tags = summarizer.get_article_tags(summary)
            
            print(f"\n📊 文章分析:")
            print(f"热度评分: {score}/10")
            print(f"提取的标签: {tags}")
            
            # 测试HTML格式转换
            if summary:
                html_content = summarizer.markdown_to_html(summary)
                print(f"\n🌐 HTML格式预览:")
                print(html_content[:300] + "..." if len(html_content) > 300 else html_content)
        
        except Exception as e:
            print(f"❌ 生成失败: {e}")
        
        print("\n" + "="*60)

def test_metadata_extraction():
    """测试元数据提取功能"""
    print("🧪 测试元数据提取功能...")
    
    # 模拟AI返回的包含元数据的内容
    sample_content = """
<h2>ChatGPT突破性更新：多模态能力震撼发布</h2>

<p>今天，OpenAI正式发布了ChatGPT的重大更新，这次更新将彻底改变我们与AI的交互方式。新版本不仅能处理文字，还能理解图像、音频，甚至视频内容。</p>

<h3>🎯 核心突破</h3>
<p>这次更新的核心在于<strong>多模态融合技术</strong>的突破。用户现在可以：</p>

<ul>
<li>上传图片让AI分析和解读</li>
<li>通过语音与AI自然对话</li>
<li>处理复杂的视觉内容理解任务</li>
</ul>

<h3>🚀 商业影响</h3>
<p>这一突破将对多个行业产生深远影响，预计在教育、医疗、创意设计等领域将迎来新的变革浪潮。</p>

<p>📊 热度评分: 9.2</p>
<p>🎯 目标受众: 开发者/企业决策者/科技爱好者</p>
<p>🏷️ 文章标签: #人工智能 #ChatGPT #多模态 #技术突破 #行业变革</p>
"""
    
    summarizer = Summarizer()
    
    print("原始内容（包含元数据）:")
    print(sample_content)
    print("\n" + "="*50)
    
    # 提取元数据
    clean_content, metadata = summarizer._extract_article_metadata(sample_content)
    
    print("清理后的内容:")
    print(clean_content)
    print("\n" + "="*50)
    
    print("提取的元数据:")
    print(f"热度评分: {metadata.get('score', 'N/A')}")
    print(f"目标受众: {metadata.get('audience', 'N/A')}")
    print(f"标签: {metadata.get('tags', 'N/A')}")
    
    # 测试独立的获取方法
    score = summarizer.get_article_engagement_score(sample_content)
    tags = summarizer.get_article_tags(sample_content)
    
    print(f"\n通过独立方法获取:")
    print(f"评分: {score}")
    print(f"标签: {tags}")

if __name__ == "__main__":
    print("🔧 增强prompt和评分系统测试开始...\n")
    
    # 测试元数据提取（不需要API调用）
    test_metadata_extraction()
    
    print("\n" + "🔔 注意：以下测试需要调用AI API")
    response = input("是否继续测试AI生成功能？(y/n): ")
    
    if response.lower() == 'y':
        test_enhanced_wechat_official_prompt()
    
    print("\n✅ 测试完成！")
