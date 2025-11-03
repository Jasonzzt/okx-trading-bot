import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)

class TradingAnalysisDB:
    """交易分析数据库"""
    
    def __init__(self, db_path: str = "trading_analysis.db"):
        self.db_path = db_path
        self._init_database()
        logger.info(f"数据库初始化完成: {db_path}")
    
    def _init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                inst_id TEXT NOT NULL,
                current_price REAL,
                recommendation TEXT,
                confidence REAL,
                analysis_summary TEXT,
                reasoning TEXT,
                support_levels TEXT,
                resistance_levels TEXT,
                market_data_json TEXT,
                raw_response TEXT,
                email_sent BOOLEAN DEFAULT FALSE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                inst_id TEXT NOT NULL,
                recommendation TEXT,
                confidence REAL,
                current_price REAL,
                message TEXT,
                sent_successfully BOOLEAN
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_analysis(self, analysis_data: Dict) -> int:
        """保存分析结果到数据库，返回记录ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_records (
                inst_id, current_price, recommendation, confidence,
                analysis_summary, reasoning, support_levels, resistance_levels,
                market_data_json, raw_response
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_data.get('inst_id'),
            analysis_data.get('current_price'),
            analysis_data.get('recommendation'),
            analysis_data.get('confidence'),
            analysis_data.get('analysis_summary'),
            analysis_data.get('reasoning'),
            json.dumps(analysis_data.get('support_levels', [])),
            json.dumps(analysis_data.get('resistance_levels', [])),
            analysis_data.get('market_data_json'),
            analysis_data.get('raw_response')
        ))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"分析结果已保存到数据库，记录ID: {record_id}")
        return record_id
    
    def save_email_alert(self, alert_data: Dict) -> int:
        """保存邮件提醒记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO email_alerts (
                inst_id, recommendation, confidence, current_price, message, sent_successfully
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            alert_data.get('inst_id'),
            alert_data.get('recommendation'),
            alert_data.get('confidence'),
            alert_data.get('current_price'),
            alert_data.get('message'),
            alert_data.get('sent_successfully', False)
        ))
        
        alert_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"邮件提醒记录已保存，ID: {alert_id}")
        return alert_id
    
    def mark_email_sent(self, record_id: int):
        """标记分析记录已发送邮件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE analysis_records 
            SET email_sent = TRUE 
            WHERE id = ?
        ''', (record_id,))
        
        conn.commit()
        conn.close()
        logger.debug(f"记录 {record_id} 已标记为邮件已发送")
