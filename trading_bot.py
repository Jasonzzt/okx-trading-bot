import logging
import time
import json
from datetime import datetime
from typing import Dict, Optional

from config import config
from market_data import OKXMarketData
from deepseek_analyzer import DeepSeekAnalyzer
from db import TradingAnalysisDB
from email_notifier import EmailNotifier

logger = logging.getLogger(__name__)

class TradingAnalysisBot:
    """交易分析机器人"""
    
    def __init__(self):
        self.inst_id = config.trading.inst_id
        self.confidence_threshold = config.trading.confidence_threshold
        
        # 初始化各个模块
        self.market_data = OKXMarketData(flag="0")
        self.analyzer = DeepSeekAnalyzer(config)
        self.database = TradingAnalysisDB(config.database.db_path)
        self.email_notifier = EmailNotifier(config)
        
        # 统计信息
        self.analysis_count = 0
        self.email_alerts_sent = 0
        self.last_analysis_time = None
        
        logger.info(f"交易分析机器人初始化完成，监控交易对: {self.inst_id}")
    
    def run_analysis_cycle(self) -> Optional[Dict]:
        """运行一次完整的分析周期"""
        logger.info(f"开始分析周期 #{self.analysis_count + 1} - {self.inst_id}")
        
        try:
            # 1. 获取市场数据
            market_data = self.market_data.get_all_market_data(self.inst_id, config)
            
            # 2. 调用DeepSeek进行分析
            analysis_result = self.analyzer.analyze_market_data(market_data, self.inst_id)
            
            # 3. 准备存储数据
            current_price = float(market_data['ticker']['data'][0]['last'])
            analysis_data = {
                'inst_id': self.inst_id,
                'current_price': current_price,
                'recommendation': analysis_result.get('recommendation', 'HOLD'),
                'confidence': float(analysis_result.get('confidence', 0)),
                'analysis_summary': analysis_result.get('analysis', ''),
                'reasoning': analysis_result.get('reasoning', ''),
                'support_levels': analysis_result.get('support_levels', []),
                'resistance_levels': analysis_result.get('resistance_levels', []),
                'market_data_json': json.dumps(market_data),
                'raw_response': json.dumps(analysis_result)
            }
            
            # 4. 保存到数据库
            record_id = self.database.save_analysis(analysis_data)
            analysis_data['record_id'] = record_id
            
            # 5. 检查是否需要发送邮件提醒
            should_send_email = self._should_send_email_alert(analysis_data)
            if should_send_email:
                self._send_email_alert(analysis_data)
            
            # 6. 输出结果
            self._print_analysis_result(analysis_data)
            
            # 更新统计
            self.analysis_count += 1
            self.last_analysis_time = datetime.now()
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"分析周期执行失败: {e}")
            return None
    
    def _should_send_email_alert(self, analysis_data: Dict) -> bool:
        """判断是否需要发送邮件提醒"""
        confidence = analysis_data.get('confidence', 0)
        recommendation = analysis_data.get('recommendation', 'HOLD')
        
        # 只有信心度超过阈值且不是HOLD建议时才发送邮件
        if (confidence >= self.confidence_threshold and 
            recommendation in ['BUY', 'SELL']):
            return True
        
        return False
    
    def _send_email_alert(self, analysis_data: Dict):
        """发送邮件提醒"""
        try:
            success = self.email_notifier.send_trading_alert(analysis_data)
            
            # 保存邮件提醒记录
            alert_data = {
                'inst_id': analysis_data['inst_id'],
                'recommendation': analysis_data['recommendation'],
                'confidence': analysis_data['confidence'],
                'current_price': analysis_data['current_price'],
                'message': f"{analysis_data['recommendation']} - {analysis_data['analysis_summary']}",
                'sent_successfully': success
            }
            
            self.database.save_email_alert(alert_data)
            
            if success:
                self.database.mark_email_sent(analysis_data['record_id'])
                self.email_alerts_sent += 1
                logger.info(f"高信心度交易提醒邮件已发送! 建议: {analysis_data['recommendation']}, 信心度: {analysis_data['confidence']}%")
            else:
                logger.error("邮件发送失败，但分析记录已保存")
                
        except Exception as e:
            logger.error(f"发送邮件提醒失败: {e}")
    
    def _print_analysis_result(self, analysis_data: Dict):
        """打印分析结果"""
        recommendation = analysis_data['recommendation']
        confidence = analysis_data['confidence']
        price = analysis_data['current_price']
        
        if recommendation == "BUY":
            color_start = "\033[92m"  # 绿色
        elif recommendation == "SELL":
            color_start = "\033[91m"  # 红色
        else:
            color_start = "\033[93m"  # 黄色
        
        color_end = "\033[0m"
        
        print("\n" + "="*70)
        print(f"📊 {self.inst_id} 分析结果")
        print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💰 当前价格: {price:.2f} USDT")
        print(f"{color_start}🎯 建议: {recommendation} (信心度: {confidence:.1f}%){color_end}")
        
        if confidence >= self.confidence_threshold:
            print(f"🚨 高信心度提醒! 建议立即关注")
        
        summary = analysis_data['analysis_summary']
        if len(summary) > 100:
            summary = summary[:100] + "..."
        print(f"📋 分析总结: {summary}")
        print("="*70 + "\n")
    
    def start_continuous_analysis(self):
        """开始连续分析"""
        interval = config.trading.analysis_interval
        
        logger.info(f"开始连续分析，间隔: {interval}秒，信心阈值: {self.confidence_threshold}%")
        print(f"\n🚀 开始监控 {self.inst_id}")
        print(f"📊 分析间隔: {interval}秒")
        print(f"🎯 信心阈值: {self.confidence_threshold}%")
        print(f"📧 邮件提醒: 已启用")
        print("="*50)
        
        try:
            while True:
                start_time = time.time()
                
                # 执行分析周期
                self.run_analysis_cycle()
                
                # 打印统计信息
                if self.analysis_count % 10 == 0:
                    self._print_statistics()
                
                # 计算等待时间
                elapsed = time.time() - start_time
                wait_time = max(1, interval - elapsed)
                
                logger.info(f"等待 {wait_time:.1f} 秒后进行下一次分析...")
                time.sleep(wait_time)
                
        except KeyboardInterrupt:
            logger.info("用户中断分析过程")
            self._print_final_statistics()
        except Exception as e:
            logger.error(f"连续分析过程出错: {e}")
            self._print_final_statistics()
            raise
    
    def _print_statistics(self):
        """打印统计信息"""
        print(f"\n📈 统计信息 (分析次数: {self.analysis_count}, 邮件提醒: {self.email_alerts_sent})")
    
    def _print_final_statistics(self):
        """打印最终统计信息"""
        print("\n" + "="*50)
        print("🏁 分析任务结束")
        print(f"📊 总分析次数: {self.analysis_count}")
        print(f"📧 邮件提醒发送: {self.email_alerts_sent}")
        print("="*50)
