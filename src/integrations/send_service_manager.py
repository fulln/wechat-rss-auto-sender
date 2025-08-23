"""
发送服务管理器
"""
from typing import Dict, Any, List

from .base_sender import SenderManager
from .wechat_client import WeChatSender
from .xiaohongshu_sender import XiaohongshuSender
from .wechat_official_sender import WeChatOfficialSender
from ..core.config import Config
from ..core.utils import setup_logger

logger = setup_logger(__name__)


class SendServiceManager:
    """发送服务管理器"""
    
    def __init__(self):
        self.sender_manager = SenderManager()
        self._initialize_senders()
    
    def _initialize_senders(self):
        """初始化所有发送器"""
        sender_configs = Config.get_sender_configs()
        enabled_senders = Config.get_enabled_senders()
        
        # 注册微信发送器
        if 'wechat' in enabled_senders and sender_configs['wechat']['enabled']:
            wechat_sender = WeChatSender(sender_configs['wechat'])
            self.sender_manager.register_sender('wechat', wechat_sender)
        
        # 注册小红书发送器
        if 'xiaohongshu' in enabled_senders and sender_configs['xiaohongshu']['enabled']:
            xiaohongshu_sender = XiaohongshuSender(sender_configs['xiaohongshu'])
            self.sender_manager.register_sender('xiaohongshu', xiaohongshu_sender)
        
        # 注册微信公众号发送器
        if 'wechat_official' in enabled_senders and sender_configs['wechat_official']['enabled']:
            official_sender = WeChatOfficialSender(sender_configs['wechat_official'])
            self.sender_manager.register_sender('wechat_official', official_sender)
        
        enabled_list = self.sender_manager.get_enabled_senders()
        logger.info(f"已启用发送器: {', '.join(enabled_list) if enabled_list else '无'}")
    
    def send_message(self, message: str, **kwargs) -> Dict[str, bool]:
        """
        发送消息到所有启用的发送器
        
        Args:
            message: 消息内容
            **kwargs: 额外参数
            
        Returns:
            各发送器的发送结果
        """
        return self.sender_manager.send_to_all(message, **kwargs)
    
    def send_to_specific(self, sender_name: str, message: str, **kwargs) -> bool:
        """
        发送消息到特定发送器
        
        Args:
            sender_name: 发送器名称
            message: 消息内容
            **kwargs: 额外参数
            
        Returns:
            发送是否成功
        """
        return self.sender_manager.send_to_specific(sender_name, message, **kwargs)
    
    def test_all_connections(self) -> Dict[str, bool]:
        """测试所有发送器连接"""
        return self.sender_manager.test_all_connections()
    
    def get_enabled_senders(self) -> List[str]:
        """获取已启用的发送器列表"""
        return self.sender_manager.get_enabled_senders()
    
    def get_sender_info(self) -> Dict[str, Dict[str, Any]]:
        """获取所有发送器信息"""
        return self.sender_manager.get_sender_info()
    
    def has_enabled_senders(self) -> bool:
        """检查是否有启用的发送器"""
        return len(self.sender_manager.enabled_senders) > 0
