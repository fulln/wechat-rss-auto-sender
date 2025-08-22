"""
微信RSS新闻推送主程序
"""
import sys
import signal
from .utils import setup_logger
from .config import Config
from .scheduler import NewsScheduler

logger = setup_logger(__name__)

def signal_handler(signum, frame):
    """信号处理器"""
    logger.info("接收到退出信号，正在关闭程序...")
    sys.exit(0)

def main():
    """主函数"""
    try:
        logger.info("=== 微信RSS新闻推送服务启动 ===")
        
        # 验证配置
        try:
            Config.validate()
            logger.info("配置验证通过")
        except ValueError as e:
            logger.error(f"配置错误: {e}")
            sys.exit(1)
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 创建并启动调度器
        scheduler = NewsScheduler()
        scheduler.start()
        
        if not scheduler.is_running:
            logger.error("调度器启动失败")
            sys.exit(1)
        
        logger.info("服务正在运行中，按 Ctrl+C 退出...")
        
        # 保持程序运行
        try:
            while True:
                import time
                time.sleep(1)
                
                # 定期输出状态
                if int(time.time()) % 300 == 0:  # 每5分钟输出一次状态
                    status = scheduler.get_status()
                    logger.info(f"服务状态: {status}")
                    
        except KeyboardInterrupt:
            logger.info("接收到键盘中断信号")
        
        # 清理资源
        scheduler.stop()
        logger.info("程序正常退出")
        
    except Exception as e:
        logger.error(f"程序运行错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()