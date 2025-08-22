#!/usr/bin/env python3
"""
测试增强版AI总结功能（使用新的提示词系统）
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.rss_fetcher import RSSFetcher
from src.summarizer import Summarizer
from src.utils import setup_logger

logger = setup_logger(__name__)

def test_enhanced_ai_features():
    """测试增强版AI功能"""
    print("=== 增强版AI总结功能测试 ===\n")
    
    try:
        # 初始化组件
        print("📡 初始化RSS获取器...")
        rss_fetcher = RSSFetcher()
        
        print("🤖 初始化增强版AI总结器...")
        summarizer = Summarizer()
        
        # 获取文章
        print("📰 获取RSS文章...")
        # 先尝试获取最新文章
        items = rss_fetcher.fetch_latest_items()
        
        # 如果没有获取到，则从缓存中获取
        if not items:
            print("💾 从缓存中获取文章...")
            items = rss_fetcher.cache.get_unsent_items()
            if not items:
                # 获取所有缓存的文章（包括已发送的）
                items = rss_fetcher.cache.get_all_items()
        
        if not items:
            print("❌ 没有获取到文章")
            return
        
        print(f"✅ 获取到 {len(items)} 篇文章\n")
        
        # 选择测试文章
        test_article = items[0]
        print(f"🎯 测试文章: {test_article.title}\n")
        
        # 1. 测试新的英文提示词单篇总结
        print("=" * 60)
        print("🔥 1. 测试新的英文提示词单篇专门总结")
        print("=" * 60)
        
        summary = summarizer.summarize_single_item(test_article)
        
        if summary:
            print("✅ 专门总结生成成功！\n")
            print("📱 微信发送内容:")
            print("-" * 50)
            print(summary)
            print("-" * 50)
            print(f"📊 字数: {len(summary)} (目标: {Config.SUMMARY_MIN_LENGTH}-{Config.SUMMARY_MAX_LENGTH})")
        else:
            print("❌ 专门总结生成失败")
        
        # 2. 测试文章分类
        print("\n" + "=" * 60)
        print("🏷️ 2. 测试文章分类功能")
        print("=" * 60)
        
        category = summarizer.classify_article(test_article)
        print(f"📂 文章分类: {category}")
        
        # 3. 测试标签生成
        print("\n" + "=" * 60)
        print("🔖 3. 测试标签生成功能")
        print("=" * 60)
        
        tags = summarizer.generate_tags(test_article)
        print(f"🏷️ 生成标签: {tags}")
        
        # 4. 测试文章评分
        print("\n" + "=" * 60)
        print("⭐ 4. 测试文章评分功能")
        print("=" * 60)
        
        score = summarizer.score_article(test_article)
        print(f"📊 文章评分: {score}/10")
        
        # 5. 综合展示
        print("\n" + "=" * 60)
        print("📋 综合分析报告")
        print("=" * 60)
        
        print(f"📰 标题: {test_article.title}")
        print(f"🔗 链接: {test_article.link}")
        print(f"📂 分类: {category}")
        print(f"🏷️ 标签: {tags}")
        print(f"⭐ 评分: {score}/10")
        print(f"📝 字数: {len(summary)}字")
        print(f"✅ 质量: {'优秀' if score >= 8 else '良好' if score >= 6 else '一般'}")
        
        # 6. 测试多篇文章的处理
        if len(items) > 1:
            print("\n" + "=" * 60)
            print("📚 多篇文章处理测试")
            print("=" * 60)
            
            # 测试前3篇文章
            test_articles = items[:3]
            print(f"🎯 测试 {len(test_articles)} 篇文章的分类和评分:")
            
            for i, article in enumerate(test_articles, 1):
                cat = summarizer.classify_article(article)
                sc = summarizer.score_article(article)
                print(f"{i}. {article.title[:40]}...")
                print(f"   分类: {cat} | 评分: {sc}/10")
                print()
        
        print("✅ 所有增强功能测试完成！")
        
    except Exception as e:
        logger.error(f"测试出错: {e}")
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_enhanced_ai_features()
