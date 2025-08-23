"""
配置管理模块
"""
import os
from typing import Optional, List

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """应用配置类"""

    # 微信配置
    WECHAT_CONTACT_NAME: str = os.getenv("WECHAT_CONTACT_NAME", "文件传输助手")

    # RSS配置
    RSS_FEED_URLS: str = os.getenv("RSS_FEED_URLS", "")  # 多RSS源，用分号分隔
    CHECK_INTERVAL_MINUTES: int = int(os.getenv("CHECK_INTERVAL_MINUTES", "30"))  # RSS检查间隔
    FETCH_ARTICLES_HOURS: int = int(os.getenv("FETCH_ARTICLES_HOURS", "6"))  # 文章获取时间范围（小时）
    
    # 图片配置
    PREFERRED_IMAGE_WIDTH: int = int(os.getenv("PREFERRED_IMAGE_WIDTH", "460"))  # 首选图片宽度
    MIN_IMAGE_WIDTH: int = int(os.getenv("MIN_IMAGE_WIDTH", "140"))  # 最小图片宽度
    MAX_IMAGE_WIDTH: int = int(os.getenv("MAX_IMAGE_WIDTH", "700"))  # 最大图片宽度
    
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

    # 发送器配置
    ENABLED_SENDERS: str = os.getenv("ENABLED_SENDERS", "wechat")  # 启用的发送器，逗号分隔
    
    # 微信发送器配置
    WECHAT_SENDER_ENABLED: bool = os.getenv("WECHAT_SENDER_ENABLED", "true").lower() == "true"
    
    # 小红书发送器配置
    XIAOHONGSHU_SENDER_ENABLED: bool = os.getenv("XIAOHONGSHU_SENDER_ENABLED", "false").lower() == "true"
    XIAOHONGSHU_COOKIE: Optional[str] = os.getenv("XIAOHONGSHU_COOKIE")
    XIAOHONGSHU_USER_AGENT: str = os.getenv("XIAOHONGSHU_USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    XIAOHONGSHU_PUBLISH_DELAY: int = int(os.getenv("XIAOHONGSHU_PUBLISH_DELAY", "5"))
    
    # 微信公众号发送器配置
    WECHAT_OFFICIAL_SENDER_ENABLED: bool = os.getenv("WECHAT_OFFICIAL_SENDER_ENABLED", "false").lower() == "true"
    WECHAT_OFFICIAL_APP_ID: Optional[str] = os.getenv("WECHAT_OFFICIAL_APP_ID")
    WECHAT_OFFICIAL_APP_SECRET: Optional[str] = os.getenv("WECHAT_OFFICIAL_APP_SECRET")
    WECHAT_OFFICIAL_USE_RICH_FORMATTING: bool = os.getenv("WECHAT_OFFICIAL_USE_RICH_FORMATTING", "true").lower() == "true"
    WECHAT_OFFICIAL_FOOTER_TEXT: str = os.getenv("WECHAT_OFFICIAL_FOOTER_TEXT", "📱 更多科技资讯，请关注我们")
    WECHAT_OFFICIAL_AUTHOR_NAME: str = os.getenv("WECHAT_OFFICIAL_AUTHOR_NAME", "RSS助手")

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

    @classmethod
    def get_rss_feed_urls(cls) -> List[str]:
        """获取所有RSS源URL列表"""
        urls = []
        
        # 解析多RSS源配置
        if cls.RSS_FEED_URLS:
            # 支持分号或逗号分隔
            separator = ';' if ';' in cls.RSS_FEED_URLS else ','
            urls = [url.strip() for url in cls.RSS_FEED_URLS.split(separator) if url.strip()]
        
        return urls

    @classmethod
    def get_sender_configs(cls) -> dict:
        """获取所有发送器配置"""
        return {
            'wechat': {
                'enabled': cls.WECHAT_SENDER_ENABLED,
                'contact_name': cls.WECHAT_CONTACT_NAME
            },
            'xiaohongshu': {
                'enabled': cls.XIAOHONGSHU_SENDER_ENABLED,
                'cookie': cls.XIAOHONGSHU_COOKIE,
                'user_agent': cls.XIAOHONGSHU_USER_AGENT,
                'publish_delay': cls.XIAOHONGSHU_PUBLISH_DELAY
            },
            'wechat_official': {
                'enabled': cls.WECHAT_OFFICIAL_SENDER_ENABLED,
                'app_id': cls.WECHAT_OFFICIAL_APP_ID,
                'app_secret': cls.WECHAT_OFFICIAL_APP_SECRET,
                'use_rich_formatting': cls.WECHAT_OFFICIAL_USE_RICH_FORMATTING,
                'footer_text': cls.WECHAT_OFFICIAL_FOOTER_TEXT,
                'author_name': cls.WECHAT_OFFICIAL_AUTHOR_NAME
            }
        }
    
    @classmethod
    def get_enabled_senders(cls) -> list:
        """获取启用的发送器列表"""
        enabled = cls.ENABLED_SENDERS.strip()
        if not enabled:
            return []
        return [sender.strip() for sender in enabled.split(',')]
