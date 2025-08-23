"""
测试微信公众号发送功能
"""
import os
import sys
import asyncio
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from src.core.config import load_config
from src.integrations.wechat_official_sender import WeChatOfficialSender
from src.services.rss_service import RSSService
from src.core.utils import setup_logger

logger = setup_logger(__name__)

async def test_wechat_official_send():
    """测试微信公众号发送功能"""
    print("=== 微信公众号发送测试 ===")
    
    # 加载配置
    config = load_config()
    print(f"配置加载完成: {len(config)} 项配置")
    
    # 创建微信公众号发送器
    sender_config = {
        'enabled': True,
        'app_id': config.get('WECHAT_OFFICIAL_APP_ID'),
        'app_secret': config.get('WECHAT_OFFICIAL_APP_SECRET'),
        'author_name': config.get('WECHAT_OFFICIAL_AUTHOR_NAME', 'RSS助手'),
        'use_rich_formatting': True
    }
    
    sender = WeChatOfficialSender(sender_config)
    print(f"微信公众号发送器创建完成")
    
    # 验证配置
    if not sender.validate_config():
        print("❌ 微信公众号配置验证失败")
        return False
    
    print("✅ 微信公众号配置验证通过")
    
    # 测试连接
    if not sender.test_connection():
        print("❌ 微信公众号连接测试失败")
        return False
        
    print("✅ 微信公众号连接测试通过")
    
    # 获取发送器状态
    status = sender.get_status()
    print(f"发送器状态: {status}")
    
    # 创建RSS服务并获取最新文章
    print("\n=== 获取RSS文章 ===")
    rss_service = RSSService(config)
    
    # 获取RSS文章
    articles = await rss_service.fetch_latest_articles()
    
    if not articles:
        print("❌ 未获取到RSS文章")
        return False
        
    print(f"✅ 获取到 {len(articles)} 篇文章")
    
    # 取第一篇文章进行测试
    test_article = articles[0]
    print(f"测试文章: {test_article.title}")
    print(f"文章内容长度: {len(test_article.summary)} 字符")
    
    if hasattr(test_article, 'local_image_path') and test_article.local_image_path:
        print(f"文章配图: {test_article.local_image_path}")
    else:
        print("文章无配图")
    
    # 准备发送内容
    message = f"""📰 {test_article.title}

✨ 核心要点：
{test_article.summary}

🔗 阅读原文：{test_article.link}

📅 发布时间：{test_article.publish_date.strftime('%Y-%m-%d %H:%M')}
"""
    
    print(f"\n=== 发送消息到微信公众号 ===")
    print(f"消息长度: {len(message)} 字符")
    
    # 发送消息（创建草稿）
    try:
        result = sender.send_message(
            message,
            type='draft',  # 创建草稿而不是直接发布
            title=test_article.title,
            rss_item=test_article
        )
        
        if result:
            print("✅ 消息发送成功！已创建为草稿")
            print("请到微信公众号后台查看草稿箱")
            return True
        else:
            print("❌ 消息发送失败")
            return False
            
    except Exception as e:
        print(f"❌ 发送过程中出现异常: {e}")
        return False

async def main():
    """主函数"""
    print(f"开始测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        success = await test_wechat_official_send()
        
        if success:
            print("\n🎉 测试完成！微信公众号发送功能正常")
        else:
            print("\n❌ 测试失败！请检查配置和网络连接")
            
    except Exception as e:
        print(f"\n💥 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())
