"""
简化版测试 - 直接使用应用实例进行测试
"""

import unittest
import json
from datetime import datetime
import warnings
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 忽略警告
warnings.filterwarnings('ignore')

# 导入应用
from app import create_app, db
from app.models import Employee, Customer, Course, Config, CommissionConfig


class SimpleProfitTest(unittest.TestCase):
    """简化的利润分配测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self._setup_test_data()
    
    def tearDown(self):
        """清理测试环境"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def _setup_test_data(self):
        """创建测试数据"""
        # 创建基本配置
        configs = [
            Config(key='new_course_shareholder_a', value='50'),
            Config(key='new_course_shareholder_b', value='50'),
            Config(key='renewal_shareholder_a', value='40'),
            Config(key='renewal_shareholder_b', value='60'),
            Config(key='trial_cost', value='30'),
            Config(key='course_cost', value='30'),
            Config(key='taobao_fee_rate', value='0.6')
        ]
        for config in configs:
            db.session.add(config)
        db.session.commit()
    
    def test_profit_report(self):
        """测试利润报告API"""
        with self.app.app_context():
            response = self.client.get('/api/profit-report?period=month')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertTrue('success' in data or 'new_courses' in data)
    
    def test_profit_config(self):
        """测试利润配置API"""
        with self.app.app_context():
            response = self.client.post('/api/profit-config', data={
                'new_course_shareholder_a': '60',
                'renewal_shareholder_a': '30'
            })
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertTrue(data.get('success', False))
    
    def test_employee_performance(self):
        """测试员工业绩API"""
        with self.app.app_context():
            # 创建测试员工
            employee = Employee(name='测试员工')
            db.session.add(employee)
            db.session.commit()
            
            response = self.client.get(f'/api/employees/{employee.id}/performance')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertEqual(data.get('employee_name'), '测试员工')


class SimpleEmployeeTest(unittest.TestCase):
    """简化的员工测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """清理测试环境"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_commission_config(self):
        """测试提成配置"""
        with self.app.app_context():
            # 创建员工
            employee = Employee(name='提成测试员工')
            db.session.add(employee)
            db.session.commit()
            
            # 更新提成配置
            response = self.client.post(
                f'/api/employees/{employee.id}/commission-config',
                json={
                    'commission_type': 'profit',
                    'trial_rate': 10,
                    'new_course_rate': 15,
                    'renewal_rate': 20,
                    'base_salary': 5000
                }
            )
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertTrue(data.get('success', False))


def run_quick_tests():
    """运行快速测试"""
    print("=== 运行快速测试 ===")
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTest(SimpleProfitTest('test_profit_report'))
    suite.addTest(SimpleProfitTest('test_profit_config'))
    suite.addTest(SimpleProfitTest('test_employee_performance'))
    suite.addTest(SimpleEmployeeTest('test_commission_config'))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回结果
    return result.wasSuccessful()


if __name__ == '__main__':
    # 运行快速测试
    success = run_quick_tests()
    
    if success:
        print("\n✅ 快速测试全部通过！")
        print("\n现在运行完整测试...")
        unittest.main(verbosity=2, argv=[''], exit=False)
    else:
        print("\n❌ 快速测试失败，请检查问题")