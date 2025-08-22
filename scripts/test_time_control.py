#!/usr/bin/env python3
"""
测试时间控制和随机延迟功能
"""
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.send_manager import SendManager
from src.utils import setup_logger

logger = setup_logger(__name__)

def test_time_control():
    """测试时间控制功能"""
    print("=== 时间控制和随机延迟功能测试 ===\n")
    
    try:
        # 初始化发送管理器
        print("🤖 初始化发送管理器...")
        send_manager = SendManager()
        
        # 显示配置信息
        print(f"📅 发送时间配置:")
        print(f"   允许发送时间: {Config.SEND_START_HOUR}:00 - {Config.SEND_END_HOUR}:00")
        print(f"   随机延迟: 0-{Config.SEND_RANDOM_DELAY_MAX}秒")
        print(f"   基础间隔: {Config.SEND_INTERVAL_MINUTES}分钟")
        
        # 测试当前时间
        current_time = datetime.now()
        print(f"\n🕐 当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 测试时间段检查
        is_allowed = send_manager.is_send_time_allowed()
        print(f"⏰ 当前时间是否允许发送: {'✅ 是' if is_allowed else '❌ 否'}")
        
        # 测试发送条件
        can_send = send_manager.can_send_now()
        print(f"🚀 当前是否可以发送: {'✅ 是' if can_send else '❌ 否'}")
        
        # 测试下次发送时间（包含随机延迟）
        print(f"\n🎲 随机延迟测试:")
        for i in range(5):
            next_time = send_manager.get_next_send_time()
            delay_seconds = (next_time - datetime.now()).total_seconds()
            print(f"   第{i+1}次: {next_time.strftime('%H:%M:%S')} (延迟: {delay_seconds:.1f}秒)")
        
        # 测试不同时间点
        print(f"\n📊 不同时间点发送检查:")
        test_hours = [0, 6, 8, 9, 12, 15, 18, 21, 23]
        
        for hour in test_hours:
            test_time = datetime.now().replace(hour=hour, minute=0, second=0)
            allowed = send_manager._is_time_in_allowed_period(test_time)
            status = "✅" if allowed else "❌"
            print(f"   {hour:2d}:00 - {status} {'允许' if allowed else '禁止'}")
        
        # 模拟晚上到早上的时间跨越
        print(f"\n🌙 夜间时间控制测试:")
        
        # 模拟晚上11点
        night_time = datetime.now().replace(hour=23, minute=30)
        print(f"   23:30 - {'✅ 允许' if send_manager._is_time_in_allowed_period(night_time) else '❌ 禁止'}")
        
        # 模拟凌晨2点
        midnight_time = datetime.now().replace(hour=2, minute=0)
        print(f"   02:00 - {'✅ 允许' if send_manager._is_time_in_allowed_period(midnight_time) else '❌ 禁止'}")
        
        # 模拟早上8点
        morning_time = datetime.now().replace(hour=8, minute=0)
        print(f"   08:00 - {'✅ 允许' if send_manager._is_time_in_allowed_period(morning_time) else '❌ 禁止'}")
        
        # 模拟早上9点
        allowed_morning_time = datetime.now().replace(hour=9, minute=0)
        print(f"   09:00 - {'✅ 允许' if send_manager._is_time_in_allowed_period(allowed_morning_time) else '❌ 禁止'}")
        
        print(f"\n✅ 时间控制功能测试完成！")
        print(f"📝 说明: 晚上{Config.SEND_END_HOUR}:00到早上{Config.SEND_START_HOUR}:00之间将不会发送消息")
        print(f"🎲 每次发送都会有0-{Config.SEND_RANDOM_DELAY_MAX}秒的随机延迟，避免机械化")
        
    except Exception as e:
        logger.error(f"测试出错: {e}")
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_time_control()
