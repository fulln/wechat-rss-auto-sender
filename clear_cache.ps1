# 微信RSS自动推送项目 - 缓存清理脚本
# 用法: .\clear_cache.ps1

Write-Host "=== 微信RSS自动推送项目缓存清理 ===" -ForegroundColor Green
Write-Host ""

$cleanedItems = 0

# 1. 清理RSS缓存
Write-Host "1. 检查RSS缓存..." -ForegroundColor Yellow
if (Test-Path "cache") {
    Write-Host "   删除RSS缓存目录..." -ForegroundColor Gray
    Remove-Item "cache" -Recurse -Force
    $cleanedItems++
    Write-Host "   ✓ RSS缓存已清理" -ForegroundColor Green
} else {
    Write-Host "   ℹ RSS缓存目录不存在" -ForegroundColor Gray
}

# 2. 清理Python字节码缓存
Write-Host "2. 清理Python字节码缓存..." -ForegroundColor Yellow
$pycacheCount = 0
Get-ChildItem -Recurse -Directory | Where-Object {$_.Name -eq "__pycache__"} | ForEach-Object {
    if ($_.FullName -notlike "*\.venv\*") {  # 跳过虚拟环境中的缓存
        Write-Host "   删除: $($_.FullName)" -ForegroundColor Gray
        Remove-Item $_.FullName -Recurse -Force
        $pycacheCount++
    }
}

$pycCount = 0
Get-ChildItem -Recurse -File | Where-Object {$_.Extension -eq ".pyc"} | ForEach-Object {
    if ($_.FullName -notlike "*\.venv\*") {  # 跳过虚拟环境中的缓存
        Write-Host "   删除: $($_.FullName)" -ForegroundColor Gray
        Remove-Item $_.FullName -Force
        $pycCount++
    }
}

if ($pycacheCount -gt 0 -or $pycCount -gt 0) {
    Write-Host "   ✓ 清理了 $pycacheCount 个__pycache__目录和 $pycCount 个.pyc文件" -ForegroundColor Green
    $cleanedItems++
} else {
    Write-Host "   ℹ 没有找到Python字节码缓存" -ForegroundColor Gray
}

# 3. 清理测试缓存
Write-Host "3. 清理测试缓存..." -ForegroundColor Yellow
if (Test-Path ".pytest_cache") {
    Write-Host "   删除pytest缓存..." -ForegroundColor Gray
    Remove-Item ".pytest_cache" -Recurse -Force
    $cleanedItems++
    Write-Host "   ✓ pytest缓存已清理" -ForegroundColor Green
} else {
    Write-Host "   ℹ pytest缓存不存在" -ForegroundColor Gray
}

# 4. 清理类型检查缓存
Write-Host "4. 清理类型检查缓存..." -ForegroundColor Yellow
if (Test-Path ".mypy_cache") {
    Write-Host "   删除mypy缓存..." -ForegroundColor Gray
    Remove-Item ".mypy_cache" -Recurse -Force
    $cleanedItems++
    Write-Host "   ✓ mypy缓存已清理" -ForegroundColor Green
} else {
    Write-Host "   ℹ mypy缓存不存在" -ForegroundColor Gray
}

# 5. 清理覆盖率报告
Write-Host "5. 清理代码覆盖率文件..." -ForegroundColor Yellow
$coverageCount = 0
if (Test-Path ".coverage") {
    Write-Host "   删除.coverage文件..." -ForegroundColor Gray
    Remove-Item ".coverage" -Force
    $coverageCount++
}

if (Test-Path "htmlcov") {
    Write-Host "   删除HTML覆盖率报告..." -ForegroundColor Gray
    Remove-Item "htmlcov" -Recurse -Force
    $coverageCount++
}

if ($coverageCount -gt 0) {
    Write-Host "   ✓ 覆盖率文件已清理" -ForegroundColor Green
    $cleanedItems++
} else {
    Write-Host "   ℹ 覆盖率文件不存在" -ForegroundColor Gray
}

# 6. 清理日志文件（可选）
Write-Host "6. 检查日志文件..." -ForegroundColor Yellow
if (Test-Path "logs") {
    $logFiles = Get-ChildItem "logs" -File
    if ($logFiles.Count -gt 0) {
        Write-Host "   发现 $($logFiles.Count) 个日志文件" -ForegroundColor Gray
        $response = Read-Host "   是否清理日志文件？(y/N)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            Remove-Item "logs\*" -Force
            Write-Host "   ✓ 日志文件已清理" -ForegroundColor Green
            $cleanedItems++
        } else {
            Write-Host "   ℹ 保留日志文件" -ForegroundColor Gray
        }
    } else {
        Write-Host "   ℹ 日志目录为空" -ForegroundColor Gray
    }
} else {
    Write-Host "   ℹ 日志目录不存在" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== 清理完成 ===" -ForegroundColor Green
if ($cleanedItems -gt 0) {
    Write-Host "清理了 $cleanedItems 类缓存文件" -ForegroundColor White
} else {
    Write-Host "没有找到需要清理的缓存文件" -ForegroundColor White
}
Write-Host ""
