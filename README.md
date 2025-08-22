# 微信## 功能特性

- 🤖 **AI智能总结**: 使用DeepSeek API将新闻总结为150-300字的专门优化内容
- 📱 **微信自动发送**: 使用wxauto库自动发送消息到指定联系人
- ⏰ **定时任务**: 每5分钟自动检查RSS更新
- 📰 **RSS支持**: 支持标准RSS/Atom格式的新闻源
- 🎯 **质量筛选**: 只发送AI评分7分以上的高质量文章
- 📝 **智能去重**: 按天维度去除相同标题的重复文章
- 🕐 **时间控制**: 晚上12点到早上9点之间不发送消息
- 🎲 **随机延迟**: 发送间隔添加0-15秒随机延迟，避免机械化
- 📋 **完整日志**: 详细的运行日志记录
- ⚙️ **灵活配置**: 通过环境变量配置各项参数
- 🔒 **敏感信息保护**: 完整的.gitignore配置
- 🧪 **完整测试**: 包含单元测试和集成测试务

一个自动获取RSS新闻并通过微信发送AI总结的Python服务。

## 功能特性

- 🤖 **AI智能总结**: 使用OpenAI API将新闻总结为100-200字的微信消息
- 📱 **微信自动发送**: 使用wxauto库自动发送消息到指定联系人
- ⏰ **定时任务**: 每5分钟自动检查RSS更新
- 📰 **RSS支持**: 支持标准RSS/Atom格式的新闻源
- � **智能去重**: 按天维度去除相同标题的重复文章
- �📝 **完整日志**: 详细的运行日志记录
- ⚙️ **灵活配置**: 通过环境变量配置各项参数
- 🧪 **完整测试**: 包含单元测试和集成测试

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境 (Windows)
.\.venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -r requirements-dev.txt
```

### 2. 配置环境

复制环境变量模板：
```bash
copy .env.example .env
```

编辑 `.env` 文件，配置必要参数：
```env
# 必须配置
OPENAI_API_KEY=your_openai_api_key_here

# 可选配置
WECHAT_CONTACT_NAME=文件传输助手
RSS_FEED_URL=https://36kr.com/feed
CHECK_INTERVAL_MINUTES=5
```

### 3. 运行服务

```bash
# 直接运行
python run.py

# 或使用PowerShell脚本（Windows）
.\dev.ps1 run

# 或使用Makefile（Linux/Mac）
make run
```

## 开发指南

### 项目结构

```
wechat-rss-auto-sender/
├── src/                    # 源代码
│   ├── __init__.py
│   ├── main.py            # 主程序入口
│   ├── config.py          # 配置管理
│   ├── utils.py           # 工具函数(日志等)
│   ├── rss_fetcher.py     # RSS获取模块
│   ├── summarizer.py      # AI总结模块
│   ├── wechat_sender.py   # 微信发送模块
│   └── scheduler.py       # 任务调度模块
├── tests/                 # 单元测试
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_rss_fetcher.py
│   ├── test_summarizer.py
│   ├── test_wechat_sender.py
│   └── test_integration.py
├── scripts/               # 脚本工具
│   ├── manual_test.py     # 手动测试脚本
│   ├── cache_test.py      # 缓存测试脚本
│   ├── simple_test.py     # 简单测试脚本
│   └── verify.py          # 验证脚本
├── cache/                 # 缓存目录（自动创建）
├── logs/                  # 日志目录
├── .env                   # 环境配置
├── .env.example           # 配置模板
├── requirements.txt       # 生产依赖
├── requirements-dev.txt   # 开发依赖
├── pyproject.toml         # 项目配置
├── .flake8               # 代码检查配置
├── Makefile              # Make命令
├── dev.ps1               # PowerShell脚本
├── run.py                # 启动脚本
└── README.md             # 说明文档
```

### 开发命令

#### Windows (PowerShell)

```bash
# 查看所有可用命令
.\dev.ps1 help

# 安装开发依赖
.\dev.ps1 install-dev

# 运行测试
.\dev.ps1 test

# 运行测试并生成覆盖率报告
.\dev.ps1 test-cov

# 代码检查
.\dev.ps1 lint

# 格式化代码
.\dev.ps1 format

# 类型检查
.\dev.ps1 type-check

# 清理临时文件
.\dev.ps1 clean

# 运行验证脚本
.\dev.ps1 verify
```

#### Linux/Mac (Make)

```bash
# 查看所有可用命令
make help

# 安装开发依赖
make install-dev

# 运行测试
make test

# 运行测试并生成覆盖率报告
make test-cov

# 代码检查
make lint

# 格式化代码
make format

# 类型检查
make type-check

# 清理临时文件
make clean

# 运行验证脚本
make verify
```

### 测试

项目包含完整的测试套件：

- **单元测试**: 测试各个模块的功能
- **集成测试**: 测试模块间的交互
- **覆盖率报告**: 确保代码覆盖率

运行测试：
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_rss_fetcher.py

# 运行测试并显示覆盖率
pytest --cov=src --cov-report=term-missing

# 生成HTML覆盖率报告
pytest --cov=src --cov-report=html
```

### 代码质量

项目使用以下工具确保代码质量：

- **Black**: 代码格式化
- **isort**: import排序
- **flake8**: 代码风格检查
- **mypy**: 类型检查
- **pytest**: 单元测试

## 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | AI API密钥 (必需) | - |
| `WECHAT_CONTACT_NAME` | 微信发送目标 | 文件传输助手 |
| `RSS_FEED_URL` | RSS源地址 | https://36kr.com/feed-article |
| `CHECK_INTERVAL_MINUTES` | RSS检查间隔(分钟) | 5 |
| `OPENAI_BASE_URL` | AI API地址 | https://api.deepseek.com/v1 |
| `SUMMARY_MIN_LENGTH` | 总结最小字数 | 150 |
| `SUMMARY_MAX_LENGTH` | 总结最大字数 | 300 |
| `MIN_QUALITY_SCORE` | 最低质量分数要求 | 7 |
| `SEND_START_HOUR` | 允许发送开始时间 | 9 |
| `SEND_END_HOUR` | 允许发送结束时间 | 24 |
| `SEND_RANDOM_DELAY_MAX` | 随机延迟最大值(秒) | 15 |

### 🕐 时间控制说明

- **发送时段**: 默认在9:00-24:00之间发送，夜间(0:00-9:00)不发送
- **随机延迟**: 每次发送前会有0-15秒的随机延迟，避免过于机械化
- **质量控制**: 只有AI评分≥7分的文章才会被发送

## 缓存机制

系统实现了智能缓存机制：

- **按天去重**: 相同日期内的重复标题会被自动过滤
- **自动清理**: 7天前的缓存文件会被自动删除
- **持久化存储**: 缓存数据存储在 `cache/` 目录的JSON文件中

## 常见问题

### Q: 微信连接失败？
A: 
- 确保微信PC版已登录
- 检查wxauto库是否正确安装
- 尝试重启微信客户端

### Q: AI总结失败？
A: 
- 检查OpenAI API密钥是否正确
- 检查网络连接
- 检查API配额是否充足

### Q: RSS获取失败？
A: 
- 检查RSS地址是否有效
- 检查网络连接
- 尝试更换RSS源

### Q: 测试失败？
A:
- 确保安装了开发依赖：`pip install -r requirements-dev.txt`
- 检查Python版本是否 >= 3.8
- 运行 `pytest --tb=short` 查看详细错误信息

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建特性分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 提交Pull Request

### 贡献指南

1. 确保代码通过所有测试
2. 运行代码格式化：`.\dev.ps1 format`
3. 运行代码检查：`.\dev.ps1 lint`
4. 添加适当的测试用例
5. 更新文档（如有必要）
