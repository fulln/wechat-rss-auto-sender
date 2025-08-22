# 微信RSS自动推送服务

> ⚠️ **重要提示**: 本项目仅支持Windows系统运行，因为依赖了wxauto库进行微信自动化操作。

一个自动获取RSS新闻并通过微信发送AI总结的Python服务。

## 功能特性

- 🤖 **AI智能总结**: 使用DeepSeek API将新闻总结为150-300字的专门优化内容
- 📱 **微信自动发送**: 使用wxauto库自动发送消息到指定联系人 (仅限Windows)
- ⏰ **定时任务**: 每5分钟自动检查RSS更新
- 📰 **RSS支持**: 支持标准RSS/Atom格式的新闻源
- 🎯 **质量筛选**: 只发送AI评分7分以上的高质量文章
- 📝 **智能去重**: 按天维度去除相同标题的重复文章
- 🕐 **时间控制**: 晚上12点到早上9点之间不发送消息
- 🎲 **随机延迟**: 发送间隔添加0-15秒随机延迟，避免机械化
- 📋 **完整日志**: 详细的运行日志记录
- ⚙️ **灵活配置**: 通过环境变量配置各项参数
- 🔒 **敏感信息保护**: 完整的.gitignore配置
- 🧪 **完整测试**: 包含单元测试和集成测试

## 快速开始

### 系统要求

- **操作系统**: Windows 10 或更高版本
- **Python版本**: Python 3.8 或更高版本
- **微信客户端**: 微信PC版客户端 (必须先登录)

### 1. 安装依赖

```powershell
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境 (PowerShell)
.\.venv\Scripts\Activate.ps1

# 或使用CMD
.\.venv\Scripts\activate.bat

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -r requirements-dev.txt
```

### 2. 配置环境

复制环境变量模板：
```powershell
copy .env.example .env
```

编辑 `.env` 文件，配置必要参数：
```env
# 必须配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 可选配置
WECHAT_CONTACT_NAME=文件传输助手
RSS_FEED_URL=https://36kr.com/feed
CHECK_INTERVAL_MINUTES=5
SLEEP_HOURS_START=0
SLEEP_HOURS_END=9
MIN_QUALITY_SCORE=7
```

### 3. 运行服务

```powershell
# 直接运行
python run.py

# 或使用PowerShell脚本
.\dev.ps1 run
```

## 配置说明

| 环境变量 | 必需 | 默认值 | 说明 |
|---------|------|--------|------|
| `DEEPSEEK_API_KEY` | ✅ | - | DeepSeek API密钥 |
| `WECHAT_CONTACT_NAME` | ❌ | 文件传输助手 | 微信联系人名称 |
| `RSS_FEED_URL` | ❌ | https://36kr.com/feed | RSS源地址 |
| `CHECK_INTERVAL_MINUTES` | ❌ | 5 | 检查间隔(分钟) |
| `SLEEP_HOURS_START` | ❌ | 0 | 休眠开始时间 |
| `SLEEP_HOURS_END` | ❌ | 9 | 休眠结束时间 |
| `MIN_QUALITY_SCORE` | ❌ | 7 | 最低质量分数 |

## 项目结构

```
wechat-rss-auto-sender/
├── src/                    # 源代码目录
│   ├── core/              # 核心模块
│   │   ├── config.py      # 配置管理
│   │   ├── prompts.py     # AI提示词
│   │   └── utils.py       # 工具函数
│   ├── services/          # 服务模块
│   │   ├── ai_service.py  # AI服务
│   │   ├── rss_service.py # RSS服务
│   │   ├── send_service.py # 发送服务
│   │   └── scheduler_service.py # 调度服务
│   ├── integrations/      # 集成模块
│   │   └── wechat_client.py # 微信客户端
│   └── models/            # 数据模型
├── tests/                 # 测试目录
├── cache/                 # 缓存目录
├── logs/                  # 日志目录
├── requirements.txt       # 生产依赖
├── requirements-dev.txt   # 开发依赖
└── run.py                # 主入口文件
```

## 开发指南

### 运行测试

```powershell
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_send_service.py

# 运行覆盖率测试
pytest --cov=src tests/

# 生成HTML覆盖率报告
pytest --cov=src tests/ --cov-report=html
```

### 代码质量检查

```powershell
# 代码格式化
black src/ tests/

# 导入排序
isort src/ tests/

# 语法检查
flake8 src/ tests/

# 类型检查
mypy src/
```

## 使用说明

1. **首次运行**：确保微信PC版已登录，程序会自动检测微信窗口
2. **联系人设置**：在`.env`中设置`WECHAT_CONTACT_NAME`为目标联系人的名称
3. **RSS源配置**：可以配置任何标准的RSS/Atom源地址
4. **时间控制**：程序会在设定的休眠时间内暂停发送
5. **质量筛选**：只有AI评分达到设定分数的文章才会被发送

## 常见问题

### Q: 为什么只支持Windows系统？
A: 本项目使用了wxauto库来自动化微信操作，该库只支持Windows系统上的微信PC版客户端。

### Q: 如何获取DeepSeek API密钥？
A: 访问 [DeepSeek官网](https://platform.deepseek.com/) 注册账号并获取API密钥。

### Q: 微信联系人名称怎么设置？
A: 在微信中找到目标联系人的显示名称，设置到`WECHAT_CONTACT_NAME`环境变量中。

### Q: 程序运行时微信窗口被遮挡会影响吗？
A: 不会，wxauto可以在后台操作微信，但微信客户端必须保持登录状态。

## 注意事项

- 🚨 **微信风控**: 频繁的自动化操作可能触发微信风控，建议合理设置发送间隔
- 💡 **网络稳定**: 确保网络连接稳定，避免RSS获取和API调用失败
- 🔐 **API密钥安全**: 请妥善保管API密钥，不要提交到版本控制系统
- 📱 **微信登录**: 微信PC版必须保持登录状态，程序才能正常工作

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进项目！
