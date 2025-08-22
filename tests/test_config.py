"""配置模块的单元测�?""

import os
from unittest.mock import patch

import pytest

from src.core.config import Config


class TestConfig:
    """配置类测�?""

    def test_default_values(self) -> None:
        """测试默认配置�?""
        assert Config.WECHAT_CONTACT_NAME == "文件传输助手"
        assert Config.RSS_FEED_URL == "https://36kr.com/feed-article"
        assert Config.CHECK_INTERVAL_MINUTES == 5
        assert Config.SUMMARY_MIN_LENGTH == 150
        assert Config.SUMMARY_MAX_LENGTH == 300
        assert Config.LOG_LEVEL == "INFO"

    @patch.dict(os.environ, {"WECHAT_CONTACT_NAME": "测试联系�?})
    def test_environment_override(self) -> None:
        """测试环境变量覆盖"""
        # 重新导入以应用环境变�?
        from importlib import reload

        import src.core.config

        reload(src.core.config)

        assert src.core.config.Config.WECHAT_CONTACT_NAME == "测试联系�?

    def test_validate_with_api_key(self) -> None:
        """测试配置验证（有API密钥�?""
        with patch.object(Config, "OPENAI_API_KEY", "test-key"):
            assert Config.validate() is True

    def test_validate_without_api_key(self) -> None:
        """测试配置验证（无API密钥�?""
        with patch.object(Config, "OPENAI_API_KEY", None):
            with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
                Config.validate()

