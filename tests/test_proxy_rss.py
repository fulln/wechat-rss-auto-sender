#!/usr/bin/env python3
"""
RSS代理测试脚本
用于测试代理配置是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import feedparser
from datetime import datetime, timedelta
from src.core.config import Config
from dotenv import load_dotenv

def test_proxy_config():
    """测试代理配置"""
    print("=== RSS代理配置测试 ===")
    
    # 加载环境变量
    load_dotenv()
    
    # 获取配置
    proxies = Config.get_proxies()
    url = Config.RSS_FEED_URL
    
    print(f"RSS URL: {url}")
    print(f"代理配置: {proxies}")
    print()
    
    return proxies, url

def test_direct_request(url, proxies):
    """测试直接HTTP请求"""
    print("=== 测试直接HTTP请求 ===")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print("发送请求...")
        response = requests.get(url, proxies=proxies, timeout=30, headers=headers)
        
        print(f"状态码: {response.status_code}")
        print(f"响应长度: {len(response.content)} bytes")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        
        # 检查内容
        content = response.text
        print(f"包含 <item> 标签: {'<item>' in content}")
        print(f"包含 <entry> 标签: {'<entry>' in content}")
        print(f"包含 <rss> 标签: {'<rss' in content}")
        print(f"包含 <feed> 标签: {'<feed' in content}")
        
        print("\n前500个字符:")
        print("-" * 50)
        print(content[:500])
        print("-" * 50)
        
        return response
        
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def test_feedparser(response):
    """测试feedparser解析"""
    print("\n=== 测试feedparser解析 ===")
    
    if not response:
        print("没有有效的响应数据")
        return None
    
    try:
        # 解析RSS
        feed = feedparser.parse(response.content)
        
        print(f"Feed标题: {feed.feed.get('title', 'Unknown')}")
        print(f"Feed描述: {feed.feed.get('description', 'Unknown')}")
        print(f"是否有解析错误: {feed.bozo}")
        if feed.bozo:
            print(f"解析错误: {feed.bozo_exception}")
        
        print(f"条目数量: {len(feed.entries)}")
        
        if len(feed.entries) > 0:
            print("\n最新的3条条目:")
            for i, entry in enumerate(feed.entries[:3]):
                print(f"  {i+1}. {entry.get('title', 'No title')}")
                print(f"     链接: {entry.get('link', 'No link')}")
                if hasattr(entry, 'published'):
                    print(f"     发布时间: {entry.published}")
                elif hasattr(entry, 'updated'):
                    print(f"     更新时间: {entry.updated}")
                print()
        
        return feed
        
    except Exception as e:
        print(f"解析失败: {e}")
        return None

def test_time_filtering(feed):
    """测试时间过滤"""
    print("=== 测试时间过滤 ===")
    
    if not feed or len(feed.entries) == 0:
        print("没有条目可测试")
        return
    
    # 测试不同的时间范围
    time_ranges = [5, 60, 1440, 7200]  # 5分钟, 1小时, 1天, 5天
    
    for minutes in time_ranges:
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        count = 0
        
        for entry in feed.entries:
            try:
                # 解析发布时间
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])
                else:
                    published = datetime.now()
                
                if published >= cutoff_time:
                    count += 1
            except Exception:
                continue
        
        print(f"最近{minutes}分钟内的文章: {count}条")

def test_rss_service():
    """测试RSS服务"""
    print("\n=== 测试RSS服务 ===")
    
    try:
        from src.services.rss_service import RSSFetcher
        
        fetcher = RSSFetcher()
        
        # 测试不同时间范围
        for minutes in [60, 1440, 7200]:  # 1小时, 1天, 5天
            print(f"\n测试获取最近{minutes}分钟的文章:")
            articles = fetcher.fetch_latest_items(since_minutes=minutes, enable_dedup=False)
            print(f"获取到 {len(articles)} 条文章")
            
            if articles:
                print("最新文章:")
                for i, article in enumerate(articles[:3]):
                    print(f"  {i+1}. {article.title}")
                    print(f"     发布时间: {article.published}")
                break
        
    except Exception as e:
        print(f"RSS服务测试失败: {e}")

def main():
    """主测试函数"""
    print("开始RSS代理功能测试...\n")
    
    # 测试代理配置
    proxies, url = test_proxy_config()
    
    # 测试直接请求
    response = test_direct_request(url, proxies)
    
    # 测试feedparser
    feed = test_feedparser(response)
    
    # 测试时间过滤
    test_time_filtering(feed)
    
    # 测试RSS服务
    test_rss_service()
    
    print("\n测试完成!")

if __name__ == "__main__":
    main()
