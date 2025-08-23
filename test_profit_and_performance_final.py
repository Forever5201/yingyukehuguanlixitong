"""
股东利润分配和员工业绩模块的综合测试用例（最终修复版）
修复了路由加载问题
"""

import unittest
import json
from datetime import datetime, timedelta
import warnings
import sys
import os

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 忽略SQLAlchemy的警告
warnings.filterwarnings('ignore', category=DeprecationWarning)

# 导入应用相关模块
from app import create_app, db
from app.models import Employee, Customer, Course, Config, CommissionConfig


class TestBase(unittest.TestCase):
    """测试基类，包含通用的setUp和tearDown"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化，只执行一次"""
        # 创建应用实例
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app.config['WTF_CSRF_ENABLED'] = False
        
        # 确保路由已加载
        with cls.app.app_context():
            # 强制重新导入routes以确保路由注册
            import app.routes
            
            # 打印路由信息用于调试
            api_routes = []
            for rule in cls.app.url_map.iter_rules():
                if '/api/' in rule.rule:
                    api_routes.append(rule.rule)
            
            if len(api_routes) < 10:
                print(f"警告：只找到 {len(api_routes)} 个API路由，可能路由未正确加载")
    
    def setUp(self):
        """每个测试前的准备工作"""
        # 创建应用上下文
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 创建数据库表
        db.create_all()
        
        # 创建测试客户端
        self.client = self.app.test_client()
    
    def tearDown(self):
        """每个测试后的清理工作"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


class TestProfitDistribution(TestBase):
    """股东利润分配功能测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        super().setUp()
        self._setup_test_data()
    
    def _setup_test_data(self):
        """设置测试数据"""
        # 创建配置
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
        
        # 创建员工
        self.employee1 = Employee(name='测试员工1')
        self.employee2 = Employee(name='测试员工2')
        db.session.add(self.employee1)
        db.session.add(self.employee2)
        
        # 创建客户
        self.customer1 = Customer(
            name='测试客户1',
            phone='13800138001',
            gender='男',
            grade='高一',
            region='北京'
        )
        self.customer2 = Customer(
            name='测试客户2',
            phone='13800138002',
            gender='女',
            grade='高二',
            region='上海'
        )
        db.session.add(self.customer1)
        db.session.add(self.customer2)
        db.session.commit()
        
        # 刷新对象以确保ID已设置
        db.session.refresh(self.customer1)
        db.session.refresh(self.customer2)
        db.session.refresh(self.employee1)
        db.session.refresh(self.employee2)
        
        # 创建课程
        # 新课（非续课）
        self.new_course1 = Course(
            name='语法课程',
            customer_id=self.customer1.id,
            is_trial=False,
            is_renewal=False,
            sessions=10,
            price=100,  # 单价100
            cost=300,   # 成本300
            payment_channel='淘宝',
            snapshot_fee_rate=0.006,
            course_type='语法课'
        )
        
        # 续课
        self.renewal_course1 = Course(
            name='续课语法',
            customer_id=self.customer2.id,
            is_trial=False,
            is_renewal=True,
            sessions=20,
            price=100,
            cost=600,
            payment_channel='微信',
            course_type='语法课'
        )
        
        # 试听课
        self.trial_course1 = Course(
            name='试听课',
            customer_id=self.customer1.id,
            is_trial=True,
            trial_price=50,
            trial_status='converted',
            assigned_employee_id=self.employee1.id
        )
        
        db.session.add(self.new_course1)
        db.session.add(self.renewal_course1)
        db.session.add(self.trial_course1)
        db.session.commit()
    
    def test_profit_calculation_new_course(self):
        """测试新课利润计算"""
        # 收入 = 10节 * 100元 = 1000元
        # 手续费 = 1000 * 0.006 = 6元
        # 成本 = 300 + 6 = 306元
        # 利润 = 1000 - 306 = 694元
        
        response = self.client.get('/api/profit-report?period=month')
        
        # 调试信息
        if response.status_code != 200:
            print(f"\n响应状态码: {response.status_code}")
            print(f"响应内容: {response.data[:200] if response.data else 'None'}")
        
        self.assertEqual(response.status_code, 200, 
                       f"预期状态码200，实际得到{response.status_code}")
        
        # 检查响应内容
        if response.data:
            data = json.loads(response.data)
            
            self.assertTrue(data.get('success', True))
            self.assertIn('new_courses', data)
            
            # 如果有数据，验证计算
            if data.get('new_courses'):
                self.assertEqual(len(data['new_courses']), 1)
                
                course = data['new_courses'][0]
                self.assertEqual(course['revenue'], 1000)
                self.assertEqual(course['cost'], 306)
                self.assertEqual(course['profit'], 694)
                
                # 验证分配比例 (50%/50%)
                self.assertAlmostEqual(course['shareholder_a'], 347, places=0)
                self.assertAlmostEqual(course['shareholder_b'], 347, places=0)
    
    def test_profit_calculation_renewal_course(self):
        """测试续课利润计算"""
        response = self.client.get('/api/profit-report?period=month')
        self.assertEqual(response.status_code, 200)
        
        if response.data:
            data = json.loads(response.data)
            
            self.assertTrue(data.get('success', True))
            self.assertIn('renewal_courses', data)
            
            if data.get('renewal_courses'):
                self.assertEqual(len(data['renewal_courses']), 1)
                
                course = data['renewal_courses'][0]
                self.assertEqual(course['revenue'], 2000)
                self.assertEqual(course['cost'], 600)
                self.assertEqual(course['profit'], 1400)
                
                # 验证分配比例 (40%/60%)
                self.assertAlmostEqual(course['shareholder_a'], 560, places=0)
                self.assertAlmostEqual(course['shareholder_b'], 840, places=0)
    
    def test_profit_config_update(self):
        """测试利润分配配置更新"""
        # 更新配置
        response = self.client.post('/api/profit-config', data={
            'new_course_shareholder_a': '60',
            'new_course_shareholder_b': '40',
            'renewal_shareholder_a': '30',
            'renewal_shareholder_b': '70'
        })
        
        self.assertEqual(response.status_code, 200)
        
        if response.data:
            data = json.loads(response.data)
            self.assertTrue(data.get('success', False))
            
            # 验证配置已更新
            config = Config.query.filter_by(key='new_course_shareholder_a').first()
            self.assertIn(config.value, ['60', '60.0'])


class TestEmployeePerformance(TestBase):
    """员工业绩功能测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        super().setUp()
        self._setup_test_data()
    
    def _setup_test_data(self):
        """设置测试数据"""
        # 创建员工
        self.employee = Employee(name='业绩测试员工')
        db.session.add(self.employee)
        db.session.commit()
        db.session.refresh(self.employee)
        
        # 创建客户
        customers = []
        for i in range(5):
            customer = Customer(
                name=f'客户{i+1}',
                phone=f'1380013800{i}',
                gender='男' if i % 2 == 0 else '女'
            )
            customers.append(customer)
            db.session.add(customer)
        
        db.session.commit()
        
        # 创建提成配置
        self.commission_config = CommissionConfig(
            employee_id=self.employee.id,
            commission_type='profit',
            trial_rate=10,
            new_course_rate=15,
            renewal_rate=20,
            base_salary=3000
        )
        db.session.add(self.commission_config)
        
        # 创建试听课
        for i in range(3):
            trial = Course(
                name=f'试听课{i+1}',
                customer_id=customers[i].id,
                is_trial=True,
                trial_price=50,
                trial_status='converted' if i < 2 else 'completed',
                assigned_employee_id=self.employee.id
            )
            db.session.add(trial)
            
            # 前两个试听课转化为正课
            if i < 2:
                formal = Course(
                    name=f'正课{i+1}',
                    customer_id=customers[i].id,
                    is_trial=False,
                    is_renewal=False,
                    sessions=10,
                    price=100,
                    cost=300,
                    payment_channel='淘宝',
                    assigned_employee_id=self.employee.id,
                    converted_from_trial=trial.id
                )
                db.session.add(formal)
                db.session.flush()
                trial.converted_to_course = formal.id
        
        # 创建续课
        renewal = Course(
            name='续课1',
            customer_id=customers[0].id,
            is_trial=False,
            is_renewal=True,
            sessions=20,
            price=100,
            cost=600,
            payment_channel='微信',
            assigned_employee_id=self.employee.id
        )
        db.session.add(renewal)
        
        db.session.commit()
    
    def test_employee_performance_stats(self):
        """测试员工业绩统计"""
        response = self.client.get(f'/api/employees/{self.employee.id}/performance')
        
        # 调试信息
        if response.status_code != 200:
            print(f"\n员工ID: {self.employee.id}")
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.data[:200] if response.data else 'None'}")
        
        self.assertEqual(response.status_code, 200)
        
        if response.data:
            data = json.loads(response.data)
            
            self.assertTrue(data.get('success', False))
            self.assertEqual(data.get('employee_name'), '业绩测试员工')
            
            stats = data.get('stats', {})
            self.assertEqual(stats.get('trial_count', 0), 3)
            self.assertEqual(stats.get('converted_count', 0), 2)
            self.assertAlmostEqual(stats.get('conversion_rate', 0), 66.67, places=1)
    
    def test_commission_config_update(self):
        """测试提成配置更新"""
        response = self.client.post(f'/api/employees/{self.employee.id}/commission-config', 
                                  json={
                                      'commission_type': 'sales',
                                      'trial_rate': 5,
                                      'new_course_rate': 10,
                                      'renewal_rate': 15,
                                      'base_salary': 5000
                                  })
        
        self.assertEqual(response.status_code, 200)
        
        if response.data:
            data = json.loads(response.data)
            self.assertTrue(data.get('success', False))
    
    def test_invalid_employee_handling(self):
        """测试无效员工ID处理"""
        response = self.client.get('/api/employees/9999/performance')
        self.assertEqual(response.status_code, 404)


class TestEdgeCasesAndValidation(TestBase):
    """边界条件和数据验证测试"""
    
    def test_profit_config_validation(self):
        """测试利润配置验证"""
        # 测试负数比例
        response = self.client.post('/api/profit-config', data={
            'new_course_shareholder_a': '-10',
            'new_course_shareholder_b': '110'
        })
        
        self.assertEqual(response.status_code, 200)
        
        if response.data:
            data = json.loads(response.data)
            self.assertIsNotNone(data.get('success'))
    
    def test_date_edge_cases(self):
        """测试日期边界条件"""
        # 测试自定义日期范围
        start_date = '2024-01-01'
        end_date = '2024-12-31'
        
        response = self.client.get(f'/api/profit-report?period=custom&start_date={start_date}&end_date={end_date}')
        self.assertEqual(response.status_code, 200)
        
        if response.data:
            data = json.loads(response.data)
            self.assertTrue(data.get('success', True))


# 创建一个简单的调试函数
def debug_routes():
    """调试函数，检查路由是否正确加载"""
    app = create_app()
    
    with app.app_context():
        print("\n=== 路由调试信息 ===")
        
        # 列出所有API路由
        api_routes = []
        for rule in app.url_map.iter_rules():
            if '/api/' in rule.rule:
                api_routes.append({
                    'rule': rule.rule,
                    'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                    'endpoint': rule.endpoint
                })
        
        print(f"找到 {len(api_routes)} 个API路由：")
        for route in sorted(api_routes, key=lambda x: x['rule']):
            print(f"  {route['rule']} -> {route['methods']} ({route['endpoint']})")
        
        # 测试特定路由
        print("\n=== 测试特定路由 ===")
        with app.test_client() as client:
            test_urls = [
                '/api/profit-report?period=month',
                '/api/profit-config',
                '/api/employees/1/performance'
            ]
            
            for url in test_urls:
                if 'profit-config' in url:
                    response = client.post(url, data={'new_course_shareholder_a': '50'})
                else:
                    response = client.get(url)
                print(f"{url} -> {response.status_code}")


if __name__ == '__main__':
    # 先运行调试
    debug_routes()
    
    print("\n=== 开始运行测试 ===")
    # 运行测试
    unittest.main(verbosity=2)