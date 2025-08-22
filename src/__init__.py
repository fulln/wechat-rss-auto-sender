"""
微信RSS新闻自动推送服务

一个自动获取RSS新闻并通过微信发送AI总结的Python服务。
"""

__version__ = "0.1.0"
__author__ = "Developer"
__email__ = "dev@example.com"

from .main import main
from .config import Config
from .rss_fetcher import RSSFetcher, RSSItem
from .summarizer import Summarizer
from .wechat_sender import WeChatSender
from .scheduler import NewsScheduler
from .send_manager import SendManager

__all__ = [
    "main",
    "Config", 
    "RSSFetcher",
    "RSSItem",
    "Summarizer",
    "WeChatSender", 
    "NewsScheduler",
    "SendManager"
]
