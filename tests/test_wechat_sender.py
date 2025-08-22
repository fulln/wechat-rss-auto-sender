"""微信发送器的单元测�?""

from unittest.mock import Mock, patch

from src.integrations.wechat_client import WeChatSender


class TestWeChatSender:
    """微信发送器测试"""

    @patch("src.integrations.wechat_client.wxauto")
    def test_send_message_success(self, mock_wxauto: Mock) -> None:
        """测试成功发送消�?""
        # 模拟wxauto
        mock_wx = Mock()
        mock_wx.GetAllMessage.return_value = []  # 模拟登录状�?
        mock_wxauto.WeChat.return_value = mock_wx

        sender = WeChatSender("测试联系�?)
        result = sender.send_message("测试消息")

        assert result is True
        mock_wx.SendMsg.assert_called_once_with("测试消息", "测试联系�?)

    @patch("src.integrations.wechat_client.wxauto")
    def test_send_empty_message(self, mock_wxauto: Mock) -> None:
        """测试发送空消息"""
        sender = WeChatSender()
        result = sender.send_message("")

        assert result is False

    @patch("src.integrations.wechat_client.wxauto")
    def test_send_long_message(self, mock_wxauto: Mock) -> None:
        """测试发送长消息（分段）"""
        mock_wx = Mock()
        mock_wx.GetAllMessage.return_value = []
        mock_wxauto.WeChat.return_value = mock_wx

        # 创建超过1000字符的长消息
        long_message = "测试" * 300  # 1200字符

        sender = WeChatSender()
        result = sender.send_message(long_message)

        assert result is True
        # 应该调用多次SendMsg（分段发送）
        assert mock_wx.SendMsg.call_count > 1

    @patch("src.integrations.wechat_client.wxauto")
    def test_wechat_not_logged_in(self, mock_wxauto: Mock) -> None:
        """测试微信未登录情�?""
        mock_wx = Mock()
        mock_wx.GetAllMessage.side_effect = Exception("未登�?)
        mock_wxauto.WeChat.return_value = mock_wx

        sender = WeChatSender()
        result = sender.send_message("测试消息")

        assert result is False

    def test_split_message(self) -> None:
        """测试消息分割功能"""
        sender = WeChatSender()

        # 测试短消�?
        short_msg = "短消�?
        parts = sender._split_message(short_msg, 100)
        assert len(parts) == 1
        assert parts[0] == "短消�?

        # 测试长消�?
        long_msg = "�?\n�?\n�?\n" * 100  # 创建长消�?
        parts = sender._split_message(long_msg, 50)
        assert len(parts) > 1

        # 验证分割后的消息不超过限�?
        for part in parts:
            assert len(part) <= 50

    @patch("src.integrations.wechat_client.wxauto")
    def test_test_connection_success(self, mock_wxauto: Mock) -> None:
        """测试连接测试成功"""
        mock_wx = Mock()
        mock_wx.GetAllMessage.return_value = []
        mock_wxauto.WeChat.return_value = mock_wx

        sender = WeChatSender()
        result = sender.test_connection()

        assert result is True

    @patch("src.integrations.wechat_client.wxauto")
    def test_test_connection_failure(self, mock_wxauto: Mock) -> None:
        """测试连接测试失败"""
        mock_wxauto.WeChat.side_effect = Exception("连接失败")

        sender = WeChatSender()
        result = sender.test_connection()

        assert result is False

