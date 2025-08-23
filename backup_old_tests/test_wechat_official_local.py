"""
测试微信公众号本地功能（不调用API）
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from src.integrations.wechat_official_sender import WeChatOfficialSender
from src.services.rss_service import RSSItem
from src.core.utils import setup_logger

logger = setup_logger(__name__)

def test_wechat_official_local():
    """测试微信公众号本地功能"""
    print("=== 微信公众号本地功能测试 ===")
    
    # 直接从环境变量获取配置
    app_id = os.getenv('WECHAT_OFFICIAL_APP_ID')
    app_secret = os.getenv('WECHAT_OFFICIAL_APP_SECRET')
    
    if not app_id or not app_secret:
        print("❌ 微信公众号配置不完整，请检查 .env 文件")
        print(f"APP_ID: {'已设置' if app_id else '未设置'}")
        print(f"APP_SECRET: {'已设置' if app_secret else '未设置'}")
        return False
    
    print("✅ 微信公众号配置加载完成")
    
    # 创建微信公众号发送器
    sender_config = {
        'enabled': True,
        'app_id': app_id,
        'app_secret': app_secret,
        'author_name': os.getenv('WECHAT_OFFICIAL_AUTHOR_NAME', 'RSS助手'),
        'use_rich_formatting': True
    }
    
    sender = WeChatOfficialSender(sender_config)
    print("微信公众号发送器创建完成")
    
    # 验证配置
    if not sender.validate_config():
        print("❌ 微信公众号配置验证失败")
        return False
    
    print("✅ 微信公众号配置验证通过")
    
    # 获取发送器状态
    status = sender.get_status()
    print(f"发送器状态: {status}")
    
    # 创建测试文章
    print("\n=== 创建测试文章 ===")
    
    test_article = RSSItem(
        title="AI技术突破：DeepSeek发布新一代多模态模型",
        link="https://example.com/ai-breakthrough",
        summary="DeepSeek今日发布了其最新的多模态AI模型，在图像理解、代码生成和数学推理方面取得了显著突破。该模型采用全新的注意力机制，能够更好地理解复杂的多模态输入，为AI应用开辟了新的可能性。",
        publish_date=datetime.now(),
        content="详细的文章内容...",
        guid="test-article-123"
    )
    
    print(f"测试文章: {test_article.title}")
    print(f"文章内容长度: {len(test_article.summary)} 字符")
    
    # 测试标题提取
    print("\n=== 测试内容格式化 ===")
    
    test_message = f"""📰 {test_article.title}

✨ 核心要点：
{test_article.summary}

🚀 技术亮点：
• 全新注意力机制设计
• 多模态理解能力提升
• 代码生成准确率提高40%
• 数学推理能力达到新高度

🔗 阅读原文：{test_article.link}

📅 发布时间：{test_article.publish_date.strftime('%Y-%m-%d %H:%M')}
"""
    
    # 测试标题提取
    extracted_title = sender._extract_title(test_message)
    print(f"提取的标题: {extracted_title}")
    
    # 测试内容格式化
    formatted_content = sender._format_content(test_message)
    print(f"格式化后内容长度: {len(formatted_content)} 字符")
    
    # 测试摘要生成
    digest = sender._generate_digest(extracted_title, formatted_content, 120)
    print(f"生成的摘要: {digest}")
    
    # 保存格式化的HTML内容到文件供查看
    output_file = "test_wechat_official_output.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(formatted_content)
    
    print(f"\n✅ HTML内容已保存到: {output_file}")
    print("可以在浏览器中打开该文件查看格式化效果")
    
    # 测试草稿创建数据结构
    print("\n=== 测试草稿数据结构 ===")
    
    article_data = {
        "title": extracted_title,
        "content": formatted_content,
        "author": sender.author_name,
        "digest": digest,
        "show_cover_pic": 0,  # 无封面图片
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
        "content_source_url": test_article.link,
    }
    
    draft_data = {
        "articles": [article_data]
    }
    
    print("草稿数据结构:")
    print(f"- 标题: {article_data['title']}")
    print(f"- 作者: {article_data['author']}")
    print(f"- 摘要: {article_data['digest'][:50]}...")
    print(f"- 内容长度: {len(article_data['content'])} 字符")
    print(f"- 原文链接: {article_data['content_source_url']}")
    
    print("\n🎉 本地功能测试完成！")
    print("所有格式化和数据结构准备功能正常工作")
    print("\n📋 下一步操作:")
    print("1. 在微信公众号开发者中心配置服务器IP白名单")
    print("2. 确保公众号有草稿箱管理权限")
    print("3. 运行完整的API测试")
    
    return True

def main():
    """主函数"""
    print(f"开始测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        success = test_wechat_official_local()
        
        if success:
            print("\n🎉 本地功能测试成功！")
        else:
            print("\n❌ 本地功能测试失败！")
            
    except Exception as e:
        print(f"\n💥 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
