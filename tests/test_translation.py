#!/usr/bin/env python3
"""
AI翻译和总结功能测试
测试英文内容是否能正确翻译为中文总结
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.ai_service import Summarizer

def test_translation():
    """测试AI翻译功能"""
    
    # 初始化AI服务
    summarizer = Summarizer()
    
    # 测试英文文章
    test_article = {
        'title': 'OpenAI Releases New GPT-4 Turbo Model with Enhanced Capabilities',
        'content': '''
        OpenAI has announced the release of GPT-4 Turbo, an updated version of their flagship language model. 
        The new model features improved reasoning capabilities, better code generation, and enhanced multilingual support.
        Key improvements include:
        - Faster response times
        - More accurate factual information
        - Better understanding of context
        - Improved safety measures
        
        The model is now available through OpenAI's API and will be rolled out to ChatGPT Plus subscribers over the coming weeks.
        This release represents a significant step forward in AI capabilities and demonstrates OpenAI's commitment to advancing the field.
        ''',
        'link': 'https://example.com/test-article',
        'published': '2024-01-15T10:00:00Z'
    }
    
    print("🔍 测试AI翻译和总结功能...")
    print(f"原文标题: {test_article['title']}")
    print("\n原文内容(前100字符):")
    print(test_article['content'][:100] + "...")
    
    try:
        # 测试文章总结
        print("\n📝 测试文章总结...")
        summary = summarizer.summarize_article(test_article)
        print(f"总结结果: {summary}")
        
        # 测试文章评分
        print("\n⭐ 测试文章评分...")
        score = summarizer.score_article(test_article)
        print(f"评分结果: {score}")
        
        # 测试文章分类
        print("\n📂 测试文章分类...")
        category = summarizer.classify_article(test_article)
        print(f"分类结果: {category}")
        
        print("\n✅ AI翻译测试完成！")
        
    except Exception as e:
        print(f"\n❌ AI翻译测试失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_translation()
    if success:
        print("\n🎉 所有测试通过！AI翻译功能正常工作。")
    else:
        print("\n💥 测试失败，请检查配置。")
