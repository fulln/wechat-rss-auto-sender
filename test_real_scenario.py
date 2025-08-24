#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实际发送测试
模拟真实的微信公众号发送场景
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.ai_service import Summarizer
from src.services.rss_service import RSSItem
from datetime import datetime

def test_real_scenario():
    """测试真实场景下的内容处理"""
    print("🧪 模拟真实发送场景...")
    
    # 创建模拟的RSS条目
    rss_item = RSSItem(
        title="Advanced Python Async Programming Techniques",
        link="https://example.com/async-python",
        description="This article covers advanced asynchronous programming techniques in Python, including coroutines, event loops, and best practices for high-performance applications.",
        pub_date=datetime.now(),
        guid="test-async-python"
    )
    
    # 创建AI服务
    summarizer = Summarizer()
    
    print("=== RSS原始信息 ===")
    print(f"标题: {rss_item.title}")
    print(f"描述: {rss_item.description}")
    print(f"链接: {rss_item.link}")
    
    # 模拟AI生成的内容（这是AI可能返回的带问题的内容）
    ai_generated_content = """
📰 **优化标题**: Python异步编程高级技巧详解

## 🚀 核心技术要点

在现代高性能Web应用开发中，**异步编程**已经成为不可或缺的关键技术。本文将深入探讨Python异步编程的高级技巧。

### 🔑 关键概念解析
- **协程(Coroutines)**: 使用`async def`定义的可暂停和恢复执行的函数
- **事件循环(Event Loop)**: 负责管理和执行异步任务的核心引擎
- **异步上下文管理器**: 支持异步资源管理的高级特性

### 💡 最佳实践建议
1. 合理使用`await`关键字，避免阻塞操作
2. 充分利用`asyncio.gather()`进行并发处理
3. 正确处理异步异常和资源清理

通过掌握这些高级技巧，开发者能够构建真正高性能的Python应用程序。

🔗 **延伸阅读**：[查看完整技术详情](https://example.com/async-python)
"""
    
    print("\n=== AI生成的原始内容 ===")
    print(ai_generated_content)
    
    # 步骤1: 内容清理
    cleaned_content = summarizer.clean_content_for_wechat(ai_generated_content)
    print("\n=== 清理后的内容 ===")
    print(cleaned_content)
    
    # 步骤2: 转换为HTML（微信公众号格式）
    html_content = summarizer.markdown_to_html(ai_generated_content)
    print("\n=== HTML格式内容 ===")
    print(html_content)
    
    # 步骤3: 验证最终效果
    print("\n=== 最终验证 ===")
    print("✅ 检查项目:")
    
    # 检查是否还有"优化标题:"
    has_title_prefix = "优化标题" in html_content
    print(f"- 是否清理标题前缀: {'❌ 仍有前缀' if has_title_prefix else '✅ 已清理'}")
    
    # 检查是否有正确的HTML标签
    has_html_tags = any(tag in html_content for tag in ['<h2>', '<h3>', '<strong>', '<ul>', '<li>'])
    print(f"- 是否包含HTML标签: {'✅ 包含' if has_html_tags else '❌ 缺失'}")
    
    # 检查内容长度是否合理
    length_reasonable = 100 < len(html_content) < 2000
    print(f"- 内容长度是否合理: {'✅ 合理' if length_reasonable else '❌ 异常'} ({len(html_content)}字符)")
    
    # 检查是否保留了链接
    has_link = "https://example.com" in html_content
    print(f"- 是否保留原文链接: {'✅ 保留' if has_link else '❌ 丢失'}")
    
    return html_content

if __name__ == "__main__":
    print("🔧 真实场景测试开始...\n")
    
    final_content = test_real_scenario()
    
    print(f"\n🎯 最终微信公众号内容预览:")
    print("=" * 60)
    print(final_content)
    print("=" * 60)
    
    print("\n✅ 真实场景测试完成！")
