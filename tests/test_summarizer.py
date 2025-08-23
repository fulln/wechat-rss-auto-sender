"""AI总结器的单元测试"""

from datetime import datetime
from unittest.mock import Mock, patch

from src.services.ai_service import Summarizer
from src.services.rss_service import RSSItem


class TestSummarizer:
    """AI总结器测"""

    def test_clean_html(self) -> None:
        """测试HTML清理功能"""
        summarizer = Summarizer()

        # 测试基本HTML清理
        html_text = "<p>这是一"strong>测试</strong>文本</p>"
        cleaned = summarizer.clean_html(html_text)
        assert cleaned == "这是一个测试文"

        # 测试空文"
        assert summarizer.clean_html("") == ""
        assert summarizer.clean_html(None) == ""

        # 测试复杂HTML
        complex_html = """
        <div>
            <h1>标题</h1>
            <p>段落1</p>
            <p>段落2</p>
        </div>
        """
        cleaned = summarizer.clean_html(complex_html)
        assert "标题" in cleaned
        assert "段落1" in cleaned
        assert "段落2" in cleaned

    @patch("src.services.ai_service.OpenAI")
    def test_summarize_items_success(self, mock_openai_class: Mock) -> None:
        """测试成功的AI总结"""
        # 模拟OpenAI响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "这是AI生成的总结内容"

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        # 创建测试数据
        items = [
            RSSItem(
                title="测试新闻1",
                link="https://test1.com",
                description="新闻1的描",
                published=datetime.now(),
            ),
            RSSItem(
                title="测试新闻2",
                link="https://test2.com",
                description="新闻2的描",
                published=datetime.now(),
            ),
        ]

        summarizer = Summarizer()
        result = summarizer.summarize_items(items)

        assert "这是AI生成的总结内容" in result
        assert "https://test1.com" in result
        assert "https://test2.com" in result

    @patch("src.services.ai_service.OpenAI")
    def test_summarize_items_api_error(self, mock_openai_class: Mock) -> None:
        """测试API错误时的降级处理"""
        # 模拟API错误
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API错误")
        mock_openai_class.return_value = mock_client

        items = [
            RSSItem(
                title="测试新闻",
                link="https://test.com",
                description="描述",
                published=datetime.now(),
            )
        ]

        summarizer = Summarizer()
        result = summarizer.summarize_items(items)

        # 应该返回简单总结
        assert "测试新闻" in result
        assert "https://test.com" in result

    def test_summarize_empty_items(self) -> None:
        """测试空条目列"""
        with patch("src.services.ai_service.OpenAI"):
            summarizer = Summarizer()
            result = summarizer.summarize_items([])
            assert result == ""

    def test_simple_summary(self) -> None:
        """测试简单总结功能"""
        with patch("src.services.ai_service.OpenAI"):
            items = [
                RSSItem(
                    title="测试新闻1",
                    link="https://test1.com",
                    description="描述1",
                    published=datetime.now(),
                ),
                RSSItem(
                    title="测试新闻2",
                    link="https://test2.com",
                    description="描述2",
                    published=datetime.now(),
                ),
            ]

            summarizer = Summarizer()
            result = summarizer._simple_summary(items)

            assert "测试新闻1" in result
            assert "测试新闻2" in result
            assert "https://test1.com" in result
            assert "https://test2.com" in result

    @patch("src.services.ai_service.OpenAI")
    def test_summarize_with_quality_check(self, mock_openai_class: Mock) -> None:
        """测试带质量检查的总结功能"""
        # 模拟OpenAI响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[
            0
        ].message.content = """
        {
            "summary": "这是一个高质量的新闻总结",
            "quality_score": 8,
            "key_points": ["关键"", "关键""],
            "reasoning": "文章内容丰富，信息价值高"
        }
        """

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        test_item = RSSItem(
            title="测试新闻",
            link="https://test.com",
            description="测试描述内容",
            published=datetime.now(),
        )

        summarizer = Summarizer()
        result = summarizer.summarize_with_quality_check(test_item)

        assert isinstance(result, dict)
        assert "summary" in result
        assert "quality_score" in result
        assert result["quality_score"] == 8

    @patch("src.services.ai_service.OpenAI")
    def test_single_item_summary(self, mock_openai_class: Mock) -> None:
        """测试单篇文章总结功能"""
        # 模拟OpenAI响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "这是针对单篇文章的深度总结内容"

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        test_item = RSSItem(
            title="单篇测试文章",
            link="https://single-test.com",
            description="详细的文章描述内容，用于测试单篇文章总结功能",
            published=datetime.now(),
        )

        summarizer = Summarizer()
        result = summarizer.summarize_single_item(test_item)

        assert result is not None
        assert "这是针对单篇文章的深度总结内容" in result

    def test_extract_quality_score(self) -> None:
        """测试质量分数提取功能"""
        summarizer = Summarizer()

        # 测试有效的JSON响应
        json_response = """
        {
            "summary": "测试总结",
            "quality_score": 7,
            "reasoning": "质量中等"
        }
        """
        result = summarizer._extract_quality_info(json_response)
        assert result["quality_score"] == 7
        assert result["summary"] == "测试总结"

        # 测试无效的JSON
        invalid_json = "这不是一个有效的JSON"
        result = summarizer._extract_quality_info(invalid_json)
        assert result["quality_score"] == 5  # 默认分数
        assert result["summary"] == invalid_json

    @patch("src.services.ai_service.OpenAI")
    def test_api_error_handling(self, mock_openai_class: Mock) -> None:
        """测试API错误处理"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API连接失败")
        mock_openai_class.return_value = mock_client

        test_item = RSSItem(
            title="测试文章",
            link="https://test.com",
            description="测试描述",
            published=datetime.now(),
        )

        summarizer = Summarizer()

        # 测试质量检查在API失败时的处理
        result = summarizer.summarize_with_quality_check(test_item)
        assert isinstance(result, dict)
        assert "summary" in result
        assert "quality_score" in result
        # 应该返回降级的结"

