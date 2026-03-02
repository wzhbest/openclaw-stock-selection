# 创建 GitHub 仓库并推送代码

## 步骤 1：在 GitHub 上创建仓库

1. 访问：https://github.com/new
2. 仓库名称输入：`openclaw-stock-selection`（或你喜欢的名称）
3. 描述：`OpenClaw Skills - A股选股技能（性能优化版）`
4. 选择：**Public** 或 **Private**
5. **重要**：**不要**勾选以下选项：
   - ❌ Add a README file
   - ❌ Add .gitignore
   - ❌ Choose a license
6. 点击 **"Create repository"**

## 步骤 2：推送代码

创建仓库后，运行以下命令：

```powershell
# 如果仓库名称不同，先删除旧的远程仓库
git remote remove origin

# 添加新的远程仓库（替换为你的实际仓库名）
git remote add origin https://github.com/wzhbest/你的仓库名.git

# 推送代码
git branch -M main
git push -u origin main
```

## 如果遇到身份验证问题

GitHub 现在要求使用 **Personal Access Token** 而不是密码：

1. 访问：https://github.com/settings/tokens
2. 点击 **"Generate new token (classic)"**
3. 输入名称（如：`openclaw-push`）
4. 选择过期时间
5. 勾选权限：**至少勾选 `repo`**
6. 点击 **"Generate token"**
7. **复制 token**（只显示一次！）
8. 推送时，用户名输入你的 GitHub 用户名，密码输入刚才复制的 token

## 当前状态

✅ 代码已提交到本地仓库
✅ 远程仓库已配置：`https://github.com/wzhbest/openclaw-stock-selection.git`
⏳ 等待在 GitHub 上创建仓库后即可推送
