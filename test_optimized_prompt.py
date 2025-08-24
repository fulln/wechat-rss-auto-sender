"""
测试优化后的微信公众号prompt和样式功能
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.ai_service import Summarizer
from src.services.rss_service import RSSItem

def test_optimized_wechat_official_prompt():
    """测试优化后的微信公众号prompt"""
    
    # 创建AI服务实例
    summarizer = Summarizer()
    
    # 创建测试RSS项目
    test_item = RSSItem(
        title="Apple Introduces Revolutionary M4 Chip with Breakthrough AI Capabilities",
        link="https://example.com/apple-m4-chip",
        description="""
        Apple has unveiled its latest M4 chip, featuring unprecedented AI processing capabilities 
        that promise to revolutionize how we interact with technology. The new chip includes 
        a dedicated Neural Engine with 40 TOPS performance, enabling real-time AI processing 
        for applications ranging from photo editing to language translation.
        
        Key features include:
        - 40% faster CPU performance compared to M3
        - 60% improvement in GPU rendering
        - Advanced machine learning accelerators
        - Enhanced power efficiency for longer battery life
        
        Industry experts believe this could be a game-changer for Apple's ecosystem, 
        particularly in AR/VR applications and professional creative workflows.
        """,
        published=datetime.now()
    )
    
    print("🔬 测试优化后的微信公众号prompt...")
    print("=" * 60)
    
    # 生成微信公众号内容
    result = summarizer.summarize_single_item(test_item, sender_type="wechat_official")
    
    print("✅ 生成的微信公众号内容:")
    print("-" * 40)
    print(result)
    print("-" * 40)
    
    # 测试HTML样式转换
    print("\n🎨 测试Markdown到HTML样式转换...")
    print("=" * 60)
    
    # 模拟Markdown内容
    markdown_content = """
## 🚀 苹果M4芯片核心突破

### 📊 性能指标对比

| 指标 | M3芯片 | M4芯片 | 提升幅度 |
|------|--------|--------|----------|
| CPU性能 | 基准 | +40% | 显著提升 |
| GPU渲染 | 基准 | +60% | 革命性改进 |
| AI算力 | 20 TOPS | 40 TOPS | 翻倍提升 |

### ⭐ 关键特性

- **AI神经引擎**: 40 TOPS超强算力，实时AI处理
- **能效比优化**: 更长续航时间，更低功耗
- **专业级性能**: 支持4K视频剪辑和3D渲染
- **生态协同**: 完美适配苹果全家桶产品

> 💡 **专家观点**: 这是苹果在AI时代的重要布局，将重新定义移动computing的边界。

### 🔮 市场影响分析

1. **AR/VR领域**: 为Vision Pro等设备提供强劲动力
2. **创意工作流**: 专业创作者的生产力将获得质的飞跃  
3. **竞争格局**: 与高通、AMD等竞争对手拉开差距

**结论**: M4芯片不仅是性能的提升，更是苹果AI战略的关键一步。
"""
    
    # 转换为HTML并应用样式
    styled_html = summarizer.markdown_to_html(markdown_content)
    
    print("✅ 转换后的HTML（带样式）:")
    print("-" * 40)
    print(styled_html)
    print("-" * 40)
    
    # 测试元数据提取
    print("\n📊 测试元数据提取...")
    print("=" * 60)
    
    # 提取元数据
    clean_content, metadata = summarizer._extract_article_metadata(result)
    
    print("📋 提取的元数据:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    
    print(f"\n📝 清理后的内容长度: {len(clean_content)} 字符")

def test_html_styling():
    """专门测试HTML样式功能"""
    
    print("\n🎨 专项测试: HTML样式功能")
    print("=" * 60)
    
    summarizer = Summarizer()
    
    # 测试各种Markdown元素
    test_markdown = """
# 主标题测试

## 二级标题测试  

### 三级标题测试

这是一个普通段落，包含**粗体文本**和*斜体文本*，还有[链接文本](https://example.com)。

> 这是一个引用块，用来突出重要信息。

### 列表测试

无序列表:
- 第一个要点
- 第二个要点  
- 第三个要点

有序列表:
1. 步骤一
2. 步骤二
3. 步骤三

### 表格测试

| 功能 | 描述 | 状态 |
|------|------|------|
| AI处理 | 智能内容生成 | ✅ |
| 样式优化 | 清新阅读体验 | ✅ |
| 多平台 | 差异化内容 | ✅ |

### 代码测试

这里有内联代码 `console.log('Hello World')` 的例子。
"""
    
    styled_html = summarizer.markdown_to_html(test_markdown)
    
    print("🎯 样式化HTML输出:")
    print("-" * 40)
    print(styled_html)
    print("-" * 40)

if __name__ == "__main__":
    test_optimized_wechat_official_prompt()
    test_html_styling()
    
    print("\n🎉 所有测试完成！")
    print("✨ 优化后的微信公众号prompt具有以下特点:")
    print("   - 结构化内容生成（概述、要点、分析、展望）")
    print("   - Markdown格式输出，便于后续HTML转换")
    print("   - 清新的文档阅读样式")
    print("   - 智能列表和表格格式化")
    print("   - 专业的排版和视觉效果")
