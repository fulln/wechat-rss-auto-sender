"""
微信发送模块
"""
import time
from .utils import setup_logger
from .config import Config

logger = setup_logger(__name__)

class WeChatSender:
    """微信消息发送器"""
    
    def __init__(self, contact_name: str = None):
        self.contact_name = contact_name or Config.WECHAT_CONTACT_NAME
        self._wx_instance = None
        
    def _get_wechat_instance(self):
        """获取微信实例"""
        if self._wx_instance is None:
            try:
                import wxauto
                self._wx_instance = wxauto.WeChat()
                logger.info("微信实例初始化成功")
            except ImportError:
                logger.error("wxauto模块未安装，请运行: pip install wxauto")
                raise
            except Exception as e:
                logger.error(f"初始化微信实例失败: {e}")
                raise
        return self._wx_instance
    
    def send_message(self, message: str) -> bool:
        """
        发送微信消息
        
        Args:
            message: 要发送的消息内容
            
        Returns:
            是否发送成功
        """
        if not message.strip():
            logger.warning("消息内容为空，跳过发送")
            return False
            
        try:
            wx = self._get_wechat_instance()
            
            # 检查微信是否已登录
            if not self._check_wechat_login():
                logger.error("微信未登录，请先登录微信")
                return False
            
            # 发送消息
            logger.info(f"准备发送消息到: {self.contact_name}")
            logger.debug(f"消息内容: {message[:100]}...")
            
            # 分段发送长消息
            if len(message) > 1000:
                parts = self._split_message(message)
                for i, part in enumerate(parts):
                    wx.SendMsg(part, self.contact_name)
                    logger.info(f"发送消息段 {i+1}/{len(parts)}")
                    if i < len(parts) - 1:  # 不是最后一段时等待
                        time.sleep(1)
            else:
                wx.SendMsg(message, self.contact_name)
                
            logger.info("消息发送成功")
            return True
            
        except Exception as e:
            logger.error(f"发送微信消息失败: {e}")
            return False
    
    def _check_wechat_login(self) -> bool:
        """检查微信登录状态"""
        try:
            wx = self._get_wechat_instance()
            # 尝试获取联系人列表来检查登录状态
            wx.GetAllMessage()
            return True
        except Exception:
            return False
    
    def _split_message(self, message: str, max_length: int = 1000) -> list:
        """
        分割长消息
        
        Args:
            message: 原始消息
            max_length: 每段最大长度
            
        Returns:
            消息段落列表
        """
        if len(message) <= max_length:
            return [message]
        
        parts = []
        current_part = ""
        
        # 按行分割
        lines = message.split('\n')
        
        for line in lines:
            if len(current_part + line + '\n') <= max_length:
                current_part += line + '\n'
            else:
                if current_part:
                    parts.append(current_part.rstrip())
                current_part = line + '\n'
        
        if current_part:
            parts.append(current_part.rstrip())
        
        return parts
    
    def test_connection(self) -> bool:
        """测试微信连接"""
        try:
            self._get_wechat_instance()
            if self._check_wechat_login():
                logger.info("微信连接测试成功")
                return True
            else:
                logger.error("微信未登录")
                return False
        except Exception as e:
            logger.error(f"微信连接测试失败: {e}")
            return False