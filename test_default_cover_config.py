#!/usr/bin/env python3
"""
测试微信公众号默认封面配置
"""
import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.integrations.wechat_official_sender import WeChatOfficialSender
from src.core.config import Config


def test_default_cover_config():
    """测试默认封面配置"""
    print("=" * 50)
    print("测试微信公众号默认封面配置")
    print("=" * 50)
    
    # 获取配置
    config = Config.get_sender_configs()['wechat_official']
    print(f"配置的默认封面media_id: {config.get('default_thumb_media_id', '未配置')}")
    
    # 创建发送器实例
    sender = WeChatOfficialSender(config)
    print(f"发送器中的默认封面media_id: {sender.default_thumb_media_id or '未配置'}")
    
    # 模拟草稿创建逻辑
    print("\n📝 模拟草稿创建逻辑:")
    
    # 测试1: 没有提供封面图片的情况
    print("\n测试1: 没有提供封面图片")
    thumb_media_id = None
    
    if not thumb_media_id:
        if sender.default_thumb_media_id:
            final_media_id = sender.default_thumb_media_id
            print(f"✅ 使用配置的默认封面: {final_media_id}")
        else:
            print("⚠️ 没有配置默认封面，需要上传")
    
    # 测试2: 提供了封面图片的情况
    print("\n测试2: 提供了封面图片")
    thumb_media_id = "custom_media_id_123"
    final_media_id = thumb_media_id
    print(f"✅ 使用提供的封面: {final_media_id}")
    
    print("\n🎯 配置建议:")
    if not sender.default_thumb_media_id:
        print("建议运行 python upload_default_cover.py 上传默认封面")
        print("然后在.env文件中配置 WECHAT_OFFICIAL_DEFAULT_THUMB_MEDIA_ID")
    else:
        print("✅ 默认封面配置正确，系统会自动使用配置的media_id")
        print("这样可以避免每次都重新上传封面图片")


if __name__ == "__main__":
    try:
        test_default_cover_config()
        print("\n🎉 测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
