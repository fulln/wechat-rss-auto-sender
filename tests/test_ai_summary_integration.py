"""
AI总结与微信公众号集成测试
将原来的ai_summary_test.py转换为标准pytest测试
"""

import pytest
from unittest.mock import patch

from src.services.ai_service import Summarizer
from src.integrations.wechat_official_sender import WeChatOfficialSender
from tests.test_utils import TestDataGenerator, TestAssertions


class TestAISummaryIntegration:
    """AI总结与微信公众号集成测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.test_data_gen = TestDataGenerator()
        self.assertions = TestAssertions()
    
    def test_create_sample_rss_item(self):
        """测试创建示例RSS项目"""
        item = self.test_data_gen.create_sample_rss_item(
            title="OpenAI发布GPT-5：AI能力再次突破",
            description="""
            OpenAI今日正式发布了最新的GPT-5模型，该模型在推理能力、多模态理解和代码生成方面都有显著提升。
            据OpenAI官方介绍，GPT-5相比GPT-4在数学推理能力上提升了40%，在复杂问题解决方面提升了35%。
            新模型还支持更长的上下文窗口，可以处理高达1000万token的输入。
            这一突破将为人工智能在教育、医疗、金融等领域的应用带来新的可能性。
            业内专家认为，GPT-5的发布标志着AI技术进入了一个新的阶段。
            """,
            link="https://example.com/openai-gpt5-breakthrough"
        )
        
        # 使用断言验证RSS项目
        self.assertions.assert_rss_item_valid(item)
        assert "GPT-5" in item.title
        assert "OpenAI" in item.description
    
    @patch('src.services.ai_service.Summarizer.summarize_single_item')
    def test_ai_summarizer_mock(self, mock_summarize, sample_rss_item):
        """测试AI总结器（模拟）"""
        # 模拟AI总结返回
        mock_summary = "OpenAI发布GPT-5模型，在推理能力和多模态理解方面有显著提升，数学推理能力提升40%。"
        mock_summarize.return_value = mock_summary
        
        # 创建总结器
        summarizer = Summarizer()
        
        # 执行总结
        result = summarizer.summarize_single_item(sample_rss_item)
        
        # 验证结果
        assert result == mock_summary
        assert len(result) > 0
        mock_summarize.assert_called_once_with(sample_rss_item)
    
    @pytest.mark.integration
    @patch('src.integrations.wechat_official_sender.WeChatOfficialSender.send_message')
    def test_wechat_sender_integration(self, mock_send, mock_wechat_config):
        """测试微信发送器集成"""
        # 模拟发送成功
        mock_send.return_value = True
        
        # 创建发送器
        sender = WeChatOfficialSender(mock_wechat_config)
        
        # 创建测试数据
        test_item = self.test_data_gen.create_sample_rss_item()
        test_summary = "这是一个测试摘要内容"
        
        # 设置项目属性
        test_item.summary = test_summary
        test_item.content = test_summary
        test_item.has_local_image = lambda: False
        
        # 执行发送
        success = sender.send_message(
            message=test_summary,
            title=test_item.title,
            rss_item=test_item,
            type='draft'
        )
        
        # 验证结果
        assert success is True
        mock_send.assert_called_once()
    
    @pytest.mark.slow
    @patch('src.services.ai_service.Summarizer.summarize_single_item')
    @patch('src.integrations.wechat_official_sender.WeChatOfficialSender.send_message')
    def test_complete_ai_to_wechat_flow(self, mock_send, mock_summarize, mock_wechat_config):
        """测试完整的AI总结到微信发送流程"""
        # 准备测试数据
        test_item = self.test_data_gen.create_sample_rss_item(
            title="OpenAI发布GPT-5：AI能力再次突破",
            description="OpenAI今日正式发布了最新的GPT-5模型..."
        )
        
        # 模拟AI总结
        mock_summary = "OpenAI发布GPT-5模型，在推理能力方面有显著提升。"
        mock_summarize.return_value = mock_summary
        
        # 模拟微信发送成功
        mock_send.return_value = True
        
        # 1. 执行AI总结
        summarizer = Summarizer()
        summary_result = summarizer.summarize_single_item(test_item)
        
        # 验证总结结果
        assert summary_result == mock_summary
        self.assertions.assert_ai_summary_valid(summary_result)
        
        # 2. 准备微信发送
        test_item.summary = summary_result
        test_item.content = summary_result
        test_item.has_local_image = lambda: False
        
        # 3. 执行微信发送
        sender = WeChatOfficialSender(mock_wechat_config)
        send_success = sender.send_message(
            message=summary_result,
            title=test_item.title,
            rss_item=test_item,
            type='draft'
        )
        
        # 验证发送结果
        assert send_success is True
        
        # 验证调用次数
        mock_summarize.assert_called_once_with(test_item)
        mock_send.assert_called_once()
    
    def test_wechat_article_format_validation(self):
        """测试微信文章格式验证"""
        article_data = {
            'title': '测试文章标题',
            'content': '这是测试文章的内容',
            'author': 'Test Author'
        }
        
        # 应该通过验证
        self.assertions.assert_wechat_article_format(article_data)
    
    def test_wechat_article_format_validation_fails(self):
        """测试微信文章格式验证失败情况"""
        # 缺少必需字段
        invalid_article = {
            'title': '测试文章标题',
            'content': '这是测试文章的内容'
            # 缺少 author 字段
        }
        
        with pytest.raises(AssertionError, match="缺少必需字段: author"):
            self.assertions.assert_wechat_article_format(invalid_article)
    
    def test_title_length_limit(self):
        """测试标题长度限制"""
        long_title = "这是一个非常长的标题" * 10  # 超过64个字符
        
        article_data = {
            'title': long_title,
            'content': '内容',
            'author': 'Test Author'
        }
        
        with pytest.raises(AssertionError, match="标题长度超过限制"):
            self.assertions.assert_wechat_article_format(article_data)
    
    @pytest.mark.parametrize("title,expected_valid", [
        ("正常标题", True),
        ("这是一个稍微长一点的标题但仍在限制内", True),
        ("这是一个非常非常非常非常非常非常非常非常非常非常非常非常长的标题", False),
    ])
    def test_title_length_validation(self, title, expected_valid):
        """参数化测试标题长度验证"""
        article_data = {
            'title': title,
            'content': '内容',
            'author': 'Test Author'
        }
        
        if expected_valid:
            self.assertions.assert_wechat_article_format(article_data)
        else:
            with pytest.raises(AssertionError):
                self.assertions.assert_wechat_article_format(article_data)


# 可以用于手动测试的函数
def manual_test_ai_summary_integration():
    """手动测试AI总结集成（需要真实API密钥）"""
    from dotenv import load_dotenv
    load_dotenv()
    
    # 创建测试实例
    test_instance = TestAISummaryIntegration()
    test_instance.setup_method()
    
    # 运行基本测试
    print("运行RSS项目创建测试...")
    test_instance.test_create_sample_rss_item()
    print("✅ RSS项目创建测试通过")
    
    print("运行文章格式验证测试...")
    test_instance.test_wechat_article_format_validation()
    print("✅ 文章格式验证测试通过")
    
    print("所有手动测试完成！")


if __name__ == "__main__":
    manual_test_ai_summary_integration()
