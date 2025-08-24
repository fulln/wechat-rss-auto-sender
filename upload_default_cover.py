#!/usr/bin/env python3
"""
微信公众号默认封面上传工具
用于一次性上传默认封面图片并获取media_id
"""
import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.integrations.wechat_official_sender import WeChatOfficialSender
from src.core.config import Config


def upload_default_cover():
    """上传默认封面并生成配置"""
    print("=" * 60)
    print("微信公众号默认封面上传工具")
    print("=" * 60)
    
    # 检查配置
    if not Config.WECHAT_OFFICIAL_APP_ID or not Config.WECHAT_OFFICIAL_APP_SECRET:
        print("❌ 错误: 未配置微信公众号AppID或AppSecret")
        print("请在.env文件中配置:")
        print("WECHAT_OFFICIAL_APP_ID=your_app_id")
        print("WECHAT_OFFICIAL_APP_SECRET=your_app_secret")
        return False
    
    # 检查是否已有配置的media_id
    if Config.WECHAT_OFFICIAL_DEFAULT_THUMB_MEDIA_ID:
        print(f"⚠️ 已配置默认封面media_id: {Config.WECHAT_OFFICIAL_DEFAULT_THUMB_MEDIA_ID}")
        choice = input("是否重新上传? (y/N): ").strip().lower()
        if choice != 'y':
            print("操作取消")
            return True
    
    # 检查默认封面文件
    default_cover_path = os.path.join(os.path.dirname(__file__), 'test_cover.jpg')
    if not os.path.exists(default_cover_path):
        print(f"❌ 错误: 未找到默认封面文件: {default_cover_path}")
        print("请确保项目根目录下有 test_cover.jpg 文件")
        return False
    
    print(f"📁 找到默认封面文件: {default_cover_path}")
    file_size = os.path.getsize(default_cover_path)
    print(f"📏 文件大小: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    # 检查文件大小限制
    if file_size > 64 * 1024:  # 64KB限制
        print("❌ 错误: 封面图片文件过大，微信要求缩略图不超过64KB")
        print("请压缩图片后重试")
        return False
    
    # 创建发送器实例
    config = Config.get_sender_configs()['wechat_official']
    sender = WeChatOfficialSender(config)
    
    try:
        # 获取access_token
        print("🔑 获取微信公众号access_token...")
        if not sender._ensure_access_token():
            print("❌ 无法获取access_token，请检查AppID和AppSecret配置")
            return False
        
        print("✅ access_token获取成功")
        
        # 上传默认封面
        print("📤 上传默认封面图片...")
        media_id = sender._upload_thumb_media(default_cover_path)
        
        if media_id:
            print("✅ 默认封面上传成功!")
            print(f"📋 Media ID: {media_id}")
            print()
            print("=" * 60)
            print("🎯 配置说明:")
            print("=" * 60)
            print("请将以下配置添加到您的 .env 文件中:")
            print()
            print(f"WECHAT_OFFICIAL_DEFAULT_THUMB_MEDIA_ID={media_id}")
            print()
            print("添加此配置后，系统将自动使用这个media_id作为默认封面，")
            print("无需每次重新上传test_cover.jpg文件。")
            print()
            print("📝 注意事项:")
            print("- media_id 永久有效，但请妥善保管")
            print("- 如需更换默认封面，可重新运行此工具")
            print("- 建议将此media_id保存到配置管理系统中")
            print("=" * 60)
            
            return True
        else:
            print("❌ 默认封面上传失败")
            return False
            
    except Exception as e:
        print(f"❌ 上传过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    try:
        success = upload_default_cover()
        if success:
            print("\n🎉 操作完成!")
        else:
            print("\n❌ 操作失败!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
