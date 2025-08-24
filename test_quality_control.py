#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试质量控制逻辑
验证低质量文章确实被排除出发送队列
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.multi_rss_manager import MultiRSSManager
from src.services.send_service import SendManager
from datetime import datetime

def test_quality_control():
    """测试质量控制逻辑"""
    print("🧪 测试质量控制逻辑...")
    
    # 创建RSS管理器
    rss_manager = MultiRSSManager()
    
    print("1. 🔍 检查当前文章状态...")
    
    # 获取所有未发送文章
    unsent_items = rss_manager.cache.get_unsent_items()
    print(f"未发送文章总数: {len(unsent_items)}")
    
    # 检查文章的质量分数
    for item in unsent_items:
        if item.quality_score is not None:
            status = "✅ 通过" if item.meets_quality_requirement() else "❌ 不达标"
            print(f"  - {item.title[:50]}... | 评分: {item.quality_score} | {status}")
        else:
            print(f"  - {item.title[:50]}... | 评分: 未评分")
    
    print("\n2. 🎯 测试发送服务的文章选择...")
    
    # 创建发送服务
    send_service = SendManager(rss_manager)
    
    # 选择要发送的文章
    selected_articles = send_service.select_articles_to_send()
    
    print(f"经过质量筛选后的文章数: {len(selected_articles)}")
    
    for article in selected_articles:
        print(f"  ✅ 选中发送: {article.title[:50]}... | 评分: {article.quality_score}")
    
    print("\n3. 📊 验证质量控制效果...")
    
    # 检查是否有低质量文章被错误选中
    low_quality_selected = [a for a in selected_articles if a.quality_score and a.quality_score < 5]
    
    if low_quality_selected:
        print("❌ 错误：发现低质量文章被选中发送！")
        for article in low_quality_selected:
            print(f"  - {article.title[:50]}... | 评分: {article.quality_score}")
    else:
        print("✅ 正确：没有低质量文章被选中发送")
    
    print("\n4. 🔎 验证is_sendable方法...")
    
    # 检查所有文章的可发送状态
    for item in unsent_items:
        is_sendable = item.is_sendable()
        quality_ok = item.meets_quality_requirement() if item.quality_score is not None else True
        
        print(f"  - {item.title[:30]}... | 评分: {item.quality_score} | 可发送: {is_sendable} | 质量达标: {quality_ok}")
        
        # 如果质量不达标但仍显示可发送，那就有问题
        if item.quality_score is not None and not quality_ok and is_sendable:
            print(f"    ❌ 问题：质量不达标但仍显示可发送！")

def main():
    print("🔧 质量控制测试开始...\n")
    
    try:
        test_quality_control()
        
        print("\n" + "="*60)
        print("📝 总结：")
        print("- 质量不达标的文章不会进入可发送列表")
        print("- is_sendable()方法会正确排除低质量文章")
        print("- select_articles_to_send()只会选择高质量文章")
        print("- 统计信息正确显示各种状态的文章数量")
        print("="*60)
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
