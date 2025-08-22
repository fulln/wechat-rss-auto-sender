#!/usr/bin/env python3
"""
测试质量评分筛选功能
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.send_manager import SendManager
from src.utils import setup_logger

logger = setup_logger(__name__)

def test_quality_scoring_filter():
    """测试质量评分筛选功能"""
    print("=== 质量评分筛选功能测试 ===\n")
    
    try:
        # 初始化发送管理器
        print("🤖 初始化发送管理器...")
        send_manager = SendManager()
        
        print(f"📊 质量要求配置: 最低 {Config.MIN_QUALITY_SCORE}/10 分\n")
        
        # 获取所有未发送的文章
        unsent_articles = send_manager.rss_fetcher.cache.get_unsent_items()
        print(f"📰 待检查文章总数: {len(unsent_articles)}")
        
        if not unsent_articles:
            print("❌ 没有待发送的文章")
            return
        
        # 测试质量评分筛选
        print("\n" + "=" * 60)
        print("🔍 开始质量评分筛选测试")
        print("=" * 60)
        
        qualified_articles = send_manager.select_articles_to_send()
        
        if qualified_articles:
            article = qualified_articles[0]
            print(f"\n✅ 找到高质量文章准备发送:")
            print(f"📰 标题: {article.title}")
            print(f"⭐ 评分: {article.quality_score}/10")
            print(f"🔗 链接: {article.link}")
            
            # 询问是否实际发送
            print(f"\n🚀 是否发送这篇高质量文章？(y/N): ", end="")
            
        else:
            print(f"\n❌ 没有文章达到质量要求")
            print(f"📊 质量要求: ≥{Config.MIN_QUALITY_SCORE}/10分")
            
            # 显示所有文章的评分情况
            print(f"\n📊 所有文章评分情况:")
            print("-" * 60)
            
            for i, article in enumerate(unsent_articles[:10], 1):  # 最多显示10篇
                if article.quality_score is not None:
                    score_info = f"{article.quality_score}/10"
                    status = "✅" if article.quality_score >= Config.MIN_QUALITY_SCORE else "❌"
                else:
                    score_info = "未评分"
                    status = "⏳"
                
                print(f"{i:2d}. {status} {article.title[:50]:<50} [{score_info}]")
                
                if i >= 10 and len(unsent_articles) > 10:
                    print(f"    ... 还有 {len(unsent_articles) - 10} 篇文章未显示")
                    break
        
        # 统计信息
        print(f"\n📈 质量统计:")
        scored_articles = [a for a in unsent_articles if a.quality_score is not None]
        if scored_articles:
            scores = [a.quality_score for a in scored_articles]
            avg_score = sum(scores) / len(scores)
            high_quality = len([s for s in scores if s >= Config.MIN_QUALITY_SCORE])
            
            print(f"   已评分文章: {len(scored_articles)}/{len(unsent_articles)}")
            print(f"   平均评分: {avg_score:.1f}/10")
            print(f"   高质量文章: {high_quality}篇 (≥{Config.MIN_QUALITY_SCORE}分)")
            print(f"   质量达标率: {high_quality/len(scored_articles)*100:.1f}%")
        else:
            print(f"   尚未对文章进行评分")
        
    except Exception as e:
        logger.error(f"测试出错: {e}")
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_quality_scoring_filter()
