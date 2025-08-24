#!/usr/bin/env python3
"""
一次性上传默认封面图片工具
用于获取WeChat Official Account的默认封面media_id
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.integrations.wechat_official_sender import WeChatOfficialSender
from src.core.config import Config

def upload_default_cover():
    """上传默认封面图片并获取media_id"""
    
    # 检查配置
    app_id = Config.WECHAT_OFFICIAL_APP_ID
    app_secret = Config.WECHAT_OFFICIAL_APP_SECRET
    
    if not app_id or not app_secret:
        print("❌ 错误：缺少WeChat Official配置")
        print("请确保在.env文件中设置：")
        print("- WECHAT_OFFICIAL_APP_ID")
        print("- WECHAT_OFFICIAL_APP_SECRET")
        return None
    
    # 创建sender实例
    sender = WeChatOfficialSender()
    
    # 封面图片路径
    cover_path = os.path.join(project_root, 'test_cover.jpg')
    
    if not os.path.exists(cover_path):
        print(f"❌ 错误：封面图片不存在: {cover_path}")
        return None
    
    try:
        print("📸 正在上传默认封面图片...")
        media_id = sender._upload_permanent_media(cover_path, 'image')
        
        if media_id:
            print("✅ 封面上传成功！")
            print(f"📄 Media ID: {media_id}")
            print("\n🔧 配置步骤：")
            print("1. 在你的 .env 文件中添加以下配置：")
            print(f"   WECHAT_OFFICIAL_DEFAULT_THUMB_MEDIA_ID={media_id}")
            print("\n2. 重启应用使配置生效")
            print("\n💡 配置完成后，系统将使用这个封面图片而不再重复上传")
            return media_id
        else:
            print("❌ 上传失败")
            return None
            
    except Exception as e:
        print(f"❌ 上传过程中出错: {e}")
        return None

if __name__ == "__main__":
    upload_default_cover()
