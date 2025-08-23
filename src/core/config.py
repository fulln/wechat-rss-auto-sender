"""
配置管理模块
"""
import os
from typing import Optional

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """应用配置类"""

    # 微信配置
    WECHAT_CONTACT_NAME: str = os.getenv("WECHAT_CONTACT_NAME", "文件传输助手")

    # RSS配置
    RSS_FEED_URL: str = os.getenv("RSS_FEED_URL", "https://36kr.com/feed")
    CHECK_INTERVAL_MINUTES: int = int(os.getenv("CHECK_INTERVAL_MINUTES", "30"))  # RSS检查间隔
    FETCH_ARTICLES_HOURS: int = int(os.getenv("FETCH_ARTICLES_HOURS", "6"))  # 文章获取时间范围（小时）
    
    # 代理配置
    HTTP_PROXY: Optional[str] = os.getenv("HTTP_PROXY")
    HTTPS_PROXY: Optional[str] = os.getenv("HTTPS_PROXY")
    PROXY_URL: Optional[str] = os.getenv("PROXY_URL")  # 统一代理地址，格式如: http://localhost:7897

    # AI总结配置
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    SUMMARY_MIN_LENGTH: int = int(
        os.getenv("SUMMARY_MIN_LENGTH", "150")
    )  # 增加到150字，支持更丰富的单篇文章总结
    SUMMARY_MAX_LENGTH: int = int(
        os.getenv("SUMMARY_MAX_LENGTH", "300")
    )  # 增加到300字，允许更深度的分析

    # 发送控制配置
    MAX_ARTICLES_PER_BATCH: int = int(
        os.getenv("MAX_ARTICLES_PER_BATCH", "3")
    )  # 每批最多发送文章数
    SEND_INTERVAL_MINUTES: int = int(
        os.getenv("SEND_INTERVAL_MINUTES", "1")
    )  # 发送间隔（分钟）
    MIN_QUALITY_SCORE: int = int(os.getenv("MIN_QUALITY_SCORE", "7"))  # 最低质量分数要求

    # 发送时间控制配置
    SEND_START_HOUR: int = int(os.getenv("SEND_START_HOUR", "9"))  # 允许发送开始时间（24小时制）
    SEND_END_HOUR: int = int(os.getenv("SEND_END_HOUR", "24"))  # 允许发送结束时间（24小时制）
    SEND_RANDOM_DELAY_MAX: int = int(
        os.getenv("SEND_RANDOM_DELAY_MAX", "15")
    )  # 随机延迟最大值（秒）

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")

    @classmethod
    def validate(cls) -> bool:
        """验证必要的配置项"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        return True

    @classmethod
    def get_proxies(cls) -> Optional[dict]:
        """获取代理配置"""
        proxies = None
        
        # 优先使用统一代理地址
        if cls.PROXY_URL:
            proxies = {
                'http': cls.PROXY_URL,
                'https': cls.PROXY_URL
            }
        # 其次使用分别配置的代理
        elif cls.HTTP_PROXY or cls.HTTPS_PROXY:
            proxies = {}
            if cls.HTTP_PROXY:
                proxies['http'] = cls.HTTP_PROXY
            if cls.HTTPS_PROXY:
                proxies['https'] = cls.HTTPS_PROXY
        
        return proxies
