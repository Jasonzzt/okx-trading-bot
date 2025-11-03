import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DeepSeekConfig:
    api_key: str
    base_url: str = "https://api.siliconflow.cn/v1"  # 硅基流动API https://cloud.siliconflow.cn/
    model: str = "deepseek-ai/DeepSeek-R1"

@dataclass
class EmailConfig:
    smtp_server: str
    smtp_port: int
    sender_email: str
    sender_password: str
    receiver_email: str
    enable_ssl: bool = True

@dataclass
class TradingConfig:
    inst_id: str = "ETH-USDT-SWAP"
    analysis_interval: int = 30  # seconds
    confidence_threshold: float = 80.0  # 信心阈值，超过此值发送邮件提醒
    kline_bar: str = "5m"
    kline_limit: int = 100
    orderbook_size: int = 20
    trades_limit: int = 50

@dataclass
class DatabaseConfig:
    db_path: str = "trading_analysis.db"

class Config:
    def __init__(self):
        # DeepSeek配置
        self.deepseek = DeepSeekConfig(
            api_key=os.getenv("DEEPSEEK_API_KEY", "your_deepseek_api_key_here"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.siliconflow.cn/v1"),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-ai/DeepSeek-R1")
        )
        
        # 邮件配置
        self.email = EmailConfig(
            smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            sender_email=os.getenv("SENDER_EMAIL", "your_email@gmail.com"),
            sender_password=os.getenv("SENDER_PASSWORD", "your_app_password"),
            receiver_email=os.getenv("RECEIVER_EMAIL", "receiver@gmail.com"),
            enable_ssl=os.getenv("ENABLE_SSL", "True").lower() == "true"
        )
        
        # 交易配置
        self.trading = TradingConfig()
        
        # 数据库配置
        self.database = DatabaseConfig()

# 全局配置实例
config = Config()
