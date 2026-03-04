# GitHub 连接问题修复脚本

Write-Host "=== GitHub 连接问题诊断和修复 ===" -ForegroundColor Green

# 1. 检查网络连接
Write-Host "`n1. 检查网络连接..." -ForegroundColor Yellow
$ping = Test-Connection github.com -Count 2 -Quiet
if ($ping) {
    Write-Host "   ✓ 网络连接正常" -ForegroundColor Green
} else {
    Write-Host "   ✗ 网络连接失败" -ForegroundColor Red
}

# 2. 检查 HTTPS 端口
Write-Host "`n2. 检查 HTTPS 端口 (443)..." -ForegroundColor Yellow
try {
    $tcp = Test-NetConnection github.com -Port 443 -WarningAction SilentlyContinue
    if ($tcp.TcpTestSucceeded) {
        Write-Host "   ✓ 端口 443 可访问" -ForegroundColor Green
    } else {
        Write-Host "   ✗ 端口 443 被阻止" -ForegroundColor Red
        Write-Host "   建议：使用代理或 VPN" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠ 无法测试端口" -ForegroundColor Yellow
}

# 3. 检查 Git 配置
Write-Host "`n3. 检查 Git 配置..." -ForegroundColor Yellow
$httpProxy = git config --global --get http.proxy
$httpsProxy = git config --global --get https.proxy
if ($httpProxy -or $httpsProxy) {
    Write-Host "   当前代理配置：" -ForegroundColor Cyan
    if ($httpProxy) { Write-Host "   HTTP Proxy: $httpProxy" -ForegroundColor Cyan }
    if ($httpsProxy) { Write-Host "   HTTPS Proxy: $httpsProxy" -ForegroundColor Cyan }
} else {
    Write-Host "   ✓ 未配置代理" -ForegroundColor Green
}

# 4. 优化 Git 配置
Write-Host "`n4. 优化 Git 配置..." -ForegroundColor Yellow
git config --global http.postBuffer 524288000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999
git config --global http.version HTTP/1.1
Write-Host "   ✓ Git 配置已优化" -ForegroundColor Green

# 5. 提供解决方案
Write-Host "`n=== 解决方案 ===" -ForegroundColor Green
Write-Host "`n方案 1: 使用代理（如果你有代理）" -ForegroundColor Cyan
Write-Host "   git config --global http.proxy http://代理地址:端口" -ForegroundColor White
Write-Host "   git config --global https.proxy http://代理地址:端口" -ForegroundColor White

Write-Host "`n方案 2: 使用 GitHub CLI (推荐)" -ForegroundColor Cyan
Write-Host "   1. 安装 GitHub CLI: winget install GitHub.cli" -ForegroundColor White
Write-Host "   2. 登录: gh auth login" -ForegroundColor White
Write-Host "   3. 创建仓库: gh repo create openclaw-stock-selection --public --source=. --remote=origin --push" -ForegroundColor White

Write-Host "`n方案 3: 手动上传（最简单）" -ForegroundColor Cyan
Write-Host "   1. 在 GitHub 上创建仓库: https://github.com/new" -ForegroundColor White
Write-Host "   2. 下载 GitHub Desktop 或使用网页上传" -ForegroundColor White

Write-Host "`n方案 4: 使用镜像站点" -ForegroundColor Cyan
Write-Host "   git remote set-url origin https://ghproxy.com/https://github.com/wzhbest/openclaw-stock-selection.git" -ForegroundColor White

Write-Host "`n当前远程仓库配置：" -ForegroundColor Yellow
git remote -v
