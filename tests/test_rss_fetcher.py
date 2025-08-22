"""RSS获取器的单元测试"""

import shutil
import tempfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

from src.services.rss_service import RSSCache, RSSFetcher, RSSItem


class TestRSSItem:
    """RSS条目测试"""

    def test_rss_item_creation(self) -> None:
        """测试RSS条目创建"""
        published = datetime(2025, 8, 23, 12, 0, 0)
        item = RSSItem(
            title="测试标题",
            link="https://example.com",
            description="测试描述",
            published=published,
        )

        assert item.title == "测试标题"
        assert item.link == "https://example.com"
        assert item.description == "测试描述"
        assert item.published == published
        assert item.date_key == "2025-08-23"
        assert len(item.title_hash) == 16

    def test_title_hash_generation(self) -> None:
        """测试标题哈希生成"""
        item1 = RSSItem("测试标题", "", "", datetime.now())
        item2 = RSSItem("测试标题", "", "", datetime.now())
        item3 = RSSItem("不同标题", "", "", datetime.now())

        assert item1.title_hash == item2.title_hash
        assert item1.title_hash != item3.title_hash

    def test_to_dict(self) -> None:
        """测试转换为字�?""
        published = datetime(2025, 8, 23, 12, 0, 0)
        item = RSSItem("测试", "https://test.com", "描述", published)

        result = item.to_dict()
        assert result["title"] == "测试"
        assert result["link"] == "https://test.com"
        assert result["published"] == "2025-08-23T12:00:00"


class TestRSSCache:
    """RSS缓存测试"""

    def setup_method(self) -> None:
        """测试前设�?""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = RSSCache(cache_dir=self.temp_dir)

    def teardown_method(self) -> None:
        """测试后清�?""
        shutil.rmtree(self.temp_dir)

    def test_cache_initialization(self) -> None:
        """测试缓存初始�?""
        assert self.cache.cache_dir.exists()
        assert isinstance(self.cache.daily_cache, dict)

    def test_add_and_check_duplicate(self) -> None:
        """测试添加和检查重�?""
        item = RSSItem("测试标题", "https://test.com", "描述", datetime.now())

        # 首次添加，不应该是重�?
        assert not self.cache.is_duplicate(item)
        self.cache.add_item(item)

        # 再次检查，应该是重�?
        assert self.cache.is_duplicate(item)

    def test_different_dates_not_duplicate(self) -> None:
        """测试不同日期的相同标题不算重�?""
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        item1 = RSSItem("测试标题", "https://test.com", "描述", today)
        item2 = RSSItem("测试标题", "https://test.com", "描述", yesterday)

        self.cache.add_item(item1)
        assert not self.cache.is_duplicate(item2)


class TestRSSFetcher:
    """RSS获取器测�?""

    def setup_method(self) -> None:
        """测试前设�?""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self) -> None:
        """测试后清�?""
        shutil.rmtree(self.temp_dir)

    @patch("src.services.rss_service.requests.get")
    @patch("src.services.rss_service.feedparser.parse")
    def test_fetch_latest_items_success(self, mock_parse: Mock, mock_get: Mock) -> None:
        """测试成功获取RSS条目"""
        # 模拟HTTP响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<rss>...</rss>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # 模拟feedparser结果
        mock_entry = MagicMock()
        mock_entry.title = "测试标题"
        mock_entry.link = "https://test.com"
        mock_entry.description = "测试描述"
        mock_entry.published_parsed = (2025, 8, 23, 12, 0, 0, 0, 0, 0)

        mock_feed = Mock()
        mock_feed.bozo = False
        mock_feed.entries = [mock_entry]
        mock_feed.feed = {"title": "测试RSS�?}

        mock_parse.return_value = mock_feed

        with patch("src.services.rss_service.RSSCache") as mock_cache_class:
            mock_cache = Mock()
            mock_cache.is_duplicate.return_value = False
            mock_cache_class.return_value = mock_cache

            fetcher = RSSFetcher()
            items = fetcher.fetch_latest_items(since_minutes=60)

            assert len(items) == 1
            assert items[0].title == "测试标题"
            assert items[0].link == "https://test.com"

    @patch("src.services.rss_service.requests.get")
    def test_fetch_latest_items_http_error(self, mock_get: Mock) -> None:
        """测试HTTP错误处理"""
        mock_get.side_effect = Exception("网络错误")

        with patch("src.services.rss_service.RSSCache"):
            fetcher = RSSFetcher()
            items = fetcher.fetch_latest_items()

            assert len(items) == 0

    def test_get_cache_status(self) -> None:
        """测试获取缓存状�?""
        with patch("src.services.rss_service.RSSCache") as mock_cache_class:
            mock_cache = Mock()
            mock_cache.cache_dir = self.temp_dir
            mock_cache.daily_cache = {"2025-08-23": {"hash1", "hash2"}}
            mock_cache_class.return_value = mock_cache

            fetcher = RSSFetcher()
            status = fetcher.get_cache_status()

            assert "cache_dir" in status
            assert "daily_stats" in status
            assert status["daily_stats"]["2025-08-23"] == 2

