"""
图片下载器模块
"""
import os
import re
import hashlib
import requests
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, urljoin

from ..core.config import Config
from ..core.utils import setup_logger

logger = setup_logger(__name__)


class ImageDownloader:
    """图片下载器"""
    
    def __init__(self, download_dir: str = "images"):
        """
        初始化图片下载器
        
        Args:
            download_dir: 图片下载目录
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        # 支持的图片格式
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        
        # 最大文件大小 (5MB)
        self.max_file_size = 5 * 1024 * 1024
        
        # 请求超时时间
        self.timeout = 10
    
    def extract_image_from_content(self, content: str, base_url: str = None) -> Optional[str]:
        """
        从内容中提取图片URL
        
        Args:
            content: 文章内容
            base_url: 基础URL，用于处理相对路径
            
        Returns:
            图片URL或None
        """
        if not content:
            return None
        
        # 匹配img标签中的src
        img_patterns = [
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',  # img标签
            r'<image[^>]+src=["\']([^"\']+)["\'][^>]*>',  # image标签
            r'!\[.*?\]\(([^)]+)\)',  # Markdown格式图片
        ]
        
        for pattern in img_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # 处理相对路径
                if base_url and not match.startswith(('http://', 'https://')):
                    image_url = urljoin(base_url, match)
                else:
                    image_url = match
                
                # 检查是否是支持的图片格式
                if self._is_valid_image_url(image_url):
                    logger.debug(f"从内容中提取到图片: {image_url}")
                    return image_url
        
        return None
    
    def extract_image_from_rss_entry(self, entry) -> Optional[str]:
        """
        从RSS条目中提取图片URL
        
        Args:
            entry: RSS条目对象
            
        Returns:
            图片URL或None
        """
        # 尝试从不同字段获取图片
        image_candidates = []
        
        # 1. 从enclosure中获取
        if hasattr(entry, 'enclosures'):
            for enclosure in entry.enclosures:
                if hasattr(enclosure, 'type') and enclosure.type.startswith('image/'):
                    image_candidates.append(enclosure.href)
                elif hasattr(enclosure, 'href') and self._is_valid_image_url(enclosure.href):
                    image_candidates.append(enclosure.href)
        
        # 2. 从media_content中获取
        if hasattr(entry, 'media_content'):
            for media in entry.media_content:
                if hasattr(media, 'type') and media.type.startswith('image/'):
                    image_candidates.append(media['url'])
        
        # 3. 从media_thumbnail中获取
        if hasattr(entry, 'media_thumbnail'):
            for thumb in entry.media_thumbnail:
                if hasattr(thumb, 'url'):
                    image_candidates.append(thumb['url'])
        
        # 4. 从description/summary中提取
        description = getattr(entry, 'description', '') or getattr(entry, 'summary', '')
        if description:
            base_url = getattr(entry, 'link', None)
            extracted_url = self.extract_image_from_content(description, base_url)
            if extracted_url:
                image_candidates.append(extracted_url)
        
        # 5. 从content中提取
        if hasattr(entry, 'content'):
            for content_item in entry.content:
                if hasattr(content_item, 'value'):
                    base_url = getattr(entry, 'link', None)
                    extracted_url = self.extract_image_from_content(content_item.value, base_url)
                    if extracted_url:
                        image_candidates.append(extracted_url)
        
        # 返回第一个有效的图片URL
        for url in image_candidates:
            if self._is_valid_image_url(url):
                logger.debug(f"从RSS条目中提取到图片: {url}")
                return url
        
        return None
    
    def download_image(self, image_url: str, filename: str = None) -> Optional[str]:
        """
        下载图片
        
        Args:
            image_url: 图片URL
            filename: 自定义文件名（可选）
            
        Returns:
            本地文件路径或None
        """
        if not self._is_valid_image_url(image_url):
            logger.warning(f"不支持的图片URL: {image_url}")
            return None
        
        try:
            # 生成文件名
            if not filename:
                filename = self._generate_filename(image_url)
            
            local_path = self.download_dir / filename
            
            # 检查文件是否已存在
            if local_path.exists():
                logger.debug(f"图片已存在: {local_path}")
                return str(local_path)
            
            # 下载图片
            logger.info(f"开始下载图片: {image_url}")
            
            proxies = Config.get_proxies()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(
                image_url, 
                headers=headers, 
                proxies=proxies, 
                timeout=self.timeout, 
                stream=True
            )
            response.raise_for_status()
            
            # 检查内容类型
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                logger.warning(f"URL返回的不是图片类型: {content_type}")
                return None
            
            # 检查文件大小
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_file_size:
                logger.warning(f"图片文件过大: {content_length} bytes")
                return None
            
            # 保存图片
            with open(local_path, 'wb') as f:
                downloaded_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 检查下载大小限制
                        if downloaded_size > self.max_file_size:
                            logger.warning("图片下载过程中超过大小限制")
                            local_path.unlink()  # 删除部分下载的文件
                            return None
            
            logger.info(f"图片下载成功: {local_path} ({downloaded_size} bytes)")
            return str(local_path)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"下载图片失败 {image_url}: {e}")
            return None
        except Exception as e:
            logger.error(f"保存图片失败 {image_url}: {e}")
            return None
    
    def _is_valid_image_url(self, url: str) -> bool:
        """检查是否是有效的图片URL"""
        if not url:
            return False
        
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # 检查文件扩展名
            path = parsed.path.lower()
            if any(path.endswith(ext) for ext in self.supported_formats):
                return True
            
            # 如果没有扩展名，也认为可能是图片（由Content-Type判断）
            if '.' not in os.path.basename(path):
                return True
            
            return False
            
        except Exception:
            return False
    
    def _generate_filename(self, url: str) -> str:
        """根据URL生成文件名"""
        try:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            
            # 如果没有文件名或扩展名，生成一个
            if not filename or '.' not in filename:
                # 使用URL的hash作为文件名
                url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()[:12]
                filename = f"image_{url_hash}.jpg"
            
            # 清理文件名
            filename = re.sub(r'[^\w\-_\.]', '_', filename)
            
            return filename
            
        except Exception:
            # 生成随机文件名
            url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()[:12]
            return f"image_{url_hash}.jpg"
    
    def cleanup_old_images(self, days: int = 30) -> int:
        """
        清理旧图片
        
        Args:
            days: 保留天数
            
        Returns:
            删除的文件数量
        """
        import time
        
        if not self.download_dir.exists():
            return 0
        
        current_time = time.time()
        cutoff_time = current_time - (days * 24 * 60 * 60)
        deleted_count = 0
        
        for file_path in self.download_dir.iterdir():
            if file_path.is_file():
                file_mtime = file_path.stat().st_mtime
                if file_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        logger.debug(f"删除旧图片: {file_path}")
                    except Exception as e:
                        logger.error(f"删除文件失败 {file_path}: {e}")
        
        if deleted_count > 0:
            logger.info(f"清理了 {deleted_count} 个旧图片文件")
        
        return deleted_count
