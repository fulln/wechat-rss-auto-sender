"""
RSS获取模块
"""
import feedparser
import requests
import json
import hashlib
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
from pathlib import Path
from .utils import setup_logger
from .config import Config

logger = setup_logger(__name__)

class RSSItem:
    """RSS条目数据类"""
    
    def __init__(self, title: str, link: str, description: str, published: datetime):
        self.title = title
        self.link = link
        self.description = description
        self.published = published
        self.title_hash = self._generate_title_hash(title)
        self.date_key = published.strftime('%Y-%m-%d')
        self.sent_status = False  # 是否已发送
        self.sent_time: Optional[datetime] = None  # 发送时间
        self.quality_score: Optional[int] = None  # AI质量评分（0-10分）
        self.scored_time: Optional[datetime] = None  # 评分时间
    
    def _generate_title_hash(self, title: str) -> str:
        """生成标题的唯一标识符"""
        # 清理标题，去除多余空格和特殊字符
        cleaned_title = ' '.join(title.strip().split())
        return hashlib.md5(cleaned_title.encode('utf-8')).hexdigest()[:16]
    
    def mark_as_sent(self) -> None:
        """标记为已发送"""
        self.sent_status = True
        self.sent_time = datetime.now()
    
    def set_quality_score(self, score: int) -> None:
        """设置质量评分"""
        self.quality_score = max(0, min(10, score))  # 确保分数在0-10范围内
        self.scored_time = datetime.now()
    
    def __str__(self):
        return f"{self.title} - {self.link}"
    
    def to_dict(self) -> dict:
        """转换为字典格式用于序列化"""
        return {
            'title': self.title,
            'link': self.link,
            'description': self.description,
            'published': self.published.isoformat(),
            'title_hash': self.title_hash,
            'date_key': self.date_key,
            'sent_status': self.sent_status,
            'sent_time': self.sent_time.isoformat() if self.sent_time else None,
            'quality_score': self.quality_score,
            'scored_time': self.scored_time.isoformat() if self.scored_time else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'RSSItem':
        """从字典创建RSS条目"""
        item = cls(
            title=data['title'],
            link=data['link'],
            description=data['description'],
            published=datetime.fromisoformat(data['published'])
        )
        item.sent_status = data.get('sent_status', False)
        if data.get('sent_time'):
            item.sent_time = datetime.fromisoformat(data['sent_time'])
        item.quality_score = data.get('quality_score')
        if data.get('scored_time'):
            item.scored_time = datetime.fromisoformat(data['scored_time'])
        return item

class RSSCache:
    """RSS缓存管理器"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.daily_cache: Dict[str, Set[str]] = {}  # date -> set of title_hashes
        self.article_details: Dict[str, Dict[str, RSSItem]] = {}  # date -> hash -> RSSItem
        self._load_cache()
    
    def _get_cache_file(self, date_key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"rss_{date_key}.json"
    
    def _load_cache(self):
        """加载缓存数据"""
        # 加载今天和昨天的缓存
        for days_back in [0, 1]:
            date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            cache_file = self._get_cache_file(date)
            
            if cache_file.exists():
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # 加载基本缓存信息
                        self.daily_cache[date] = set(data.get('title_hashes', []))
                        
                        # 加载文章详细信息
                        self.article_details[date] = {}
                        for item_data in data.get('articles', []):
                            item = RSSItem.from_dict(item_data)
                            self.article_details[date][item.title_hash] = item
                        
                        logger.debug(f"加载缓存 {date}: {len(self.daily_cache[date])} 条记录")
                except Exception as e:
                    logger.error(f"加载缓存文件失败 {cache_file}: {e}")
                    self.daily_cache[date] = set()
                    self.article_details[date] = {}
            else:
                self.daily_cache[date] = set()
                self.article_details[date] = {}
    
    def _save_cache(self, date_key: str):
        """保存缓存数据"""
        if date_key not in self.daily_cache:
            return
            
        cache_file = self._get_cache_file(date_key)
        try:
            # 收集文章详细信息
            articles = []
            if date_key in self.article_details:
                for item in self.article_details[date_key].values():
                    articles.append(item.to_dict())
            
            data = {
                'date': date_key,
                'title_hashes': list(self.daily_cache[date_key]),
                'articles': articles,
                'updated_at': datetime.now().isoformat()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            logger.debug(f"保存缓存 {date_key}: {len(self.daily_cache[date_key])} 条记录")
        except Exception as e:
            logger.error(f"保存缓存文件失败 {cache_file}: {e}")
    
    def is_duplicate(self, item: RSSItem) -> bool:
        """检查文章是否重复"""
        return item.title_hash in self.daily_cache.get(item.date_key, set())
    
    def add_item(self, item: RSSItem):
        """添加文章到缓存"""
        if item.date_key not in self.daily_cache:
            self.daily_cache[item.date_key] = set()
            self.article_details[item.date_key] = {}
        
        self.daily_cache[item.date_key].add(item.title_hash)
        self.article_details[item.date_key][item.title_hash] = item
        self._save_cache(item.date_key)
    
    def update_item_sent_status(self, item: RSSItem):
        """更新文章发送状态"""
        if (item.date_key in self.article_details and 
            item.title_hash in self.article_details[item.date_key]):
            
            self.article_details[item.date_key][item.title_hash].sent_status = item.sent_status
            self.article_details[item.date_key][item.title_hash].sent_time = item.sent_time
            self._save_cache(item.date_key)
    
    def get_unsent_items(self, date_key: str = None) -> List[RSSItem]:
        """获取未发送的文章"""
        unsent_items = []
        
        if date_key:
            # 获取指定日期的未发送文章
            if date_key in self.article_details:
                for item in self.article_details[date_key].values():
                    if not item.sent_status:
                        unsent_items.append(item)
        else:
            # 获取所有日期的未发送文章
            for date_articles in self.article_details.values():
                for item in date_articles.values():
                    if not item.sent_status:
                        unsent_items.append(item)
        
        # 按发布时间排序（最新的在前）
        unsent_items.sort(key=lambda x: x.published, reverse=True)
        return unsent_items
    
    def cleanup_old_cache(self, keep_days: int = 7):
        """清理旧的缓存文件"""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        for cache_file in self.cache_dir.glob("rss_*.json"):
            try:
                # 从文件名提取日期
                date_str = cache_file.stem.replace('rss_', '')
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                if file_date < cutoff_date:
                    cache_file.unlink()
                    logger.info(f"删除旧缓存文件: {cache_file}")
                    
                    # 从内存中移除
                    if date_str in self.daily_cache:
                        del self.daily_cache[date_str]
                        
            except Exception as e:
                logger.error(f"清理缓存文件失败 {cache_file}: {e}")

class RSSFetcher:
    """RSS获取器"""
    
    def __init__(self, feed_url: str = None):
        self.feed_url = feed_url or Config.RSS_FEED_URL
        self.last_check_time: Optional[datetime] = None
        self.cache = RSSCache()
        
    def fetch_latest_items(self, since_minutes: int = None, enable_dedup: bool = True) -> List[RSSItem]:
        """
        获取最新的RSS条目
        
        Args:
            since_minutes: 获取多少分钟内的文章，默认为配置的检查间隔
            enable_dedup: 是否启用去重功能
            
        Returns:
            RSS条目列表
        """
        try:
            logger.info(f"开始获取RSS数据: {self.feed_url}")
            
            # 获取RSS数据
            response = requests.get(self.feed_url, timeout=30)
            response.raise_for_status()
            
            # 解析RSS
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                logger.warning(f"RSS解析警告: {feed.bozo_exception}")
            
            # 计算时间范围
            since_minutes = since_minutes or Config.CHECK_INTERVAL_MINUTES
            cutoff_time = datetime.now() - timedelta(minutes=since_minutes)
            
            items = []
            duplicate_count = 0
            
            for entry in feed.entries:
                try:
                    # 解析发布时间
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published = datetime(*entry.updated_parsed[:6])
                    else:
                        published = datetime.now()
                    
                    # 只获取指定时间范围内的文章
                    if published >= cutoff_time:
                        item = RSSItem(
                            title=entry.get('title', '无标题'),
                            link=entry.get('link', ''),
                            description=entry.get('description', ''),
                            published=published
                        )
                        
                        # 检查是否重复
                        if enable_dedup and self.cache.is_duplicate(item):
                            duplicate_count += 1
                            logger.debug(f"跳过重复文章: {item.title}")
                            continue
                        
                        items.append(item)
                        
                        # 添加到缓存
                        if enable_dedup:
                            self.cache.add_item(item)
                        
                except Exception as e:
                    logger.error(f"解析RSS条目时出错: {e}")
                    continue
            
            # 清理旧缓存
            if enable_dedup:
                self.cache.cleanup_old_cache()
            
            logger.info(f"成功获取 {len(items)} 条最新文章")
            if duplicate_count > 0:
                logger.info(f"跳过 {duplicate_count} 条重复文章")
                
            return items
            
        except requests.RequestException as e:
            logger.error(f"获取RSS数据失败: {e}")
            return []
        except Exception as e:
            logger.error(f"RSS解析失败: {e}")
            return []
    
    def get_feed_info(self) -> Dict[str, str]:
        """获取RSS源信息"""
        try:
            response = requests.get(self.feed_url, timeout=30)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            
            return {
                'title': feed.feed.get('title', '未知源'),
                'description': feed.feed.get('description', ''),
                'link': feed.feed.get('link', ''),
                'last_updated': feed.feed.get('updated', '')
            }
        except Exception as e:
            logger.error(f"获取RSS源信息失败: {e}")
            return {}
    
    def get_cache_status(self) -> Dict[str, any]:
        """获取缓存状态"""
        status = {
            'cache_dir': str(self.cache.cache_dir),
            'daily_stats': {}
        }
        
        for date_key, title_hashes in self.cache.daily_cache.items():
            status['daily_stats'][date_key] = len(title_hashes)
        
        # 统计缓存文件
        cache_files = list(self.cache.cache_dir.glob("rss_*.json"))
        status['cache_files_count'] = len(cache_files)
        status['total_cached_items'] = sum(status['daily_stats'].values())
        
        return status
    
    def clear_cache(self, date_key: str = None):
        """清理缓存"""
        if date_key:
            # 清理指定日期的缓存
            if date_key in self.cache.daily_cache:
                del self.cache.daily_cache[date_key]
            
            cache_file = self.cache._get_cache_file(date_key)
            if cache_file.exists():
                cache_file.unlink()
                logger.info(f"清理缓存: {date_key}")
        else:
            # 清理所有缓存
            self.cache.daily_cache.clear()
            for cache_file in self.cache.cache_dir.glob("rss_*.json"):
                cache_file.unlink()
            logger.info("清理所有缓存")