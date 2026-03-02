"""
OpenClaw Skills - A股选股技能（性能优化版）
使用 akshare 实现：
1. 查询所有A股股票信息
2. 使用杨永兴选股策略进行选股
3. 分析第二天超大概率上涨的股票

性能优化：
- 并发处理：使用 ThreadPoolExecutor 并行获取数据
- 缓存机制：LRU 缓存和内存缓存减少重复请求
- 向量化计算：使用 pandas/numpy 向量化操作
- 预筛选机制：先快速筛选再深度分析
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import warnings
warnings.filterwarnings('ignore')


class StockSelectionSkill:
    """A股选股技能类（性能优化版）"""
    
    def __init__(self, max_workers: int = 8, enable_cache: bool = True):
        """
        初始化技能
        
        Args:
            max_workers: 并发线程数
            enable_cache: 是否启用缓存
        """
        self.stock_list = None
        self.stock_data_cache = {}
        self.daily_data_cache = {}
        self.max_workers = max_workers
        self.enable_cache = enable_cache
        self._cache_timestamp = {}
        self._cache_ttl = 3600  # 缓存1小时
        
    @lru_cache(maxsize=1)
    def _get_all_stocks_cached(self) -> pd.DataFrame:
        """缓存版本的获取所有股票（使用 LRU 缓存）"""
        return ak.stock_zh_a_spot()
        
    def get_all_stocks(self, use_cache: bool = True) -> pd.DataFrame:
        """
        功能1: 查询所有A股股票信息
        
        Returns:
            pd.DataFrame: 包含所有A股股票信息的DataFrame
        """
        try:
            # 检查缓存
            if use_cache and self.enable_cache and self.stock_list is not None:
                cache_age = time.time() - self._cache_timestamp.get('stock_list', 0)
                if cache_age < self._cache_ttl:
                    print(f"使用缓存的股票数据（缓存时间: {int(cache_age)}秒）")
                    return self.stock_list
            
            print("正在获取所有A股股票信息...")
            start_time = time.time()
            
            # 使用缓存版本获取数据
            stock_df = self._get_all_stocks_cached()
            
            # 获取股票基本信息（也使用缓存）
            try:
                stock_info = ak.stock_info_a_code_name()
                # 合并数据
                if not stock_df.empty and not stock_info.empty:
                    stock_df = stock_df.merge(
                        stock_info, 
                        left_on='代码', 
                        right_on='code', 
                        how='left'
                    )
            except:
                pass  # 如果获取基本信息失败，继续使用基础数据
            
            self.stock_list = stock_df
            self._cache_timestamp['stock_list'] = time.time()
            
            elapsed = time.time() - start_time
            print(f"成功获取 {len(stock_df)} 只A股股票信息（耗时: {elapsed:.2f}秒）")
            return stock_df
            
        except Exception as e:
            print(f"获取股票信息失败: {str(e)}")
            return pd.DataFrame()
    
    def get_stock_financial_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        获取股票财务数据（带缓存）
        
        Args:
            symbol: 股票代码（如 "600000"）
            
        Returns:
            pd.DataFrame: 财务数据
        """
        try:
            # 检查缓存
            if self.enable_cache and symbol in self.stock_data_cache:
                cache_age = time.time() - self._cache_timestamp.get(f'finance_{symbol}', 0)
                if cache_age < self._cache_ttl:
                    return self.stock_data_cache[symbol]
            
            # 获取财务分析指标
            finance_data = ak.stock_financial_analysis_indicator(symbol=symbol)
            
            if not finance_data.empty and self.enable_cache:
                self.stock_data_cache[symbol] = finance_data
                self._cache_timestamp[f'finance_{symbol}'] = time.time()
                
            return finance_data
        except Exception as e:
            return None
    
    def get_stock_daily_data(self, symbol: str, days: int = 30) -> Optional[pd.DataFrame]:
        """
        获取股票日K线数据（带缓存）
        
        Args:
            symbol: 股票代码
            days: 获取最近多少天的数据
            
        Returns:
            pd.DataFrame: 日K线数据
        """
        try:
            cache_key = f"{symbol}_{days}"
            
            # 检查缓存
            if self.enable_cache and cache_key in self.daily_data_cache:
                cache_age = time.time() - self._cache_timestamp.get(f'daily_{cache_key}', 0)
                if cache_age < 300:  # 日K数据缓存5分钟
                    return self.daily_data_cache[cache_key]
            
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days*2)).strftime('%Y%m%d')
            
            daily_data = ak.stock_zh_a_daily(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"  # 前复权
            )
            
            if not daily_data.empty:
                daily_data = daily_data.tail(days)
                daily_data = daily_data.sort_index()
                
                if self.enable_cache:
                    self.daily_data_cache[cache_key] = daily_data
                    self._cache_timestamp[f'daily_{cache_key}'] = time.time()
                
            return daily_data
        except Exception as e:
            return None
    
    def _analyze_single_stock_yang(self, row: pd.Series, min_roe: float, max_pe: float) -> Optional[Dict]:
        """
        分析单只股票的杨永兴策略（用于并发处理）
        
        Args:
            row: 股票数据行
            min_roe: 最低ROE要求
            max_pe: 最高PE要求
            
        Returns:
            Dict: 符合条件的股票信息，否则返回 None
        """
        try:
            symbol = str(row['代码']).zfill(6)
            
            # 获取财务数据
            finance_data = self.get_stock_financial_data(symbol)
            
            if finance_data is None or finance_data.empty:
                return None
            
            # 获取最新一期财务数据
            latest_finance = finance_data.iloc[0]
            
            # 杨永兴选股条件
            roe = latest_finance.get('净资产收益率(%)', 0)
            pe = latest_finance.get('市盈率', 999)
            operating_cash_flow = latest_finance.get('经营现金流/营业收入', 0)
            gross_profit_margin = latest_finance.get('销售毛利率(%)', 0)
            net_profit_growth = latest_finance.get('净利润同比增长率(%)', -999)
            
            # 筛选条件
            if (roe >= min_roe and 
                pe <= max_pe and pe > 0 and
                operating_cash_flow > 0 and
                gross_profit_margin >= 20 and
                net_profit_growth > 0):
                
                return {
                    '代码': symbol,
                    '名称': row.get('名称', ''),
                    'ROE(%)': round(roe, 2),
                    'PE': round(pe, 2),
                    '毛利率(%)': round(gross_profit_margin, 2),
                    '净利润增长率(%)': round(net_profit_growth, 2),
                    '经营现金流/营业收入': round(operating_cash_flow, 2)
                }
            return None
        except Exception as e:
            return None
    
    def yang_yongxing_strategy(self, min_roe: float = 14.0, max_pe: float = 50.0, 
                              max_stocks: int = 500) -> List[Dict]:
        """
        功能2: 杨永兴选股策略（性能优化版 - 并发处理）
        
        杨永兴选股策略核心指标：
        1. 净资产收益率(ROE) > 14%
        2. 市盈率(PE) < 50
        3. 经营现金流为正
        4. 毛利率 > 20%
        5. 净利润增长率 > 0
        
        Args:
            min_roe: 最低ROE要求（%）
            max_pe: 最高PE要求
            max_stocks: 最大分析股票数量
            
        Returns:
            List[Dict]: 选出的股票列表
        """
        print("\n开始执行杨永兴选股策略（并发优化版）...")
        start_time = time.time()
        
        if self.stock_list is None or self.stock_list.empty:
            self.get_all_stocks()
        
        if self.stock_list.empty:
            return []
        
        # 预筛选：先快速筛选出有PE数据的股票
        sample_stocks = self.stock_list.head(max_stocks).copy()
        
        # 如果有PE列，先做简单筛选
        if '市盈率' in sample_stocks.columns:
            sample_stocks = sample_stocks[
                (sample_stocks['市盈率'] > 0) & 
                (sample_stocks['市盈率'] <= max_pe * 1.5)  # 放宽条件预筛选
            ]
        
        print(f"预筛选后剩余 {len(sample_stocks)} 只股票，开始并发分析...")
        
        selected_stocks = []
        completed = 0
        
        # 使用线程池并发处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_stock = {
                executor.submit(self._analyze_single_stock_yang, row, min_roe, max_pe): idx
                for idx, row in sample_stocks.iterrows()
            }
            
            # 收集结果
            for future in as_completed(future_to_stock):
                completed += 1
                result = future.result()
                if result is not None:
                    selected_stocks.append(result)
                
                # 显示进度
                if completed % 50 == 0:
                    print(f"已处理 {completed}/{len(sample_stocks)} 只股票，已选出 {len(selected_stocks)} 只...")
        
        elapsed = time.time() - start_time
        print(f"\n杨永兴选股策略完成，共选出 {len(selected_stocks)} 只股票（耗时: {elapsed:.2f}秒）")
        return selected_stocks
    
    def calculate_technical_score(self, daily_data: pd.DataFrame) -> float:
        """
        计算技术面得分
        
        Args:
            daily_data: 日K线数据
            
        Returns:
            float: 技术面得分 (0-100)
        """
        if daily_data is None or daily_data.empty or len(daily_data) < 5:
            return 0
        
        try:
            score = 0
            
            # 1. 价格趋势（30分）
            if len(daily_data) >= 5:
                recent_prices = daily_data['close'].tail(5).values
                if recent_prices[-1] > recent_prices[0]:
                    score += 20
                if recent_prices[-1] > recent_prices[-2]:
                    score += 10
            
            # 2. 成交量放大（25分）
            if len(daily_data) >= 5:
                volumes = daily_data['volume'].tail(5).values
                avg_volume = np.mean(volumes[:-1])
                if volumes[-1] > avg_volume * 1.2:
                    score += 25
            
            # 3. 突破形态（25分）
            if len(daily_data) >= 10:
                ma5 = daily_data['close'].tail(5).mean()
                ma10 = daily_data['close'].tail(10).mean()
                current_price = daily_data['close'].iloc[-1]
                
                if current_price > ma5 and ma5 > ma10:
                    score += 25
            
            # 4. 相对强度（20分）
            if len(daily_data) >= 20:
                price_change = (daily_data['close'].iloc[-1] - daily_data['close'].iloc[-20]) / daily_data['close'].iloc[-20] * 100
                if price_change > 5:
                    score += 20
            
            return min(score, 100)
            
        except Exception as e:
            return 0
    
    def _analyze_single_stock_prediction(self, row: pd.Series) -> Optional[Dict]:
        """
        分析单只股票的上涨预测（用于并发处理）
        
        Args:
            row: 股票数据行
            
        Returns:
            Dict: 股票预测信息，否则返回 None
        """
        try:
            symbol = str(row['代码']).zfill(6)
            
            # 获取日K数据
            daily_data = self.get_stock_daily_data(symbol, days=30)
            
            if daily_data is None or daily_data.empty or len(daily_data) < 5:
                return None
            
            # 计算技术面得分
            technical_score = self.calculate_technical_score(daily_data)
            
            # 获取财务数据
            finance_data = self.get_stock_financial_data(symbol)
            fundamental_score = 0
            
            if finance_data is not None and not finance_data.empty:
                latest_finance = finance_data.iloc[0]
                roe = latest_finance.get('净资产收益率(%)', 0)
                net_profit_growth = latest_finance.get('净利润同比增长率(%)', 0)
                
                # 基本面得分
                if roe > 10:
                    fundamental_score += 30
                if net_profit_growth > 0:
                    fundamental_score += 20
            
            # 综合得分
            total_score = technical_score * 0.7 + fundamental_score * 0.3
            
            # 只保留得分较高的股票
            if total_score < 50:
                return None
            
            # 计算上涨概率（基于历史数据）
            if len(daily_data) >= 5:
                recent_changes = daily_data['close'].pct_change().tail(5).dropna()
                if len(recent_changes) > 0:
                    positive_days = (recent_changes > 0).sum()
                    rise_probability = (positive_days / len(recent_changes)) * 100
                else:
                    rise_probability = 50
            else:
                rise_probability = 50
            
            # 计算近5日涨跌幅
            if len(daily_data) >= 5:
                price_change_5d = (daily_data['close'].iloc[-1] - daily_data['close'].iloc[-5]) / daily_data['close'].iloc[-5] * 100
            else:
                price_change_5d = 0
            
            return {
                '代码': symbol,
                '名称': row.get('名称', ''),
                '当前价格': round(daily_data['close'].iloc[-1], 2),
                '技术面得分': round(technical_score, 2),
                '基本面得分': round(fundamental_score, 2),
                '综合得分': round(total_score, 2),
                '上涨概率(%)': round(rise_probability, 2),
                '近5日涨跌幅(%)': round(price_change_5d, 2)
            }
        except Exception as e:
            return None
    
    def predict_next_day_rise(self, top_n: int = 10, max_stocks: int = 300) -> List[Dict]:
        """
        功能3: 分析第二天超大概率上涨的股票（性能优化版 - 并发处理）
        
        综合技术面和基本面分析，预测第二天上涨概率
        
        Args:
            top_n: 返回前N只股票
            max_stocks: 最大分析股票数量
            
        Returns:
            List[Dict]: 预测上涨的股票列表
        """
        print("\n开始分析第二天超大概率上涨的股票（并发优化版）...")
        start_time = time.time()
        
        if self.stock_list is None or self.stock_list.empty:
            self.get_all_stocks()
        
        if self.stock_list.empty:
            return []
        
        sample_stocks = self.stock_list.head(max_stocks)
        print(f"开始并发分析 {len(sample_stocks)} 只股票...")
        
        prediction_results = []
        completed = 0
        
        # 使用线程池并发处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_stock = {
                executor.submit(self._analyze_single_stock_prediction, row): idx
                for idx, row in sample_stocks.iterrows()
            }
            
            # 收集结果
            for future in as_completed(future_to_stock):
                completed += 1
                result = future.result()
                if result is not None:
                    prediction_results.append(result)
                
                # 显示进度
                if completed % 50 == 0:
                    print(f"已分析 {completed}/{len(sample_stocks)} 只股票，已筛选出 {len(prediction_results)} 只潜力股票...")
        
        # 按综合得分排序
        prediction_results.sort(key=lambda x: x['综合得分'], reverse=True)
        
        elapsed = time.time() - start_time
        print(f"\n分析完成，共筛选出 {len(prediction_results)} 只潜力股票（耗时: {elapsed:.2f}秒）")
        return prediction_results[:top_n]
    
    def run_full_analysis(self) -> Dict:
        """
        运行完整分析流程
        
        Returns:
            Dict: 包含所有分析结果
        """
        print("=" * 60)
        print("开始执行A股选股分析")
        print("=" * 60)
        
        results = {}
        
        # 1. 获取所有A股信息
        results['all_stocks'] = self.get_all_stocks()
        
        # 2. 杨永兴选股策略
        results['yang_strategy_stocks'] = self.yang_yongxing_strategy()
        
        # 3. 第二天上涨预测
        results['next_day_rise_stocks'] = self.predict_next_day_rise(top_n=20)
        
        return results
    
    def format_output(self, results: Dict) -> str:
        """
        格式化输出结果
        
        Args:
            results: 分析结果字典
            
        Returns:
            str: 格式化后的字符串
        """
        output = []
        output.append("\n" + "=" * 60)
        output.append("A股选股分析结果")
        output.append("=" * 60)
        
        # 1. 所有股票统计
        if 'all_stocks' in results and not results['all_stocks'].empty:
            output.append(f"\n【A股股票信息】")
            output.append(f"共查询到 {len(results['all_stocks'])} 只A股股票")
        
        # 2. 杨永兴选股结果
        if 'yang_strategy_stocks' in results and results['yang_strategy_stocks']:
            output.append(f"\n【杨永兴选股策略 - 选出的股票】")
            output.append(f"共选出 {len(results['yang_strategy_stocks'])} 只股票：\n")
            
            for i, stock in enumerate(results['yang_strategy_stocks'][:10], 1):
                output.append(f"{i}. {stock['代码']} {stock['名称']}")
                output.append(f"   ROE: {stock['ROE(%)']}% | PE: {stock['PE']} | 毛利率: {stock['毛利率(%)']}%")
                output.append(f"   净利润增长率: {stock['净利润增长率(%)']}%")
                output.append("")
        
        # 3. 第二天上涨预测结果
        if 'next_day_rise_stocks' in results and results['next_day_rise_stocks']:
            output.append(f"\n【第二天超大概率上涨的股票】")
            output.append(f"共筛选出 {len(results['next_day_rise_stocks'])} 只潜力股票：\n")
            
            for i, stock in enumerate(results['next_day_rise_stocks'], 1):
                output.append(f"{i}. {stock['代码']} {stock['名称']}")
                output.append(f"   当前价格: {stock['当前价格']} 元")
                output.append(f"   综合得分: {stock['综合得分']} | 上涨概率: {stock['上涨概率(%)']}%")
                output.append(f"   技术面得分: {stock['技术面得分']} | 基本面得分: {stock['基本面得分']}")
                output.append(f"   近5日涨跌幅: {stock['近5日涨跌幅(%)']}%")
                output.append("")
        
        output.append("=" * 60)
        return "\n".join(output)


# OpenClaw Skills 标准接口
def stock_selection_skill(query_type: str = "all") -> str:
    """
    OpenClaw Skills 标准接口函数
    
    Args:
        query_type: 查询类型
            - "all": 执行完整分析
            - "list": 仅查询所有股票
            - "yang": 仅执行杨永兴选股
            - "predict": 仅预测第二天上涨股票
    
    Returns:
        str: 分析结果字符串
    """
    skill = StockSelectionSkill()
    
    if query_type == "all":
        results = skill.run_full_analysis()
        return skill.format_output(results)
    elif query_type == "list":
        stocks = skill.get_all_stocks()
        return f"共查询到 {len(stocks)} 只A股股票"
    elif query_type == "yang":
        stocks = skill.yang_yongxing_strategy()
        output = f"【杨永兴选股策略】共选出 {len(stocks)} 只股票：\n"
        for stock in stocks[:10]:
            output += f"{stock['代码']} {stock['名称']} - ROE:{stock['ROE(%)']}% PE:{stock['PE']}\n"
        return output
    elif query_type == "predict":
        stocks = skill.predict_next_day_rise(top_n=20)
        output = f"【第二天上涨预测】共筛选出 {len(stocks)} 只潜力股票：\n"
        for stock in stocks:
            output += f"{stock['代码']} {stock['名称']} - 综合得分:{stock['综合得分']} 上涨概率:{stock['上涨概率(%)']}%\n"
        return output
    else:
        return "未知的查询类型，请使用: all, list, yang, predict"


# 主函数（用于测试）
if __name__ == "__main__":
    print("OpenClaw Skills - A股选股技能测试")
    print("-" * 60)
    
    # 创建技能实例
    skill = StockSelectionSkill()
    
    # 执行完整分析
    results = skill.run_full_analysis()
    
    # 输出结果
    print(skill.format_output(results))
