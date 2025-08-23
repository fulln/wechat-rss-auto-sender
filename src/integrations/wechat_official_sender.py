"""
微信公众号发送模块
"""
import os
import re
import requests
import time
import json
from typing import Dict, Any, Optional

from .base_sender import BaseSender
from ..core.utils import setup_logger

logger = setup_logger(__name__)


class WeChatOfficialSender(BaseSender):
    """微信公众号发送器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.app_id = self.config.get('app_id', '')
        self.app_secret = self.config.get('app_secret', '')
        self.access_token = None
        self.token_expires_at = 0
        
        # HTML格式化配置
        self.use_rich_formatting = self.config.get('use_rich_formatting', True)
        self.custom_css = self.config.get('custom_css', '')
        self.footer_text = self.config.get('footer_text', '📱 更多科技资讯，请关注我们')
        self.author_name = self.config.get('author_name', 'RSS助手')
        
    def send_message(self, message: str, **kwargs) -> bool:
        """
        发送消息到微信公众号
        
        Args:
            message: 消息内容
            **kwargs: 额外参数，可包含 title, media_id, rss_item 等
            
        Returns:
            是否发送成功
        """
        if not message.strip():
            logger.warning("消息内容为空，跳过发送")
            return False
        
        try:
            # 确保有有效的access_token
            if not self._ensure_access_token():
                logger.error("无法获取微信公众号access_token")
                return False
            
            article_type = kwargs.get('type', 'draft')  # draft 或 publish
            title = kwargs.get('title', self._extract_title(message))
            rss_item = kwargs.get('rss_item')  # RSS条目对象，包含图片信息
            content = self._format_content(message, rss_item=rss_item)
            
            logger.info(f"准备发布微信公众号文章: {title[:30]}...")
            
            # 处理封面图片
            thumb_media_id = None
            if rss_item and rss_item.has_local_image():
                thumb_media_id = self._upload_thumb_media(rss_item.local_image_path)
                if thumb_media_id:
                    logger.info(f"封面图片上传成功: {thumb_media_id}")
                else:
                    logger.warning("封面图片上传失败")
            
            if article_type == 'draft':
                result = self._create_draft_v2(title, content, thumb_media_id, rss_item)
            else:
                result = self._publish_article_v2(title, content, thumb_media_id, rss_item)
                
            if result:
                logger.info(f"微信公众号文章{article_type}成功")
                return True
            else:
                logger.error(f"微信公众号文章{article_type}失败")
                return False
                
        except Exception as e:
            logger.error(f"发送微信公众号消息失败: {e}")
            return False
    
    def _ensure_access_token(self) -> bool:
        """确保有有效的access_token"""
        current_time = time.time()
        
        # 如果token还有效，直接返回
        if self.access_token and current_time < self.token_expires_at:
            return True
        
        # 获取新的access_token
        token = self._get_access_token()
        return token is not None
    
    def _get_access_token(self) -> Optional[str]:
        """
        获取微信公众号access_token
        
        Returns:
            access_token或None
        """
        try:
            url = "https://api.weixin.qq.com/cgi-bin/token"
            params = {
                'grant_type': 'client_credential',
                'appid': self.app_id,
                'secret': self.app_secret
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'access_token' in data:
                self.access_token = data['access_token']
                # 提前5分钟过期，确保安全边际
                current_time = time.time()
                self.token_expires_at = current_time + data.get('expires_in', 7200) - 300
                logger.info("微信公众号access_token获取成功")
                return self.access_token
            else:
                logger.error(f"获取access_token失败: {data}")
                return None
                
        except Exception as e:
            logger.error(f"获取access_token异常: {e}")
            return None
    
    def _upload_permanent_media(self, image_path: str, media_type: str = "image") -> Optional[str]:
        """
        上传永久素材
        
        Args:
            image_path: 本地图片路径
            media_type: 媒体类型 (image, voice, video, thumb)
            
        Returns:
            media_id或None
        """
        if not os.path.exists(image_path):
            logger.error(f"图片文件不存在: {image_path}")
            return None
        
        try:
            url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={self.access_token}&type={media_type}"
            
            # 检查文件大小限制
            file_size = os.path.getsize(image_path)
            size_limits = {
                'image': 10 * 1024 * 1024,  # 10MB
                'voice': 2 * 1024 * 1024,   # 2MB
                'video': 10 * 1024 * 1024,  # 10MB
                'thumb': 64 * 1024          # 64KB
            }
            
            max_size = size_limits.get(media_type, 10 * 1024 * 1024)
            if file_size > max_size:
                logger.error(f"文件过大 ({file_size} bytes)，超过{media_type}类型限制 ({max_size} bytes)")
                return None
            
            with open(image_path, 'rb') as f:
                files = {'media': f}
                # 对于永久素材，需要添加description参数
                data = {
                    'description': '{"title":"RSS文章配图","introduction":"自动上传的RSS文章配图"}'
                } if media_type == 'video' else {}
                
                response = requests.post(url, files=files, data=data, timeout=30)
                result = response.json()
                
                if result.get('errcode') == 0 or 'media_id' in result:
                    media_id = result['media_id']
                    logger.info(f"永久素材上传成功: {media_id}")
                    return media_id
                else:
                    logger.error(f"永久素材上传失败: {result}")
                    return None
                    
        except Exception as e:
            logger.error(f"上传永久素材异常: {e}")
            return None
    
    def _upload_thumb_media(self, image_path: str) -> Optional[str]:
        """
        上传缩略图素材 (用于文章封面)
        
        Args:
            image_path: 本地图片路径
            
        Returns:
            media_id或None
        """
        return self._upload_permanent_media(image_path, "thumb")
    
    def _upload_image_media(self, image_path: str) -> Optional[str]:
        """
        上传图片素材 (用于文章正文)
        
        Args:
            image_path: 本地图片路径
            
        Returns:
            media_id或None
        """
        return self._upload_permanent_media(image_path, "image")
    
    def _create_draft_v2(self, title: str, content: str, thumb_media_id: str = None, rss_item = None) -> bool:
        """
        创建草稿 (使用正式API)
        
        Args:
            title: 文章标题
            content: 文章内容 (HTML格式)
            thumb_media_id: 封面图片media_id
            rss_item: RSS条目对象，包含原文链接
            
        Returns:
            是否创建成功
        """
        try:
            url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={self.access_token}"
            
            # 根据API要求，图文消息必须有thumb_media_id
            # 如果没有提供，需要创建一个默认封面
            if not thumb_media_id:
                logger.info("没有提供封面图片，上传默认封面")
                # 尝试使用默认封面图片
                default_cover_path = os.path.join(os.path.dirname(__file__), '../../test_cover.jpg')
                if os.path.exists(default_cover_path):
                    thumb_media_id = self._upload_thumb_media(default_cover_path)
                    if not thumb_media_id:
                        logger.error("上传默认封面失败")
                        return False
                else:
                    logger.error("没有找到默认封面图片，草稿创建失败")
                    return False
            
            # 构建文章数据
            # 确保标题长度符合微信要求（最多64个字符）
            # 修复全角字符问题
            title = title.replace('：', ':')  # 全角冒号转半角冒号
            title = title.replace('，', ',')  # 全角逗号转半角逗号  
            title = title.replace('。', '.')  # 全角句号转半角句号
            title = title[:64] if len(title) > 64 else title
            logger.debug(f"文章标题: '{title}' (长度: {len(title)})")
            
            # 使用传入的摘要或生成默认摘要
            # 不传摘要字段，让微信自动抓取正文前54个字符
            logger.debug("不提供摘要，使用微信自动抓取")
            
            # 确保作者名长度限制，且微信API不支持中文作者名
            author = self.author_name[:20] if len(self.author_name) > 20 else self.author_name
            # 如果作者名包含中文，替换为英文
            if any('\u4e00' <= char <= '\u9fff' for char in author):
                author = "RSS Bot"  # 使用英文替代
            logger.debug(f"作者名称: '{author}' (长度: {len(author)})")
            
            # 获取原文链接
            content_source_url = ""
            if rss_item and hasattr(rss_item, 'link') and rss_item.link:
                content_source_url = rss_item.link
                logger.info(f"设置原文链接: {content_source_url}")
            
            article_data = {
                "title": title,
                "content": content,
                "author": author,
                "thumb_media_id": thumb_media_id,  # API要求必填
                "show_cover_pic": 1,  # 显示封面
                "need_open_comment": 1,  # 允许评论
                "only_fans_can_comment": 0,  # 所有人可评论
                "content_source_url": content_source_url,  # 原文链接
            }
            # 不添加digest字段，让微信自动生成摘要
            
            data = {
                "articles": [article_data]
            }
            
            # 调试：记录请求数据
            logger.info(f"草稿创建请求数据: {data}")
            
            # 确保UTF-8编码，避免Unicode转义
            headers = {
                'Content-Type': 'application/json; charset=utf-8'
            }
            
            # 使用json.dumps确保中文不被转义
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            
            response = requests.post(
                url, 
                data=json_data.encode('utf-8'), 
                headers=headers, 
                timeout=30
            )
            result = response.json()
            
            # 调试：记录完整响应
            logger.debug(f"草稿创建API响应: {result}")
            
            # 检查是否有错误码
            if 'errcode' in result and result['errcode'] != 0:
                logger.error(f"草稿创建失败: {result}")
                return False
            
            # 成功的响应包含media_id
            if 'media_id' in result:
                media_id = result.get('media_id')
                logger.info(f"草稿创建成功，media_id: {media_id}")
                
                # 可以选择性地保存media_id用于后续发布
                self._last_draft_media_id = media_id
                
                return True
            else:
                logger.error(f"草稿创建响应格式异常: {result}")
                return False
                
        except Exception as e:
            logger.error(f"创建草稿异常: {e}")
            return False
    
    def _generate_digest(self, title: str, content: str, max_length: int = 120) -> str:
        """
        生成文章摘要
        
        Args:
            title: 标题
            content: 内容
            max_length: 最大长度
            
        Returns:
            摘要文本
        """
        # 从HTML内容中提取纯文本
        text_content = re.sub(r'<[^>]+>', '', content)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        # 如果内容较短，直接使用
        if len(text_content) <= max_length:
            return text_content
        
        # 尝试在句号处截断
        sentences = text_content.split('。')
        digest = ""
        for sentence in sentences:
            if len(digest + sentence + "。") <= max_length:
                digest += sentence + "。"
            else:
                break
        
        # 如果没有合适的句号截断点，直接截断
        if not digest:
            digest = text_content[:max_length-3] + "..."
        
        return digest
    
    def _publish_article_v2(self, title: str, content: str, thumb_media_id: str = None, rss_item = None) -> bool:
        """
        发布文章 (先创建草稿再发布)
        
        Args:
            title: 文章标题
            content: 文章内容
            thumb_media_id: 封面图片media_id
            rss_item: RSS条目对象，包含原文链接
            
        Returns:
            是否发布成功
        """
        try:
            # 先创建草稿
            if not self._create_draft_v2(title, content, thumb_media_id, rss_item):
                return False
            
            # 获取草稿的media_id
            draft_media_id = getattr(self, '_last_draft_media_id', None)
            if not draft_media_id:
                logger.error("无法获取草稿media_id")
                return False
            
            # 发布草稿 (这里需要根据实际需求实现)
            # 注意: 微信公众号的文章发布可能需要额外的权限和流程
            logger.info(f"草稿已创建，media_id: {draft_media_id}")
            logger.info("注意: 文章发布需要在微信公众平台手动操作或使用发布接口")
            
            return True
            
        except Exception as e:
            logger.error(f"发布文章异常: {e}")
            return False
    
    def _extract_title(self, message: str) -> str:
        """从消息中提取标题"""
        lines = message.strip().split('\n')
        # 取第一行非空内容作为标题，并清理格式
        for line in lines:
            clean_line = line.strip().replace('📰', '').replace('🔥', '').replace('#', '').strip()
            if clean_line and len(clean_line) > 5:
                return clean_line[:64]  # 微信公众号标题长度限制
        return "科技资讯分享"
    
    def _format_content(self, message: str, rss_item = None) -> str:
        """格式化内容适配微信公众号HTML"""
        if not self.use_rich_formatting:
            # 简单格式化
            return self._simple_format(message)
        
        # 丰富格式化
        sections = self._parse_message_sections(message)
        
        # 如果有RSS条目，添加原文链接到sections
        if rss_item and hasattr(rss_item, 'link') and rss_item.link and not sections['link']:
            sections['link'] = rss_item.link
        
        html_content = self._build_html_content(sections)
        
        return html_content
    
    def _simple_format(self, message: str) -> str:
        """简单HTML格式化"""
        # 使用更简单的HTML格式，避免复杂CSS
        content = message.replace('\n', '<br>')
        
        # 只使用基本的HTML标签和内联样式
        return f'''
        <div>
            <p style="font-size: 16px; line-height: 1.6; color: #333;">
                {content}
            </p>
        </div>
        '''
    
    def _parse_message_sections(self, message: str) -> dict:
        """解析消息的各个部分"""
        lines = message.strip().split('\n')
        sections = {
            'title': '',
            'summary': '',
            'highlights': [],
            'content': '',
            'tags': [],
            'link': ''
        }
        
        content_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 识别标题（通常是第一行，包含表情符号）
            if not sections['title'] and ('📰' in line or '🔥' in line):
                sections['title'] = line.replace('📰', '').replace('🔥', '').strip()
                continue
            
            # 识别标签
            if line.startswith('#') or '##' in line:
                tags = [tag.strip() for tag in line.split('#') if tag.strip()]
                sections['tags'].extend(tags)
                continue
            
            # 识别链接
            if line.startswith('http') or '阅读原文：' in line:
                sections['link'] = line.replace('阅读原文：', '').strip()
                continue
            
            # 识别要点（包含特殊符号的行）
            if any(symbol in line for symbol in ['✨', '🚀', '💡', '🌍', '•', '-']):
                sections['highlights'].append(line)
                continue
            
            # 其他内容
            content_lines.append(line)
        
        sections['content'] = '\n'.join(content_lines)
        return sections
    
    def _build_html_content(self, sections: dict) -> str:
        """构建HTML格式的内容"""
        html_parts = []
        
        # 添加CSS样式
        css_style = self._get_css_styles()
        html_parts.append(css_style)
        
        html_parts.append('<div class="article-container">')
        
        # 添加标题
        if sections['title']:
            title_html = f'<h1 class="article-title">{sections["title"]}</h1>'
            html_parts.append(title_html)
        
        # 添加主要内容
        if sections['content']:
            content_html = f'<div class="article-content">{self._format_paragraphs(sections["content"])}</div>'
            html_parts.append(content_html)
        
        # 添加要点高亮
        if sections['highlights']:
            highlights_html = '<div class="highlights-list">'
            highlights_html += '<div style="font-weight: bold; margin-bottom: 10px; color: #007bff;">📌 核心要点：</div>'
            for highlight in sections['highlights']:
                formatted_highlight = self._format_highlight_text(highlight)
                highlights_html += f'<div class="highlight-item">{formatted_highlight}</div>'
            highlights_html += '</div>'
            html_parts.append(highlights_html)
        
        # 添加标签
        if sections['tags']:
            tags_html = '<div class="tags-container">'
            for tag in sections['tags']:
                tags_html += f'<span class="tag">#{tag}</span>'
            tags_html += '</div>'
            html_parts.append(tags_html)
        
        # 添加阅读原文链接
        if sections['link']:
            link_html = f'''
            <div class="read-more">
                <a href="{sections['link']}" target="_blank">📖 阅读原文</a>
            </div>
            '''
            html_parts.append(link_html)
        
        # 添加页脚
        footer_html = f'''
        <div class="footer">
            <p>{self.footer_text}</p>
            <p style="font-size: 12px; color: #999;">本内容由AI智能整理，仅供参考</p>
        </div>
        '''
        html_parts.append(footer_html)
        
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)
    
    def _get_css_styles(self) -> str:
        """获取增强的CSS样式"""
        default_css = """
        <style>
        .article-container {
            max-width: 100%;
            margin: 0 auto;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            line-height: 1.7;
            color: #2c3e50;
            background-color: #fdfdfd;
        }
        .article-title {
            font-size: 24px;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 20px;
            text-align: center;
            line-height: 1.3;
            padding: 0 10px;
            position: relative;
        }
        .article-title::after {
            content: '';
            display: block;
            width: 60px;
            height: 3px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            margin: 15px auto 0;
            border-radius: 2px;
        }
        .article-content {
            font-size: 16px;
            line-height: 1.8;
            margin-bottom: 25px;
            text-align: justify;
            color: #34495e;
        }
        .article-content p {
            margin-bottom: 16px;
            text-indent: 2em;
        }
        .article-content p:first-child {
            font-size: 17px;
            font-weight: 500;
            color: #2980b9;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
            text-indent: 0;
            margin-bottom: 20px;
        }
        .highlight-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            position: relative;
        }
        .highlight-box::before {
            content: '💡';
            position: absolute;
            top: -10px;
            left: 20px;
            background: white;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }
        .highlights-list {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            background-clip: text;
            -webkit-background-clip: text;
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            position: relative;
        }
        .highlights-list::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(45deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3);
            border-radius: 12px 12px 0 0;
        }
        .highlight-item {
            margin: 12px 0;
            padding: 8px 0 8px 15px;
            font-size: 15px;
            color: #495057;
            position: relative;
            border-left: 3px solid transparent;
            border-image: linear-gradient(45deg, #667eea, #764ba2) 1;
        }
        .highlight-item::before {
            content: '▶';
            color: #667eea;
            font-size: 12px;
            position: absolute;
            left: -12px;
            top: 50%;
            transform: translateY(-50%);
        }
        .tags-container {
            margin: 25px 0;
            text-align: center;
            padding: 15px;
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            border-radius: 12px;
        }
        .tag {
            display: inline-block;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 8px 16px;
            margin: 5px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            text-decoration: none;
            box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
            transition: all 0.3s ease;
        }
        .read-more {
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }
        .read-more a {
            display: inline-block;
            background: linear-gradient(45deg, #ffffff, #f8f9fa);
            color: #667eea;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 25px;
            font-weight: 600;
            font-size: 16px;
            box-shadow: 0 4px 15px rgba(255,255,255,0.3);
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }
        .read-more::before {
            content: '📖 点击阅读完整原文';
            display: block;
            color: white;
            font-size: 14px;
            margin-bottom: 10px;
            font-weight: 400;
        }
        .footer {
            margin-top: 40px;
            padding: 25px 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            text-align: center;
            color: #718096;
            font-size: 14px;
            border-top: 3px solid transparent;
            border-image: linear-gradient(45deg, #667eea, #764ba2) 1;
        }
        .footer p:first-child {
            font-size: 16px;
            color: #4a5568;
            font-weight: 500;
            margin-bottom: 8px;
        }
        /* 响应式设计 */
        @media (max-width: 480px) {
            .article-container {
                padding: 15px;
            }
            .article-title {
                font-size: 20px;
            }
            .article-content {
                font-size: 15px;
            }
        }
        /* 强调文本样式 */
        strong {
            color: #e74c3c;
            font-weight: 600;
        }
        em {
            color: #9b59b6;
            font-style: normal;
            background: linear-gradient(45deg, #f093fb, #f5576c);
            background-clip: text;
            -webkit-background-clip: text;
            font-weight: 500;
        }
        /* 引用样式 */
        blockquote {
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin: 20px 0;
            font-style: italic;
            color: #5d6d7e;
            background: #f8f9fa;
            padding: 15px 20px;
            border-radius: 0 8px 8px 0;
        }
        </style>
        """
        
        # 如果有自定义CSS，则追加
        if self.custom_css:
            return default_css + f"\n<style>\n{self.custom_css}\n</style>"
        
        return default_css
    
    def _format_paragraphs(self, content: str) -> str:
        """格式化段落内容"""
        paragraphs = content.split('\n')
        formatted_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 转换表情符号和特殊格式
            para = para.replace('📰', '🔥').replace('✨', '⭐').replace('🚀', '🌟')
            
            # 加粗关键词
            para = self._highlight_keywords(para)
            
            formatted_paragraphs.append(f'<p>{para}</p>')
        
        return '\n'.join(formatted_paragraphs)
    
    def _format_highlight_text(self, text: str) -> str:
        """格式化要点文本"""
        # 移除开头的符号
        text = text.strip()
        for symbol in ['✨', '🚀', '💡', '🌍', '•', '-']:
            if text.startswith(symbol):
                text = text[1:].strip()
                break
        
        # 添加自定义图标
        return f'💫 {text}'
    
    def _highlight_keywords(self, text: str) -> str:
        """高亮关键词"""
        keywords = [
            'AI', 'GPT', '人工智能', '机器学习', '深度学习', 
            '区块链', '云计算', '大数据', '物联网', '5G',
            '突破', '创新', '发布', '升级', '优化'
        ]
        
        for keyword in keywords:
            if keyword in text:
                text = text.replace(keyword, f'<strong style="color: #1976d2;">{keyword}</strong>')
        
        return text
    
    def _create_draft(self, title: str, content: str) -> bool:
        """创建草稿"""
        try:
            url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={self.access_token}"
            
            data = {
                "articles": [{
                    "title": title,
                    "content": content,
                    "author": "RSS助手",
                    "digest": title[:54],  # 摘要
                    "show_cover_pic": 0,
                    "need_open_comment": 0,
                    "only_fans_can_comment": 0
                }]
            }
            
            response = requests.post(url, json=data, timeout=30)
            result = response.json()
            
            if result.get('errcode') == 0:
                logger.info(f"草稿创建成功，media_id: {result.get('media_id')}")
                return True
            else:
                logger.error(f"草稿创建失败: {result}")
                return False
                
        except Exception as e:
            logger.error(f"创建草稿异常: {e}")
            return False
    
    def _publish_article(self, title: str, content: str) -> bool:
        """发布文章"""
        try:
            # 先创建草稿
            if not self._create_draft(title, content):
                return False
            
            # 然后发布（这里需要实际的发布逻辑）
            logger.info("文章发布功能需要进一步实现")
            return True
            
        except Exception as e:
            logger.error(f"发布文章异常: {e}")
            return False
    
    def test_connection(self) -> bool:
        """测试微信公众号连接"""
        try:
            return self._ensure_access_token()
        except Exception as e:
            logger.error(f"微信公众号连接测试失败: {e}")
            return False
    
    def get_sender_info(self) -> Dict[str, Any]:
        """获取发送器信息"""
        return {
            'name': 'WeChatOfficial',
            'type': 'official_account',
            'enabled': self.is_enabled(),
            'app_id': self.app_id[:8] + '...' if self.app_id else '',
            'has_token': bool(self.access_token),
            'description': '微信公众号文章发布'
        }
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态信息 (get_sender_info的别名)"""
        return self.get_sender_info()
    
    def validate_config(self) -> bool:
        """验证配置"""
        if not self.app_id:
            logger.error("微信公众号AppID未配置")
            return False
        
        if not self.app_secret:
            logger.error("微信公众号AppSecret未配置")
            return False
        
        return True
