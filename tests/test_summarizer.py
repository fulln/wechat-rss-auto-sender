"""AI总结器的单元测试"""

from unittest.mock import Mock, patch
from datetime import datetime

from src.summarizer import Summarizer
from src.rss_fetcher import RSSItem


class TestSummarizer:
    """AI总结器测试"""

    def test_clean_html(self) -> None:
        """测试HTML清理功能"""
        summarizer = Summarizer()
        
        # 测试基本HTML清理
        html_text = "<p>这是一个<strong>测试</strong>文本</p>"
        cleaned = summarizer.clean_html(html_text)
        assert cleaned == "这是一个测试文本"
        
        # 测试空文本
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

    @patch('src.summarizer.OpenAI')
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
                description="新闻1的描述",
                published=datetime.now()
            ),
            RSSItem(
                title="测试新闻2", 
                link="https://test2.com",
                description="新闻2的描述",
                published=datetime.now()
            )
        ]
        
        summarizer = Summarizer()
        result = summarizer.summarize_items(items)
        
        assert "这是AI生成的总结内容" in result
        assert "https://test1.com" in result
        assert "https://test2.com" in result

    @patch('src.summarizer.OpenAI')
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
                published=datetime.now()
            )
        ]
        
        summarizer = Summarizer()
        result = summarizer.summarize_items(items)
        
        # 应该返回简单总结
        assert "测试新闻" in result
        assert "https://test.com" in result

    def test_summarize_empty_items(self) -> None:
        """测试空条目列表"""
        with patch('src.summarizer.OpenAI'):
            summarizer = Summarizer()
            result = summarizer.summarize_items([])
            assert result == ""

    def test_simple_summary(self) -> None:
        """测试简单总结功能"""
        with patch('src.summarizer.OpenAI'):
            items = [
                RSSItem(
                    title="测试新闻1",
                    link="https://test1.com", 
                    description="描述1",
                    published=datetime.now()
                ),
                RSSItem(
                    title="测试新闻2",
                    link="https://test2.com",
                    description="描述2", 
                    published=datetime.now()
                )
            ]
            
            summarizer = Summarizer()
            result = summarizer._simple_summary(items)
            
            assert "测试新闻1" in result
            assert "测试新闻2" in result
            assert "https://test1.com" in result
            assert "https://test2.com" in result
