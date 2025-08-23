"""
任务调度模块
"""
import threading
import time
from datetime import datetime

import schedule

from ..core.config import Config
from ..core.utils import setup_logger
from .send_service import SendManager
from .multi_rss_manager import MultiRSSManager

logger = setup_logger(__name__)


class NewsScheduler:
    """新闻推送调度器"""

    def __init__(self):
        # 使用多RSS管理器
        self.multi_rss_manager = MultiRSSManager()
        self.send_manager = SendManager()
        self.is_running = False
        self._thread = None

    def fetch_new_articles(self):
        """获取新文章并加入缓存"""
        try:
            logger.info("开始检查RSS更新...")

            # 使用多RSS管理器获取最新文章
            items = self.multi_rss_manager.fetch_latest_items(
                since_minutes=Config.CHECK_INTERVAL_MINUTES * 60  # 转换为分钟
            )

            if not items:
                logger.info("没有新的文章")
                return 0

            logger.info(f"发现 {len(items)} 篇新文章，已加入发送队列")
            return len(items)

        except Exception as e:
            logger.error(f"检查RSS更新时发生错误: {e}")
            return 0

    def process_send_queue(self):
        """处理发送队列"""
        try:
            logger.info("检查发送队列...")
            sent_count = self.send_manager.process_pending_articles()

            if sent_count > 0:
                logger.info(f"成功发送 {sent_count} 篇文章")

            # 显示发送状态
            status = self.send_manager.get_send_status()
            if status["unsent_articles_count"] > 0:
                logger.info(f"待发送文章数: {status['unsent_articles_count']}")
                if not status["can_send_now"] and status["next_send_time"]:
                    logger.info(f"下次发送时间: {status['next_send_time']}")

            return sent_count

        except Exception as e:
            logger.error(f"处理发送队列时发生错误: {e}")
            return 0

    def run_cycle(self):
        """运行一个完整的检查周期"""
        try:
            logger.info("=" * 50)
            logger.info("开始新的检查周期")

            # 1. 获取新文章
            new_count = self.fetch_new_articles()

            # 2. 处理发送队列
            sent_count = self.process_send_queue()

            logger.info(f"周期结束 - 新增文章: {new_count}, 发送文章: {sent_count}")
            logger.info("=" * 50)

        except Exception as e:
            logger.error(f"运行周期时发生错误: {e}")

    def start(self):
        """启动调度器"""
        if self.is_running:
            logger.warning("调度器已在运行")
            return

        try:
            # 测试各个组件
            logger.info("正在测试各个组件...")

            # 测试发送器连接
            connection_results = self.send_manager.send_service_manager.test_all_connections()
            if not connection_results:
                logger.error("没有可用的发送器")
                return
            
            failed_senders = [name for name, result in connection_results.items() if not result]
            if failed_senders:
                logger.warning(f"以下发送器连接失败: {', '.join(failed_senders)}")
            
            successful_senders = [name for name, result in connection_results.items() if result]
            if successful_senders:
                logger.info(f"以下发送器连接成功: {', '.join(successful_senders)}")
            else:
                logger.error("所有发送器连接失败")
                return

            # 测试RSS源连接
            rss_sources = self.multi_rss_manager.rss_sources
            if rss_sources:
                logger.info(f"已配置 {len(rss_sources)} 个RSS源，第一个源: {rss_sources[0].name}")
            else:
                logger.warning("未配置RSS源")

            # 配置定时任务
            # 每隔检查间隔时间运行一次完整周期
            schedule.every(Config.CHECK_INTERVAL_MINUTES).minutes.do(self.run_cycle)

            # 每分钟检查一次发送队列（处理待发送文章）
            schedule.every(1).minutes.do(self.process_send_queue)

            logger.info("调度器启动成功")
            logger.info(f"RSS检查间隔: {Config.CHECK_INTERVAL_MINUTES} 分钟")
            logger.info("发送队列检查间隔: 1 分钟")
            logger.info(f"每批最多发送: {Config.MAX_ARTICLES_PER_BATCH} 篇文章")
            logger.info(f"发送间隔: {Config.SEND_INTERVAL_MINUTES} 分钟")

            # 立即执行一次检查
            logger.info("执行首次检查...")
            self.run_cycle()

            # 在后台线程中运行
            self.is_running = True
            self._thread = threading.Thread(target=self._run_schedule, daemon=True)
            self._thread.start()

            logger.info("调度器已在后台运行")

        except Exception as e:
            logger.error(f"启动调度器失败: {e}")
            self.is_running = False

    def stop(self):
        """停止调度器"""
        if not self.is_running:
            logger.warning("调度器未在运行")
            return

        self.is_running = False
        schedule.clear()
        logger.info("调度器已停止")

    def _run_schedule(self):
        """运行调度循环"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"调度循环错误: {e}")
                time.sleep(5)

    def get_status(self) -> dict:
        """获取调度器状态"""
        send_status = self.send_manager.get_send_status()

        return {
            "is_running": self.is_running,
            "next_run": schedule.next_run() if schedule.jobs else None,
            "jobs_count": len(schedule.jobs),
            "current_time": datetime.now().isoformat(),
            "send_status": send_status,
        }

    def setup_schedule(self):
        """设置定时任务计划"""
        try:
            # 清除之前的任务
            schedule.clear()
            
            # 设置定期任务
            interval_minutes = Config.CHECK_INTERVAL_MINUTES
            schedule.every(interval_minutes).minutes.do(self.process_news_task)
            
            logger.info(f"定时任务已设置，间隔: {interval_minutes} 分钟")
        except Exception as e:
            logger.error(f"设置定时任务失败: {e}")

    def process_news_task(self):
        """处理新闻任务 - 获取、处理和发送文章"""
        try:
            logger.info("开始处理新闻任务...")
            
            # 获取新文章
            new_count = self.fetch_new_articles()
            
            # 发送队列中的文章
            sent_count = self.process_send_queue()
            
            logger.info(f"新闻任务完成 - 新增: {new_count}, 发送: {sent_count}")
        except Exception as e:
            logger.error(f"处理新闻任务时发生错误: {e}")
            # 不重新抛出异常，让调度器继续运行

    @property
    def running(self) -> bool:
        """兼容性属性：running -> is_running"""
        return self.is_running
