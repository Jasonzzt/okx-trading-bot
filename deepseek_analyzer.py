import logging
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

class DeepSeekAnalyzer:
    """DeepSeek API分析器"""
    
    def __init__(self, config):
        self.api_key = config.deepseek.api_key
        self.base_url = config.deepseek.base_url
        self.model = config.deepseek.model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logger.info("DeepSeek分析器初始化完成")
    
    def analyze_market_data(self, market_data: Dict, inst_id: str) -> Dict:
        """
        分析市场数据并返回交易建议
        """
        prompt = self._build_analysis_prompt(market_data, inst_id)
        
        try:
            logger.info("调用DeepSeek API进行分析...")
            response = self._call_deepseek_api(prompt)
            analysis_result = self._parse_analysis_response(response)
            logger.info(f"DeepSeek分析完成，建议: {analysis_result.get('recommendation', 'UNKNOWN')}")
            return analysis_result
        except Exception as e:
            logger.error(f"DeepSeek分析失败: {e}")
            return {
                "analysis": "分析失败",
                "recommendation": "HOLD",
                "confidence": 0.0,
                "reasoning": f"分析过程中出现错误: {e}",
                "support_levels": [],
                "resistance_levels": []
            }
    
    def _build_analysis_prompt(self, market_data: Dict, inst_id: str) -> str:
        """构建分析提示词"""
        ticker = market_data['ticker']['data'][0]
        orderbook = market_data['orderbook']['data'][0]
        klines = market_data['candlesticks']['data']
        trades = market_data['trades']['data']
        
        tech_indicators = self._calculate_technical_indicators(klines)
        
        prompt = f"""
        你是一个专业的加密货币交易分析师。请基于以下{inst_id}永续合约的市场数据进行分析，并给出明确的交易建议。

        当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        ## 实时行情数据:
        - 最新价格: {ticker['last']} USDT
        - 24小时变化: 最高 {ticker['high24h']} / 最低 {ticker['low24h']}
        - 买一价: {ticker['bidPx']} (数量: {ticker['bidSz']})
        - 卖一价: {ticker['askPx']} (数量: {ticker['askSz']})
        - 24小时成交量: {ticker['volCcy24h']} USDT

        ## 市场深度分析 (前10档):
        买盘深度:
        {self._format_orderbook_levels(orderbook['bids'][:10])}

        卖盘深度:
        {self._format_orderbook_levels(orderbook['asks'][:10])}

        ## 技术指标 (基于5分钟K线):
        {tech_indicators}

        ## 近期成交概况 (最近50笔):
        - 总成交笔数: {len(trades)}
        - 大额成交统计: {self._analyze_trades(trades)}

        请基于以上数据给出:
        1. 市场趋势分析
        2. 支撑位和阻力位识别
        3. 多空力量对比
        4. 明确的交易建议: BUY(买入), SELL(卖出), 或 HOLD(持有)
        5. 信心水平 (0-100%)
        6. 详细的分析理由

        请用JSON格式返回分析结果，包含以下字段:
        - analysis: 市场分析总结
        - recommendation: BUY/SELL/HOLD
        - confidence: 信心水平 (0-100)
        - support_levels: 支撑位列表
        - resistance_levels: 阻力位列表
        - reasoning: 详细分析理由
        """
        
        return prompt
    
    def _format_orderbook_levels(self, levels: List) -> str:
        """格式化订单簿层级"""
        formatted = []
        for i, level in enumerate(levels):
            formatted.append(f"  档位{i+1}: 价格 {level[0]} | 数量 {level[1]}")
        return "\n".join(formatted)
    
    def _calculate_technical_indicators(self, klines: List) -> str:
        """计算技术指标"""
        if not klines:
            return "无K线数据"
        
        try:
            df = pd.DataFrame(klines, columns=['ts', 'o', 'h', 'l', 'c', 'vol', 'volCcy', 'volCcyQuote', 'confirm'])
            
            for col in ['o', 'h', 'l', 'c', 'vol', 'volCcy']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.dropna()
            
            if len(df) < 20:
                return "数据不足计算技术指标"
            
            df['sma_10'] = df['c'].rolling(window=10).mean()
            df['sma_20'] = df['c'].rolling(window=20).mean()
            df = self._calculate_rsi(df, window=14)
            
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            indicators = f"""
            - 当前价格: {latest['c']:.2f}
            - 10周期SMA: {latest['sma_10']:.2f} {'↑' if latest['sma_10'] > prev['sma_10'] else '↓'}
            - 20周期SMA: {latest['sma_20']:.2f} {'↑' if latest['sma_20'] > prev['sma_20'] else '↓'}
            - RSI(14): {latest.get('rsi', 'N/A'):.2f}
            - 价格趋势: {'上涨' if latest['c'] > prev['c'] else '下跌'}
            """
            
            return indicators
        except Exception as e:
            logger.error(f"计算技术指标失败: {e}")
            return f"技术指标计算错误: {e}"
    
    def _calculate_rsi(self, df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """计算RSI指标"""
        delta = df['c'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df
    
    def _analyze_trades(self, trades: List) -> str:
        """分析成交数据"""
        if not trades:
            return "无成交数据"
        
        try:
            buy_volume = sum(float(trade.get('sz', 0)) for trade in trades[:50] if trade.get('side') == 'buy')
            sell_volume = sum(float(trade.get('sz', 0)) for trade in trades[:50] if trade.get('side') == 'sell')
            
            return f"买入量: {buy_volume:.2f} | 卖出量: {sell_volume:.2f}"
        except Exception as e:
            return f"成交分析错误: {e}"
    
    def _call_deepseek_api(self, prompt: str) -> Dict:
        """调用DeepSeek API"""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的加密货币交易分析师，专注于技术分析和市场趋势判断。请用JSON格式返回分析结果。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 2048
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            # 记录详细的错误信息
            if response.status_code != 200:
                logger.error(f"API请求失败 - 状态码: {response.status_code}")
                logger.error(f"响应内容: {response.text}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error("API请求超时")
            raise Exception("API请求超时，请检查网络连接")
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求异常: {e}")
            raise
    
    def _parse_analysis_response(self, response: Dict) -> Dict:
        """解析DeepSeek API响应"""
        try:
            content = response['choices'][0]['message']['content']
            
            # 尝试从响应中提取JSON
            if '{' in content and '}' in content:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
                
                # 验证必要字段
                required_fields = ['recommendation', 'confidence', 'analysis', 'reasoning']
                for field in required_fields:
                    if field not in result:
                        result[field] = "未知"
                
                return result
            else:
                return {
                    "analysis": content,
                    "recommendation": "HOLD",
                    "confidence": 50.0,
                    "reasoning": content,
                    "support_levels": [],
                    "resistance_levels": []
                }
        except Exception as e:
            logger.error(f"解析DeepSeek响应失败: {e}")
            return {
                "analysis": "解析失败",
                "recommendation": "HOLD",
                "confidence": 0.0,
                "reasoning": f"解析失败: {e}",
                "support_levels": [],
                "resistance_levels": []
            }
