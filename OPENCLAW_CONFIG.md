# OpenClaw Skills 配置指南

本文档说明如何在 OpenClaw 上配置和使用 A 股选股技能。

## 一、部署前准备

### 1. 服务器要求
- **推荐配置**：2vCPU + 2GiB 内存 + 40GiB 云盘
- **操作系统**：支持 Linux（推荐 Ubuntu 20.04+）
- **Python 版本**：Python 3.8+

### 2. 依赖安装

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 或者使用 pip3
pip3 install -r requirements.txt
```

## 二、OpenClaw 部署步骤

### 方法一：通过阿里云一键部署（推荐）

1. **访问部署页面**
   - 访问阿里云 OpenClaw 部署页面
   - 选择 OpenClaw 镜像（Moltbot/Clawdbot）

2. **配置服务器**
   - 选择配置：2vCPU + 2GiB 内存
   - 地域：建议选择美国弗吉尼亚（免备案）
   - 放通端口：18789（OpenClaw 核心通信端口）

3. **配置 API Key**
   - 在阿里云控制台获取百炼 API Key
   - 在 OpenClaw 配置界面粘贴 Access Key ID 和 Secret

4. **生成访问 Token**
   ```bash
   ssh root@你的服务器公网IP
   cat /root/.openclaw/openclaw.json | grep token
   ```

5. **验证部署**
   - 浏览器访问：`http://服务器公网IP:18789`
   - 输入 Token 登录

### 方法二：手动部署到现有 OpenClaw 实例

1. **上传技能文件**
   ```bash
   # 将以下文件上传到 OpenClaw skills 目录
   # 通常位于：/root/.openclaw/skills/ 或类似路径
   
   scp stock_selection_skill.py user@server:/path/to/openclaw/skills/
   scp _meta.json user@server:/path/to/openclaw/skills/stock-selection-skill/
   scp package.json user@server:/path/to/openclaw/skills/stock-selection-skill/
   scp requirements.txt user@server:/path/to/openclaw/skills/stock-selection-skill/
   ```

2. **安装依赖**
   ```bash
   ssh user@server
   cd /path/to/openclaw/skills/stock-selection-skill
   pip install -r requirements.txt
   ```

3. **注册技能**
   - 在 OpenClaw 管理界面中，找到 "Skills" 或 "技能管理"
   - 点击 "添加技能" 或 "Register Skill"
   - 选择技能目录或直接指定 `_meta.json` 文件路径

## 三、技能配置

### 1. 配置文件说明

- **`_meta.json`**：技能元数据，定义技能名称、描述、函数接口等
- **`package.json`**：包管理文件，定义依赖和脚本
- **`requirements.txt`**：Python 依赖列表

### 2. 自定义配置

在 `_meta.json` 中可以修改以下配置：

```json
{
  "config": {
    "max_workers": 8,      // 并发线程数（可根据服务器性能调整）
    "enable_cache": true    // 是否启用缓存
  }
}
```

## 四、使用方法

### 1. 在 OpenClaw 中调用

#### 方式一：通过对话界面
```
用户：帮我执行A股选股分析
AI：正在执行完整分析...
```

#### 方式二：通过 API 调用
```python
from stock_selection_skill import stock_selection_skill

# 完整分析
result = stock_selection_skill("all")

# 仅查询股票列表
result = stock_selection_skill("list")

# 仅执行杨永兴选股
result = stock_selection_skill("yang")

# 仅预测第二天上涨股票
result = stock_selection_skill("predict")
```

### 2. 命令行测试

```bash
# 直接运行测试
python stock_selection_skill.py

# 或使用 npm script（如果配置了）
npm test
```

## 五、性能优化说明

### 1. 并发处理
- 默认使用 8 个线程并发处理
- 可通过 `max_workers` 参数调整
- 建议根据服务器 CPU 核心数设置（核心数 × 2）

### 2. 缓存机制
- **股票列表缓存**：1 小时
- **财务数据缓存**：1 小时
- **日K数据缓存**：5 分钟
- 可通过 `enable_cache=False` 禁用缓存

### 3. 预筛选机制
- 杨永兴策略：先按 PE 预筛选，再深度分析
- 上涨预测：只分析得分 ≥ 50 的股票

## 六、定时任务配置

### 使用 OpenClaw 定时任务

在 OpenClaw 管理界面配置定时任务：

```json
{
  "name": "每日选股分析",
  "schedule": "0 9 * * 1-5",  // 每个工作日 9:00 执行
  "skill": "stock-selection-skill",
  "function": "stock_selection_skill",
  "params": {
    "query_type": "all"
  }
}
```

### 使用 crontab（Linux）

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每个工作日 9:00 执行）
0 9 * * 1-5 cd /path/to/skill && python stock_selection_skill.py >> /var/log/stock_selection.log 2>&1
```

## 七、QQ 机器人集成（可选）

1. **安装 QQ 渠道插件**
   ```bash
   git clone https://github.com/sliverp/qqbot.git /root/.openclaw/qqbot
   openclaw plugins install qqbot
   ```

2. **配置 QQ 机器人**
   - 进入 QQ 开放平台
   - 复制 AppID、AppSecret、Token
   - 在 OpenClaw 配置界面粘贴并保存

3. **使用方式**
   ```
   QQ群：@机器人 帮我选股
   机器人：正在执行A股选股分析...
   ```

## 八、故障排查

### 1. 技能未识别
- 检查 `_meta.json` 格式是否正确
- 确认文件路径是否正确
- 查看 OpenClaw 日志：`/var/log/openclaw/`

### 2. 依赖安装失败
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 数据获取失败
- 检查网络连接
- akshare 可能受到访问频率限制，建议启用缓存
- 查看错误日志定位问题

### 4. 性能问题
- 减少 `max_stocks` 参数（默认 300-500）
- 增加缓存时间
- 调整 `max_workers` 线程数

## 九、监控和维护

### 1. 日志查看
```bash
# OpenClaw 日志
tail -f /var/log/openclaw/openclaw.log

# 技能执行日志（如果配置了）
tail -f /var/log/stock_selection.log
```

### 2. 性能监控
- 记录每次执行时间
- 监控内存使用情况
- 跟踪选股准确率（需要手动验证）

### 3. 定期更新
```bash
# 更新 akshare
pip install --upgrade akshare

# 更新技能代码
git pull  # 如果使用 git 管理
```

## 十、注意事项

1. **数据准确性**：本技能仅供参考，不构成投资建议
2. **API 限制**：akshare 是免费库，可能受到访问频率限制
3. **数据延迟**：股票数据可能存在延迟，请以实际交易数据为准
4. **合规性**：请遵守相关法律法规，不得用于非法用途

## 十一、技术支持

如遇到问题，可以：
1. 查看 OpenClaw 官方文档
2. 检查 akshare 文档：https://akshare.akfamily.xyz/
3. 查看错误日志定位问题

---

**最后更新**：2024年
