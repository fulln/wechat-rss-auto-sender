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
    & $PIP install -r requirements-dev.txt
}

function Run-Tests {
    Write-Host "运行测试..." -ForegroundColor Blue
    & $PYTHON -m pytest tests/ -v
}

function Run-TestsWithCoverage {
    Write-Host "运行测试并生成覆盖率报告..." -ForegroundColor Blue
    & $PYTHON -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
}

function Run-Lint {
    Write-Host "运行代码检查..." -ForegroundColor Blue
    & $PYTHON -m flake8 src tests
    & $PYTHON -m pylint src
}

function Format-Code {
    Write-Host "格式化代码..." -ForegroundColor Blue
    & $PYTHON -m black src tests
    & $PYTHON -m isort src tests
}

function Run-TypeCheck {
    Write-Host "运行类型检查..." -ForegroundColor Blue
    & $PYTHON -m mypy src
}

function Clean-Files {
    Write-Host "清理临时文件..." -ForegroundColor Blue
    
    # 清理 .pyc 文件
    try {
        $pycFiles = Get-ChildItem -Recurse -Name "*.pyc" -ErrorAction SilentlyContinue
        if ($pycFiles) {
            $pycFiles | Remove-Item -Force -ErrorAction SilentlyContinue
            Write-Host "已清理 .pyc 文件" -ForegroundColor Green
        }
    } catch {
        Write-Host "清理 .pyc 文件时出错: $_" -ForegroundColor Yellow
    }
    
    # 清理 __pycache__ 目录
    try {
        $pycacheDirs = Get-ChildItem -Recurse -Name "__pycache__" -Directory -ErrorAction SilentlyContinue
        if ($pycacheDirs) {
            $pycacheDirs | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "已清理 __pycache__ 目录" -ForegroundColor Green
        }
    } catch {
        Write-Host "清理 __pycache__ 目录时出错: $_" -ForegroundColor Yellow
    }
    
    # 清理其他缓存目录和文件
    $pathsToClean = @(".pytest_cache", "htmlcov", ".mypy_cache", ".coverage")
    
    foreach ($path in $pathsToClean) {
        if (Test-Path $path) {
            try {
                Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "已清理: $path" -ForegroundColor Green
            } catch {
                Write-Host "清理 $path 时出错: $_" -ForegroundColor Yellow
            }
        }
    }
    
    # 清理 .egg-info 目录
    try {
        $eggInfoDirs = Get-ChildItem -Name "*.egg-info" -Directory -ErrorAction SilentlyContinue
        if ($eggInfoDirs) {
            $eggInfoDirs | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "已清理 .egg-info 目录" -ForegroundColor Green
        }
    } catch {
        Write-Host "清理 .egg-info 目录时出错: $_" -ForegroundColor Yellow
    }
    
    Write-Host "临时文件清理完成！" -ForegroundColor Green
}

function Run-App {
    Write-Host "运行应用..." -ForegroundColor Blue
    & $PYTHON run.py
}

function Run-Verify {
    Write-Host "运行验证脚本..." -ForegroundColor Blue
    if (Test-Path "scripts/verify.py") {
        & $PYTHON scripts/verify.py
    } else {
        Write-Host "验证脚本不存在" -ForegroundColor Yellow
    }
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
