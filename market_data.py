import logging
import okx.MarketData as MarketData
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class OKXMarketData:
    """OKX市场数据API封装类"""
    
    def __init__(self, flag: str = "0"):
        """
        初始化市场数据API
        
        Args:
            flag: 环境标识，"0"表示实盘，"1"表示模拟盘
        """
        self.flag = flag
        self.api = MarketData.MarketAPI(flag=flag)
        logger.info(f"OKX市场数据API初始化完成 (环境: {'实盘' if flag == '0' else '模拟盘'})")
    
    def get_ticker(self, inst_id: str) -> Dict:
        """获取单个产品行情信息"""
        try:
            result = self.api.get_ticker(instId=inst_id)
            if result['code'] != '0':
                logger.error(f"获取行情数据失败: {result}")
                raise Exception(f"API错误: {result['msg']}")
            return result
        except Exception as e:
            logger.error(f"获取行情数据异常: {e}")
            raise
    
    def get_orderbook(self, inst_id: str, sz: str = "20") -> Dict:
        """获取产品深度"""
        try:
            result = self.api.get_orderbook(instId=inst_id, sz=sz)
            if result['code'] != '0':
                logger.error(f"获取深度数据失败: {result}")
                raise Exception(f"API错误: {result['msg']}")
            return result
        except Exception as e:
            logger.error(f"获取深度数据异常: {e}")
            raise
    
    def get_candlesticks(self, inst_id: str, bar: str = "5m", limit: str = "200") -> Dict:
        """获取K线数据"""
        try:
            result = self.api.get_candlesticks(instId=inst_id, bar=bar, limit=limit)
            if result['code'] != '0':
                logger.error(f"获取K线数据失败: {result}")
                raise Exception(f"API错误: {result['msg']}")
            return result
        except Exception as e:
            logger.error(f"获取K线数据异常: {e}")
            raise
    
    def get_trades(self, inst_id: str, limit: str = "200") -> Dict:
        """获取交易产品公共成交数据"""
        try:
            result = self.api.get_trades(instId=inst_id, limit=limit)
            if result['code'] != '0':
                logger.error(f"获取成交数据失败: {result}")
                raise Exception(f"API错误: {result['msg']}")
            return result
        except Exception as e:
            logger.error(f"获取成交数据异常: {e}")
            raise
    
    def get_all_market_data(self, inst_id: str, config) -> Dict:
        """获取所有市场数据"""
        logger.info(f"开始获取 {inst_id} 的市场数据...")
        
        return {
            'ticker': self.get_ticker(inst_id),
            'orderbook': self.get_orderbook(inst_id, sz=str(config.trading.orderbook_size)),
            'candlesticks': self.get_candlesticks(
                inst_id, 
                bar=config.trading.kline_bar, 
                limit=str(config.trading.kline_limit)
            ),
            'trades': self.get_trades(inst_id, limit=str(config.trading.trades_limit))
        }
