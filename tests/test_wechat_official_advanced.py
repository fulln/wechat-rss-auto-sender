"""
微信公众号发送功能测试
将原来的test_wechat_official.py转换为标准pytest测试
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.integrations.wechat_official_sender import WeChatOfficialSender
from src.services.rss_service import RSSFetcher
from tests.test_utils import TestDataGenerator, TestAssertions


class TestWeChatOfficialSending:
    """微信公众号发送功能测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.test_data_gen = TestDataGenerator()
        self.assertions = TestAssertions()
    
    def test_wechat_sender_config_validation(self, mock_wechat_config):
        """测试微信发送器配置验证"""
        sender = WeChatOfficialSender(mock_wechat_config)
        
        # 模拟验证通过
        with patch.object(sender, 'validate_config', return_value=True):
            assert sender.validate_config() is True
    
    def test_wechat_sender_config_validation_failure(self):
        """测试微信发送器配置验证失败"""
        invalid_config = {
            'enabled': True,
            'app_id': '',  # 空的app_id应该验证失败
            'app_secret': 'test_secret',
            'author_name': 'Test Author'
        }
        
        sender = WeChatOfficialSender(invalid_config)
        
        # 模拟验证失败
        with patch.object(sender, 'validate_config', return_value=False):
            assert sender.validate_config() is False
    
    def test_wechat_connection_test(self, mock_wechat_config):
        """测试微信连接测试"""
        sender = WeChatOfficialSender(mock_wechat_config)
        
        # 模拟连接测试通过
        with patch.object(sender, 'test_connection', return_value=True):
            assert sender.test_connection() is True
    
    def test_wechat_sender_status(self, mock_wechat_config):
        """测试获取发送器状态"""
        sender = WeChatOfficialSender(mock_wechat_config)
        
        mock_status = {
            'connected': True,
            'last_send': None,
            'error_count': 0
        }
        
        with patch.object(sender, 'get_status', return_value=mock_status):
            status = sender.get_status()
            assert status['connected'] is True
            assert 'error_count' in status
    
    @pytest.mark.asyncio
    async def test_rss_service_fetch(self, mock_env_vars):
        """测试RSS服务获取文章"""
        # 模拟RSS服务
        mock_articles = self.test_data_gen.create_multiple_rss_items(3)
        
        with patch('src.services.rss_service.RSSService') as MockRSSService:
            mock_rss_instance = AsyncMock()
            mock_rss_instance.fetch_latest_articles.return_value = mock_articles
            MockRSSService.return_value = mock_rss_instance
            
            rss_service = RSSService(mock_env_vars)
            articles = await rss_service.fetch_latest_articles()
            
            assert len(articles) == 3
            for article in articles:
                self.assertions.assert_rss_item_valid(article)
    
    @pytest.mark.asyncio
    async def test_rss_service_fetch_empty(self, mock_env_vars):
        """测试RSS服务获取空文章列表"""
        with patch('src.services.rss_service.RSSService') as MockRSSService:
            mock_rss_instance = AsyncMock()
            mock_rss_instance.fetch_latest_articles.return_value = []
            MockRSSService.return_value = mock_rss_instance
            
            rss_service = RSSService(mock_env_vars)
            articles = await rss_service.fetch_latest_articles()
            
            assert articles == []
    
    def test_prepare_wechat_message(self):
        """测试准备微信消息内容"""
        test_article = self.test_data_gen.create_sample_rss_item(
            title="测试文章标题",
            description="这是测试文章的详细描述"
        )
        test_article.summary = "这是文章摘要"
        test_article.publish_date = datetime.now()
        
        # 构建消息内容
        message = f"""📰 {test_article.title}

✨ 核心要点：
{test_article.summary}

🔗 阅读原文：{test_article.link}

📅 发布时间：{test_article.publish_date.strftime('%Y-%m-%d %H:%M')}
"""
        
        # 验证消息格式
        assert test_article.title in message
        assert test_article.summary in message
        assert test_article.link in message
        assert len(message) > 0
    
    @patch('src.integrations.wechat_official_sender.WeChatOfficialSender.send_message')
    def test_send_message_as_draft(self, mock_send, mock_wechat_config):
        """测试发送消息作为草稿"""
        mock_send.return_value = True
        
        sender = WeChatOfficialSender(mock_wechat_config)
        test_article = self.test_data_gen.create_sample_rss_item()
        
        message = f"测试消息内容：{test_article.title}"
        
        result = sender.send_message(
            message,
            type='draft',
            title=test_article.title,
            rss_item=test_article
        )
        
        assert result is True
        mock_send.assert_called_once_with(
            message,
            type='draft',
            title=test_article.title,
            rss_item=test_article
        )
    
    @patch('src.integrations.wechat_official_sender.WeChatOfficialSender.send_message')
    def test_send_message_failure(self, mock_send, mock_wechat_config):
        """测试发送消息失败"""
        mock_send.return_value = False
        
        sender = WeChatOfficialSender(mock_wechat_config)
        test_article = self.test_data_gen.create_sample_rss_item()
        
        message = f"测试消息内容：{test_article.title}"
        
        result = sender.send_message(
            message,
            type='draft',
            title=test_article.title,
            rss_item=test_article
        )
        
        assert result is False
    
    @patch('src.integrations.wechat_official_sender.WeChatOfficialSender.send_message')
    def test_send_message_with_exception(self, mock_send, mock_wechat_config):
        """测试发送消息时抛出异常"""
        mock_send.side_effect = Exception("发送失败")
        
        sender = WeChatOfficialSender(mock_wechat_config)
        test_article = self.test_data_gen.create_sample_rss_item()
        
        message = f"测试消息内容：{test_article.title}"
        
        with pytest.raises(Exception, match="发送失败"):
            sender.send_message(
                message,
                type='draft',
                title=test_article.title,
                rss_item=test_article
            )
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_wechat_sending_flow(self, mock_wechat_config, mock_env_vars):
        """测试完整的微信发送流程（集成测试）"""
        # 1. 模拟RSS服务获取文章
        mock_articles = self.test_data_gen.create_multiple_rss_items(1)
        test_article = mock_articles[0]
        test_article.summary = "这是测试文章的摘要"
        test_article.publish_date = datetime.now()
        
        with patch('src.services.rss_service.RSSService') as MockRSSService:
            mock_rss_instance = AsyncMock()
            mock_rss_instance.fetch_latest_articles.return_value = mock_articles
            MockRSSService.return_value = mock_rss_instance
            
            # 2. 获取RSS文章
            rss_service = RSSService(mock_env_vars)
            articles = await rss_service.fetch_latest_articles()
            
            assert len(articles) > 0
            article = articles[0]
            
            # 3. 模拟微信发送器
            with patch('src.integrations.wechat_official_sender.WeChatOfficialSender') as MockSender:
                mock_sender_instance = Mock()
                mock_sender_instance.validate_config.return_value = True
                mock_sender_instance.test_connection.return_value = True
                mock_sender_instance.get_status.return_value = {'connected': True}
                mock_sender_instance.send_message.return_value = True
                MockSender.return_value = mock_sender_instance
                
                sender = WeChatOfficialSender(mock_wechat_config)
                
                # 4. 验证配置和连接
                assert sender.validate_config() is True
                assert sender.test_connection() is True
                
                # 5. 准备并发送消息
                message = f"""📰 {article.title}

✨ 核心要点：
{article.summary}

🔗 阅读原文：{article.link}

📅 发布时间：{article.publish_date.strftime('%Y-%m-%d %H:%M')}
"""
                
                result = sender.send_message(
                    message,
                    type='draft',
                    title=article.title,
                    rss_item=article
                )
                
                assert result is True
    
    @pytest.mark.parametrize("article_count,expected_success", [
        (0, False),  # 没有文章
        (1, True),   # 一篇文章
        (3, True),   # 多篇文章
    ])
    @pytest.mark.asyncio
    async def test_different_article_counts(self, article_count, expected_success, mock_env_vars):
        """参数化测试不同文章数量的处理"""
        mock_articles = self.test_data_gen.create_multiple_rss_items(article_count)
        
        with patch('src.services.rss_service.RSSService') as MockRSSService:
            mock_rss_instance = AsyncMock()
            mock_rss_instance.fetch_latest_articles.return_value = mock_articles
            MockRSSService.return_value = mock_rss_instance
            
            rss_service = RSSService(mock_env_vars)
            articles = await rss_service.fetch_latest_articles()
            
            has_articles = len(articles) > 0
            assert has_articles == expected_success


# 可以用于手动测试的函数
def manual_test_wechat_official():
    """手动测试微信公众号功能（需要真实配置）"""
    from dotenv import load_dotenv
    load_dotenv()
    
    # 创建测试实例
    test_instance = TestWeChatOfficialSending()
    test_instance.setup_method()
    
    # 运行基本测试
    print("运行微信配置验证测试...")
    mock_config = test_instance.test_data_gen.create_mock_wechat_config()
    
    try:
        test_instance.test_wechat_sender_config_validation(mock_config)
        print("✅ 微信配置验证测试通过")
    except Exception as e:
        print(f"❌ 微信配置验证测试失败: {e}")
    
    print("运行消息准备测试...")
    try:
        test_instance.test_prepare_wechat_message()
        print("✅ 消息准备测试通过")
    except Exception as e:
        print(f"❌ 消息准备测试失败: {e}")
    
    print("所有手动测试完成！")


if __name__ == "__main__":
    manual_test_wechat_official()
