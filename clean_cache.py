#!/usr/bin/env python3
"""
缓存清理工具 - 清除测试文章和过期数据
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.multi_rss_manager import MultiRSSManager


def clean_test_articles():
    """清除测试文章"""
    print("=" * 80)
    print("🧹 缓存清理工具 - 清除测试文章")
    print("=" * 80)
    
    try:
        # 创建RSS管理器
        multi_rss_manager = MultiRSSManager()
        cache = multi_rss_manager.cache
        
        print("📊 清理前缓存状态分析...")
        
        # 统计清理前的数据
        total_articles = 0
        test_articles = 0
        real_articles = 0
        cleaned_articles = []
        
        for date_key in list(cache.article_details.keys()):
            date_articles = cache.article_details[date_key]
            articles_to_remove = []
            
            for article_hash, article in list(date_articles.items()):
                total_articles += 1
                
                # 识别测试文章的条件
                is_test_article = (
                    article.link.startswith("https://test.com/") or
                    article.title in ["优质文章1", "优质文章2", "中等文章1", "低质文章1", "低质文章2", "低质文章3"] or
                    "测试文章" in article.description or
                    article.title == "测试标题"
                )
                
                if is_test_article:
                    test_articles += 1
                    articles_to_remove.append(article_hash)
                    cleaned_articles.append({
                        "title": article.title,
                        "link": article.link,
                        "date": date_key
                    })
                    print(f"   🗑️ 标记清除: {article.title} ({article.link})")
                else:
                    real_articles += 1
            
            # 删除测试文章
            for article_hash in articles_to_remove:
                del date_articles[article_hash]
            
            # 如果该日期下没有文章了，删除整个日期条目和对应的缓存文件
            if not date_articles:
                del cache.article_details[date_key]
                print(f"   📅 删除空日期条目: {date_key}")
                
                # 删除对应的缓存文件
                cache_file = Path(f"cache/rss_{date_key}.json")
                if cache_file.exists():
                    cache_file.unlink()
                    print(f"   🗑️ 删除空缓存文件: {cache_file.name}")
        
        print(f"\n📈 清理统计:")
        print(f"   总文章数: {total_articles}")
        print(f"   测试文章: {test_articles}")
        print(f"   真实文章: {real_articles}")
        print(f"   清理文章: {len(cleaned_articles)}")
        
        # 保存清理后的缓存
        if cleaned_articles:
            print("\n💾 保存清理后的缓存...")
            
            # 为每个修改的日期保存缓存
            modified_dates = set()
            for article in cleaned_articles:
                modified_dates.add(article['date'])
            
            for date_key in modified_dates:
                if date_key in cache.article_details:
                    cache._save_cache(date_key)
                    print(f"   ✅ 已保存 {date_key} 的缓存")
            
            print("✅ 缓存已更新")
            
            # 显示被清理的文章
            print(f"\n📋 被清理的文章列表:")
            for article in cleaned_articles:
                print(f"   - {article['title']} ({article['date']})")
        else:
            print("ℹ️ 没有发现需要清理的测试文章")
        
        return len(cleaned_articles)
        
    except Exception as e:
        print(f"❌ 清理失败: {e}")
        import traceback
        traceback.print_exc()
        return 0


def clean_old_cache(days_to_keep=7):
    """清除过期缓存文件"""
    print(f"\n🗂️ 清理过期缓存文件 (保留 {days_to_keep} 天)...")
    
    try:
        cache_dir = Path("cache")
        if not cache_dir.exists():
            print("⚠️ 缓存目录不存在")
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_files = []
        
        for cache_file in cache_dir.glob("rss_*.json"):
            try:
                # 从文件名提取日期
                date_str = cache_file.stem.replace("rss_", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date < cutoff_date:
                    cache_file.unlink()
                    deleted_files.append(cache_file.name)
                    print(f"   🗑️ 删除过期文件: {cache_file.name}")
                    
            except (ValueError, OSError) as e:
                print(f"   ⚠️ 处理文件 {cache_file.name} 时出错: {e}")
        
        if deleted_files:
            print(f"✅ 删除了 {len(deleted_files)} 个过期缓存文件")
        else:
            print("ℹ️ 没有发现过期的缓存文件")
            
        return len(deleted_files)
        
    except Exception as e:
        print(f"❌ 清理过期文件失败: {e}")
        return 0


def verify_cleanup():
    """验证清理结果"""
    print(f"\n🔍 验证清理结果...")
    
    try:
        multi_rss_manager = MultiRSSManager()
        cache = multi_rss_manager.cache
        
        # 检查是否还有测试文章
        remaining_test_articles = []
        total_articles = 0
        
        for date_key in cache.article_details:
            for article in cache.article_details[date_key].values():
                total_articles += 1
                
                is_test_article = (
                    article.link.startswith("https://test.com/") or
                    article.title in ["优质文章1", "优质文章2", "中等文章1", "低质文章1", "低质文章2", "低质文章3"] or
                    "测试文章" in article.description
                )
                
                if is_test_article:
                    remaining_test_articles.append(article.title)
        
        print(f"   总文章数: {total_articles}")
        print(f"   剩余测试文章: {len(remaining_test_articles)}")
        
        if remaining_test_articles:
            print("   ⚠️ 仍有测试文章未清理:")
            for title in remaining_test_articles:
                print(f"     - {title}")
            return False
        else:
            print("   ✅ 所有测试文章已清理干净")
            return True
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False


if __name__ == "__main__":
    print("🚀 开始缓存清理...")
    
    # 清理测试文章
    cleaned_count = clean_test_articles()
    
    # 清理过期文件
    deleted_count = clean_old_cache(days_to_keep=7)
    
    # 验证清理结果
    is_clean = verify_cleanup()
    
    print("\n" + "=" * 80)
    print("📊 清理结果总结")
    print("=" * 80)
    
    print(f"✅ 清理测试文章: {cleaned_count} 篇")
    print(f"✅ 删除过期文件: {deleted_count} 个")
    print(f"✅ 清理状态: {'完全清理' if is_clean else '部分清理'}")
    
    if is_clean and (cleaned_count > 0 or deleted_count > 0):
        print("\n🎉 缓存清理完成！系统现在只包含真实的RSS文章")
    elif cleaned_count == 0 and deleted_count == 0:
        print("\n💡 缓存已经很干净，没有需要清理的内容")
    else:
        print("\n⚠️ 清理完成，但可能还有残留数据需要手动检查")
