"""
测试工具模块
提供常用的测试辅助函数和数据
"""

from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

from src.services.rss_service import RSSItem
from tests.memory import test_memory


class TestDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def create_sample_rss_item(
        title: str = "测试文章标题",
        description: str = "这是一个测试文章的详细描述，包含了丰富的内容信息...",
        link: str = "https://example.com/test-article"
    ) -> RSSItem:
        """创建示例RSS项目"""
        return RSSItem(
            title=title,
            link=link,
            description=description,
            published=datetime.now(),
            summary="测试摘要内容",
            image_url="https://example.com/test-image.jpg"
        )
    
    @staticmethod
    def create_multiple_rss_items(count: int = 3) -> List[RSSItem]:
        """创建多个RSS项目"""
        items = []
        for i in range(count):
            item = TestDataGenerator.create_sample_rss_item(
                title=f"测试文章标题 {i+1}",
                description=f"这是第{i+1}个测试文章的描述...",
                link=f"https://example.com/test-article-{i+1}"
            )
            items.append(item)
        return items
    
    @staticmethod
    def create_mock_wechat_config() -> Dict[str, Any]:
        """创建模拟微信配置"""
        return {
            'enabled': True,
            'app_id': 'test_app_id',
            'app_secret': 'test_app_secret',
            'author_name': 'Test Author',
            'max_title_length': 64,
            'max_summary_length': 120
        }
    
    @staticmethod
    def create_mock_ai_config() -> Dict[str, Any]:
        """创建模拟AI配置"""
        return {
            'enabled': True,
            'api_key': 'test_api_key',
            'model': 'gpt-3.5-turbo',
            'temperature': 0.7,
            'max_tokens': 1000
        }


class TestAssertions:
    """测试断言辅助类"""
    
    @staticmethod
    def assert_rss_item_valid(item: RSSItem):
        """断言RSS项目有效"""
        assert item is not None
        assert item.title
        assert item.link
        assert item.description
        assert item.published
    
    @staticmethod
    def assert_wechat_article_format(article_data: Dict[str, Any]):
        """断言微信文章格式正确"""
        required_fields = ['title', 'content', 'author']
        for field in required_fields:
            assert field in article_data, f"缺少必需字段: {field}"
        
        # 检查标题长度
        assert len(article_data['title']) <= 64, "标题长度超过限制"
        
        # 检查内容不为空
        assert article_data['content'].strip(), "内容不能为空"
    
    @staticmethod
    def assert_ai_summary_valid(summary: str):
        """断言AI摘要有效"""
        assert summary
        assert len(summary.strip()) > 0
        assert len(summary) <= 500, "摘要长度超过限制"


class TestFileManager:
    """测试文件管理器"""
    
    def __init__(self):
        self.temp_files: List[Path] = []
    
    def create_temp_file(self, content: str, suffix: str = ".txt") -> Path:
        """创建临时文件"""
        import tempfile
        fd, temp_path = tempfile.mkstemp(suffix=suffix)
        temp_file = Path(temp_path)
        
        with open(fd, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.temp_files.append(temp_file)
        test_memory.add_temp_file(str(temp_file))
        return temp_file
    
    def cleanup(self):
        """清理临时文件"""
        for temp_file in self.temp_files:
            if temp_file.exists():
                temp_file.unlink()
        self.temp_files.clear()


def mock_async_function(return_value=None):
    """模拟异步函数装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if return_value is not None:
                return return_value
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def capture_print_output():
    """捕获print输出的上下文管理器"""
    import io
    import sys
    from contextlib import contextmanager
    
    @contextmanager
    def _capture():
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        try:
            yield captured_output
        finally:
            sys.stdout = old_stdout
    
    return _capture()
