"""
WeChat RSS Auto Sender - 微信RSS自动推送服务

模块化架构:
- core: 核心配置和工具类
- services: 业务服务层
- integrations: 外部系统集成
- models: 数据模型 (预留)
"""

__version__ = "2.0.0"
__author__ = "WeChat RSS Auto Sender Team"
__email__ = "dev@example.com"

# 核心模块
from .core import Config, PromptTemplates, setup_logger

# 外部集成
from .integrations import WeChatSender

# 主程序入口
from .main import main

# 业务服务
from .services import (
    NewsScheduler,
    RSSCache,
    RSSFetcher,
    RSSItem,
    SendManager,
    Summarizer,
)

__all__ = [
    # Core
    "Config",
    "setup_logger",
    "PromptTemplates",
    # Services
    "RSSFetcher",
    "RSSItem",
    "RSSCache",
    "Summarizer",
    "SendManager",
    "NewsScheduler",
    # Integrations
    "WeChatSender",
    # Main
    "main",
]
