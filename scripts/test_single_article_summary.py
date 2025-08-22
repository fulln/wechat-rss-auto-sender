#!/usr/bin/env python3
"""
测试单篇文章专门总结功能
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

def test_single_article_summary():
    """测试单篇文章的专门AI总结功能"""
    print("=== 单篇文章专门总结功能测试 ===\n")
    
    try:
        # 初始化组件
        print("📡 初始化RSS获取器...")
        rss_fetcher = RSSFetcher()
        
        print("🤖 初始化AI总结器...")
        summarizer = Summarizer()
        
        # 获取文章
        print("📰 获取RSS文章...")
        items = rss_fetcher.fetch_rss()
        
        if not items:
            print("❌ 没有获取到文章")
            return
        
        print(f"✅ 获取到 {len(items)} 篇文章\n")
        
        # 测试单篇文章总结
        test_article = items[0]
        print(f"🎯 测试文章: {test_article.title}\n")
        print(f"📝 原始描述: {test_article.description[:100]}...\n")
        
        print("🤖 生成专门的AI总结...")
        summary = summarizer.summarize_single_item(test_article)
        
        if summary:
            print("✅ AI总结生成成功！\n")
            print("=" * 50)
            print("📱 微信发送内容预览:")
            print("=" * 50)
            print(summary)
            print("=" * 50)
            print(f"\n📊 总结统计:")
            print(f"   字数: {len(summary)}")
            print(f"   配置范围: {Config.SUMMARY_MIN_LENGTH}-{Config.SUMMARY_MAX_LENGTH}字")
            print(f"   是否符合要求: {'✅' if Config.SUMMARY_MIN_LENGTH <= len(summary) <= Config.SUMMARY_MAX_LENGTH else '❌'}")
        else:
            print("❌ AI总结生成失败")
            
        # 对比测试：旧的批量总结 vs 新的单篇总结
        print("\n" + "=" * 60)
        print("🔄 对比测试：批量总结 vs 单篇专门总结")
        print("=" * 60)
        
        print("\n🔹 旧方式 - 批量总结:")
        batch_summary = summarizer.summarize_items([test_article])
        print(batch_summary[:200] + "..." if len(batch_summary) > 200 else batch_summary)
        
        print(f"\n🔹 新方式 - 单篇专门总结:")
        print(summary[:200] + "..." if len(summary) > 200 else summary)
        
        print(f"\n📈 改进效果:")
        print(f"   批量总结字数: {len(batch_summary)}")
        print(f"   单篇总结字数: {len(summary)}")
        print(f"   内容丰富度提升: {'+' if len(summary) > len(batch_summary) else '-'}{abs(len(summary) - len(batch_summary))}字")
        
    except Exception as e:
        logger.error(f"测试出错: {e}")
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_single_article_summary()
