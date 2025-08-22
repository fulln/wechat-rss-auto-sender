"""配置模块的单元测试"""

import os
import pytest
from unittest.mock import patch

from src.config import Config


class TestConfig:
    """配置类测试"""

    def test_default_values(self) -> None:
        """测试默认配置值"""
        assert Config.WECHAT_CONTACT_NAME == "文件传输助手"
        assert Config.RSS_FEED_URL == "https://36kr.com/feed"
        assert Config.CHECK_INTERVAL_MINUTES == 5
        assert Config.SUMMARY_MIN_LENGTH == 100
        assert Config.SUMMARY_MAX_LENGTH == 200
        assert Config.LOG_LEVEL == "INFO"

    @patch.dict(os.environ, {"WECHAT_CONTACT_NAME": "测试联系人"})
    def test_environment_override(self) -> None:
        """测试环境变量覆盖"""
        # 重新导入以应用环境变量
        from importlib import reload
        import src.config
        reload(src.config)
        
        assert src.config.Config.WECHAT_CONTACT_NAME == "测试联系人"

    def test_validate_with_api_key(self) -> None:
        """测试配置验证（有API密钥）"""
        with patch.object(Config, 'OPENAI_API_KEY', 'test-key'):
            assert Config.validate() is True

    def test_validate_without_api_key(self) -> None:
        """测试配置验证（无API密钥）"""
        with patch.object(Config, 'OPENAI_API_KEY', None):
            with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
                Config.validate()
