"""
发送器基类和抽象接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from ..core.utils import setup_logger

logger = setup_logger(__name__)


class BaseSender(ABC):
    """发送器基类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化发送器
        
        Args:
            config: 发送器配置参数
        """
        self.config = config or {}
        self.enabled = self.config.get('enabled', False)
        self.name = self.__class__.__name__
        
    @abstractmethod
    def send_message(self, message: str, **kwargs) -> bool:
        """
        发送消息
        
        Args:
            message: 要发送的消息内容
            **kwargs: 额外参数
            
        Returns:
            是否发送成功
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        测试连接
        
        Returns:
            连接是否正常
        """
        pass
    
    @abstractmethod
    def get_sender_info(self) -> Dict[str, Any]:
        """
        获取发送器信息
        
        Returns:
            发送器信息字典
        """
        pass
    
    def is_enabled(self) -> bool:
        """检查发送器是否启用"""
        return self.enabled
    
    def validate_config(self) -> bool:
        """
        验证配置是否正确
        
        Returns:
            配置是否有效
        """
        return True
    
    def setup(self) -> bool:
        """
        初始化设置
        
        Returns:
            设置是否成功
        """
        if not self.is_enabled():
            logger.info(f"{self.name} 发送器未启用")
            return False
            
        if not self.validate_config():
            logger.error(f"{self.name} 配置验证失败")
            return False
            
        logger.info(f"{self.name} 发送器初始化成功")
        return True


class SenderManager:
    """发送器管理器"""
    
    def __init__(self):
        self.senders: Dict[str, BaseSender] = {}
        self.enabled_senders: List[str] = []  # 存储发送器的注册名称而不是实例
        
    def register_sender(self, sender_name: str, sender: BaseSender):
        """
        注册发送器
        
        Args:
            sender_name: 发送器名称
            sender: 发送器实例
        """
        self.senders[sender_name] = sender
        
        if sender.setup() and sender.is_enabled():
            self.enabled_senders.append(sender_name)  # 存储注册名称
            logger.info(f"注册并启用发送器: {sender_name}")
        else:
            logger.info(f"注册发送器但未启用: {sender_name}")
    
    def send_to_all(self, message: str, **kwargs) -> Dict[str, bool]:
        """
        向所有启用的发送器发送消息
        
        Args:
            message: 消息内容
            **kwargs: 额外参数
            
        Returns:
            各发送器的发送结果
        """
        results = {}
        
        if not self.enabled_senders:
            logger.warning("没有启用的发送器")
            return results
        
        for sender_name in self.enabled_senders:
            sender = self.senders[sender_name]
            try:
                result = sender.send_message(message, **kwargs)
                results[sender_name] = result
                
                if result:
                    logger.info(f"{sender_name} 发送成功")
                else:
                    logger.error(f"{sender_name} 发送失败")
                    
            except Exception as e:
                logger.error(f"{sender_name} 发送异常: {e}")
                results[sender_name] = False
        
        return results
    
    def send_to_specific(self, sender_name: str, message: str, **kwargs) -> bool:
        """
        向特定发送器发送消息
        
        Args:
            sender_name: 发送器名称
            message: 消息内容
            **kwargs: 额外参数
            
        Returns:
            发送是否成功
        """
        if sender_name not in self.senders:
            logger.error(f"发送器 {sender_name} 不存在")
            return False
        
        sender = self.senders[sender_name]
        if not sender.is_enabled():
            logger.error(f"发送器 {sender_name} 未启用")
            return False
        
        return sender.send_message(message, **kwargs)
    
    def test_all_connections(self) -> Dict[str, bool]:
        """
        测试所有发送器连接
        
        Returns:
            各发送器的连接测试结果
        """
        results = {}
        
        for name, sender in self.senders.items():
            if sender.is_enabled():
                try:
                    results[name] = sender.test_connection()
                except Exception as e:
                    logger.error(f"{name} 连接测试异常: {e}")
                    results[name] = False
            else:
                results[name] = False
        
        return results
    
    def get_enabled_senders(self) -> List[str]:
        """获取已启用的发送器名称列表"""
        return self.enabled_senders
    
    def get_sender_info(self) -> Dict[str, Dict[str, Any]]:
        """获取所有发送器信息"""
        info = {}
        for name, sender in self.senders.items():
            info[name] = sender.get_sender_info()
        return info
