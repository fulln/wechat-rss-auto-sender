"""
多RSS源管理器
支持配置和管理多个RSS源，提供统一的文章获取接口
"""
from datetime import datetime
from typing import List, Dict, Optional, Set
from concurrent.futures import ThreadPoolExecutor
import threading

from ..core.config import Config
from ..core.utils import setup_logger
from .rss_service import RSSFetcher, RSSItem

logger = setup_logger(__name__)


class RSSSource:
    """RSS源配置类"""
    
    def __init__(self, url: str, name: str = None, priority: int = 1, enabled: bool = True):
        self.url = url
        self.name = name or self._extract_domain_name(url)
        self.priority = priority  # 优先级，数字越小优先级越高
        self.enabled = enabled
        self.last_fetch_time: Optional[datetime] = None
        self.last_error: Optional[str] = None
        self.success_count = 0
        self.error_count = 0
        
    def _extract_domain_name(self, url: str) -> str:
        """从URL提取域名作为名称"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            # 移除www前缀
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return "unknown"
    
    def mark_success(self):
        """标记成功获取"""
        self.success_count += 1
        self.last_fetch_time = datetime.now()
        self.last_error = None
    
    def mark_error(self, error: str):
        """标记获取错误"""
        self.error_count += 1
        self.last_error = error
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        total = self.success_count + self.error_count
        if total == 0:
            return 1.0
        return self.success_count / total
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'url': self.url,
            'name': self.name,
            'priority': self.priority,
            'enabled': self.enabled,
            'last_fetch_time': self.last_fetch_time.isoformat() if self.last_fetch_time else None,
            'last_error': self.last_error,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'success_rate': self.get_success_rate()
        }


class MultiRSSManager:
    """多RSS源管理器"""
    
    def __init__(self):
        self.sources: List[RSSSource] = []
        self.fetchers: Dict[str, RSSFetcher] = {}
        self._load_sources()
        self._lock = threading.Lock()
    
    def _load_sources(self):
        """从配置加载RSS源"""
        urls = Config.get_rss_feed_urls()
        
        if not urls:
            logger.warning("没有配置RSS源")
            return
        
        for i, url in enumerate(urls):
            source = RSSSource(
                url=url,
                priority=i + 1,  # 配置顺序决定优先级
                enabled=True
            )
            self.sources.append(source)
            self.fetchers[url] = RSSFetcher(url)
        
        logger.info(f"加载了 {len(self.sources)} 个RSS源")
        for source in self.sources:
            logger.info(f"  - {source.name}: {source.url}")
    
    @property
    def rss_sources(self) -> List[RSSSource]:
        """获取所有RSS源列表"""
        return self.sources.copy()
    
    @property
    def cache(self):
        """获取缓存对象（使用第一个fetcher的缓存）"""
        if self.fetchers:
            return next(iter(self.fetchers.values())).cache
        return None
    
    def add_source(self, url: str, name: str = None, priority: int = None) -> bool:
        """
        添加新的RSS源
        
        Args:
            url: RSS源URL
            name: 源名称（可选）
            priority: 优先级（可选）
            
        Returns:
            是否添加成功
        """
        # 检查是否已存在
        if any(source.url == url for source in self.sources):
            logger.warning(f"RSS源已存在: {url}")
            return False
        
        if priority is None:
            priority = len(self.sources) + 1
        
        source = RSSSource(url=url, name=name, priority=priority)
        self.sources.append(source)
        self.fetchers[url] = RSSFetcher(url)
        
        logger.info(f"添加RSS源: {source.name} ({url})")
        return True
    
    def remove_source(self, url: str) -> bool:
        """
        移除RSS源
        
        Args:
            url: RSS源URL
            
        Returns:
            是否移除成功
        """
        for i, source in enumerate(self.sources):
            if source.url == url:
                del self.sources[i]
                if url in self.fetchers:
                    del self.fetchers[url]
                logger.info(f"移除RSS源: {source.name} ({url})")
                return True
        
        logger.warning(f"RSS源不存在: {url}")
        return False
    
    def enable_source(self, url: str) -> bool:
        """启用RSS源"""
        for source in self.sources:
            if source.url == url:
                source.enabled = True
                logger.info(f"启用RSS源: {source.name}")
                return True
        return False
    
    def disable_source(self, url: str) -> bool:
        """禁用RSS源"""
        for source in self.sources:
            if source.url == url:
                source.enabled = False
                logger.info(f"禁用RSS源: {source.name}")
                return True
        return False
    
    def get_enabled_sources(self) -> List[RSSSource]:
        """获取启用的RSS源"""
        return [source for source in self.sources if source.enabled]
    
    def fetch_from_source(self, source: RSSSource, since_minutes: int = None) -> List[RSSItem]:
        """
        从单个RSS源获取文章
        
        Args:
            source: RSS源
            since_minutes: 获取多少分钟内的文章
            
        Returns:
            文章列表
        """
        if not source.enabled:
            return []
        
        try:
            fetcher = self.fetchers[source.url]
            items = fetcher.fetch_latest_items(since_minutes=since_minutes, enable_dedup=True)
            
            # 给文章添加源信息
            for item in items:
                item.source_name = source.name
                item.source_url = source.url
            
            source.mark_success()
            logger.info(f"从 {source.name} 获取到 {len(items)} 篇文章")
            return items
            
        except Exception as e:
            error_msg = str(e)
            source.mark_error(error_msg)
            logger.error(f"从 {source.name} 获取文章失败: {error_msg}")
            return []
    
    def fetch_latest_items(self, since_minutes: int = None, max_workers: int = 3) -> List[RSSItem]:
        """
        从所有启用的RSS源并发获取最新文章
        
        Args:
            since_minutes: 获取多少分钟内的文章
            max_workers: 最大并发工作线程数
            
        Returns:
            去重后的文章列表，按时间倒序排列
        """
        enabled_sources = self.get_enabled_sources()
        
        if not enabled_sources:
            logger.warning("没有启用的RSS源")
            return []
        
        logger.info(f"开始从 {len(enabled_sources)} 个RSS源获取文章")
        
        all_items = []
        
        # 使用线程池并发获取
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有获取任务
            future_to_source = {
                executor.submit(self.fetch_from_source, source, since_minutes): source 
                for source in enabled_sources
            }
            
            # 收集结果
            for future in future_to_source:
                source = future_to_source[future]
                try:
                    items = future.result(timeout=60)  # 60秒超时
                    all_items.extend(items)
                except Exception as e:
                    logger.error(f"从 {source.name} 获取文章超时或失败: {e}")
                    source.mark_error(str(e))
        
        # 去重处理
        unique_items = self._deduplicate_items(all_items)
        
        # 按发布时间倒序排列
        unique_items.sort(key=lambda x: x.published, reverse=True)
        
        logger.info(f"总共获取 {len(all_items)} 篇文章，去重后 {len(unique_items)} 篇")
        
        return unique_items
    
    def _deduplicate_items(self, items: List[RSSItem]) -> List[RSSItem]:
        """
        文章去重
        
        Args:
            items: 文章列表
            
        Returns:
            去重后的文章列表
        """
        seen_titles: Set[str] = set()
        seen_links: Set[str] = set()
        unique_items = []
        
        for item in items:
            # 基于标题和链接去重
            title_key = item.title.lower().strip()
            link_key = item.link.lower().strip()
            
            if title_key not in seen_titles and link_key not in seen_links:
                seen_titles.add(title_key)
                seen_links.add(link_key)
                unique_items.append(item)
            else:
                logger.debug(f"跳过重复文章: {item.title}")
        
        return unique_items
    
    def get_source_stats(self) -> List[Dict]:
        """获取所有RSS源的统计信息"""
        stats = []
        for source in self.sources:
            stats.append(source.to_dict())
        
        # 按优先级排序
        stats.sort(key=lambda x: x['priority'])
        return stats
    
    def get_feed_info(self) -> Dict:
        """获取所有RSS源的基本信息"""
        enabled_sources = self.get_enabled_sources()
        
        total_sources = len(self.sources)
        enabled_count = len(enabled_sources)
        
        # 获取第一个启用源的信息作为示例
        sample_info = {}
        if enabled_sources:
            try:
                first_source = enabled_sources[0]
                fetcher = self.fetchers[first_source.url]
                sample_info = fetcher.get_feed_info()
            except Exception as e:
                logger.error(f"获取示例RSS信息失败: {e}")
        
        return {
            'total_sources': total_sources,
            'enabled_sources': enabled_count,
            'source_names': [source.name for source in enabled_sources],
            'sample_feed_info': sample_info
        }
    
    def test_all_sources(self) -> Dict[str, bool]:
        """
        测试所有RSS源的连接
        
        Returns:
            每个源的测试结果
        """
        results = {}
        
        for source in self.sources:
            if not source.enabled:
                results[source.name] = False
                continue
            
            try:
                fetcher = self.fetchers[source.url]
                # 尝试获取feed信息来测试连接
                info = fetcher.get_feed_info()
                results[source.name] = bool(info)
                if info:
                    logger.info(f"RSS源连接正常: {source.name} - {info.get('title', 'Unknown')}")
                else:
                    logger.warning(f"RSS源连接异常: {source.name}")
            except Exception as e:
                results[source.name] = False
                logger.error(f"RSS源连接失败: {source.name} - {e}")
        
        return results
