# Git 提交和 GitHub 连接指南

## 第一步：配置 Git 用户信息

在 PowerShell 中运行以下命令（替换为你的信息）：

```powershell
git config --global user.name "你的GitHub用户名"
git config --global user.email "你的GitHub邮箱"
```

例如：
```powershell
git config --global user.name "zhangsan"
git config --global user.email "zhangsan@example.com"
```

## 第二步：提交代码

代码已经添加到暂存区，现在提交：

```powershell
git commit -m "Initial commit: OpenClaw Stock Selection Skill - Optimized Version"
```

## 第三步：连接到 GitHub

### 方法一：如果你还没有 GitHub 仓库

1. **在 GitHub 上创建新仓库**
   - 访问 https://github.com/new
   - 输入仓库名称（例如：`openclaw-stock-selection`）
   - 选择 Public 或 Private
   - **不要**勾选 "Initialize this repository with a README"（因为我们已经有了）
   - 点击 "Create repository"

2. **添加远程仓库并推送**
   ```powershell
   # 替换为你的仓库地址
   git remote add origin https://github.com/你的用户名/仓库名.git
   git branch -M main
   git push -u origin main
   ```

### 方法二：如果你已经有 GitHub 仓库

```powershell
# 替换为你的仓库地址
git remote add origin https://github.com/你的用户名/仓库名.git
git branch -M main
git push -u origin main
```

## 快速执行脚本

或者，你可以直接运行我创建的脚本：

```powershell
.\setup_git.ps1
```

这个脚本会：
1. 检查并配置 Git 用户信息
2. 自动提交代码
3. 引导你连接 GitHub

## 常见问题

### 1. 如果提示需要身份验证

GitHub 现在要求使用 Personal Access Token 而不是密码：

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限：至少勾选 `repo`
4. 生成后复制 token
5. 推送时使用 token 作为密码

### 2. 如果使用 SSH 方式

```powershell
# 使用 SSH 地址
git remote add origin git@github.com:你的用户名/仓库名.git
git push -u origin main
```

### 3. 如果分支名称是 master 而不是 main

```powershell
git branch -M main
git push -u origin main
```

## 文件说明

已准备提交的文件：
- ✅ `stock_selection_skill.py` - 主技能文件（性能优化版）
- ✅ `_meta.json` - OpenClaw 元数据配置
- ✅ `package.json` - 包管理配置
- ✅ `requirements.txt` - Python 依赖
- ✅ `README.md` - 使用说明
- ✅ `OPENCLAW_CONFIG.md` - OpenClaw 配置指南
- ✅ `.gitignore` - Git 忽略文件

## 下一步

提交成功后，你可以：
1. 在 GitHub 上查看你的代码
2. 添加更多功能并继续提交
3. 分享仓库链接给其他人
4. 设置 GitHub Actions 进行自动化测试
