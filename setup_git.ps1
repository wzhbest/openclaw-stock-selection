# Git 配置和提交脚本
# 使用方法：在 PowerShell 中运行此脚本

Write-Host "=== Git 配置和提交脚本 ===" -ForegroundColor Green

# 检查是否已配置 Git 用户信息
$userName = git config --global user.name
$userEmail = git config --global user.email

if (-not $userName -or -not $userEmail) {
    Write-Host "`n需要配置 Git 用户信息" -ForegroundColor Yellow
    Write-Host "请输入您的 GitHub 用户名：" -ForegroundColor Cyan
    $name = Read-Host
    Write-Host "请输入您的 GitHub 邮箱：" -ForegroundColor Cyan
    $email = Read-Host
    
    git config --global user.name $name
    git config --global user.email $email
    Write-Host "`nGit 用户信息已配置！" -ForegroundColor Green
} else {
    Write-Host "`nGit 用户信息已配置：" -ForegroundColor Green
    Write-Host "  用户名: $userName" -ForegroundColor Cyan
    Write-Host "  邮箱: $userEmail" -ForegroundColor Cyan
}

# 提交代码
Write-Host "`n正在提交代码..." -ForegroundColor Yellow
git add .
git commit -m "Initial commit: OpenClaw Stock Selection Skill - Optimized Version"
Write-Host "代码已提交！" -ForegroundColor Green

# 检查是否已有远程仓库
$remote = git remote -v
if (-not $remote) {
    Write-Host "`n=== 连接到 GitHub ===" -ForegroundColor Yellow
    Write-Host "请按照以下步骤操作：" -ForegroundColor Cyan
    Write-Host "1. 在 GitHub 上创建一个新仓库（如果还没有）" -ForegroundColor White
    Write-Host "2. 复制仓库地址（例如：https://github.com/username/repo.git）" -ForegroundColor White
    Write-Host "3. 运行以下命令添加远程仓库：" -ForegroundColor White
    Write-Host "   git remote add origin <你的仓库地址>" -ForegroundColor Green
    Write-Host "4. 推送代码：" -ForegroundColor White
    Write-Host "   git push -u origin master" -ForegroundColor Green
    Write-Host "`n或者，如果你已经有仓库地址，请输入：" -ForegroundColor Cyan
    $repoUrl = Read-Host "GitHub 仓库地址"
    if ($repoUrl) {
        git remote add origin $repoUrl
        Write-Host "`n远程仓库已添加！" -ForegroundColor Green
        Write-Host "现在可以运行：git push -u origin master" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n远程仓库已配置：" -ForegroundColor Green
    Write-Host $remote -ForegroundColor Cyan
    Write-Host "`n可以运行以下命令推送代码：" -ForegroundColor Yellow
    Write-Host "git push -u origin master" -ForegroundColor Green
}
