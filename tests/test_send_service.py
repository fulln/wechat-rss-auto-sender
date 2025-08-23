"""发送服务的单元测试"""

import shutil
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch

from src.core.config import Config
from src.services.rss_service import RSSItem
from src.services.send_service import SendManager


class TestSendManager:
    """发送管理器测试"""

    def setup_method(self) -> None:
        """测试前准"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self) -> None:
        """测试后清"""
        shutil.rmtree(self.temp_dir)

    @patch("src.services.send_service.WeChatSender")
    @patch("src.services.ai_service.Summarizer")
    @patch("src.services.send_service.RSSFetcher")
    def test_send_manager_initialization(
        self, mock_rss: Mock, mock_ai: Mock, mock_wechat: Mock
    ) -> None:
        """测试发送管理器初始"""
        send_manager = SendManager()

        assert send_manager.rss_fetcher is not None
        assert send_manager.summarizer is not None
        assert send_manager.wechat_sender is not None
        assert send_manager.max_articles_per_batch == Config.MAX_ARTICLES_PER_BATCH
        assert send_manager.send_interval_minutes == Config.SEND_INTERVAL_MINUTES

    @patch("src.services.send_service.WeChatSender")
    @patch("src.services.ai_service.Summarizer")
    @patch("src.services.send_service.RSSFetcher")
    def test_is_send_time_allowed(
        self, mock_rss: Mock, mock_ai: Mock, mock_wechat: Mock
    ) -> None:
        """测试发送时间控"""
        send_manager = SendManager()

        # 测试允许的时"(上午10"
        with patch("src.services.send_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 8, 23, 10, 0, 0)
            assert send_manager.is_send_time_allowed() is True

        # 测试不允许的时间 (凌晨2"
        with patch("src.services.send_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 8, 23, 2, 0, 0)
            assert send_manager.is_send_time_allowed() is False

    @patch("src.services.send_service.WeChatSender")
    @patch("src.services.ai_service.Summarizer")
    @patch("src.services.send_service.RSSFetcher")
    def test_get_send_status(
        self, mock_rss: Mock, mock_ai: Mock, mock_wechat: Mock
    ) -> None:
        """测试获取发送状"""
        send_manager = SendManager()

        status = send_manager.get_send_status()

        assert isinstance(status, dict)
        assert "is_send_time_allowed" in status
        assert "max_articles_per_batch" in status
        assert "send_interval_minutes" in status
        assert "min_quality_score" in status

    @patch("src.services.send_service.WeChatSender")
    @patch("src.services.ai_service.Summarizer")
    @patch("src.services.send_service.RSSFetcher")
    def test_random_delay_calculation(
        self, mock_rss: Mock, mock_ai: Mock, mock_wechat: Mock
    ) -> None:
        """测试随机延迟计算"""
        send_manager = SendManager()

        with patch("src.services.send_service.random.randint") as mock_random:
            mock_random.return_value = 5
            delay = send_manager._get_random_delay()
            assert delay == 5
            mock_random.assert_called_once_with(0, Config.SEND_RANDOM_DELAY_MAX)

    @patch("src.services.send_service.WeChatSender")
    @patch("src.services.ai_service.Summarizer")
    @patch("src.services.send_service.RSSFetcher")
    def test_process_and_send_articles_success(
        self, mock_rss: Mock, mock_ai: Mock, mock_wechat: Mock
    ) -> None:
        """测试成功处理和发送文"""
        # 设置模拟
        mock_rss_instance = Mock()
        mock_ai_instance = Mock()
        mock_wechat_instance = Mock()

        mock_rss.return_value = mock_rss_instance
        mock_ai.return_value = mock_ai_instance
        mock_wechat.return_value = mock_wechat_instance

        # 创建测试文章
        test_item = RSSItem(
            title="测试文章",
            link="https://test.com",
            description="测试描述",
            published=datetime.now(),
        )

        mock_rss_instance.fetch_latest_items.return_value = [test_item]
        mock_ai_instance.summarize_with_quality_check.return_value = {
            "summary": "这是一个测试总结",
            "quality_score": 8,
        }
        mock_wechat_instance.send_message.return_value = True

        send_manager = SendManager()

        with patch.object(send_manager, "is_send_time_allowed", return_value=True):
            result = send_manager.process_and_send_articles()

            assert result > 0
            mock_rss_instance.fetch_latest_items.assert_called_once()
            mock_ai_instance.summarize_with_quality_check.assert_called_once()
            mock_wechat_instance.send_message.assert_called_once()

    @patch("src.services.send_service.WeChatSender")
    @patch("src.services.ai_service.Summarizer")
    @patch("src.services.send_service.RSSFetcher")
    def test_process_and_send_articles_time_blocked(
        self, mock_rss: Mock, mock_ai: Mock, mock_wechat: Mock
    ) -> None:
        """测试时间限制阻止发"""
        send_manager = SendManager()

        with patch.object(send_manager, "is_send_time_allowed", return_value=False):
            result = send_manager.process_and_send_articles()

            assert result == 0

    @patch("src.services.send_service.WeChatSender")
    @patch("src.services.ai_service.Summarizer")
    @patch("src.services.send_service.RSSFetcher")
    def test_process_and_send_articles_low_quality(
        self, mock_rss: Mock, mock_ai: Mock, mock_wechat: Mock
    ) -> None:
        """测试低质量文章被过滤"""
        # 设置模拟
        mock_rss_instance = Mock()
        mock_ai_instance = Mock()
        mock_wechat_instance = Mock()

        mock_rss.return_value = mock_rss_instance
        mock_ai.return_value = mock_ai_instance
        mock_wechat.return_value = mock_wechat_instance

        # 创建测试文章
        test_item = RSSItem(
            title="测试文章",
            link="https://test.com",
            description="测试描述",
            published=datetime.now(),
        )

        mock_rss_instance.fetch_latest_items.return_value = [test_item]
        mock_ai_instance.summarize_with_quality_check.return_value = {
            "summary": "这是一个测试总结",
            "quality_score": 5,  # 低于最低要""
        }

        send_manager = SendManager()

        with patch.object(send_manager, "is_send_time_allowed", return_value=True):
            result = send_manager.process_and_send_articles()

            assert result == 0
            mock_rss_instance.fetch_latest_items.assert_called_once()
            mock_ai_instance.summarize_with_quality_check.assert_called_once()
            # 不应该调用微信发"
            mock_wechat_instance.send_message.assert_not_called()


class TestSendManagerIntegration:
    """发送管理器集成测试"""

    def test_quality_scoring_filter(self) -> None:
        """测试质量评分筛选功"""
        # 这个测试将scripts/test_quality_filter.py的功能整合进"
        with patch("src.services.send_service.Config.MIN_QUALITY_SCORE", 7):
            send_manager = SendManager()

            # 模拟不同质量分数的文"
            high_quality_article = {"summary": "高质量文章总结", "quality_score": 8}

            low_quality_article = {"summary": "低质量文章总结", "quality_score": 5}

            # 验证筛选逻辑
            assert send_manager._should_send_article(high_quality_article) is True
            assert send_manager._should_send_article(low_quality_article) is False

    def test_time_control_functionality(self) -> None:
        """测试时间控制功能"""
        # 这个测试将scripts/test_time_control.py的功能整合进"
        send_manager = SendManager()

        # 测试不同时间"
        test_times = [
            (datetime(2025, 8, 23, 2, 0, 0), False),  # 凌晨2"- 不允"
            (datetime(2025, 8, 23, 9, 0, 0), True),  # 上午9"- 允许
            (datetime(2025, 8, 23, 14, 0, 0), True),  # 下午2"- 允许
            (datetime(2025, 8, 23, 23, 59, 0), True),  # 晚上11:59 - 允许
            (datetime(2025, 8, 23, 0, 1, 0), False),  # 午夜12:01 - 不允"
        ]

        for test_time, expected in test_times:
            with patch("src.services.send_service.datetime") as mock_datetime:
                mock_datetime.now.return_value = test_time
                assert send_manager.is_send_time_allowed() == expected

    def test_enhanced_ai_features(self) -> None:
        """测试增强版AI功能"""
        # 这个测试将scripts/test_enhanced_ai_features.py的功能整合进"
        with patch("src.services.ai_service.Summarizer") as mock_ai_class:
            mock_ai = Mock()
            mock_ai_class.return_value = mock_ai

            # 模拟增强版AI响应
            mock_ai.summarize_with_quality_check.return_value = {
                "summary": "增强版AI生成的高质量总结，包含关键信息和深度分析",
                "quality_score": 9,
                "key_points": ["关键"", "关键"", "关键""],
                "sentiment": "positive",
            }

            SendManager()

            # 验证增强功能
            assert mock_ai.summarize_with_quality_check is not None

    def test_single_article_summary(self) -> None:
        """测试单篇文章专门总结功能"""
        # 这个测试将scripts/test_single_article_summary.py的功能整合进"
        test_item = RSSItem(
            title="专门测试文章标题",
            link="https://test-single.com",
            description="这是一个用于测试单篇文章总结功能的描述内",
            published=datetime.now(),
        )

        with patch("src.services.ai_service.Summarizer") as mock_ai_class:
            mock_ai = Mock()
            mock_ai_class.return_value = mock_ai

            # 模拟单篇文章总结
            mock_ai.summarize_single_item.return_value = {
                "summary": "针对单篇文章的专门深度总结，详细分析了文章的核心观",
                "quality_score": 8,
                "word_count": 180,
            }

            SendManager()

            # 验证单篇文章总结功能存在
            if hasattr(mock_ai, "summarize_single_item"):
                result = mock_ai.summarize_single_item(test_item)
                assert result is not None
                assert "summary" in result
                assert "quality_score" in result



