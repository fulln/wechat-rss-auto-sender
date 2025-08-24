"""
AI总结模块
"""
import re
import logging
from typing import List, Optional
from openai import OpenAI
import time
from bs4 import BeautifulSoup
import subprocess
import tempfile
import os

from ..core.config import Config
from ..core.prompts import PromptTemplates
from ..core.utils import setup_logger
from .rss_service import RSSItem

logger = setup_logger(__name__)


class Summarizer:
    """AI总结器"""

    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("需要配置OPENAI_API_KEY")

        # 基础配置
        client_kwargs = {
            "api_key": Config.OPENAI_API_KEY,
            "base_url": Config.OPENAI_BASE_URL
        }
        
        # 尝试添加代理配置
        try:
            proxies = Config.get_proxies() if hasattr(Config, 'get_proxies') else None
            if proxies:
                import httpx
                # 使用新版本的httpx代理配置
                proxy_url = proxies.get('https') or proxies.get('http')
                if proxy_url:
                    client_kwargs["http_client"] = httpx.Client(proxy=proxy_url)
                    logger.info(f"Summarizer使用代理: {proxy_url}")
        except Exception as e:
            logger.warning(f"代理配置失败，使用默认连接: {e}")
        
        try:
            self.client = OpenAI(**client_kwargs)
            logger.info("OpenAI客户端初始化成功")
        except Exception as e:
            logger.error(f"OpenAI客户端初始化失败: {e}")
            # 如果代理配置有问题，尝试不使用代理
            logger.info("尝试不使用代理重新初始化...")
            client_kwargs_no_proxy = {
                "api_key": Config.OPENAI_API_KEY,
                "base_url": Config.OPENAI_BASE_URL
            }
            try:
                self.client = OpenAI(**client_kwargs_no_proxy)
                logger.info("OpenAI客户端已使用默认连接初始化成功")
            except Exception as e2:
                logger.error(f"无代理初始化也失败: {e2}")
                raise


    def clean_html(self, text: str) -> str:
        """清理HTML标签"""
        if not text:
            return ""

        # 使用BeautifulSoup清理HTML
        soup = BeautifulSoup(text, "html.parser")
        cleaned = soup.get_text()

        # 清理多余的空白字符
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def clean_content_for_wechat(self, content: str) -> str:
        """专门为微信公众号清理内容格式"""
        if not content:
            return ""
        
        # 1. 清理不需要的标题前缀（保留原始结构）
        prefixes_to_remove = [
            r'📰\s*\*\*优化标题\*\*:\s*',
            r'优化标题:\s*',
            r'📰\s*\*\*标题\*\*:\s*',
            r'标题:\s*',
        ]
        
        for prefix in prefixes_to_remove:
            content = re.sub(prefix, '', content, flags=re.IGNORECASE)
        
        # 2. 适度清理空白字符，保留段落结构
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)  # 多个连续空行合并为两个
        content = re.sub(r'[ \t]+', ' ', content)  # 多个空格合并为一个
        content = re.sub(r'^\s+', '', content, flags=re.MULTILINE)  # 去除行首空格
        content = re.sub(r'\s+$', '', content, flags=re.MULTILINE)  # 去除行尾空格
        
        # 3. 清理HTML中的多余空格（如果已经是HTML）
        if '<' in content and '>' in content:
            content = re.sub(r'>\s+<', '><', content)  # 去除标签间空格
            content = re.sub(r'<p>\s*</p>', '', content)  # 移除空段落
            content = re.sub(r'<div>\s*</div>', '', content)  # 移除空div
        
        return content.strip()

    def markdown_to_html(self, text: str) -> str:
        """将Markdown格式转换为HTML格式，使用pandoc进行转换并清理空格"""
        if not text:
            return ""
        
        try:
            # 先进行基本清理
            text = self.clean_content_for_wechat(text)
            
            # 使用pandoc进行转换
            try:
                import pypandoc
                # 将markdown转换为HTML
                html_content = pypandoc.convert_text(
                    text, 
                    'html', 
                    format='md',
                    extra_args=[
                        '--no-highlight',  # 禁用代码高亮
                        '--wrap=none',     # 不自动换行
                        '--email-obfuscation=none'  # 不混淆邮箱
                    ]
                )
                
                # 进一步清理HTML
                html_content = self.clean_content_for_wechat(html_content)
                
                return html_content
                
            except ImportError:
                logger.warning("pypandoc未安装，使用简单转换")
                return self._simple_markdown_to_html(text)
                
        except Exception as e:
            logger.error(f"Markdown转HTML失败: {e}")
            return self._simple_markdown_to_html(text)
    
    def _simple_markdown_to_html(self, text: str) -> str:
        """简单的Markdown到HTML转换（备用方案）"""
        if not text:
            return ""
        
        # 先进行基本清理
        text = self.clean_content_for_wechat(text)
        
        # 转换标题（在转换其他内容之前）
        text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        
        # 转换列表项（先收集所有列表项）
        lines = text.split('\n')
        processed_lines = []
        in_list = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # 检查是否是列表项
            if re.match(r'^[-\*\+]\s+', line_stripped):
                if not in_list:
                    processed_lines.append('<ul>')
                    in_list = True
                # 转换列表项
                list_content = re.sub(r'^[-\*\+]\s+', '', line_stripped)
                processed_lines.append(f'<li>{list_content}</li>')
            else:
                if in_list:
                    processed_lines.append('</ul>')
                    in_list = False
                processed_lines.append(line)
        
        # 如果文档结束时还在列表中，关闭列表
        if in_list:
            processed_lines.append('</ul>')
        
        text = '\n'.join(processed_lines)
        
        # 转换粗体和斜体
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        # 转换链接 [text](url) -> <a href="url">text</a>
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        
        # 处理段落（避免把已有的HTML标签包装在p标签中）
        paragraphs = text.split('\n\n')
        html_paragraphs = []
        
        for p in paragraphs:
            p = p.strip()
            if p:
                # 检查是否已经是HTML标签（标题、列表等）
                if re.match(r'<(h[1-6]|ul|ol|li)', p) or p.startswith('<'):
                    html_paragraphs.append(p)
                else:
                    # 普通文本包装在p标签中
                    html_paragraphs.append(f'<p>{p}</p>')
        
        result = '\n\n'.join(html_paragraphs)
        
        # 最后清理
        return result

    def _extract_article_metadata(self, content: str) -> tuple[str, dict]:
        """从AI生成的内容中提取评分和标签等元数据"""
        metadata = {}
        
        # 查找评分信息
        score_pattern = r'📊\s*热度评分[：:]\s*(\d+(?:\.\d+)?)'
        score_match = re.search(score_pattern, content)
        if score_match:
            metadata['score'] = float(score_match.group(1))
        
        # 查找目标受众
        audience_pattern = r'🎯\s*目标受众[：:]\s*([^\n]+)'
        audience_match = re.search(audience_pattern, content)
        if audience_match:
            metadata['audience'] = audience_match.group(1).strip()
        
        # 查找标签
        tags_pattern = r'🏷️\s*文章标签[：:]\s*([^\n]+)'
        tags_match = re.search(tags_pattern, content)
        if tags_match:
            tags_text = tags_match.group(1).strip()
            # 提取所有标签，去除HTML标签
            tags_text = re.sub(r'<[^>]+>', '', tags_text)  # 清理HTML标签
            tag_matches = re.findall(r'#([^#\s<>]+)', tags_text)
            metadata['tags'] = tag_matches
        
        # 移除元数据部分，只保留主要内容
        # 查找元数据开始的位置（通常在最后）
        metadata_start = content.find('📊 热度评分')
        if metadata_start == -1:
            metadata_start = content.find('**📊 热度评分')
        
        if metadata_start != -1:
            clean_content = content[:metadata_start].strip()
        else:
            clean_content = content
        
        return clean_content, metadata

    def get_article_engagement_score(self, content: str) -> float:
        """获取文章的参与度评分"""
        try:
            _, metadata = self._extract_article_metadata(content)
            return metadata.get('score', 5.0)  # 默认评分5.0
        except:
            return 5.0

    def get_article_tags(self, content: str) -> list:
        """获取文章标签"""
        try:
            _, metadata = self._extract_article_metadata(content)
            return metadata.get('tags', [])
        except:
            return []

    def summarize_single_item(self, item: RSSItem, sender_type: str = "wechat") -> str:
        """
        为单篇文章生成专门的AI总结

        Args:
            item: 单个RSS条目
            sender_type: 发送源类型 ("wechat", "wechat_official", "xiaohongshu")

        Returns:
            针对该文章的专门总结内容
        """
        if not item:
            return ""

        try:
            # 清理文章内容
            clean_title = item.title.strip()
            clean_desc = self.clean_html(item.description)

            # 根据发送源选择不同的提示词模板
            if sender_type in ["wechat_official", "xiaohongshu"]:
                # 公众号和小红书不限制字数
                prompt = PromptTemplates.get_single_article_prompt(
                    title=clean_title,
                    content=clean_desc[:1000],  # 增加内容长度用于深度分析
                    link=item.link,
                    min_length=0,  # 不限制最小长度
                    max_length=0,  # 不限制最大长度
                    sender_type=sender_type,
                )
                max_tokens = 2000  # 增加token限制
            else:
                # 微信个人号保持原有限制
                prompt = PromptTemplates.get_single_article_prompt(
                    title=clean_title,
                    content=clean_desc[:500],  # 限制内容长度避免token超限
                    link=item.link,
                    min_length=Config.SUMMARY_MIN_LENGTH,
                    max_length=Config.SUMMARY_MAX_LENGTH,
                    sender_type=sender_type,
                )
                max_tokens = 800

            # 调用AI API，使用发送源对应的系统角色
            response = self.client.chat.completions.create(
                model="deepseek-chat",  # 使用DeepSeek模型
                messages=[
                    {
                        "role": "system",
                        "content": PromptTemplates.get_system_role(
                            "content_strategist", sender_type
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.8,
            )

            summary = response.choices[0].message.content.strip()

            # 解析和处理评分标签信息（仅对微信公众号）
            if sender_type == "wechat_official":
                summary, metadata = self._extract_article_metadata(summary)
                
                # 记录评分和标签信息
                if metadata:
                    logger.info(f"文章元数据 - 热度评分: {metadata.get('score', 'N/A')}, "
                              f"目标受众: {metadata.get('audience', 'N/A')}, "
                              f"标签: {metadata.get('tags', 'N/A')}")
                
                if "延伸阅读" not in summary and "原文链接" not in summary and item.link not in summary:
                    summary += f"\n\n🔗 **延伸阅读**：[查看完整技术详情]({item.link})"
                # 对微信公众号内容进行Markdown到HTML转换
                summary = self.markdown_to_html(summary)
            elif sender_type == "xiaohongshu":
                if "了解更多" not in summary and "原文" not in summary and item.link not in summary:
                    summary += f"\n\n📖 想了解更多技术细节？👆点击查看原文哦~\n{item.link}"
            else:
                if "阅读原文" not in summary and item.link not in summary:
                    summary += f"\n\n📖 阅读原文：{item.link}"

            logger.info(f"单篇文章AI总结完成 ({sender_type}) - 标题: {clean_title[:30]}..., 字数: {len(summary)}")
            return summary

        except Exception as e:
            logger.error(f"单篇文章AI总结失败: {e}")
            # 降级到简单总结
            return self._simple_single_summary(item)

    def summarize_items(self, items: List[RSSItem], sender_type: str = "wechat") -> str:
        """
        为多个RSS条目生成总结（保持向后兼容）
        现在改为分别总结每篇文章

        Args:
            items: RSS条目列表
            sender_type: 发送源类型

        Returns:
            总结后的微信消息内容
        """
        if not items:
            return ""

        # 如果只有一篇文章，直接使用单篇总结
        if len(items) == 1:
            return self.summarize_single_item(items[0], sender_type)

        # 多篇文章时，生成简化的汇总
        try:
            summaries = []
            for item in items[:3]:  # 最多处理3篇
                summary = self.summarize_single_item(item)
                if summary:
                    summaries.append(f"📰 {item.title}\n{summary}")

            if summaries:
                return "\n\n" + "=" * 20 + "\n\n".join(summaries)
            else:
                return self._simple_summary(items)

        except Exception as e:
            logger.error(f"批量文章总结失败: {e}")
            return self._simple_summary(items)

    def _simple_single_summary(self, item: RSSItem) -> str:
        """单篇文章的简单总结方式（当AI失败时使用）"""
        if not item:
            return ""

        # 清理标题和描述
        clean_title = item.title.strip()
        clean_desc = self.clean_html(item.description)

        # 生成简单但结构化的总结
        summary = f"📰 {clean_title}\n\n"

        # 添加描述（截断到合适长度）
        if clean_desc:
            desc_limit = Config.SUMMARY_MAX_LENGTH - len(summary) - 100  # 为链接预留空间
            if len(clean_desc) > desc_limit:
                summary += f"💡 {clean_desc[:desc_limit]}...\n\n"
            else:
                summary += f"💡 {clean_desc}\n\n"

        # 添加链接
        summary += f"🔗 阅读原文：{item.link}"

        return summary

    def _simple_summary(self, items: List[RSSItem]) -> str:
        """简单的总结方式（当AI失败时使用）"""
        if not items:
            return ""

        summary = f"📰 最新资讯 ({len(items)}条)\n\n"

        for i, item in enumerate(items[:3], 1):
            summary += f"{i}. {item.title}\n"
            if len(summary) > Config.SUMMARY_MAX_LENGTH:
                summary = summary[: Config.SUMMARY_MAX_LENGTH - 10] + "..."
                break

        summary += "\n🔗 查看详情："
        for i, item in enumerate(items[:3], 1):
            return summary

    def classify_article(self, item: RSSItem) -> str:
        """
        对文章进行分类

        Args:
            item: RSS条目

        Returns:
            文章分类（Technology, Development, Entertainment, Finance, Health, Politics, Other）
        """
        if not item:
            return "Other"

        try:
            # 准备文章内容
            content = f"Title: {item.title}\nContent: {self.clean_html(item.description)[:300]}"

            response = self.client.chat.completions.create(
                model="deepseek-chat",  # 文章分类使用DeepSeek模型
                messages=[
                    {
                        "role": "system",
                        "content": PromptTemplates.get_system_role("content_analyst"),
                    },
                    {
                        "role": "user",
                        "content": f"{PromptTemplates.ARTICLE_CLASSIFICATION}\n\nContent:\n{content}",
                    },
                ],
                max_tokens=50,
                temperature=0.1,
            )

            category = response.choices[0].message.content.strip()
            logger.info(f"文章分类完成: {item.title[:30]}... -> {category}")
            return category

        except Exception as e:
            logger.error(f"文章分类失败: {e}")
            return "Other"

    def generate_tags(self, item: RSSItem) -> str:
        """
        为文章生成标签

        Args:
            item: RSS条目

        Returns:
            文章标签（逗号分隔）
        """
        if not item:
            return ""

        try:
            # 准备文章内容
            content = f"Title: {item.title}\nContent: {self.clean_html(item.description)[:300]}"

            response = self.client.chat.completions.create(
                model="deepseek-chat",  # 标签生成使用DeepSeek模型
                messages=[
                    {
                        "role": "system",
                        "content": PromptTemplates.get_system_role("content_analyst"),
                    },
                    {
                        "role": "user",
                        "content": f"{PromptTemplates.ARTICLE_TAGS}\n\nContent:\n{content}",
                    },
                ],
                max_tokens=100,
                temperature=0.3,
            )

            tags = response.choices[0].message.content.strip()
            logger.info(f"标签生成完成: {item.title[:30]}... -> {tags}")
            return tags

        except Exception as e:
            logger.error(f"标签生成失败: {e}")
            return ""

    def score_article(self, item: RSSItem) -> int:
        """
        为文章评分

        Args:
            item: RSS条目

        Returns:
            文章评分（0-10）
        """
        if not item:
            return 0

        try:
            # 准备文章内容
            content = f"Title: {item.title}\nContent: {self.clean_html(item.description)[:500]}"

            response = self.client.chat.completions.create(
                model="deepseek-chat",  # 文章评分使用DeepSeek模型
                messages=[
                    {
                        "role": "system",
                        "content": PromptTemplates.get_system_role("content_analyst"),
                    },
                    {
                        "role": "user",
                        "content": f"{PromptTemplates.ARTICLE_SCORING}\n\nContent:\n{content}",
                    },
                ],
                max_tokens=20,
                temperature=0.1,
            )

            score_text = response.choices[0].message.content.strip()
            try:
                score = int(score_text)
                score = max(0, min(10, score))  # 确保分数在0-10范围内
            except ValueError:
                score = 5  # 默认分数

            logger.info(f"文章评分完成: {item.title[:30]}... -> {score}")
            return score

        except Exception as e:
            logger.error(f"文章评分失败: {e}")
            # 基于简单规则的降级评分
            return self._simple_score_article(item)

    def _simple_score_article(self, item: RSSItem) -> int:
        """
        简单的文章评分方法（当AI失败时使用）
        基于标题长度、描述长度和关键词来评分
        """
        score = 5  # 基础分数

        try:
            # 标题质量评分
            title_len = len(item.title.strip())
            if title_len > 10:
                score += 1
            if title_len > 20:
                score += 1

            # 描述质量评分
            desc_len = len(self.clean_html(item.description))
            if desc_len > 100:
                score += 1
            if desc_len > 300:
                score += 1

            # 关键词加分
            quality_keywords = [
                "获奖",
                "突破",
                "创新",
                "发布",
                "宣布",
                "合作",
                "投资",
                "融资",
                "上市",
                "收购",
            ]
            content_text = (item.title + " " + item.description).lower()
            for keyword in quality_keywords:
                if keyword in content_text:
                    score += 0.5
                    break

            score = max(0, min(10, int(score)))
            logger.info(f"简单评分完成: {item.title[:30]}... -> {score}")
            return score

        except Exception as e:
            logger.error(f"简单评分也失败: {e}")
            return 5

    def _extract_quality_info(self, response_text: str) -> dict:
        """从AI响应中提取质量信息
        
        Args:
            response_text: AI响应文本
            
        Returns:
            包含quality_score, summary, reasoning等字段的字典
        """
        try:
            import json
            # 尝试解析JSON格式的响应
            data = json.loads(response_text.strip())
            return {
                'quality_score': data.get('quality_score', 5),
                'summary': data.get('summary', ''),
                'reasoning': data.get('reasoning', ''),
                'key_points': data.get('key_points', [])
            }
        except (json.JSONDecodeError, ValueError):
            # 如果不是JSON格式，尝试从文本中提取分数
            import re
            score_match = re.search(r'(?:quality_score|评分|分数).*?(\d+)', response_text, re.IGNORECASE)
            score = int(score_match.group(1)) if score_match else 5
            
            return {
                'quality_score': min(10, max(0, score)),
                'summary': response_text[:200] if len(response_text) > 200 else response_text,
                'reasoning': '无法解析详细评分信息',
                'key_points': []
            }
