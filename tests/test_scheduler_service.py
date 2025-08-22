"""调度服务的单元测�?""

import threading
import time
from unittest.mock import Mock, patch

import pytest

from src.services.scheduler_service import NewsScheduler


class TestNewsScheduler:
    """新闻调度器测�?""

    @patch("src.services.scheduler_service.SendManager")
    def test_scheduler_initialization(self, mock_send_manager: Mock) -> None:
        """测试调度器初始化"""
        scheduler = NewsScheduler()

        assert scheduler.send_manager is not None
        assert scheduler.running is False
        mock_send_manager.assert_called_once()

    @patch("src.services.scheduler_service.SendManager")
    @patch("src.services.scheduler_service.schedule")
    def test_setup_schedule(self, mock_schedule: Mock, mock_send_manager: Mock) -> None:
        """测试调度任务设置"""
        scheduler = NewsScheduler()
        scheduler.setup_schedule()

        # 验证调度任务被正确设�?
        mock_schedule.every.assert_called()

    @patch("src.services.scheduler_service.SendManager")
    def test_process_news_task(self, mock_send_manager: Mock) -> None:
        """测试新闻处理任务"""
        mock_manager_instance = Mock()
        mock_manager_instance.process_and_send_articles.return_value = 2
        mock_send_manager.return_value = mock_manager_instance

        scheduler = NewsScheduler()
        scheduler.process_news_task()

        mock_manager_instance.process_and_send_articles.assert_called_once()

    @patch("src.services.scheduler_service.SendManager")
    @patch("src.services.scheduler_service.schedule")
    def test_start_scheduler(
        self, mock_schedule: Mock, mock_send_manager: Mock
    ) -> None:
        """测试启动调度�?""
        # 模拟schedule.run_pending不会无限循环
        mock_schedule.run_pending.return_value = None

        scheduler = NewsScheduler()

        # 在另一个线程中启动调度器，避免阻塞测试
        def start_and_stop():
            scheduler.start()
            time.sleep(0.1)  # 让调度器运行一会儿
            scheduler.stop()

        thread = threading.Thread(target=start_and_stop)
        thread.start()
        thread.join(timeout=1.0)

        # 验证调度器状�?
        assert scheduler.running is False

    @patch("src.services.scheduler_service.SendManager")
    def test_stop_scheduler(self, mock_send_manager: Mock) -> None:
        """测试停止调度�?""
        scheduler = NewsScheduler()
        scheduler.running = True

        scheduler.stop()

        assert scheduler.running is False

    @patch("src.services.scheduler_service.SendManager")
    def test_get_status(self, mock_send_manager: Mock) -> None:
        """测试获取调度器状�?""
        mock_manager_instance = Mock()
        mock_manager_instance.get_send_status.return_value = {
            "is_send_time_allowed": True,
            "max_articles_per_batch": 3,
        }
        mock_send_manager.return_value = mock_manager_instance

        scheduler = NewsScheduler()
        status = scheduler.get_status()

        assert isinstance(status, dict)
        assert "running" in status
        assert "send_manager_status" in status
        assert status["running"] is False

    @patch("src.services.scheduler_service.SendManager")
    def test_error_handling_in_process_news_task(self, mock_send_manager: Mock) -> None:
        """测试新闻处理任务中的错误处理"""
        mock_manager_instance = Mock()
        mock_manager_instance.process_and_send_articles.side_effect = Exception("处理错误")
        mock_send_manager.return_value = mock_manager_instance

        scheduler = NewsScheduler()

        # 应该不抛出异常，而是记录日志
        try:
            scheduler.process_news_task()
        except Exception:
            pytest.fail("process_news_task应该处理异常而不是抛�?)

    @patch("src.services.scheduler_service.SendManager")
    @patch("src.services.scheduler_service.time.sleep")
    def test_scheduler_loop_behavior(
        self, mock_sleep: Mock, mock_send_manager: Mock
    ) -> None:
        """测试调度器循环行�?""
        scheduler = NewsScheduler()

        # 模拟一个短暂的运行周期
        call_count = 0

        def mock_sleep_side_effect(duration):
            nonlocal call_count
            call_count += 1
            if call_count >= 2:  # 在第二次sleep后停�?
                scheduler.stop()

        mock_sleep.side_effect = mock_sleep_side_effect

        with patch("src.services.scheduler_service.schedule.run_pending"):
            scheduler.start()

        assert call_count >= 1  # 至少被调用了一�?


class TestNewsSchedulerIntegration:
    """新闻调度器集成测�?""

    @patch("src.services.scheduler_service.SendManager")
    def test_full_scheduler_cycle(self, mock_send_manager: Mock) -> None:
        """测试完整的调度周�?""
        # 模拟发送管理器
        mock_manager_instance = Mock()
        mock_manager_instance.process_and_send_articles.return_value = 1
        mock_manager_instance.get_send_status.return_value = {
            "is_send_time_allowed": True,
            "max_articles_per_batch": 3,
            "send_interval_minutes": 1,
            "min_quality_score": 7,
        }
        mock_send_manager.return_value = mock_manager_instance

        scheduler = NewsScheduler()

        # 执行一次任务处�?
        scheduler.process_news_task()

        # 获取状�?
        status = scheduler.get_status()

        # 验证结果
        mock_manager_instance.process_and_send_articles.assert_called_once()
        assert status["running"] is False
        assert "send_manager_status" in status

    @patch("src.services.scheduler_service.SendManager")
    @patch("src.services.scheduler_service.schedule")
    def test_schedule_configuration(
        self, mock_schedule: Mock, mock_send_manager: Mock
    ) -> None:
        """测试调度配置"""
        scheduler = NewsScheduler()
        scheduler.setup_schedule()

        # 验证调度配置是否按照Config设置
        mock_schedule.every.assert_called()
        # 可以进一步验证调度间隔是否正�?

    @patch("src.services.scheduler_service.SendManager")
    def test_concurrent_scheduler_safety(self, mock_send_manager: Mock) -> None:
        """测试调度器并发安全�?""
        scheduler = NewsScheduler()

        # 测试多次启动和停�?
        for _ in range(3):
            scheduler.start()
            time.sleep(0.01)
            scheduler.stop()

        # 调度器应该能正常处理多次启动/停止
        assert scheduler.running is False

    @patch("src.services.scheduler_service.SendManager")
    def test_scheduler_with_real_time_constraints(
        self, mock_send_manager: Mock
    ) -> None:
        """测试调度器在实际时间约束下的行为"""
        mock_manager_instance = Mock()

        # 模拟不同时间的发送状�?
        def get_status_side_effect():
            import random

            return {
                "is_send_time_allowed": random.choice([True, False]),
                "max_articles_per_batch": 3,
            }

        mock_manager_instance.get_send_status.side_effect = get_status_side_effect
        mock_manager_instance.process_and_send_articles.return_value = 0
        mock_send_manager.return_value = mock_manager_instance

        scheduler = NewsScheduler()

        # 执行多次任务处理
        for _ in range(5):
            scheduler.process_news_task()

        # 验证任务被正确执�?
        assert mock_manager_instance.process_and_send_articles.call_count == 5

