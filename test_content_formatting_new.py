#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试内容格式化
验证修复后的内容处理逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.ai_service import Summarizer
from src.integrations.wechat_official_sender import WeChatOfficialSender
from src.services.rss_service import RSSItem
from datetime import datetime

def test_content_cleaning():
    """测试内容清理功能"""
    print("🧪 测试内容清理功能...")
    
    ai_service = Summarizer()
    
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
    print("\n" + "="*50)

def test_markdown_to_html():
    """测试Markdown到HTML转换"""
    print("🧪 测试Markdown到HTML转换...")
    
    ai_service = Summarizer()
    
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

[查看完整技术详情](https://example.com)
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

def test_complete_workflow():
    """测试完整的工作流程"""
    print("🧪 测试完整工作流程...")
    
    # 模拟AI生成的带有问题的内容
    problematic_content = """
📰 **优化标题**: Python异步编程最佳实践详解      



## 🚀 技术要点    

在现代Web开发中，    **异步编程**已成为提升应用性能的关键技术。


### 🔑 核心概念   
- **协程(Coroutines)**: 使用`async def`定义的可暂停和恢复的函数   
- **事件循环(Event Loop)**: 管理和执行异步任务的核心引擎    
- *并发处理*: 同时处理多个I/O操作


### 💡 实践建议   
1. 合理使用`await`关键字   
2. 避免在异步函数中使用阻塞操作   
3. 充分利用**异步上下文管理器**    


通过掌握这些技术，开发者可以构建高性能的Web应用程序。   


[查看完整技术详情](https://example.com/async-python)
"""
    
    ai_service = Summarizer()
    sender = WeChatOfficialSender()
    
    print("=== 步骤1: 原始AI生成内容 ===")
    print(repr(problematic_content))
    
    print("\n=== 步骤2: 清理内容格式 ===")
    cleaned = ai_service.clean_content_for_wechat(problematic_content)
    print(repr(cleaned))
    
    print("\n=== 步骤3: 转换为HTML ===")
    html_content = ai_service.markdown_to_html(problematic_content)
    print(html_content)
    
    print("\n=== 步骤4: 提取标题 ===")
    title = sender._extract_title(problematic_content)
    print(f"提取的标题: '{title}'")
    
    print("\n=== 最终效果对比 ===")
    print("原始内容长度:", len(problematic_content))
    print("清理后内容长度:", len(cleaned))
    print("HTML内容长度:", len(html_content))

if __name__ == "__main__":
    print("🔧 内容格式化测试开始...\n")
    
    test_content_cleaning()
    test_markdown_to_html()
    test_title_extraction()
    test_complete_workflow()
    
    print("✅ 所有测试完成！")
