#!/usr/bin/env python3
"""
测试微信公众号access_token获取（通过代理）
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.integrations.wechat_official_sender import WeChatOfficialSender
from src.core.config import Config

def test_wechat_token_with_proxy():
    """测试通过代理获取微信公众号access_token"""
    print("=" * 60)
    print("🔐 测试微信公众号access_token获取（通过代理）")
    print("=" * 60)
    
    try:
        # 检查代理配置
        proxies = Config.get_proxies()
        if proxies:
            print(f"✅ 检测到代理配置: {proxies}")
        else:
            print("⚠️ 未检测到代理配置")
        
        # 检查微信公众号配置
        app_id = Config.WECHAT_OFFICIAL_APP_ID
        app_secret = Config.WECHAT_OFFICIAL_APP_SECRET
        
        if not app_id or not app_secret:
            print("❌ 缺少微信公众号配置 (APP_ID/APP_SECRET)")
            return False
        
        print(f"📱 微信公众号配置:")
        print(f"   APP_ID: {app_id[:8]}***{app_id[-4:] if len(app_id) > 12 else app_id}")
        print(f"   APP_SECRET: {'*' * (len(app_secret) - 8)}{app_secret[-4:] if len(app_secret) > 8 else '****'}")
        
        # 创建发送器实例
        wechat_config = {
            'enabled': True,
            'app_id': app_id,
            'app_secret': app_secret,
            'use_rich_formatting': True,
            'footer_text': '📱 更多科技资讯，请关注我们',
            'author_name': 'RSS助手'
        }
        sender = WeChatOfficialSender(wechat_config)
        print("✅ 微信公众号发送器创建成功")
        
        # 测试获取access_token
        print("\n🔄 开始获取access_token...")
        success = sender._ensure_access_token()
        
        if success:
            print("🎉 access_token获取成功！")
            print(f"   Token: {sender.access_token[:20]}...{sender.access_token[-4:] if len(sender.access_token) > 24 else sender.access_token}")
            print(f"   过期时间: {sender.token_expires_at}")
            return True
        else:
            print("❌ access_token获取失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_proxy_connectivity():
    """测试代理连接性"""
    print("\n" + "=" * 60)
    print("🌐 测试代理连接性")
    print("=" * 60)
    
    try:
        import requests
        
        proxies = Config.get_proxies()
        if not proxies:
            print("⚠️ 未配置代理，跳过连接性测试")
            return True
        
        # 测试代理连接到外网
        test_url = "https://httpbin.org/ip"
        print(f"🔍 测试代理访问: {test_url}")
        
        response = requests.get(test_url, proxies=proxies, timeout=10)
        data = response.json()
        
        print(f"✅ 代理连接成功")
        print(f"   出口IP: {data.get('origin', '未知')}")
        
        # 测试微信API连接性
        wechat_test_url = "https://api.weixin.qq.com"
        print(f"\n🔍 测试微信API可达性: {wechat_test_url}")
        
        response = requests.get(wechat_test_url, proxies=proxies, timeout=10)
        print(f"✅ 微信API可达 (状态码: {response.status_code})")
        
        return True
        
    except Exception as e:
        print(f"❌ 代理连接测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始微信公众号代理测试...")
    
    # 运行测试
    tests = [
        test_proxy_connectivity,
        test_wechat_token_with_proxy,
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
        print("\n🎉 所有测试通过！代理配置正常工作。")
        print("\n💡 使用建议:")
        print("   1. 代理已正确配置，所有微信API调用将使用固定IP")
        print("   2. 确保代理服务稳定运行以避免token获取失败")
        print("   3. 监控日志以确认API调用成功")
    else:
        print("\n⚠️ 部分测试失败，请检查:")
        print("   1. 代理服务是否正常运行")
        print("   2. 微信公众号配置是否正确")
        print("   3. 网络连接是否正常")
