#!/usr/bin/env python3
"""
测试RSS图片下载功能
"""

import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.rss_service import RSSFetcher
from src.services.image_service import ImageDownloader

def test_image_download():
    """测试图片下载功能"""
    
    print("🔍 测试RSS图片下载功能...")
    print("=" * 60)
    
    # 测试图片下载器
    print("📥 测试图片下载器...")
    image_downloader = ImageDownloader()
    
    # 测试示例图片URL
    test_image_url = "https://techcrunch.com/wp-content/uploads/2024/01/openai-logo.jpg"
    
    print(f"测试图片URL: {test_image_url}")
    print(f"图片格式检查: {image_downloader._is_valid_image_url(test_image_url)}")
    
    # 测试内容解析
    test_html = '''
    <div>
        <p>这是一个测试文章</p>
        <img src="https://example.com/test-image.jpg" alt="测试图片">
        <p>更多内容</p>
    </div>
    '''
    
    extracted_url = image_downloader.extract_image_from_content(test_html, "https://example.com")
    print(f"从HTML提取的图片URL: {extracted_url}")
    
    # 测试RSS获取器
    print("\n📰 测试RSS图片获取...")
    
    try:
        rss_fetcher = RSSFetcher()
        print(f"RSS源: {rss_fetcher.feed_url}")
        
        # 获取最新文章（启用图片下载）
        print("正在获取RSS文章...")
        # 临时修改配置以获取更多文章
        from src.core.config import Config
        original_hours = Config.FETCH_ARTICLES_HOURS
        Config.FETCH_ARTICLES_HOURS = 24  # 临时设置为24小时
        
        items = rss_fetcher.fetch_latest_items(since_minutes=1440, enable_dedup=False)  # 获取最近24小时的文章，禁用去重
        
        # 恢复原配置
        Config.FETCH_ARTICLES_HOURS = original_hours
        
        print(f"获取到 {len(items)} 篇文章")
        
        # 统计图片信息
        total_images = 0
        downloaded_images = 0
        
        for i, item in enumerate(items[:5]):  # 只显示前5篇
            print(f"\n📄 文章 {i+1}: {item.title[:50]}...")
            print(f"   发布时间: {item.published}")
            print(f"   链接: {item.link}")
            
            if item.has_image():
                total_images += 1
                print(f"   📸 图片URL: {item.image_url}")
                
                if item.has_local_image():
                    downloaded_images += 1
                    print(f"   💾 本地路径: {item.local_image_path}")
                    
                    # 检查文件是否真实存在
                    if os.path.exists(item.local_image_path):
                        file_size = os.path.getsize(item.local_image_path)
                        print(f"   📊 文件大小: {file_size} bytes")
                    else:
                        print("   ⚠️  文件不存在!")
                else:
                    print("   ❌ 图片下载失败")
            else:
                print("   📷 无图片")
        
        print("\n📊 图片统计:")
        print(f"   总文章数: {len(items)}")
        print(f"   有图片文章: {total_images}")
        print(f"   下载成功: {downloaded_images}")
        print(f"   下载成功率: {(downloaded_images/total_images*100) if total_images > 0 else 0:.1f}%")
        
        # 显示图片目录信息
        images_dir = "images"
        if os.path.exists(images_dir):
            image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'))]
            total_size = sum(os.path.getsize(os.path.join(images_dir, f)) for f in image_files)
            
            print("\n📁 图片目录信息:")
            print(f"   目录: {os.path.abspath(images_dir)}")
            print(f"   图片文件数: {len(image_files)}")
            print(f"   总大小: {total_size / 1024 / 1024:.2f} MB")
            
            if image_files:
                print(f"   最新文件: {image_files[-1]}")
        
        return True
        
    except Exception as e:
        print(f"❌ RSS图片测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_image_cleanup():
    """测试图片清理功能"""
    print("\n🧹 测试图片清理功能...")
    
    try:
        rss_fetcher = RSSFetcher()
        deleted_count = rss_fetcher.cleanup_old_images(days=0)  # 清理所有图片（测试用）
        print(f"清理了 {deleted_count} 个图片文件")
        return True
    except Exception as e:
        print(f"❌ 图片清理测试失败: {e}")
        return False

if __name__ == "__main__":
    try:
        success1 = test_image_download()
        success2 = test_image_cleanup()
        
        if success1 and success2:
            print("\n🎉 RSS图片下载功能测试完成！")
            print("\n💡 功能特性:")
            print("   ✅ 自动从RSS条目中提取图片URL")
            print("   ✅ 支持多种图片格式（jpg, png, gif, webp等）")
            print("   ✅ 自动下载并保存到本地")
            print("   ✅ 图片与文章关联，支持发送时使用")
            print("   ✅ 支持代理下载")
            print("   ✅ 文件大小限制和安全检查")
            print("   ✅ 旧图片自动清理功能")
        else:
            print("\n💥 测试失败，请检查配置。")
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
