#!/usr/bin/env python3
"""
测试修复效果的脚本
验证淘宝手续费计算和取消结算功能
"""

from app import create_app, db
from app.models import TaobaoOrder, Config
from datetime import datetime

def test_taobao_fee_calculation():
    """测试淘宝手续费计算"""
    app = create_app()
    with app.app_context():
        # 获取当前手续费率
        config = Config.query.filter_by(key='taobao_fee_rate').first()
        if config:
            fee_rate = float(config.value)
            print(f"当前淘宝手续费率: {fee_rate}%")
            
            # 测试计算
            test_amounts = [100, 500, 1000]
            for amount in test_amounts:
                calculated_fee = amount * (fee_rate / 100)
                print(f"刷单金额: ¥{amount}, 计算的手续费: ¥{calculated_fee:.2f}")
        else:
            print("未找到淘宝手续费率配置")

def test_settlement_status():
    """测试结算状态功能"""
    app = create_app()
    with app.app_context():
        # 查看现有订单的结算状态
        orders = TaobaoOrder.query.all()
        print(f"\n当前订单数量: {len(orders)}")
        
        for order in orders[:5]:  # 只显示前5个订单
            status = "已结算" if order.settled else "未结算"
            settled_time = order.settled_at.strftime('%Y-%m-%d %H:%M:%S') if order.settled_at else "无"
            print(f"订单ID: {order.id}, 客户: {order.name}, 金额: ¥{order.amount}, "
                  f"手续费: ¥{order.taobao_fee}, 状态: {status}, 结算时间: {settled_time}")

def test_config_api():
    """测试配置API"""
    app = create_app()
    with app.test_client() as client:
        # 测试获取淘宝手续费率
        response = client.get('/api/config/taobao_fee_rate')
        if response.status_code == 200:
            data = response.get_json()
            print(f"\nAPI返回的手续费率: {data}")
        else:
            print(f"API请求失败: {response.status_code}")

if __name__ == '__main__':
    print("=== 测试修复效果 ===")
    
    print("\n1. 测试淘宝手续费计算:")
    test_taobao_fee_calculation()
    
    print("\n2. 测试结算状态:")
    test_settlement_status()
    
    print("\n3. 测试配置API:")
    test_config_api()
    
    print("\n=== 测试完成 ===")