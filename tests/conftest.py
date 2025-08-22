"""pytest配置文件"""

import shutil
import tempfile
from pathlib import Path

import pytest


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
        "WECHAT_CONTACT_NAME": "测试联系�?,
        "RSS_FEED_URL": "https://test.example.com/feed",
        "CHECK_INTERVAL_MINUTES": "10",
        "LOG_LEVEL": "DEBUG",
    }

    for key, value in test_vars.items():
        monkeypatch.setenv(key, value)

    return test_vars

