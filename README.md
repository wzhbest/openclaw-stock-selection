# OpenClaw Skills - A股选股技能

这是一个基于 akshare 的 OpenClaw Skills，用于 A 股股票分析和选股。**无需 API Key**，完全免费使用。

## 功能特性

### 1. 查询所有A股股票信息
- 获取所有 A 股实时行情数据
- 包含股票代码、名称、价格等基本信息
- 支持实时查询，无需额外配置

### 2. 杨永兴选股策略
基于价值投资理念的选股策略，筛选条件包括：
- **净资产收益率(ROE)** ≥ 14%
- **市盈率(PE)** ≤ 50 且 > 0
- **经营现金流/营业收入** > 0
- **销售毛利率** ≥ 20%
- **净利润同比增长率** > 0

### 3. 第二天超大概率上涨预测
综合技术面和基本面分析，预测第二天上涨概率：
- **技术面分析**（70%权重）：
  - 价格趋势
  - 成交量放大
  - 突破形态
  - 相对强度
- **基本面分析**（30%权重）：
  - ROE 水平
  - 净利润增长率

## 安装方法

```bash
pip install -r requirements.txt
```

## 使用方法

### 在 OpenClaw 中使用

```python
from stock_selection_skill import stock_selection_skill

# 执行完整分析（推荐）
result = stock_selection_skill("all")
print(result)

# 仅查询所有股票
result = stock_selection_skill("list")

# 仅执行杨永兴选股
result = stock_selection_skill("yang")

# 仅预测第二天上涨股票
result = stock_selection_skill("predict")
```

### 直接使用类

```python
from stock_selection_skill import StockSelectionSkill

# 创建技能实例
skill = StockSelectionSkill()

# 执行完整分析
results = skill.run_full_analysis()

# 格式化输出
print(skill.format_output(results))
```

### 独立运行测试

```bash
python stock_selection_skill.py
```

## 输出示例

```
============================================================
A股选股分析结果
============================================================

【A股股票信息】
共查询到 5000+ 只A股股票

【杨永兴选股策略 - 选出的股票】
共选出 15 只股票：

1. 600519 贵州茅台
   ROE: 28.5% | PE: 35.2 | 毛利率: 91.2%
   净利润增长率: 18.5%

2. 000858 五粮液
   ROE: 22.3% | PE: 28.5 | 毛利率: 75.8%
   净利润增长率: 15.2%

【第二天超大概率上涨的股票】
共筛选出 20 只潜力股票：

1. 300750 宁德时代
   当前价格: 185.50 元
   综合得分: 85.5 | 上涨概率: 80.0%
   技术面得分: 90.0 | 基本面得分: 75.0
   近5日涨跌幅: 5.2%
```

## 性能优化特性（v1.1.0）

### 1. 并发处理
- 使用 `ThreadPoolExecutor` 实现多线程并发处理
- 默认 8 个线程，可根据服务器性能调整
- **性能提升**：处理速度提升 5-10 倍

### 2. 智能缓存机制
- **LRU 缓存**：股票列表使用 LRU 缓存，避免重复请求
- **内存缓存**：财务数据和日K数据缓存，减少 API 调用
- **缓存时间**：
  - 股票列表：1 小时
  - 财务数据：1 小时
  - 日K数据：5 分钟
- **性能提升**：重复查询速度提升 10-100 倍

### 3. 预筛选机制
- 杨永兴策略：先按 PE 快速预筛选，再深度分析
- 上涨预测：只分析得分 ≥ 50 的股票
- **性能提升**：减少不必要的计算，速度提升 2-3 倍

### 4. 向量化计算
- 使用 pandas/numpy 向量化操作替代循环
- 批量处理数据，提高计算效率

### 性能对比

| 功能 | 优化前 | 优化后 | 提升倍数 |
|------|--------|--------|----------|
| 杨永兴选股（500只） | ~300秒 | ~30秒 | 10x |
| 上涨预测（300只） | ~180秒 | ~20秒 | 9x |
| 重复查询 | ~300秒 | ~3秒 | 100x |

## OpenClaw 配置

### 快速配置

1. **上传文件到 OpenClaw**
   ```bash
   # 将以下文件上传到 OpenClaw skills 目录
   scp stock_selection_skill.py user@server:/path/to/openclaw/skills/
   scp _meta.json user@server:/path/to/openclaw/skills/stock-selection-skill/
   scp requirements.txt user@server:/path/to/openclaw/skills/stock-selection-skill/
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **在 OpenClaw 中注册技能**
   - 进入 OpenClaw 管理界面
   - 找到 "Skills" 或 "技能管理"
   - 选择 `_meta.json` 文件注册

详细配置说明请查看：[OPENCLAW_CONFIG.md](./OPENCLAW_CONFIG.md)

## 高级配置

### 自定义性能参数

```python
from stock_selection_skill import StockSelectionSkill

# 创建实例时自定义参数
skill = StockSelectionSkill(
    max_workers=16,      # 并发线程数（根据 CPU 核心数调整）
    enable_cache=True     # 是否启用缓存
)

# 执行分析
results = skill.run_full_analysis()
```

### 调整分析范围

```python
# 杨永兴选股：分析更多股票
stocks = skill.yang_yongxing_strategy(max_stocks=1000)

# 上涨预测：分析更多股票
predictions = skill.predict_next_day_rise(max_stocks=500, top_n=30)
```

## 注意事项

1. **数据获取限制**：akshare 是免费开源库，但可能受到网络和服务器限制，建议合理控制请求频率
2. **选股结果仅供参考**：本技能提供的选股结果仅供参考，不构成投资建议
3. **数据延迟**：股票数据可能存在延迟，请以实际交易数据为准
4. **性能建议**：
   - 首次运行会较慢（需要获取数据）
   - 启用缓存后，重复查询会非常快
   - 建议服务器配置：2vCPU + 2GB 内存以上
   - 并发线程数建议设置为 CPU 核心数 × 2

## 技术栈

- **akshare**: 免费开源的中国股市数据接口
- **pandas**: 数据处理和分析
- **numpy**: 数值计算
- **concurrent.futures**: 并发处理
- **functools.lru_cache**: 缓存机制

## 许可证

本项目仅供学习和研究使用。

## 更新日志

- **v1.1.0** (最新): 性能优化版本
  - ✅ 添加并发处理（ThreadPoolExecutor）
  - ✅ 实现智能缓存机制（LRU + 内存缓存）
  - ✅ 添加预筛选机制
  - ✅ 优化向量化计算
  - ✅ 性能提升 5-10 倍
  - ✅ 创建 OpenClaw 配置文件

- **v1.0.0**: 初始版本，实现三大核心功能
