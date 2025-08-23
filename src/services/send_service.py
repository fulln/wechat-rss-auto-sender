"""
发送管理器模块
"""
import random
from datetime import datetime, timedelta
from typing import List, Optional

from ..core.config import Config
from ..core.utils import setup_logger
from ..integrations.send_service_manager import SendServiceManager
from .ai_service import Summarizer
from .multi_rss_manager import MultiRSSManager, RSSItem

logger = setup_logger(__name__)


class SendManager:
    """发送管理器 - 控制文章发送策略"""

    def __init__(self):
        # 使用多RSS管理器替代单一RSS获取器
        self.multi_rss_manager = MultiRSSManager()
        self.summarizer = Summarizer()
        self.send_service_manager = SendServiceManager()
        self.last_send_time: Optional[datetime] = None

        # 检查是否有启用的发送器
        if not self.send_service_manager.has_enabled_senders():
            logger.warning("没有启用的发送器，请检查配置")
        else:
            enabled_senders = self.send_service_manager.get_enabled_senders()
            logger.info(f"已启用的发送器: {', '.join(enabled_senders)}")

    def is_send_time_allowed(self) -> bool:
        """检查当前时间是否允许发送（晚上12点到早上9点不发送）"""
        current_hour = datetime.now().hour

        # 如果结束时间是0（午夜），表示跨天的时间段
        if Config.SEND_END_HOUR == 0 or Config.SEND_END_HOUR == 24:
            # 从开始时间到23:59，或者从0:00到结束时间
            if Config.SEND_START_HOUR <= current_hour <= 23:
                return True
            elif 0 <= current_hour < Config.SEND_START_HOUR:
                return False
        else:
            # 普通的一天内时间段
            if Config.SEND_START_HOUR <= current_hour < Config.SEND_END_HOUR:
                return True

        return False

    def can_send_now(self) -> bool:
        """检查当前是否可以发送（考虑时间段限制和发送间隔）"""
        # 首先检查时间段限制
        if not self.is_send_time_allowed():
            current_hour = datetime.now().hour
            logger.info(
                f"当前时间 {current_hour}:xx 不在允许发送时段内（{Config.SEND_START_HOUR}:00-{Config.SEND_END_HOUR}:00）"
            )
            return False

        # 然后检查发送间隔
        if not self.last_send_time:
            return True

        time_since_last = datetime.now() - self.last_send_time
        min_interval = timedelta(minutes=Config.SEND_INTERVAL_MINUTES)

        return time_since_last >= min_interval

    def get_next_send_time(self) -> Optional[datetime]:
        """获取下次可发送时间（包含随机延迟）"""
        if not self.last_send_time:
            base_time = datetime.now()
        else:
            base_time = self.last_send_time + timedelta(
                minutes=Config.SEND_INTERVAL_MINUTES
            )

        # 添加随机延迟（0-15秒）
        random_delay = random.randint(0, Config.SEND_RANDOM_DELAY_MAX)
        next_time = base_time + timedelta(seconds=random_delay)

        # 如果计算出的时间在不允许发送的时段内，调整到下个允许的时段
        while not self._is_time_in_allowed_period(next_time):
            # 调整到下个允许发送的时间段开始
            next_day = next_time.date() + timedelta(days=1)
            next_time = datetime.combine(next_day, datetime.min.time()) + timedelta(
                hours=Config.SEND_START_HOUR
            )
            # 重新添加随机延迟
            random_delay = random.randint(0, Config.SEND_RANDOM_DELAY_MAX)
            next_time += timedelta(seconds=random_delay)

        if next_time <= datetime.now():
            return datetime.now()
        return next_time

    def _is_time_in_allowed_period(self, check_time: datetime) -> bool:
        """检查指定时间是否在允许发送的时段内"""
        hour = check_time.hour

        if Config.SEND_END_HOUR == 0 or Config.SEND_END_HOUR == 24:
            # 跨天时间段
            if Config.SEND_START_HOUR <= hour <= 23:
                return True
            elif 0 <= hour < Config.SEND_START_HOUR:
                return False
        else:
            # 普通时间段
            if Config.SEND_START_HOUR <= hour < Config.SEND_END_HOUR:
                return True

        return False

    def select_articles_to_send(self, max_count: int = None) -> List[RSSItem]:
        """选择要发送的文章（添加质量评分筛选，只发送高质量文章）"""
        # 获取未发送的文章
        unsent_items = self.multi_rss_manager.cache.get_unsent_items()

        if not unsent_items:
            logger.info("没有待发送的文章")
            return []

        # 对文章进行质量评分筛选
        logger.info(f"开始对 {len(unsent_items)} 篇文章进行质量评分...")
        qualified_articles = []

        for article in unsent_items:
            try:
                # 检查是否已有评分，避免重复评分
                if article.quality_score is None:
                    logger.info(f"为文章评分: {article.title[:50]}...")
                    score = self.summarizer.score_article(article)
                    article.set_quality_score(score)
                    # 更新缓存中的评分信息
                    self.multi_rss_manager.cache.update_item_sent_status(article)
                else:
                    score = article.quality_score
                    logger.info(f"使用已有评分: {article.title[:50]}... (评分: {score}/10)")

                # 只选择评分达到要求的文章
                if score >= Config.MIN_QUALITY_SCORE:
                    qualified_articles.append((article, score))
                    logger.info(f"✅ 文章通过质量检查: {article.title[:50]}... (评分: {score}/10)")
                else:
                    logger.info(
                        f"❌ 文章未达到质量要求: {article.title[:50]}... (评分: {score}/10, 需要: {Config.MIN_QUALITY_SCORE}/10)"
                    )

            except Exception as e:
                logger.error(f"文章评分失败: {article.title[:50]}... - {e}")
                continue

        if not qualified_articles:
            logger.info(f"没有文章达到最低质量要求（{Config.MIN_QUALITY_SCORE}/10分）")
            return []

        # 按评分排序，选择质量最高的文章
        qualified_articles.sort(key=lambda x: x[1], reverse=True)

        # 一次只选择一篇质量最高的文章
        best_article, best_score = qualified_articles[0]
        selected = [best_article]

        logger.info(f"选择最高质量文章准备发送: {best_article.title[:50]}... (评分: {best_score}/10)")
        logger.info(f"质量合格文章总数: {len(qualified_articles)}, 待检查总数: {len(unsent_items)}")
        return selected

    def send_single_article(self, article: RSSItem) -> bool:
        """发送单篇文章（使用专门的AI总结）"""
        if not article:
            return True

        if not self.can_send_now():
            next_time = self.get_next_send_time()
            logger.info(f"发送间隔未到，下次可发送时间: {next_time}")
            return False

        try:
            # 记录发送尝试
            article.mark_send_attempt()
            self.multi_rss_manager.cache.update_item_sent_status(article)
            
            # 使用新的单篇文章专门总结功能
            summary = self.summarizer.summarize_single_item(article)

            if not summary:
                error_msg = "AI总结失败"
                article.mark_send_failed(error_msg)
                self.multi_rss_manager.cache.update_item_sent_status(article)
                logger.warning(f"文章AI总结失败，跳过发送: {article.title}")
                return False

            # 发送到所有启用的发送器
            send_results = self.send_service_manager.send_message(summary)
            
            # 检查是否至少有一个发送器发送成功
            success = any(send_results.values()) if send_results else False

            if success:
                # 标记文章为已发送
                article.mark_as_sent()
                self.multi_rss_manager.cache.update_item_sent_status(article)

                self.last_send_time = datetime.now()

                title_preview = (
                    article.title[:50] + "..."
                    if len(article.title) > 50
                    else article.title
                )
                logger.info(f"成功发送文章: {title_preview}")
                return True
            else:
                # 记录发送失败
                failed_senders = [k for k, v in send_results.items() if not v] if send_results else ["all"]
                error_msg = f"发送器失败: {', '.join(failed_senders)}"
                article.mark_send_failed(error_msg)
                self.multi_rss_manager.cache.update_item_sent_status(article)
                logger.error(f"微信发送失败: {article.title} - {error_msg}")
                return False

        except Exception as e:
            # 记录发送异常
            error_msg = f"发送异常: {str(e)}"
            article.mark_send_failed(error_msg)
            self.multi_rss_manager.cache.update_item_sent_status(article)
            logger.error(f"发送文章时出错: {e}")
            return False

    def process_pending_articles(self) -> int:
        """处理待发送的文章（改为单篇发送模式）"""
        try:
            # 检查是否可以发送
            if not self.can_send_now():
                next_time = self.get_next_send_time()
                wait_seconds = (next_time - datetime.now()).total_seconds()
                logger.info(f"等待发送间隔，剩余 {wait_seconds:.0f} 秒")
                return 0

            # 选择要发送的文章（现在一次只选择一篇）
            articles = self.select_articles_to_send()

            if not articles:
                return 0

            # 发送单篇文章（使用专门的AI总结）
            article = articles[0]
            if self.send_single_article(article):
                return 1
            else:
                return 0

        except Exception as e:
            logger.error(f"处理待发送文章时出错: {e}")
            return 0

    # 保持向后兼容的批量发送方法
    def send_articles_batch(self, articles: List[RSSItem]) -> bool:
        """批量发送文章（保持向后兼容）"""
        if not articles:
            return True

        # 如果只有一篇文章，使用单篇发送
        if len(articles) == 1:
            return self.send_single_article(articles[0])

        # 多篇文章时使用原有逻辑
        if not self.can_send_now():
            next_time = self.get_next_send_time()
            logger.info(f"发送间隔未到，下次可发送时间: {next_time}")
            return False

        try:
            # 记录所有文章的发送尝试
            for article in articles:
                article.mark_send_attempt()
                self.multi_rss_manager.cache.update_item_sent_status(article)
            
            # 使用多篇文章总结
            summary = self.summarizer.summarize_items(articles)

            if not summary:
                error_msg = "批量AI总结失败"
                for article in articles:
                    article.mark_send_failed(error_msg)
                    self.multi_rss_manager.cache.update_item_sent_status(article)
                logger.warning("AI总结失败，跳过发送")
                return False

            # 发送到所有启用的发送器
            send_results = self.send_service_manager.send_message(summary)
            
            # 检查是否至少有一个发送器发送成功
            success = any(send_results.values()) if send_results else False

            if success:
                # 标记文章为已发送
                for article in articles:
                    article.mark_as_sent()
                    self.multi_rss_manager.cache.update_item_sent_status(article)

                self.last_send_time = datetime.now()

                titles = [
                    article.title[:30] + "..."
                    if len(article.title) > 30
                    else article.title
                    for article in articles
                ]
                logger.info(f"成功发送 {len(articles)} 篇文章: {', '.join(titles)}")
                return True
            else:
                # 记录批量发送失败
                failed_senders = [k for k, v in send_results.items() if not v] if send_results else ["all"]
                error_msg = f"批量发送失败: {', '.join(failed_senders)}"
                for article in articles:
                    article.mark_send_failed(error_msg)
                    self.multi_rss_manager.cache.update_item_sent_status(article)
                logger.error(f"微信批量发送失败 - {error_msg}")
                return False

        except Exception as e:
            # 记录批量发送异常
            error_msg = f"批量发送异常: {str(e)}"
            for article in articles:
                article.mark_send_failed(error_msg)
                self.multi_rss_manager.cache.update_item_sent_status(article)
            logger.error(f"批量发送文章时出错: {e}")
            return False

    def get_send_status(self) -> dict:
        """获取发送状态"""
        unsent_count = len(self.multi_rss_manager.cache.get_unsent_items())

        return {
            "unsent_articles_count": unsent_count,
            "last_send_time": self.last_send_time.isoformat()
            if self.last_send_time
            else None,
            "can_send_now": self.can_send_now(),
            "next_send_time": self.get_next_send_time().isoformat()
            if self.get_next_send_time()
            else None,
            "max_articles_per_batch": Config.MAX_ARTICLES_PER_BATCH,
            "send_interval_minutes": Config.SEND_INTERVAL_MINUTES,
        }
