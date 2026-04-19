#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🇳🇬 尼日利亚客户跟进时机优化器

功能：基于客户行为数据和当地文化因素，智能优化最佳联系时间
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import pytz

class NigeriaTimingOptimizer:
    """尼日利亚客户跟进时机优化器"""
    
    def __init__(self):
        self.lagos_tz = pytz.timezone('Africa/Lagos')
        self.config = {
            'best_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday'],
            'best_hours': list(range(10, 17)),  # 10:00-16:00
            'avoid_fridays': True,
            'avoid_weekends': True,
            'holidays': [
                '2026-04-10', '2026-04-11',  # Easter
                '2026-05-01',  # Labour Day
                '2026-06-03', '2026-06-04',  # Eid al-Fitr
                '2026-12-25', '2026-12-26'   # Christmas
            ],
            'response_tracking_file': '/Users/zhuxiaolei/.openclaw/workspace/logs/nigeria-clients/send_tracking.json',
            'optimal_retry_window': 48  # 小时
        }
    
    def is_good_time_to_contact(self, target_datetime=None):
        """检查是否是合适的联系时间"""
        if target_datetime is None:
            target_datetime = datetime.now(self.lagos_tz)
        elif target_datetime.tzinfo is None:
            target_datetime = self.lagos_tz.localize(target_datetime)
        
        # 检查节假日
        date_str = target_datetime.strftime('%Y-%m-%d')
        if date_str in self.config['holidays']:
            return False, f"节假日: {date_str}"
        
        # 检查星期几
        day_name = target_datetime.strftime('%A')
        if day_name == 'Friday' and self.config['avoid_fridays']:
            return False, "周五（宗教日）"
        if day_name in ['Saturday', 'Sunday'] and self.config['avoid_weekends']:
            return False, "周末"
        if day_name not in self.config['best_days']:
            return False, f"非最佳联系日: {day_name}"
        
        # 检查时间段
        hour = target_datetime.hour
        if hour not in self.config['best_hours']:
            return False, f"非最佳时间段: {hour}:00"
        
        return True, "最佳联系时间"
    
    def get_optimal_contact_times(self, days_ahead=7):
        """获取未来N天的最佳联系时间窗口"""
        optimal_times = []
        now = datetime.now(self.lagos_tz)
        
        for day_offset in range(days_ahead):
            base_date = now + timedelta(days=day_offset)
            base_date = base_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            for hour in self.config['best_hours']:
                candidate_time = base_date + timedelta(hours=hour)
                is_good, reason = self.is_good_time_to_contact(candidate_time)
                
                if is_good:
                    optimal_times.append({
                        'datetime': candidate_time.isoformat(),
                        'timestamp': int(candidate_time.timestamp()),
                        'reason': reason
                    })
        
        return optimal_times[:20]  # 返回前20个最佳时间
    
    def analyze_response_patterns(self):
        """分析客户回复模式"""
        tracking_file = Path(self.config['response_tracking_file'])
        if not tracking_file.exists():
            return {"message": "暂无追踪数据"}
        
        with open(tracking_file, 'r', encoding='utf-8') as f:
            tracking_data = json.load(f)
        
        # 分析回复时间和模板效果
        template_stats = {}
        response_times = []
        
        for phone, data in tracking_data.items():
            template = data['template']
            if template not in template_stats:
                template_stats[template] = {'sent': 0, 'replied': 0}
            
            template_stats[template]['sent'] += 1
            
            if data['replies']:
                template_stats[template]['replied'] += 1
                # 计算回复时间（简化版）
                response_times.append(len(data['replies']))
        
        # 计算回复率
        for template, stats in template_stats.items():
            stats['reply_rate'] = round(stats['replied'] / stats['sent'] * 100, 1) if stats['sent'] > 0 else 0
        
        return {
            'template_performance': template_stats,
            'average_responses': round(sum(response_times) / len(response_times), 1) if response_times else 0,
            'total_tracked': len(tracking_data)
        }
    
    def get_smart_retry_schedule(self, initial_send_time):
        """基于最佳实践生成智能重试计划"""
        if isinstance(initial_send_time, str):
            initial_time = datetime.fromisoformat(initial_send_time.replace('Z', '+00:00'))
        else:
            initial_time = initial_send_time
        
        # 转换为拉各斯时间
        if initial_time.tzinfo is None:
            initial_time = pytz.UTC.localize(initial_time)
        lagos_time = initial_time.astimezone(self.lagos_tz)
        
        retry_schedule = []
        
        # 第一次重试：7天后
        retry1 = lagos_time + timedelta(days=7)
        is_good, _ = self.is_good_time_to_contact(retry1)
        if not is_good:
            # 找到下一个好时机
            retry1 = self.find_next_good_time(retry1)
        retry_schedule.append({
            'attempt': 1,
            'datetime': retry1.isoformat(),
            'reason': '首次重试（7天后）'
        })
        
        # 第二次重试：21天后
        retry2 = lagos_time + timedelta(days=21)
        is_good, _ = self.is_good_time_to_contact(retry2)
        if not is_good:
            retry2 = self.find_next_good_time(retry2)
        retry_schedule.append({
            'attempt': 2,
            'datetime': retry2.isoformat(),
            'reason': '二次重试（21天后）'
        })
        
        return retry_schedule
    
    def find_next_good_time(self, start_time):
        """从指定时间开始找到下一个合适的联系时间"""
        current = start_time
        max_attempts = 100  # 防止无限循环
        
        for _ in range(max_attempts):
            is_good, _ = self.is_good_time_to_contact(current)
            if is_good:
                return current
            current += timedelta(hours=1)
        
        # 如果找不到，返回原时间
        return start_time

def main():
    """主函数 - 展示优化器功能"""
    optimizer = NigeriaTimingOptimizer()
    
    # 检查是否为工作日（周一到周五）
    current_day = datetime.now().weekday()  # 0=Monday, 6=Sunday
    if current_day >= 5:  # 周六(5)或周日(6)
        print("📅 今天是周末，跳过时机优化测试")
        return
    
    print("=" * 60)
    print("🇳🇬 尼日利亚客户跟进时机优化器")
    print("=" * 60)
    
    # 检查当前时间是否合适
    now = datetime.now(optimizer.lagos_tz)
    is_good, reason = optimizer.is_good_time_to_contact(now)
    print(f"\n🕐 当前拉各斯时间: {now.strftime('%Y-%m-%d %H:%M')}")
    print(f"📊 当前是否适合联系: {'✅ 是' if is_good else '❌ 否'} ({reason})")
    
    # 获取未来最佳联系时间
    print("\n⏰ 未来最佳联系时间窗口:")
    optimal_times = optimizer.get_optimal_contact_times(3)
    for i, time_info in enumerate(optimal_times[:5], 1):
        dt = datetime.fromisoformat(time_info['datetime'])
        print(f"   {i}. {dt.strftime('%m-%d %H:%M')} ({time_info['reason']})")
    
    # 分析回复模式
    print("\n📈 客户回复模式分析:")
    response_analysis = optimizer.analyze_response_patterns()
    if 'template_performance' in response_analysis:
        for template, stats in response_analysis['template_performance'].items():
            print(f"   • {template}: {stats['reply_rate']}% 回复率 ({stats['replied']}/{stats['sent']})")
    else:
        print(f"   {response_analysis['message']}")
    
    # 智能重试计划示例
    print("\n🔄 智能重试计划示例 (基于今天发送):")
    retry_plan = optimizer.get_smart_retry_schedule(now)
    for retry in retry_plan:
        dt = datetime.fromisoformat(retry['datetime'])
        print(f"   • {retry['attempt']}: {dt.strftime('%m-%d %H:%M')} - {retry['reason']}")
    
    print("\n🎯 优化建议:")
    print("   1. 在最佳时间窗口内发送消息")
    print("   2. 根据模板效果选择高回复率话术")
    print("   3. 按照智能重试计划进行跟进")
    print("   4. 避开当地节假日和宗教日")

if __name__ == '__main__':
    main()