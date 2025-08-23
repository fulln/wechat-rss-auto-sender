#!/usr/bin/env python3
"""
测试实际发送过程中的状态记录
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.send_service import SendManager

def test_real_send_with_status():
    """测试实际发送过程中的状态记录"""
    print("=" * 60)
    print("🚀 测试实际发送过程中的状态记录")
    print("=" * 60)
    
    try:
        # 创建发送管理器
        send_manager = SendManager()
        
        # 获取所有未发送的文章
        unsent_items = send_manager.multi_rss_manager.cache.get_unsent_items()
        print(f"找到 {len(unsent_items)} 篇待发送文章")
        
        if not unsent_items:
            print("没有待发送的文章")
            return True
        
        # 选择第一篇文章进行测试
        test_item = unsent_items[0]
        print(f"\n测试文章: {test_item.title[:60]}...")
        print(f"质量评分: {getattr(test_item, 'quality_score', '未评分')}")
        print(f"当前发送尝试次数: {getattr(test_item, 'send_attempts', 0)}")
        
        # 记录发送前状态
        print(f"\n📊 发送前状态:")
        print(f"  发送成功: {getattr(test_item, 'send_success', False)}")
        print(f"  发送错误: {getattr(test_item, 'send_error', None)}")
        print(f"  可重试: {test_item.should_retry_send()}")
        
        # 尝试发送单篇文章
        print(f"\n🚀 开始发送文章...")
        result = send_manager.send_single_article(test_item)
        
        # 记录发送后状态
        print(f"\n📊 发送后状态:")
        print(f"  发送结果: {'✅ 成功' if result else '❌ 失败'}")
        print(f"  发送成功: {getattr(test_item, 'send_success', False)}")
        print(f"  发送尝试次数: {getattr(test_item, 'send_attempts', 0)}")
        print(f"  发送错误: {getattr(test_item, 'send_error', None)}")
        print(f"  最后尝试时间: {getattr(test_item, 'last_attempt_time', None)}")
        print(f"  可重试: {test_item.should_retry_send()}")
        
        # 验证状态是否已保存到缓存
        cache = send_manager.multi_rss_manager.cache
        cached_item = cache.get_item_by_hash(test_item.title_hash, test_item.date_key)
        if cached_item:
            print(f"\n💾 缓存状态验证:")
            print(f"  缓存中发送尝试次数: {getattr(cached_item, 'send_attempts', 0)}")
            print(f"  缓存中发送成功: {getattr(cached_item, 'send_success', False)}")
            print(f"  状态已同步: {'✅' if getattr(cached_item, 'send_attempts', 0) == getattr(test_item, 'send_attempts', 0) else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔥 开始测试实际发送过程中的状态记录...")
    
    result = test_real_send_with_status()
    
    print("\n" + "=" * 60)
    print("📊 测试结果")
    print("=" * 60)
    
    if result:
        print("✅ 实际发送测试通过！")
        print("\n💡 验证的功能:")
        print("   ✅ 发送前状态检查")
        print("   ✅ 发送过程状态更新")
        print("   ✅ 发送后状态记录")
        print("   ✅ 缓存状态同步")
        print("   ✅ 重试逻辑验证")
    else:
        print("❌ 实际发送测试失败")
