# 缓存清理脚本
# 用于清除测试文章和过期缓存

Write-Host "🧹 开始清理RSS缓存..." -ForegroundColor Cyan

# 运行Python清理脚本
python clean_cache.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 缓存清理完成！" -ForegroundColor Green
} else {
    Write-Host "❌ 缓存清理失败！" -ForegroundColor Red
}

Write-Host "`n📊 当前缓存状态:" -ForegroundColor Yellow
Get-ChildItem -Path "cache\*.json" | ForEach-Object {
    $size = [math]::Round($_.Length / 1KB, 2)
    Write-Host "   $($_.Name) ($size KB)" -ForegroundColor Gray
}

Write-Host "`n💡 提示: 如需手动清理特定内容，请编辑 clean_cache.py 文件" -ForegroundColor Blue
