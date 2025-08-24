# 工具目录

这个目录包含了项目的实用工具脚本。

## 可用工具

### upload_cover.py
**功能**: 上传默认封面图片到微信公众号并获取 media_id

**用途**: 一次性上传 `test_cover.jpg` 作为默认封面，避免每次发送文章时重复上传。

**使用方法**:
```bash
cd C:\opt\work\web\wechat-rss-auto-sender
python tools\upload_cover.py
```

**前提条件**:
1. 在 `.env` 文件中配置好微信公众号的 `WECHAT_OFFICIAL_APP_ID` 和 `WECHAT_OFFICIAL_APP_SECRET`
2. 确保项目根目录下有 `test_cover.jpg` 文件
3. 图片文件大小不超过 64KB（微信缩略图限制）

**输出**:
- 成功上传后，会显示 `media_id`
- 将此 `media_id` 添加到 `.env` 文件中的 `WECHAT_OFFICIAL_DEFAULT_THUMB_MEDIA_ID` 配置项
- 配置后，系统将自动使用此 `media_id` 作为默认封面，无需重复上传

**已知可用的 media_id**:
如果工具运行遇到问题，可以直接使用之前成功获取的 media_id：
```
WECHAT_OFFICIAL_DEFAULT_THUMB_MEDIA_ID=YukaF4kTzUcFv1lOIkz0VMffT3syuZaSg9-gVxBgGjr-c38vpgStqIDtyC8nCDFn
```

**注意事项**:
- `media_id` 是永久有效的，请妥善保管
- 如果遇到 access_token 错误，请检查 AppID 和 AppSecret 配置
- 建议将 `media_id` 保存到配置管理系统中

## 添加新工具

如果需要添加新的工具脚本：

1. 将脚本放在此目录下
2. 在脚本开头添加正确的路径设置：
   ```python
   import sys
   import os
   sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))
   ```
3. 在本 README 中添加工具说明
4. 确保工具有适当的错误处理和用户友好的输出
