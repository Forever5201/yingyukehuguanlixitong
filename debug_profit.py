#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models import Course, Customer, Config

def analyze_trial_profit():
    app = create_app()
    with app.app_context():
        print('=== 试听课数据分析 ===')
        
        # 获取淘宝手续费率配置
        taobao_fee_config = Config.query.filter_by(key='taobao_fee_rate').first()
        taobao_fee_rate = float(taobao_fee_config.value) / 100 if taobao_fee_config else 0.006
        print(f'淘宝手续费率: {taobao_fee_rate * 100}%')
        
        # 获取所有试听课
        trial_courses = Course.query.filter(Course.is_trial == True).all()
        print(f'试听课总数: {len(trial_courses)}')
        
        total_profit = 0
        
        for i, course in enumerate(trial_courses, 1):
            print(f'\n--- 试听课 {i} ---')
            print(f'ID: {course.id}')
            customer_name = course.customer.name if course.customer else "未知"
            print(f'客户: {customer_name}')
            print(f'状态: {course.trial_status or "registered"}')
            print(f'试听价格: ¥{course.trial_price or 0}')
        print(f'原始成本: ¥{course.cost or 0}')
        print(f'来源: {course.source or "未知"}')
        print(f'退费金额: ¥{course.refund_amount or 0}')
        print(f'退费手续费: ¥{course.refund_fee or 0}')
        
        # 检查成本是否异常
        original_cost = course.cost or 0
        if original_cost > 50:  # 如果成本超过50元，可能有问题
            print(f'⚠️  成本异常高: ¥{original_cost}')
            
            # 计算利润
            status = course.trial_status or 'registered'
            
            if status == 'registered':
                revenue = course.trial_price or 0
                cost = course.cost or 0
                fees = revenue * taobao_fee_rate if course.source == '淘宝' else 0
                profit = revenue - cost - fees
                
            elif status == 'not_registered':
                revenue = 0
                cost = course.cost or 0
                fees = 0
                profit = -cost
                
            elif status == 'refunded':
                revenue = 0
                cost = (course.cost or 0) + (course.refund_amount or 0) + (course.refund_fee or 0)
                fees = 0
                profit = -cost
                
            elif status == 'converted':
                revenue = course.trial_price or 0
                cost = course.cost or 0
                fees = revenue * taobao_fee_rate if course.source == '淘宝' else 0
                profit = revenue - cost - fees
                
            elif status == 'no_action':
                revenue = course.trial_price or 0
                cost = course.cost or 0
                fees = revenue * taobao_fee_rate if course.source == '淘宝' else 0
                profit = revenue - cost - fees
            
            print(f'收入: ¥{revenue}')
            print(f'手续费: ¥{fees}')
            print(f'利润: ¥{profit}')
            
            total_profit += profit
        
        print(f'\n=== 总计 ===')
        print(f'总利润: ¥{total_profit:.2f}')

if __name__ == '__main__':
    analyze_trial_profit()