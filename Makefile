# Makefile for WeChat RSS Auto Sender

.PHONY: help install install-dev test lint format type-check clean run

# 默认目标
help:
	@echo "WeChat RSS Auto Sender - 可用命令:"
	@echo "  install      - 安装生产依赖"
	@echo "  install-dev  - 安装开发依赖"
	@echo "  test         - 运行单元测试"
	@echo "  test-cov     - 运行测试并生成覆盖率报告"
	@echo "  lint         - 运行代码检查"
	@echo "  format       - 格式化代码"
	@echo "  type-check   - 运行类型检查"
	@echo "  clean        - 清理临时文件"
	@echo "  run          - 运行应用"
	@echo "  verify       - 运行验证脚本"

# 安装依赖
install:
	pip install -r requirements.txt

install-dev: install
	pip install -r requirements-dev.txt

# 测试
test:
	pytest

test-cov:
	pytest --cov=src --cov-report=html --cov-report=term-missing

# 代码质量
lint:
	flake8 src tests
	mypy src

format:
	black src tests scripts
	isort src tests scripts

type-check:
	mypy src

# 清理
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -rf .coverage

# 运行
run:
	python run.py

# 验证
verify:
	python scripts/verify.py
