"""
微信公众号发送模块测试
"""
import pytest
import os
import tempfile
from unittest.mock import Mock, patch

from src.integrations.wechat_official_sender import WeChatOfficialSender
from src.services.rss_service import RSSItem


class TestWeChatOfficialSender:
    
    def setup_method(self):
        """测试初始化"""
        self.env_config = {
            'WECHAT_OFFICIAL_APP_ID': 'test_app_id',
            'WECHAT_OFFICIAL_APP_SECRET': 'test_app_secret',
            'WECHAT_OFFICIAL_AUTHOR_NAME': 'Test Author',
            'WECHAT_OFFICIAL_ENABLED': 'true'
        }
        
        # 发送器配置
        self.sender_config = {
            'enabled': True,
            'app_id': 'test_app_id',
            'app_secret': 'test_app_secret',
            'author_name': 'Test Author'
        }
        
        # Mock环境变量并创建发送器
        with patch.dict(os.environ, self.env_config):
            self.sender = WeChatOfficialSender(self.sender_config)
    
    def test_initialization(self):
        """测试初始化"""
        assert self.sender.app_id == 'test_app_id'
        assert self.sender.app_secret == 'test_app_secret'
        assert self.sender.author_name == 'Test Author'
        assert self.sender.is_enabled()
    
    def test_extract_title(self):
        """测试标题提取"""
        message = """📰 OpenAI发布ChatGPT-4
        
        这是一个重要的AI技术突破
        具有更强的推理能力"""
        
        title = self.sender._extract_title(message)
        assert "OpenAI发布ChatGPT-4" in title
    
    def test_generate_digest(self):
        """测试摘要生成"""
        title = "测试标题"
        content = "<p>这是一段很长的内容。" + "测试内容。" * 20 + "</p>"
        
        digest = self.sender._generate_digest(title, content, 50)
        assert len(digest) <= 50
        assert "这是一段很长的内容" in digest
    
    def test_format_content_basic(self):
        """测试基本内容格式化"""
        message = """📰 AI技术新突破
        
        ✨ 主要亮点：
        • 性能提升50%
        • 支持多模态输入
        
        🔗 阅读原文：https://example.com"""
        
        formatted = self.sender._format_content(message)
        
        # 验证HTML结构 - 检查实际存在的HTML标签
        assert '<style>' in formatted
        assert '</style>' in formatted
        assert '<div' in formatted
        assert 'AI技术新突破' in formatted
        assert '性能提升50%' in formatted
    
    def test_format_content_with_highlighting(self):
        """测试带高亮的内容格式化"""
        message = """📰 重要新闻
        
        ✨ 要点：
        - 第一个要点
        - 第二个要点
        
        🌍 影响：全球范围"""
        
        formatted = self.sender._format_content(message)
        
        # 验证高亮内容被正确包装 - 检查实际的CSS类
        assert 'article-container' in formatted
        assert '第一个要点' in formatted
        assert '第二个要点' in formatted
    
    @patch('requests.get')
    def test_get_access_token_success(self, mock_get):
        """测试获取access_token成功"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'test_token_123',
            'expires_in': 7200
        }
        mock_get.return_value = mock_response
        
        result = self.sender._get_access_token()
        assert result == 'test_token_123'
        assert self.sender.access_token == 'test_token_123'
    
    @patch('requests.get')
    def test_get_access_token_failure(self, mock_get):
        """测试获取access_token失败"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'errcode': 40013,
            'errmsg': 'invalid appid'
        }
        mock_get.return_value = mock_response
        
        result = self.sender._get_access_token()
        assert result is None
    
    @patch('requests.post')
    def test_upload_permanent_media_success(self, mock_post):
        """测试上传永久素材成功"""
        # 创建临时图片文件
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(b'fake_image_data')
            tmp_path = tmp_file.name
        
        try:
            mock_response = Mock()
            mock_response.json.return_value = {
                'errcode': 0,
                'media_id': 'permanent_media_id_123',
                'url': 'http://mmbiz.qpic.cn/xxx'
            }
            mock_post.return_value = mock_response
            
            self.sender.access_token = 'test_token'
            result = self.sender._upload_permanent_media(tmp_path, 'image')
            
            assert result == 'permanent_media_id_123'
        finally:
            os.unlink(tmp_path)
    
    @patch('requests.post')
    def test_upload_thumb_media_success(self, mock_post):
        """测试上传缩略图成功"""
        # 创建临时图片文件
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(b'fake_image_data')
            tmp_path = tmp_file.name
        
        try:
            mock_response = Mock()
            mock_response.json.return_value = {
                'errcode': 0,
                'media_id': 'thumb_media_id_123',
                'url': 'http://mmbiz.qpic.cn/xxx'
            }
            mock_post.return_value = mock_response
            
            self.sender.access_token = 'test_token'
            result = self.sender._upload_thumb_media(tmp_path)
            
            assert result == 'thumb_media_id_123'
        finally:
            os.unlink(tmp_path)
    
    @patch('requests.post')
    def test_upload_image_media_success(self, mock_post):
        """测试上传图片素材成功"""
        # 创建临时图片文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(b'fake_image_data')
            tmp_path = tmp_file.name
        
        try:
            mock_response = Mock()
            mock_response.json.return_value = {
                'errcode': 0,
                'media_id': 'image_media_id_456',
                'url': 'http://mmbiz.qpic.cn/yyy'
            }
            mock_post.return_value = mock_response
            
            self.sender.access_token = 'test_token'
            result = self.sender._upload_image_media(tmp_path)
            
            assert result == 'image_media_id_456'
        finally:
            os.unlink(tmp_path)
    
    @patch('requests.post')
    def test_create_draft_success(self, mock_post):
        """测试创建草稿成功"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'errcode': 0,
            'media_id': 'draft_media_id_789'
        }
        mock_post.return_value = mock_response
        
        self.sender.access_token = 'test_token'
        
        result = self.sender._create_draft_v2(
            title="测试文章标题",
            content="<p>测试文章内容</p>",
            thumb_media_id="thumb_123"
        )
        
        assert result
        assert hasattr(self.sender, '_last_draft_media_id')
        assert self.sender._last_draft_media_id == 'draft_media_id_789'
    
    @patch('requests.post')
    def test_create_draft_failure(self, mock_post):
        """测试创建草稿失败"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'errcode': 40001,
            'errmsg': 'invalid credential'
        }
        mock_post.return_value = mock_response
        
        self.sender.access_token = 'test_token'
        
        result = self.sender._create_draft_v2(
            title="测试文章标题",
            content="<p>测试文章内容</p>"
        )
        
        assert not result
    
    def test_send_message_with_rss_item(self):
        """测试发送包含RSS图片的消息"""
        # 创建模拟的RSS项目
        rss_item = Mock(spec=RSSItem)
        rss_item.has_local_image.return_value = True
        rss_item.local_image_path = '/path/to/image.jpg'
        
        message = "📰 测试新闻标题\n\n✨ 这是测试内容"
        
        with patch.object(self.sender, '_ensure_access_token', return_value=True), \
             patch.object(self.sender, '_upload_thumb_media', return_value='thumb_123'), \
             patch.object(self.sender, '_create_draft_v2', return_value=True):
            
            result = self.sender.send_message(
                message, 
                type='draft',
                title='自定义标题',
                rss_item=rss_item
            )
            
            assert result
    
    def test_send_message_without_image(self):
        """测试发送不包含图片的消息"""
        message = "📰 测试新闻标题\n\n✨ 这是测试内容"
        
        with patch.object(self.sender, '_ensure_access_token', return_value=True), \
             patch.object(self.sender, '_create_draft_v2', return_value=True):
            
            result = self.sender.send_message(message, type='draft')
            
            assert result
    
    def test_get_status(self):
        """测试获取状态信息"""
        self.sender.access_token = 'test_token_123'
        
        status = self.sender.get_status()
        
        assert status['name'] == 'WeChatOfficial'
        assert status['type'] == 'official_account'
        assert status['enabled']
        assert status['has_token']
        assert 'test_app' in status['app_id']  # 应该被截断显示
        assert status['description'] == '微信公众号文章发布'
    
    def test_validate_config_success(self):
        """测试配置验证成功"""
        assert self.sender.validate_config()
    
    def test_validate_config_missing_app_id(self):
        """测试缺少AppID的配置验证"""
        self.sender.app_id = None
        assert not self.sender.validate_config()
    
    def test_validate_config_missing_app_secret(self):
        """测试缺少AppSecret的配置验证"""
        self.sender.app_secret = None
        assert not self.sender.validate_config()


if __name__ == '__main__':
    pytest.main([__file__])
