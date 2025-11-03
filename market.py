import okx.MarketData as MarketData


class OKXMarketData:
    """OKX市场数据API封装类"""
    
    def __init__(self, flag="0"):
        """
        初始化市场数据API
        
        Args:
            flag: 环境标识，"0"表示实盘，"1"表示模拟盘
        """
        self.flag = flag
        self.api = MarketData.MarketAPI(flag=flag)
    
    def get_ticker(self, inst_id):
        """
        获取单个产品行情信息
        
        Args:
            inst_id: 产品ID，如 "BTC-USDT-SWAP"
            
        Returns:
            dict: 行情信息，包含以下字段：
                - instType: 产品类型
                - instId: 产品ID
                - last: 最新成交价
                - lastSz: 最新成交的数量，0代表没有成交量
                - askPx: 卖一价
                - askSz: 卖一价对应的数量
                - bidPx: 买一价
                - bidSz: 买一价对应的数量
                - open24h: 24小时开盘价
                - high24h: 24小时最高价
                - low24h: 24小时最低价
                - volCcy24h: 24小时成交量(币为单位)，衍生品为交易货币数量，币币为计价货币数量
                - vol24h: 24小时成交量(张为单位)，衍生品为合约张数，币币为交易货币数量
                - sodUtc0: UTC+0时开盘价
                - sodUtc8: UTC+8时开盘价
                - ts: ticker数据产生时间(毫秒时间戳)
        """
        result = self.api.get_ticker(instId=inst_id)
        return result
    
    def get_orderbook(self, inst_id, sz="20"):
        """
        获取产品深度
        
        Args:
            inst_id: 产品ID，如 "BTC-USDT-SWAP"
            sz: 深度档位数量，默认"20"
            
        Returns:
            dict: 订单簿深度数据，包含以下字段：
                - asks: 卖方深度(数组)
                - bids: 买方深度(数组)
                - ts: 深度产生的时间(毫秒时间戳)
                
            每个asks/bids数组项格式为 ["价格", "数量", "0", "订单数"]：
                - 索引0: 深度价格
                - 索引1: 数量(合约为张数，现货/杠杆为交易币数量)
                - 索引2: 已弃用字段(始终为0)
                - 索引3: 该价格的订单数量
                
            示例: ["411.8", "10", "0", "4"]
        """
        result = self.api.get_orderbook(instId=inst_id, sz=sz)
        return result
    
    def get_candlesticks(self, inst_id, bar="5m", limit="200"):
        """
        获取K线数据
        
        Args:
            inst_id: 产品ID，如 "BTC-USDT-SWAP"
            bar: K线周期，如 "1m", "5m", "15m", "1H", "1D"
            limit: 返回数据条数，默认"200"
            
        Returns:
            dict: K线数据，每条K线为数组格式 [ts, o, h, l, c, vol, volCcy, volCcyQuote, confirm]：
                - 索引0 (ts): 开始时间(毫秒时间戳)
                - 索引1 (o): 开盘价格
                - 索引2 (h): 最高价格
                - 索引3 (l): 最低价格
                - 索引4 (c): 收盘价格
                - 索引5 (vol): 交易量(张为单位)，衍生品为合约张数，币币为交易货币数量
                - 索引6 (volCcy): 交易量(币为单位)，衍生品为交易货币数量，币币为计价货币数量
                - 索引7 (volCcyQuote): 交易量(计价货币为单位)
                - 索引8 (confirm): K线状态，0=未完结，1=已完结
                
            注意：
                - 第一条K线数据可能不是完整周期K线
                - 当前周期无成交时，开高收低默认取上一周期收盘价
        """
        result = self.api.get_candlesticks(instId=inst_id, bar=bar, limit=limit)
        return result
    
    def get_trades(self, inst_id, limit="200"):
        """
        获取交易产品公共成交数据
        
        Args:
            inst_id: 产品ID，如 "BTC-USDT-SWAP"
            limit: 返回数据条数，默认"200"
            
        Returns:
            dict: 公共成交数据，包含以下字段：
                - instId: 产品ID
                - tradeId: 成交ID
                - px: 成交价格
                - sz: 成交数量(币币为交易货币单位，合约/期权为张)
                - side: 吃单方向(buy=买, sell=卖)
                - source: 订单来源(0=普通订单)
                - ts: 成交时间(毫秒时间戳)
        """
        result = self.api.get_trades(instId=inst_id, limit=limit)
        return result


# 使用示例
if __name__ == "__main__":
    # 创建市场数据实例
    market = OKXMarketData(flag="0")
    
    # 获取单个产品行情信息
    # result = market.get_ticker("BTC-USDT-SWAP")
    # print(result)
    
    # 获取产品深度
    # result = market.get_orderbook("BTC-USDT-SWAP", sz="20")
    # print(result)
    
    # 获取K线数据
    # result = market.get_candlesticks("BTC-USDT-SWAP", bar="5m", limit="200")
    # print(result)
    
    # 获取交易产品公共成交数据
    # result = market.get_trades("BTC-USDT-SWAP", limit="200")
    # print(result)