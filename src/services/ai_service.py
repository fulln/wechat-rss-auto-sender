"""
AI总结模块
"""
import re
from typing import List

from bs4 import BeautifulSoup
from openai import OpenAI

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

        # 获取代理配置
        proxies = Config.get_proxies() if hasattr(Config, 'get_proxies') else None
        client_kwargs = {
            "api_key": Config.OPENAI_API_KEY,
            "base_url": Config.OPENAI_BASE_URL
        }
        if proxies:
            import httpx
            # 尝试多种代理配置方式以兼容不同版本的httpx
            try:
                # 方式1: 使用proxy参数 (新版本)
                proxy_url = proxies.get('https') or proxies.get('http')
                if proxy_url:
                    client_kwargs["http_client"] = httpx.Client(proxy=proxy_url)
                    logger.info(f"Summarizer使用代理 (proxy): {proxy_url}")
            except Exception as e1:
                try:
                    # 方式2: 使用proxies参数 (旧版本)
                    client_kwargs["http_client"] = httpx.Client(proxies=proxies)
                    logger.info(f"Summarizer使用代理 (proxies): {proxies}")
                except Exception as e2:
                    logger.warning(f"代理配置失败，使用默认连接. 错误1: {e1}, 错误2: {e2}")
        
        try:
            self.client = OpenAI(**client_kwargs)
        except Exception as e:
            logger.error(f"OpenAI客户端初始化失败: {e}")
            # 如果代理配置有问题，尝试不使用代理
            if "proxies" in str(e) or "proxy" in str(e):
                logger.info("尝试不使用代理重新初始化...")
                client_kwargs_no_proxy = {
                    "api_key": Config.OPENAI_API_KEY,
                    "base_url": Config.OPENAI_BASE_URL
                }
                self.client = OpenAI(**client_kwargs_no_proxy)
                logger.info("OpenAI客户端已使用默认连接初始化")
            else:
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

    def summarize_single_item(self, item: RSSItem) -> str:
        """
        为单篇文章生成专门的AI总结

        Args:
            item: 单个RSS条目

        Returns:
            针对该文章的专门总结内容
        """
        if not item:
            return ""

        try:
            # 清理文章内容
            clean_title = item.title.strip()
            clean_desc = self.clean_html(item.description)

            # 使用新的提示词模板
            prompt = PromptTemplates.get_single_article_prompt(
                title=clean_title,
                content=clean_desc[:500],  # 限制内容长度避免token超限
                link=item.link,
                min_length=Config.SUMMARY_MIN_LENGTH,
                max_length=Config.SUMMARY_MAX_LENGTH,
            )

            # 调用AI API，使用专门的系统角色
            response = self.client.chat.completions.create(
                model="deepseek-chat",  # 使用DeepSeek模型
                messages=[
                    {
                        "role": "system",
                        "content": PromptTemplates.get_system_role(
                            "content_strategist"
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=800,  # 增加token限制以支持更丰富的内容
                temperature=0.8,
            )

            summary = response.choices[0].message.content.strip()

            # 确保包含原文链接
            if "阅读原文" not in summary and item.link not in summary:
                summary += f"\n\n📖 阅读原文：{item.link}"

            logger.info(f"单篇文章AI总结完成 - 标题: {clean_title[:30]}..., 字数: {len(summary)}")
            return summary

        except Exception as e:
            logger.error(f"单篇文章AI总结失败: {e}")
            # 降级到简单总结
            return self._simple_single_summary(item)

    def summarize_items(self, items: List[RSSItem]) -> str:
        """
        为多个RSS条目生成总结（保持向后兼容）
        现在改为分别总结每篇文章

        Args:
            items: RSS条目列表

        Returns:
            总结后的微信消息内容
        """
        if not items:
            return ""

        # 如果只有一篇文章，直接使用单篇总结
        if len(items) == 1:
            return self.summarize_single_item(items[0])

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
