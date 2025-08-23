#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
退费功能测试脚本
"""

import os
import sys
from datetime import datetime
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Course, Customer, Employee, CourseRefund
from app.routes import calculate_course_profit_with_refund

class TestRefundFunctionality(unittest.TestCase):
    """退费功能测试类"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.client = cls.app.test_client()
        
        with cls.app.app_context():
            db.create_all()
    
    def setUp(self):
        """每个测试前的准备"""
        with self.app.app_context():
            # 清空数据
            CourseRefund.query.delete()
            Course.query.delete()
            Customer.query.delete()
            Employee.query.delete()
            db.session.commit()
            
            # 创建测试数据
            self.employee = Employee(name='测试员工')
            db.session.add(self.employee)
            
            self.customer = Customer(
                name='测试客户',
                phone='13800138000',
                gender='男',
                grade='高中一年级',
                region='北京'
            )
            db.session.add(self.customer)
            db.session.commit()
            
            # 创建正课
            self.course = Course(
                name='测试正课',  # 添加name字段
                customer_id=self.customer.id,
                is_trial=False,
                course_type='一对一',
                sessions=20,
                price=200,
                gift_sessions=2,
                cost=2000,
                other_cost=500,
                payment_channel='淘宝',
                snapshot_fee_rate=0.006
            )
            db.session.add(self.course)
            db.session.commit()
    
    def test_calculate_profit_without_refund(self):
        """测试无退费时的利润计算"""
        with self.app.app_context():
            profit_info = calculate_course_profit_with_refund(self.course)
            
            # 收入 = 20 * 200 = 4000
            # 手续费 = 4000 * 0.006 = 24
            # 成本 = 2000 + 24 = 2024
            # 利润 = 4000 - 2024 = 1976
            
            self.assertEqual(profit_info['revenue'], 4000)
            self.assertEqual(profit_info['cost'], 2024)
            self.assertEqual(profit_info['profit'], 1976)
            self.assertFalse(profit_info['has_refund'])
    
    def test_calculate_profit_with_partial_refund(self):
        """测试部分退费后的利润计算"""
        with self.app.app_context():
            # 创建退费记录
            refund = CourseRefund(
                course_id=self.course.id,
                refund_sessions=5,
                refund_amount=1000,  # 5 * 200
                refund_reason='个人原因',
                refund_channel='原路退回',
                status='completed'
            )
            db.session.add(refund)
            db.session.commit()
            
            profit_info = calculate_course_profit_with_refund(self.course)
            
            # 原始收入 = 4000
            # 退费金额 = 1000
            # 实际收入 = 3000
            # 手续费 = 24（不退）
            # 变动成本 = 1500，固定成本 = 500
            # 调整后成本 = 1500 * 15/20 + 500 = 1625
            # 总成本 = 1625 + 24 = 1649
            # 利润 = 3000 - 1649 = 1351
            
            self.assertEqual(profit_info['revenue'], 3000)
            self.assertEqual(profit_info['cost'], 1649)
            self.assertEqual(profit_info['profit'], 1351)
            self.assertTrue(profit_info['has_refund'])
            self.assertEqual(profit_info['refund_info']['sessions'], 5)
            self.assertEqual(profit_info['refund_info']['amount'], 1000)
    
    def test_calculate_profit_with_full_refund(self):
        """测试全额退费后的利润计算"""
        with self.app.app_context():
            # 创建全额退费记录
            refund = CourseRefund(
                course_id=self.course.id,
                refund_sessions=20,
                refund_amount=4000,
                refund_reason='教学质量',
                refund_channel='原路退回',
                status='completed'
            )
            db.session.add(refund)
            db.session.commit()
            
            profit_info = calculate_course_profit_with_refund(self.course)
            
            # 实际收入 = 0
            # 成本保留 = 2000
            # 手续费 = 24（不退）
            # 利润 = 0 - 2000 - 24 = -2024
            
            self.assertEqual(profit_info['revenue'], 0)
            self.assertEqual(profit_info['cost'], 2024)
            self.assertEqual(profit_info['profit'], -2024)
            self.assertTrue(profit_info['has_refund'])
    
    def test_refund_api_endpoints(self):
        """测试退费API接口"""
        with self.app.app_context():
            # 测试获取退费信息
            response = self.client.get(f'/api/courses/{self.course.id}/refund-info')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['refundable_sessions'], 20)
            
            # 测试申请退费
            refund_data = {
                'refund_sessions': 5,
                'refund_reason': '个人原因',
                'refund_channel': '微信',
                'refund_fee': 10,
                'remark': '测试退费'
            }
            response = self.client.post(
                f'/api/courses/{self.course.id}/refund',
                json=refund_data
            )
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['refund_amount'], 1000)
            self.assertEqual(data['data']['actual_refund'], 990)
            
            # 测试退费历史
            response = self.client.get(f'/api/courses/{self.course.id}/refund-history')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['success'])
            self.assertEqual(len(data['refunds']), 1)

def run_tests():
    """运行测试"""
    print("=== 退费功能测试 ===")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRefundFunctionality)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("-" * 50)
    if result.wasSuccessful():
        print("✅ 所有测试通过！")
    else:
        print("❌ 测试失败！")
        print(f"失败数：{len(result.failures)}")
        print(f"错误数：{len(result.errors)}")

if __name__ == "__main__":
    run_tests()