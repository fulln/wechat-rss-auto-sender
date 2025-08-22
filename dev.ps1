# PowerShell脚本用于项目管理
param(
    [Parameter(Position = 0)]
    [ValidateSet("help", "install", "install-dev", "test", "test-cov", "lint", "format", "type-check", "clean", "run", "verify")]
    [string]$Command = "help"
)

$PYTHON = "C:/opt/work/web/.venv/Scripts/python.exe"
$PIP = "C:/opt/work/web/.venv/Scripts/pip.exe"

function Show-Help {
    Write-Host "WeChat RSS Auto Sender - 可用命令:" -ForegroundColor Green
    Write-Host "  install      - 安装生产依赖" -ForegroundColor White
    Write-Host "  install-dev  - 安装开发依赖" -ForegroundColor White  
    Write-Host "  test         - 运行单元测试" -ForegroundColor White
    Write-Host "  test-cov     - 运行测试并生成覆盖率报告" -ForegroundColor White
    Write-Host "  lint         - 运行代码检查" -ForegroundColor White
    Write-Host "  format       - 格式化代码" -ForegroundColor White
    Write-Host "  type-check   - 运行类型检查" -ForegroundColor White
    Write-Host "  clean        - 清理临时文件" -ForegroundColor White
    Write-Host "  run          - 运行应用" -ForegroundColor White
    Write-Host "  verify       - 运行验证脚本" -ForegroundColor White
    Write-Host ""
    Write-Host "用法: .\dev.ps1 <command>" -ForegroundColor Yellow
}

function Install-Dependencies {
    Write-Host "安装生产依赖..." -ForegroundColor Blue
    & $PIP install -r requirements.txt
}

function Install-DevDependencies {
    Write-Host "安装开发依赖..." -ForegroundColor Blue
    Install-Dependencies
    & $PIP install -r requirements-dev.txt
}

function Run-Tests {
    Write-Host "运行单元测试..." -ForegroundColor Blue
    & $PYTHON -m pytest
}

function Run-TestsWithCoverage {
    Write-Host "运行测试并生成覆盖率报告..." -ForegroundColor Blue
    & $PYTHON -m pytest --cov=src --cov-report=html --cov-report=term-missing
}

function Run-Lint {
    Write-Host "运行代码检查..." -ForegroundColor Blue
    & $PYTHON -m flake8 src tests
    & $PYTHON -m mypy src
}

function Format-Code {
    Write-Host "格式化代码..." -ForegroundColor Blue
    & $PYTHON -m black src tests scripts
    & $PYTHON -m isort src tests scripts
}

function Run-TypeCheck {
    Write-Host "运行类型检查..." -ForegroundColor Blue
    & $PYTHON -m mypy src
}

function Clean-Files {
    Write-Host "清理临时文件..." -ForegroundColor Blue
    Get-ChildItem -Recurse -Name "*.pyc" | Remove-Item -Force
    Get-ChildItem -Recurse -Name "__pycache__" -Directory | Remove-Item -Recurse -Force
    if (Test-Path ".pytest_cache") { Remove-Item ".pytest_cache" -Recurse -Force }
    if (Test-Path "htmlcov") { Remove-Item "htmlcov" -Recurse -Force }
    if (Test-Path ".mypy_cache") { Remove-Item ".mypy_cache" -Recurse -Force }
    if (Test-Path ".coverage") { Remove-Item ".coverage" -Force }
}

function Run-App {
    Write-Host "运行应用..." -ForegroundColor Blue
    & $PYTHON run.py
}

function Run-Verify {
    Write-Host "运行验证脚本..." -ForegroundColor Blue
    & $PYTHON scripts/verify.py
}

# 执行命令
switch ($Command) {
    "help" { Show-Help }
    "install" { Install-Dependencies }
    "install-dev" { Install-DevDependencies }
    "test" { Run-Tests }
    "test-cov" { Run-TestsWithCoverage }
    "lint" { Run-Lint }
    "format" { Format-Code }
    "type-check" { Run-TypeCheck }
    "clean" { Clean-Files }
    "run" { Run-App }
    "verify" { Run-Verify }
    default { Show-Help }
}
