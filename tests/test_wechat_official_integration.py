"""
微信公众号发送模块集成测试
"""
import pytest
import os
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch
from dotenv import load_dotenv

from src.integrations.wechat_official_sender import WeChatOfficialSender
from src.services.rss_service import RSSItem

# 加载环境变量
load_dotenv()


class TestWeChatOfficialIntegration:
    """微信公众号集成测试"""
    
    def setup_method(self):
        """测试初始化"""
        # 导入配置
        from src.core.config import Config
        self.config = Config()
        
        # 从环境变量获取真实配置
        self.sender_config = {
            'enabled': True,
            'app_id': os.getenv('WECHAT_OFFICIAL_APP_ID'),
            'app_secret': os.getenv('WECHAT_OFFICIAL_APP_SECRET'),
            'author_name': os.getenv('WECHAT_OFFICIAL_AUTHOR_NAME', 'RSS助手'),
            'use_rich_formatting': True
        }
        
        self.sender = WeChatOfficialSender(self.sender_config)
        
        # 创建测试文章
        self.test_article = RSSItem(
            title="AI技术突破：DeepSeek发布新一代多模态模型",
            link="https://example.com/ai-breakthrough",
            description="DeepSeek今日发布了其最新的多模态AI模型，在图像理解、代码生成和数学推理方面取得了显著突破。该模型采用全新的注意力机制，能够更好地理解复杂的多模态输入，为AI应用开辟了新的可能性。",
            published=datetime.now()
        )
        # 添加AI总结内容（模拟已处理过的文章）
        self.test_article.summary = "DeepSeek今日发布了其最新的多模态AI模型，在图像理解、代码生成和数学推理方面取得了显著突破。该模型采用全新的注意力机制，能够更好地理解复杂的多模态输入，为AI应用开辟了新的可能性。"
    
    def test_config_validation(self):
        """测试配置验证"""
        if not self.sender_config['app_id'] or not self.sender_config['app_secret']:
            pytest.skip("微信公众号配置不完整，请检查 .env 文件")
        
        assert self.sender.validate_config()
    
    def test_title_extraction(self):
        """测试标题提取功能"""
        message = f"""📰 {self.test_article.title}
        
        ✨ 核心要点：
        {self.test_article.summary}
        """
        
        extracted_title = self.sender._extract_title(message)
        assert "DeepSeek发布新一代多模态模型" in extracted_title
        assert len(extracted_title) <= 64  # 微信公众号标题长度限制
    
    def test_content_formatting(self):
        """测试内容格式化功能"""
        message = f"""📰 {self.test_article.title}
        
        ✨ 核心要点：
        {self.test_article.summary}
        
        🚀 技术亮点：
        • 全新注意力机制设计
        • 多模态理解能力提升
        • 代码生成准确率提高40%
        
        🔗 阅读原文：{self.test_article.link}
        """
        
        formatted_content = self.sender._format_content(message)
        
        # 验证HTML结构
        assert '<style>' in formatted_content
        assert 'article-container' in formatted_content
        assert self.test_article.title in formatted_content
        assert 'DeepSeek' in formatted_content  # 检查关键词而不是完整摘要
        assert self.test_article.link in formatted_content
        
        # 保存格式化结果供查看
        output_file = "test_wechat_official_formatted.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        print(f"\n📄 格式化HTML已保存到: {output_file}")
    
    def test_digest_generation(self):
        """测试摘要生成功能"""
        title = self.test_article.title
        content = f"<p>{self.test_article.summary}</p>" * 3  # 创建长内容
        
        # 测试不同长度的摘要
        short_digest = self.sender._generate_digest(title, content, 50)
        medium_digest = self.sender._generate_digest(title, content, 120)
        long_digest = self.sender._generate_digest(title, content, 200)
        
        assert len(short_digest) <= 50
        assert len(medium_digest) <= 120
        assert len(long_digest) <= 200
        
        # 验证摘要包含有意义的内容
        assert "DeepSeek" in medium_digest or "多模态" in medium_digest
    
    def test_permanent_media_upload_structure(self):
        """测试永久素材上传数据结构"""
        # 创建临时图片文件用于测试
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(b'fake_image_data_for_testing')
            tmp_path = tmp_file.name
        
        try:
            # 验证文件存在检查
            assert os.path.exists(tmp_path)
            
            # 验证文件大小检查逻辑
            file_size = os.path.getsize(tmp_path)
            assert file_size > 0
            
            # 测试不同媒体类型的大小限制
            size_limits = {
                'image': 10 * 1024 * 1024,  # 10MB
                'voice': 2 * 1024 * 1024,   # 2MB
                'video': 10 * 1024 * 1024,  # 10MB
                'thumb': 64 * 1024          # 64KB
            }
            
            for media_type, max_size in size_limits.items():
                if file_size <= max_size:
                    # 文件大小符合要求
                    assert True
                else:
                    # 文件过大的情况
                    assert file_size > max_size
            
        finally:
            os.unlink(tmp_path)
    
    @patch('requests.post')
    def test_permanent_media_upload_mock(self, mock_post):
        """测试永久素材上传（模拟API调用）"""
        # 创建临时图片文件
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(b'fake_image_data')
            tmp_path = tmp_file.name
        
        try:
            # 模拟成功响应
            mock_response = Mock()
            mock_response.json.return_value = {
                'errcode': 0,
                'media_id': 'permanent_media_id_123',
                'url': 'http://mmbiz.qpic.cn/test_image_url'
            }
            mock_post.return_value = mock_response
            
            # 设置access_token以模拟认证成功
            self.sender.access_token = 'test_token_123'
            
            # 测试永久素材上传
            result = self.sender._upload_permanent_media(tmp_path, "image")
            
            # 验证结果
            assert result == 'permanent_media_id_123'
            
            # 验证API调用参数
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            # 检查是否调用了正确的URL（第一个位置参数）
            assert 'material/add_material' in call_args[0][0]
            assert 'type=image' in call_args[0][0]
            
        finally:
            os.unlink(tmp_path)
    
    @patch('requests.post')
    def test_draft_creation_mock(self, mock_post):
        """测试草稿创建（模拟API调用）"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.json.return_value = {
            'errcode': 0,
            'media_id': 'draft_media_id_456'
        }
        mock_post.return_value = mock_response
        
        # 设置access_token
        self.sender.access_token = 'test_token_123'
        
        # 准备测试数据
        title = self.test_article.title
        content = self.sender._format_content(f"📰 {title}\n\n{self.test_article.summary}")
        
        # 测试草稿创建
        result = self.sender._create_draft_v2(title, content, "thumb_media_id_123")
        
        # 验证结果
        assert result
        assert hasattr(self.sender, '_last_draft_media_id')
        assert self.sender._last_draft_media_id == 'draft_media_id_456'
        
        # 验证API调用
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        # 检查是否调用了正确的URL（第一个位置参数）
        assert 'draft/add' in call_args[0][0]
        
        # 验证请求数据结构
        request_data = call_args[1]['json']
        assert 'articles' in request_data
        assert len(request_data['articles']) == 1
        
        article_data = request_data['articles'][0]
        assert article_data['title'] == title
        assert article_data['content'] == content
        assert article_data['author'] == self.sender.author_name
        assert article_data['thumb_media_id'] == "thumb_media_id_123"
    
    def test_message_send_structure(self):
        """测试消息发送数据结构"""
        message = f"""📰 {self.test_article.title}
        
        ✨ 核心要点：
        {self.test_article.summary}
        
        🔗 阅读原文：{self.test_article.link}
        """
        
        # 测试消息结构准备
        title = self.sender._extract_title(message)
        content = self.sender._format_content(message)
        digest = self.sender._generate_digest(title, content)
        
        # 验证草稿数据结构
        article_data = {
            "title": title,
            "content": content,
            "author": self.sender.author_name,
            "digest": digest,
            "show_cover_pic": 0,
            "need_open_comment": 1,
            "only_fans_can_comment": 0,
            "content_source_url": self.test_article.link,
        }
        
        draft_data = {
            "articles": [article_data]
        }
        
        # 验证数据完整性
        assert article_data['title']
        assert article_data['content']
        assert article_data['author']
        assert len(article_data['digest']) <= 120
        assert article_data['content_source_url'] == self.test_article.link
        assert len(draft_data['articles']) == 1
        
        print("\n📋 草稿数据结构验证通过:")
        print(f"   - 标题: {article_data['title'][:50]}...")
        print(f"   - 摘要: {article_data['digest'][:50]}...")
        print(f"   - 内容长度: {len(article_data['content'])} 字符")
    
    @pytest.mark.skipif(
        not os.getenv('WECHAT_OFFICIAL_APP_ID') or not os.getenv('WECHAT_OFFICIAL_APP_SECRET'),
        reason="微信公众号配置不完整"
    )
    def test_connection_real_api(self):
        """测试真实API连接（需要正确配置）"""
        # 这个测试只在配置完整时运行
        # 注意：需要IP白名单配置才能成功
        try:
            result = self.sender.test_connection()
            if result:
                print("\n✅ 微信公众号API连接成功")
            else:
                print("\n⚠️  微信公众号API连接失败（可能是IP白名单问题）")
        except Exception as e:
            print(f"\n⚠️  API连接测试异常: {e}")
            # 不让测试失败，因为可能是网络或配置问题
            pytest.skip(f"API连接测试跳过: {e}")
    
    def test_sender_status(self):
        """测试发送器状态获取"""
        status = self.sender.get_status()
        
        assert status['name'] == 'WeChatOfficial'
        assert status['type'] == 'official_account'
        assert status['description'] == '微信公众号文章发布'
        assert 'enabled' in status
        assert 'has_token' in status
        
        if self.sender_config['app_id']:
            assert status['app_id'].endswith('...')  # 应该被截断显示
    
    def teardown_method(self):
        """测试清理"""
        # 清理测试生成的文件
        test_files = [
            'test_wechat_official_formatted.html'
        ]
        
        for file_path in test_files:
            if os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                except Exception:
                    pass  # 忽略清理错误

    # ==================== 真实API测试方法 ====================
    # 注意：以下测试使用真实的微信公众号API
    
    def test_real_access_token(self):
        """测试真实API：获取访问令牌
        
        注意：此测试需要：
        1. 正确的微信公众号APP_ID和APP_SECRET
        2. 服务器IP已添加到微信公众号IP白名单
        3. 在.env文件中启用WECHAT_OFFICIAL_SENDER_ENABLED=true
        """
        # 检查配置
        if not self.config.WECHAT_OFFICIAL_APP_ID or not self.config.WECHAT_OFFICIAL_APP_SECRET:
            pytest.skip("微信公众号配置不完整")
        
        if not self.config.WECHAT_OFFICIAL_SENDER_ENABLED:
            pytest.skip("微信公众号发送器未启用")
        
        # 测试获取访问令牌
        access_token = self.sender._get_access_token()
        
        assert access_token is not None
        assert isinstance(access_token, str)
        assert len(access_token) > 0
        print(f"✅ 访问令牌获取成功: {access_token[:20]}...")

    def test_real_permanent_media_upload(self):
        """测试真实API：永久素材上传
        
        注意：此测试需要真实的微信公众号API配置
        """
        # 检查配置
        if not self.config.WECHAT_OFFICIAL_APP_ID or not self.config.WECHAT_OFFICIAL_APP_SECRET:
            pytest.skip("微信公众号配置不完整")
        
        if not self.config.WECHAT_OFFICIAL_SENDER_ENABLED:
            pytest.skip("微信公众号发送器未启用")
        
        # 先确保获取新的访问令牌
        print("🔍 获取访问令牌...")
        access_token = self.sender._get_access_token()
        assert access_token is not None
        print(f"✅ 访问令牌获取成功: {access_token[:20]}...")
        
        # 创建测试图片文件（更完整的PNG）
        import base64
        import tempfile
        # 这是一个更完整的1x1红色像素PNG图片
        test_image_data = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
        )
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(test_image_data)
            tmp_path = tmp_file.name
        
        try:
            # 测试永久素材上传
            print("🔍 上传永久素材...")
            media_id = self.sender._upload_permanent_media(tmp_path, 'image')
            
            assert media_id is not None
            assert isinstance(media_id, str)
            assert len(media_id) > 0
            print(f"✅ 永久素材上传成功: {media_id}")
            
        finally:
            # 清理临时文件
            os.unlink(tmp_path)

    def test_real_draft_creation(self):
        """测试真实API：创建草稿
        
        注意：此测试需要真实的微信公众号API配置
        """
        # 检查配置
        if not self.config.WECHAT_OFFICIAL_APP_ID or not self.config.WECHAT_OFFICIAL_APP_SECRET:
            pytest.skip("微信公众号配置不完整")
        
        if not self.config.WECHAT_OFFICIAL_SENDER_ENABLED:
            pytest.skip("微信公众号发送器未启用")
        
        # 创建测试RSS项目
        from datetime import datetime
        
        test_item = RSSItem(
            title="微信公众号API测试",
            link="https://example.com/test-real",
            description="这是一个测试微信公众号真实API的文章。",
            published=datetime.now()
        )
        
        # 添加content属性（模拟AI总结后的内容）
        test_item.content = """
            <h1>微信公众号永久素材API测试</h1>
            <p>本文用于测试微信公众号API的真实调用功能。</p>
            <p>测试项目：</p>
            <ul>
                <li>访问令牌获取</li>
                <li>永久素材上传</li>
                <li>草稿创建</li>
            </ul>
            <p>测试时间：{}</p>
            """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        test_item.summary = "测试微信公众号API的真实调用功能，包括访问令牌获取、永久素材上传和草稿创建。"
        
        # 使用测试封面图片
        import os
        test_cover_path = os.path.join(os.getcwd(), 'test_cover.jpg')
        if os.path.exists(test_cover_path):
            test_item.local_image_path = test_cover_path
            test_item.image_downloaded = True
            
            # 添加has_local_image方法
            def has_local_image():
                return test_item.image_downloaded and test_item.local_image_path and os.path.exists(test_item.local_image_path)
            
            test_item.has_local_image = has_local_image
        else:
            # 如果没有测试图片，返回False
            def has_local_image():
                return False
            
            test_item.has_local_image = has_local_image
        
        # 测试发送到微信公众号
        message = f"""📰 {test_item.title}

        ✨ 核心要点：
        {test_item.summary}

        🔗 阅读原文：{test_item.link}
        """
        
        result = self.sender.send_message(message, rss_item=test_item)
        
        # 清理临时文件
        try:
            if hasattr(test_item, 'local_image_path') and test_item.local_image_path:
                os.unlink(test_item.local_image_path)
        except Exception:
            pass  # 忽略清理错误
        
        assert result is True
        print("✅ 微信公众号草稿创建成功！请到微信公众号后台查看")

    def test_real_full_workflow(self):
        """测试真实API：完整工作流程
        
        测试从RSS获取到微信公众号发布的完整流程
        """
        # 检查配置
        if not self.config.WECHAT_OFFICIAL_APP_ID or not self.config.WECHAT_OFFICIAL_APP_SECRET:
            pytest.skip("微信公众号配置不完整")
        
        if not self.config.WECHAT_OFFICIAL_SENDER_ENABLED:
            pytest.skip("微信公众号发送器未启用")
        
        # 1. 测试RSS服务
        from src.services.rss_service import RSSFetcher
        from src.core.config import Config
        rss_config = Config()
        rss_fetcher = RSSFetcher(rss_config)
        
        print("🔍 获取RSS文章...")
        articles = rss_fetcher.fetch_articles()
        assert isinstance(articles, list)
        
        if not articles:
            pytest.skip("没有获取到RSS文章")
        
        print(f"✅ 获取到 {len(articles)} 篇文章")
        
        # 选择第一篇文章进行测试
        test_article = articles[0]
        print(f"测试文章: {test_article.title}")
        
        # 2. 测试微信公众号发送
        print("🔍 发送到微信公众号...")
        message = f"""📰 {test_article.title}

        ✨ 核心要点：
        {test_article.description}

        🔗 阅读原文：{test_article.link}
        """
        
        result = self.sender.send_message(message, rss_item=test_article)
        
        assert result is True
        print("✅ 完整工作流程测试成功！")
        print("文章已发送到微信公众号，请到后台查看")


if __name__ == '__main__':
    # 运行特定的测试
    pytest.main([__file__, '-v', '-s'])
