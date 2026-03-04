# 推送代码到 GitHub - 完整指南

## 问题原因

连接超时的主要原因是：**GitHub 仓库可能还没有创建**。

Git 无法推送到一个不存在的仓库，所以会显示连接超时错误。

## 最简单解决方案

### 方法 1：使用 GitHub CLI（推荐）🚀

如果你安装了 GitHub CLI：

```powershell
# 1. 登录 GitHub
gh auth login

# 2. 创建仓库并推送（一键完成）
gh repo create openclaw-stock-selection --public --source=. --remote=origin --push
```

如果没有安装，先安装：
```powershell
winget install GitHub.cli
```

### 方法 2：手动创建仓库（最可靠）✅

**步骤 1：在 GitHub 上创建仓库**

1. 打开浏览器，访问：https://github.com/new
2. 填写信息：
   - **Repository name**: `openclaw-stock-selection`
   - **Description**: `OpenClaw Skills - A股选股技能（性能优化版）`
   - **Visibility**: 选择 Public 或 Private
   - **重要**：不要勾选以下选项：
     - ❌ Add a README file
     - ❌ Add .gitignore  
     - ❌ Choose a license
3. 点击绿色的 **"Create repository"** 按钮

**步骤 2：推送代码**

创建仓库后，在 PowerShell 中运行：

```powershell
git push -u origin main
```

**步骤 3：身份验证**

如果提示输入用户名和密码：
- **Username**: `wzhbest`
- **Password**: 使用 **Personal Access Token**（不是 GitHub 密码）

**如何获取 Token：**
1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 输入名称（如：`git-push`）
4. 选择过期时间
5. **勾选权限**：至少勾选 `repo`（完整仓库访问权限）
6. 点击 "Generate token"
7. **复制 token**（只显示一次，请保存好！）
8. 推送时，密码输入这个 token

## 当前代码状态

✅ **已提交的代码：**
- `1522421` - Initial commit: OpenClaw Stock Selection Skill - Optimized Version
- `7abdc01` - Add repository creation guide
- `最新` - Add GitHub connection troubleshooting guide

✅ **远程仓库已配置：**
```
origin  https://github.com/wzhbest/openclaw-stock-selection.git
```

✅ **所有文件已准备好：**
- stock_selection_skill.py（主技能文件）
- _meta.json（OpenClaw 配置）
- README.md（使用说明）
- requirements.txt（依赖列表）
- 其他配置文件

## 推送命令总结

```powershell
# 检查状态
git status
git log --oneline

# 推送代码（创建仓库后运行）
git push -u origin main

# 如果失败，检查远程仓库
git remote -v
```

## 常见问题

**Q: 提示 "repository not found"**  
A: 仓库还没有创建，请先按照方法 2 创建仓库

**Q: 提示 "authentication failed"**  
A: 需要使用 Personal Access Token，不是 GitHub 密码

**Q: 提示 "connection timeout"**  
A: 可能是网络问题，尝试：
- 使用 VPN
- 检查防火墙设置
- 稍后重试

## 完成后的验证

推送成功后，访问以下地址查看你的代码：
```
https://github.com/wzhbest/openclaw-stock-selection
```

---

**现在请按照"方法 2"在 GitHub 上创建仓库，然后运行 `git push -u origin main` 即可！**
