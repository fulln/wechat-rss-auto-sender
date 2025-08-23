#!/usr/bin/env python3
"""
测试运行脚本
提供便捷的测试运行命令
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, description: str = None):
    """运行命令并显示结果"""
    if description:
        print(f"\\n{'='*50}")
        print(f"{description}")
        print('='*50)
    
    print(f"运行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=Path(__file__).parent.parent)
    return result.returncode == 0


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("""
测试运行脚本

用法:
    python tests/run_tests.py <选项>

选项:
    all         - 运行所有测试
    unit        - 运行单元测试
    integration - 运行集成测试
    slow        - 运行慢速测试
    fast        - 运行快速测试（排除慢速）
    coverage    - 运行测试并生成覆盖率报告
    watch       - 监视模式（需要pytest-xdist）
    
示例:
    python tests/run_tests.py all
    python tests/run_tests.py unit
    python tests/run_tests.py coverage
        """)
        return
    
    option = sys.argv[1].lower()
    
    if option == "all":
        success = run_command("pytest tests/", "运行所有测试")
    
    elif option == "unit":
        success = run_command("pytest tests/ -m unit", "运行单元测试")
    
    elif option == "integration":
        success = run_command("pytest tests/ -m integration", "运行集成测试")
    
    elif option == "slow":
        success = run_command("pytest tests/ -m slow", "运行慢速测试")
    
    elif option == "fast":
        success = run_command('pytest tests/ -m "not slow"', "运行快速测试")
    
    elif option == "coverage":
        success = run_command(
            "pytest tests/ --cov=src --cov-report=html --cov-report=term-missing",
            "运行测试并生成覆盖率报告"
        )
        if success:
            print("\\n覆盖率报告已生成:")
            print("  - HTML报告: htmlcov/index.html")
            print("  - 终端报告: 已显示在上方")
    
    elif option == "watch":
        success = run_command("pytest tests/ -f", "监视模式运行测试")
    
    elif option == "verbose":
        success = run_command("pytest tests/ -v -s", "详细模式运行测试")
    
    elif option == "wechat":
        success = run_command("pytest tests/ -m wechat", "运行微信相关测试")
    
    elif option == "rss":
        success = run_command("pytest tests/ -m rss", "运行RSS相关测试")
    
    elif option == "ai":
        success = run_command("pytest tests/ -m ai", "运行AI相关测试")
    
    else:
        print(f"未知选项: {option}")
        print("运行 'python tests/run_tests.py' 查看帮助")
        return
    
    if success:
        print("\\n✅ 测试运行完成")
    else:
        print("\\n❌ 测试运行失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
