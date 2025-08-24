#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试内容格式化
验证修复后的内容处理逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.ai_service import AIService
from src.integrations.wechat_official_sender import WeChatOfficialSender
from src.services.rss_service import RSSItem
from datetime import datetime

def test_content_cleaning():
    """测试内容清理功能"""
    print("🧪 测试内容清理功能...")
    
    ai_service = AIService()
    
    # 测试包含多余空格和标题前缀的内容
    messy_content = """
📰 **优化标题**: Python异步编程最佳实践



## 核心要点    

在现代Python开发中，    **异步编程**已经成为提升性能的关键技术。


### 主要优势   
- 高并发处理能力   
- **资源利用率**提升    
-     更好的用户体验


这是一个包含多种格式的段落。    


"""
    
    print("原始内容（带多余空格）:")
    print(repr(messy_content))
    
    cleaned = ai_service.clean_content_for_wechat(messy_content)
    print("\n清理后的内容:")
    print(repr(cleaned))
    print("\n显示效果:")
    print(cleaned)
    print("\n" + "="*50)python3
# -*- coding: utf-8 -*-
"""
测试内容格式化
验证修复后的内容处理逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.ai_service import AIService
from src.integrations.wechat_official_sender import WeChatOfficialSender
from src.services.rss_service import RSSItem
from datetime import datetime

def test_markdown_to_html():
    """测试Markdown到HTML转换"""
    print("🧪 测试Markdown到HTML转换...")
    
    ai_service = AIService()
    
    # 测试文本包含各种Markdown格式
    test_markdown = """
📰 **优化标题**: Python异步编程最佳实践

## 核心要点
在现代Python开发中，**异步编程**已经成为提升性能的关键技术。

### 主要优势
- *高并发处理*能力
- **资源利用率**提升
- 更好的用户体验

这是一个包含多种格式的段落，其中有**粗体文字**和*斜体文字*。

🔗 **延伸阅读**：[查看完整技术详情](https://example.com)
"""
    
    # 转换为HTML
    html_result = ai_service.markdown_to_html(test_markdown)
    
    print("原始Markdown:")
    print(test_markdown)
    print("\n转换后的HTML:")
    print(html_result)
    print("\n" + "="*50)

def test_title_extraction():
    """测试标题提取"""
    print("🧪 测试标题提取...")
    
    sender = WeChatOfficialSender()
    
    # 测试各种标题格式
    test_messages = [
        "📰 **优化标题**: Python异步编程最佳实践\n\n内容...",
        "优化标题: 深度学习模型训练技巧\n\n内容...",
        "**标题**: 云计算架构设计\n\n内容...",
        "### 区块链技术解析\n\n这是内容...",
        "🔥 JavaScript新特性详解\n\n内容..."
    ]
    
    for i, message in enumerate(test_messages, 1):
        title = sender._extract_title(message)
        print(f"测试 {i}:")
        print(f"原始消息: {message.split()[0]}...")
        print(f"提取标题: {title}")
        print()

def test_content_formatting():
    """测试完整的内容格式化流程"""
    print("🧪 测试完整内容格式化...")
    
    # 创建模拟的RSS条目
    rss_item = RSSItem(
        title="Python异步编程最佳实践",
        link="https://example.com/async-python",
        description="关于Python异步编程的详细介绍",
        pub_date=datetime.now(),
        guid="test-guid"
    )
    
    # 创建AI服务
    ai_service = AIService()
    
    # 模拟AI生成的内容（包含Markdown格式）
    ai_generated_content = """
📰 **优化标题**: Python异步编程最佳实践详解

## 🚀 技术要点

在现代Web开发中，**异步编程**已成为提升应用性能的关键技术。Python的`asyncio`库为开发者提供了强大的异步编程工具。

### 🔑 核心概念
- **协程(Coroutines)**: 使用`async def`定义的可暂停和恢复的函数
- **事件循环(Event Loop)**: 管理和执行异步任务的核心引擎
- *并发处理*: 同时处理多个I/O操作

### 💡 实践建议
1. 合理使用`await`关键字
2. 避免在异步函数中使用阻塞操作
3. 充分利用**异步上下文管理器**

通过掌握这些技术，开发者可以构建高性能的Web应用程序。

🔗 **延伸阅读**：[查看完整技术详情](https://example.com/async-python)
"""
    
    print("AI生成的原始内容:")
    print(ai_generated_content)
    print("\n" + "="*50)
    
    # 测试Markdown转HTML（模拟微信公众号处理）
    html_content = ai_service.markdown_to_html(ai_generated_content)
    print("转换为HTML格式:")
    print(html_content)
    print("\n" + "="*50)
    
    # 测试标题提取
    sender = WeChatOfficialSender()
    extracted_title = sender._extract_title(ai_generated_content)
    print(f"提取的标题: {extracted_title}")

if __name__ == "__main__":
    print("🔧 内容格式化测试开始...\n")
    
    test_markdown_to_html()
    test_title_extraction()
    test_content_formatting()
    
    print("✅ 所有测试完成！")
