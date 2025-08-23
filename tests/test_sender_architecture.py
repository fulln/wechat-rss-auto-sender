"""
发送器架构测试
"""
import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.integrations.send_service_manager import SendServiceManager
from src.core.config import Config

def test_sender_architecture():
    """测试发送器架构"""
    print("🔍 测试发送器架构...")
    
    # 显示配置信息
    print("\n📋 当前配置:")
    sender_configs = Config.get_sender_configs()
    enabled_senders = Config.get_enabled_senders()
    
    print(f"启用的发送器列表: {enabled_senders}")
    
    for sender_name, config in sender_configs.items():
        status = "✅ 启用" if config['enabled'] else "❌ 禁用"
        print(f"  {sender_name}: {status}")
    
    # 初始化发送服务管理器
    print("\n🚀 初始化发送服务管理器...")
    try:
        send_manager = SendServiceManager()
        
        # 获取发送器信息
        print("\n📊 发送器信息:")
        sender_info = send_manager.get_sender_info()
        
        for name, info in sender_info.items():
            print(f"  {name}:")
            for key, value in info.items():
                print(f"    {key}: {value}")
        
        # 测试连接
        print("\n🔗 测试连接:")
        connection_results = send_manager.test_all_connections()
        
        for sender_name, result in connection_results.items():
            status = "✅ 成功" if result else "❌ 失败"
            print(f"  {sender_name}: {status}")
        
        # 测试发送消息
        print("\n📤 测试发送消息:")
        test_message = "🧪 这是一条测试消息，用于验证发送器架构是否正常工作。"
        
        if send_manager.has_enabled_senders():
            send_results = send_manager.send_message(test_message)
            
            for sender_name, result in send_results.items():
                status = "✅ 成功" if result else "❌ 失败"
                print(f"  {sender_name}: {status}")
        else:
            print("  ⚠️ 没有启用的发送器")
        
        print("\n🎉 发送器架构测试完成！")
        return True
        
    except Exception as e:
        print(f"\n💥 发送器架构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sender_architecture()
    if success:
        print("\n✅ 所有测试通过！")
    else:
        print("\n❌ 测试失败，请检查配置。")
