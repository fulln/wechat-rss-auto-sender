"""集成测试"""

from datetime import datetime
from unittest.mock import Mock, patch

from src.services.rss_service import RSSItem
from src.services.scheduler_service import NewsScheduler


class TestIntegration:
    """集成测试�?""

    @patch("src.services.send_service.WeChatSender")
    @patch("src.services.send_service.AISummarizer")
    @patch("src.services.send_service.RSSFetcher")
    def test_complete_news_flow(
        self, mock_rss_class: Mock, mock_summarizer_class: Mock, mock_sender_class: Mock
    ) -> None:
        """测试完整的新闻流�?""
        # 模拟RSS获取�?
        mock_items = [
            RSSItem(
                title="测试新闻1",
                link="https://test1.com",
                description="新闻1描述",
                published=datetime.now(),
            ),
            RSSItem(
                title="测试新闻2",
                link="https://test2.com",
                description="新闻2描述",
                published=datetime.now(),
            ),
        ]

        mock_rss = Mock()
        mock_rss.fetch_latest_items.return_value = mock_items
        mock_rss.get_feed_info.return_value = {"title": "测试RSS�?}
        mock_rss_class.return_value = mock_rss

        # 模拟AI总结�?
        mock_summarizer = Mock()
        mock_summarizer.summarize_with_quality_check.return_value = {
            "summary": "AI生成的高质量总结内容",
            "quality_score": 8,
        }
        mock_summarizer_class.return_value = mock_summarizer

        # 模拟微信发送器
        mock_sender = Mock()
        mock_sender.test_connection.return_value = True
        mock_sender.send_message.return_value = True
        mock_sender_class.return_value = mock_sender

        # 执行完整流程
        scheduler = NewsScheduler()
        scheduler.check_and_send_news()

        # 验证调用�?
        mock_rss.fetch_latest_items.assert_called_once()
        mock_summarizer.summarize_items.assert_called_once_with(mock_items)
        mock_sender.send_message.assert_called_once_with("AI生成的总结内容，包含新闻链�?)

    @patch("src.scheduler.WeChatSender")
    @patch("src.scheduler.Summarizer")
    @patch("src.scheduler.RSSFetcher")
    def test_no_new_articles_flow(
        self, mock_rss_class: Mock, mock_summarizer_class: Mock, mock_sender_class: Mock
    ) -> None:
        """测试没有新文章的流程"""
        # 模拟没有新文�?
        mock_rss = Mock()
        mock_rss.fetch_latest_items.return_value = []
        mock_rss_class.return_value = mock_rss

        mock_summarizer = Mock()
        mock_summarizer_class.return_value = mock_summarizer

        mock_sender = Mock()
        mock_sender_class.return_value = mock_sender

        scheduler = NewsScheduler()
        scheduler.check_and_send_news()

        # 验证没有调用总结和发�?
        mock_summarizer.summarize_items.assert_not_called()
        mock_sender.send_message.assert_not_called()

    @patch("src.scheduler.WeChatSender")
    @patch("src.scheduler.Summarizer")
    @patch("src.scheduler.RSSFetcher")
    def test_summarizer_failure_flow(
        self, mock_rss_class: Mock, mock_summarizer_class: Mock, mock_sender_class: Mock
    ) -> None:
        """测试AI总结失败的流�?""
        # 模拟RSS获取成功
        mock_items = [RSSItem("测试", "https://test.com", "描述", datetime.now())]
        mock_rss = Mock()
        mock_rss.fetch_latest_items.return_value = mock_items
        mock_rss_class.return_value = mock_rss

        # 模拟总结失败
        mock_summarizer = Mock()
        mock_summarizer.summarize_items.return_value = ""  # 空总结
        mock_summarizer_class.return_value = mock_summarizer

        mock_sender = Mock()
        mock_sender_class.return_value = mock_sender

        scheduler = NewsScheduler()
        scheduler.check_and_send_news()

        # 验证没有发送消�?
        mock_sender.send_message.assert_not_called()

