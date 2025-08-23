"""pytest配置文件"""

import shutil
import tempfile
from pathlib import Path
import sys

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.memory import test_memory, get_project_root, get_src_path, get_tests_path


@pytest.fixture(scope="session")
def project_root():
    """项目根目录fixture"""
    return get_project_root()


@pytest.fixture(scope="session")
def src_path():
    """src目录路径fixture"""
    return get_src_path()


@pytest.fixture(scope="session")
def test_memory_instance():
    """测试内存实例fixture"""
    return test_memory


@pytest.fixture(scope="session")
def temp_cache_dir():
    """创建临时缓存目录的fixture"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_env_vars(monkeypatch):
    """模拟环境变量的fixture"""
    test_vars = {
        "OPENAI_API_KEY": "test-api-key",
        "WECHAT_CONTACT_NAME": "测试联系人",
        "RSS_FEED_URL": "https://test.example.com/feed",
        "CHECK_INTERVAL_MINUTES": "10",
        "LOG_LEVEL": "DEBUG",
        "WECHAT_OFFICIAL_APP_ID": "test_app_id",
        "WECHAT_OFFICIAL_APP_SECRET": "test_app_secret",
        "WECHAT_OFFICIAL_AUTHOR_NAME": "Test Author",
        "WECHAT_OFFICIAL_ENABLED": "true"
    }

    for key, value in test_vars.items():
        monkeypatch.setenv(key, value)

    return test_vars


@pytest.fixture
def sample_rss_item():
    """示例RSS项目fixture"""
    from src.services.rss_service import RSSItem
    from datetime import datetime
    
    return RSSItem(
        title="测试文章标题",
        link="https://example.com/test-article",
        description="这是一个测试文章的描述...",
        published=datetime.now(),
        summary="测试摘要",
        image_url="https://example.com/test-image.jpg"
    )


@pytest.fixture
def mock_wechat_config():
    """模拟微信配置fixture"""
    return {
        'enabled': True,
        'app_id': 'test_app_id',
        'app_secret': 'test_app_secret',
        'author_name': 'Test Author'
    }


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """自动清理测试数据"""
    yield
    # 测试结束后清理临时文件
    test_memory.cleanup_temp_files()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """设置测试环境"""
    # 确保测试目录存在
    test_paths = [
        get_tests_path() / "temp",
        get_project_root() / "cache" / "test",
        get_project_root() / "logs" / "test"
    ]
    
    for path in test_paths:
        path.mkdir(parents=True, exist_ok=True)
    
    yield
    
    # 清理测试环境
    for path in test_paths:
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)

