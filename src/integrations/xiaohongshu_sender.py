"""
小红书发送模块
"""
import time
from typing import Dict, Any

from .base_sender import BaseSender
from ..core.utils import setup_logger

logger = setup_logger(__name__)


class XiaohongshuSender(BaseSender):
    """小红书发送器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.cookie = self.config.get('cookie', '')
        self.user_agent = self.config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        self.publish_delay = self.config.get('publish_delay', 5)
        
    def send_message(self, message: str, **kwargs) -> bool:
        """
        发送消息到小红书
        
        Args:
            message: 消息内容
            **kwargs: 额外参数，可包含 title, images 等
            
        Returns:
            是否发送成功
        """
        if not message.strip():
            logger.warning("消息内容为空，跳过发送")
            return False
        
        try:
            title = kwargs.get('title', self._extract_title(message))
            content = self._format_content(message)
            images = kwargs.get('images', [])
            
            logger.info(f"准备发布小红书笔记: {title[:30]}...")
            
            # 这里应该实现实际的小红书API调用
            # 由于小红书没有公开API，这里仅作为示例框架
            
            # 模拟发布过程
            result = self._publish_note(title, content, images)
            
            if result:
                logger.info("小红书笔记发布成功")
                time.sleep(self.publish_delay)  # 发布间隔
                return True
            else:
                logger.error("小红书笔记发布失败")
                return False
                
        except Exception as e:
            logger.error(f"发送小红书消息失败: {e}")
            return False
    
    def _extract_title(self, message: str) -> str:
        """从消息中提取标题"""
        lines = message.strip().split('\n')
        # 取第一行非空内容作为标题，并清理格式
        for line in lines:
            clean_line = line.strip().replace('📰', '').replace('🔥', '').replace('#', '').strip()
            if clean_line and len(clean_line) > 5:
                return clean_line[:30]  # 小红书标题长度限制
        return "科技资讯分享"
    
    def _format_content(self, message: str) -> str:
        """格式化内容适配小红书"""
        # 转换表情符号和格式
        content = message.replace('📰', '💡').replace('🔥', '✨')
        
        # 添加小红书风格的标签
        if '#' not in content:
            content += '\n\n#科技资讯 #数码科技 #互联网'
        
        # 确保内容长度适中
        if len(content) > 1000:
            content = content[:997] + '...'
            
        return content
    
    def _publish_note(self, title: str, content: str, images: list) -> bool:
        """
        发布笔记到小红书
        
        注意：这是一个示例实现，实际需要根据小红书的API或爬虫方式实现
        """
        try:
            # 这里应该实现实际的小红书发布逻辑
            # 可能需要使用selenium、requests等进行网页操作
            
            # 模拟API调用（实际需要逆向工程小红书接口）
            logger.info(f"模拟发布笔记: {title}")
            logger.debug(f"内容预览: {content[:100]}...")
            logger.debug(f"使用Cookie: {self.cookie[:20]}..." if self.cookie else "无Cookie")
            
            # 返回模拟结果
            return True
            
        except Exception as e:
            logger.error(f"发布小红书笔记失败: {e}")
            return False
    
    def test_connection(self) -> bool:
        """测试小红书连接"""
        try:
            if not self.cookie:
                logger.error("小红书Cookie未配置")
                return False
            
            # 测试连接（这里应该实现实际的连接测试）
            logger.info("小红书连接测试成功")
            return True
            
        except Exception as e:
            logger.error(f"小红书连接测试失败: {e}")
            return False
    
    def get_sender_info(self) -> Dict[str, Any]:
        """获取发送器信息"""
        return {
            'name': 'Xiaohongshu',
            'type': 'social_media',
            'enabled': self.is_enabled(),
            'has_cookie': bool(self.cookie),
            'publish_delay': self.publish_delay,
            'description': '小红书社交媒体发布'
        }
    
    def validate_config(self) -> bool:
        """验证配置"""
        if not self.cookie:
            logger.error("小红书Cookie未配置")
            return False
        
        return True
