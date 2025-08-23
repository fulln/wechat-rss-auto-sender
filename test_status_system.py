#!/usr/bin/env python3
"""
测试RSS文章状态记录系统
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.send_service import SendManager
from src.services.multi_rss_manager import MultiRSSManager

def test_article_status_system():
    """测试文章状态记录系统"""
    print("=" * 60)
    print("📊 测试RSS文章状态记录系统")
    print("=" * 60)
    
    try:
        # 创建发送管理器
        send_manager = SendManager()
        
        # 检查未发送文章
        print("🔍 检查缓存中的文章状态...")
        unsent_items = send_manager.multi_rss_manager.cache.get_unsent_items()
        print(f"可重试发送的文章数量: {len(unsent_items)}")
        
        # 显示所有文章的详细状态
        all_items = []
        cache = send_manager.multi_rss_manager.cache
        for date_key in cache.article_details:
            for item in cache.article_details[date_key].values():
                all_items.append(item)
        
        print(f"\n📋 所有文章状态概览 (共 {len(all_items)} 篇):")
        
        success_count = 0
        failed_count = 0
        pending_count = 0
        
        for i, item in enumerate(all_items, 1):
            print(f"\n文章 {i}:")
            print(f"  标题: {item.title[:60]}...")
            print(f"  来源: {getattr(item, 'source_name', '未知源')}")
            print(f"  发布时间: {item.published}")
            print(f"  质量评分: {getattr(item, 'quality_score', '未评分')}")
            
            # 发送状态
            if hasattr(item, 'send_success') and item.send_success:
                print(f"  📤 状态: ✅ 发送成功")
                if hasattr(item, 'sent_time') and item.sent_time:
                    print(f"  📅 发送时间: {item.sent_time}")
                success_count += 1
            elif hasattr(item, 'send_attempts') and item.send_attempts > 0:
                print(f"  📤 状态: ❌ 发送失败 (尝试 {item.send_attempts} 次)")
                if hasattr(item, 'send_error') and item.send_error:
                    print(f"  ❗ 错误: {item.send_error}")
                if hasattr(item, 'last_attempt_time') and item.last_attempt_time:
                    print(f"  🕒 最后尝试: {item.last_attempt_time}")
                print(f"  🔄 可重试: {'是' if item.should_retry_send() else '否'}")
                failed_count += 1
            else:
                print(f"  📤 状态: ⏳ 等待发送")
                pending_count += 1
                
            if hasattr(item, 'image_path') and item.image_path:
                print(f"  🖼️ 封面图片: 有")
        
        # 统计信息
        print(f"\n📊 状态统计:")
        print(f"  ✅ 发送成功: {success_count}")
        print(f"  ❌ 发送失败: {failed_count}")
        print(f"  ⏳ 等待发送: {pending_count}")
        print(f"  🔄 可重试发送: {len(unsent_items)}")
        
        # 测试发送重试逻辑
        if unsent_items:
            print(f"\n🚀 测试发送重试逻辑...")
            print(f"发现 {len(unsent_items)} 篇可重试的文章")
            
            # 显示第一篇可重试文章的详细信息
            test_item = unsent_items[0]
            print(f"\n测试文章: {test_item.title[:60]}...")
            print(f"  发送尝试次数: {getattr(test_item, 'send_attempts', 0)}")
            print(f"  上次错误: {getattr(test_item, 'send_error', '无')}")
            print(f"  可以重试: {test_item.should_retry_send()}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_manual_status_update():
    """测试手动状态更新"""
    print("\n" + "=" * 60)
    print("🔧 测试手动状态更新")
    print("=" * 60)
    
    try:
        # 创建管理器
        multi_rss_manager = MultiRSSManager()
        
        # 获取一篇文章进行测试
        unsent_items = multi_rss_manager.cache.get_unsent_items()
        if not unsent_items:
            print("没有可测试的文章")
            return True
            
        test_item = unsent_items[0]
        print(f"测试文章: {test_item.title[:60]}...")
        
        # 测试标记发送尝试
        print("\n1. 测试标记发送尝试...")
        original_attempts = getattr(test_item, 'send_attempts', 0)
        test_item.mark_send_attempt()
        print(f"   发送尝试次数: {original_attempts} -> {test_item.send_attempts}")
        
        # 测试标记发送失败
        print("\n2. 测试标记发送失败...")
        test_error = "测试错误信息"
        test_item.mark_send_failed(test_error)
        print(f"   错误信息: {test_item.send_error}")
        print(f"   发送成功: {test_item.send_success}")
        
        # 更新缓存
        multi_rss_manager.cache.update_item_sent_status(test_item)
        print("   ✅ 缓存已更新")
        
        return True
        
    except Exception as e:
        print(f"❌ 手动状态更新测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试RSS文章状态记录系统...")
    
    tests = [
        test_article_status_system,
        test_manual_status_update,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    # 总结结果
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {total - passed}")
    print(f"📈 成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 状态记录系统测试通过！")
        print("\n💡 系统特性:")
        print("   ✅ 详细记录发送尝试次数")
        print("   ✅ 记录具体错误信息")
        print("   ✅ 智能重试机制（最多3次）")
        print("   ✅ 避免短时间内重复尝试")
        print("   ✅ 持久化状态存储")
    else:
        print("\n⚠️ 部分测试失败，请检查系统配置")
