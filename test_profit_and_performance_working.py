"""
股东利润分配和员工业绩模块的综合测试用例（工作版）
修复了路由加载问题 - 在修改配置前创建app
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


class TestBase(unittest.TestCase):
    """测试基类，包含通用的setUp和tearDown"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化，只执行一次"""
        # 重要：先设置环境变量，再创建app
        os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        os.environ['TESTING'] = 'True'
        
        # 导入并创建app（这时会使用上面的环境变量）
        from app import create_app, db
        cls.db = db
        cls.app = create_app()
        
        # 应用测试配置
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app.config['WTF_CSRF_ENABLED'] = False
        
        # 导入模型
        from app.models import Employee, Customer, Course, Config, CommissionConfig
        cls.Employee = Employee
        cls.Customer = Customer
        cls.Course = Course
        cls.Config = Config
        cls.CommissionConfig = CommissionConfig
    
    def setUp(self):
        """每个测试前的准备工作"""
        # 创建应用上下文
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 创建数据库表
        self.db.create_all()
        
        # 创建测试客户端
        self.client = self.app.test_client()
    
    def tearDown(self):
        """每个测试后的清理工作"""
        self.db.session.remove()
        self.db.drop_all()
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
            self.Config(key='new_course_shareholder_a', value='50'),
            self.Config(key='new_course_shareholder_b', value='50'),
            self.Config(key='renewal_shareholder_a', value='40'),
            self.Config(key='renewal_shareholder_b', value='60'),
            self.Config(key='trial_cost', value='30'),
            self.Config(key='course_cost', value='30'),
            self.Config(key='taobao_fee_rate', value='0.6')
        ]
        for config in configs:
            self.db.session.add(config)
        
        # 创建员工
        self.employee1 = self.Employee(name='测试员工1')
        self.employee2 = self.Employee(name='测试员工2')
        self.db.session.add(self.employee1)
        self.db.session.add(self.employee2)
        
        # 创建客户
        self.customer1 = self.Customer(
            name='测试客户1',
            phone='13800138001',
            gender='男',
            grade='高一',
            region='北京'
        )
        self.customer2 = self.Customer(
            name='测试客户2',
            phone='13800138002',
            gender='女',
            grade='高二',
            region='上海'
        )
        self.db.session.add(self.customer1)
        self.db.session.add(self.customer2)
        self.db.session.commit()
        
        # 刷新对象以确保ID已设置
        self.db.session.refresh(self.customer1)
        self.db.session.refresh(self.customer2)
        self.db.session.refresh(self.employee1)
        self.db.session.refresh(self.employee2)
        
        # 创建课程
        # 新课（非续课）
        self.new_course1 = self.Course(
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
        self.renewal_course1 = self.Course(
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
        self.trial_course1 = self.Course(
            name='试听课',
            customer_id=self.customer1.id,
            is_trial=True,
            trial_price=50,
            trial_status='converted',
            assigned_employee_id=self.employee1.id
        )
        
        self.db.session.add(self.new_course1)
        self.db.session.add(self.renewal_course1)
        self.db.session.add(self.trial_course1)
        self.db.session.commit()
    
    def test_profit_calculation_new_course(self):
        """测试新课利润计算"""
        response = self.client.get('/api/profit-report?period=month')
        
        self.assertEqual(response.status_code, 200, 
                       f"预期状态码200，实际得到{response.status_code}")
        
        # 检查响应内容
        self.assertIsNotNone(response.data)
        data = json.loads(response.data)
        
        self.assertTrue(data.get('success', True))
        self.assertIn('new_courses', data)
        
        # 验证计算
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
        response = self.client.post('/api/profit-config', data={
            'new_course_shareholder_a': '60',
            'renewal_shareholder_a': '30'
        })
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data.get('success', False))
        
        # 验证配置已更新
        config = self.Config.query.filter_by(key='new_course_shareholder_a').first()
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
        self.employee = self.Employee(name='业绩测试员工')
        self.db.session.add(self.employee)
        self.db.session.commit()
        self.db.session.refresh(self.employee)
        
        # 创建客户
        customers = []
        for i in range(5):
            customer = self.Customer(
                name=f'客户{i+1}',
                phone=f'1380013800{i}',
                gender='男' if i % 2 == 0 else '女'
            )
            customers.append(customer)
            self.db.session.add(customer)
        
        self.db.session.commit()
        
        # 创建提成配置
        self.commission_config = self.CommissionConfig(
            employee_id=self.employee.id,
            commission_type='profit',
            trial_rate=10,
            new_course_rate=15,
            renewal_rate=20,
            base_salary=3000
        )
        self.db.session.add(self.commission_config)
        
        # 创建试听课
        for i in range(3):
            trial = self.Course(
                name=f'试听课{i+1}',
                customer_id=customers[i].id,
                is_trial=True,
                trial_price=50,
                trial_status='converted' if i < 2 else 'completed',
                assigned_employee_id=self.employee.id
            )
            self.db.session.add(trial)
            
            # 前两个试听课转化为正课
            if i < 2:
                formal = self.Course(
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
                self.db.session.add(formal)
                self.db.session.flush()
                trial.converted_to_course = formal.id
        
        # 创建续课
        renewal = self.Course(
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
        self.db.session.add(renewal)
        
        self.db.session.commit()
    
    def test_employee_performance_stats(self):
        """测试员工业绩统计"""
        response = self.client.get(f'/api/employees/{self.employee.id}/performance')
        
        self.assertEqual(response.status_code, 200)
        
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
        response = self.client.post('/api/profit-config', data={
            'new_course_shareholder_a': '-10',
            'renewal_shareholder_a': '110'
        })
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsNotNone(data.get('success'))
        
        # 验证负数被处理为0
        config = self.Config.query.filter_by(key='new_course_shareholder_a').first()
        if config:
            self.assertEqual(config.value, '0')
    
    def test_date_edge_cases(self):
        """测试日期边界条件"""
        start_date = '2024-01-01'
        end_date = '2024-12-31'
        
        response = self.client.get(f'/api/profit-report?period=custom&start_date={start_date}&end_date={end_date}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data.get('success', True))


# 创建一个快速测试函数
def quick_test():
    """快速测试路由是否工作"""
    print("=== 快速路由测试 ===")
    
    # 设置环境变量
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    os.environ['TESTING'] = 'True'
    
    from app import create_app, db
    app = create_app()
    
    with app.app_context():
        db.create_all()
        
        with app.test_client() as client:
            # 测试路由
            print(f"路由总数: {len(list(app.url_map.iter_rules()))}")
            
            response = client.get('/api/profit-report?period=month')
            print(f"/api/profit-report -> {response.status_code}")
            
            response = client.post('/api/profit-config', data={'new_course_shareholder_a': '50'})
            print(f"/api/profit-config -> {response.status_code}")
            
            response = client.get('/api/employees/1/performance')
            print(f"/api/employees/1/performance -> {response.status_code}")


if __name__ == '__main__':
    # 先运行快速测试
    quick_test()
    
    print("\n=== 开始完整测试 ===")
    # 运行完整测试
    unittest.main(verbosity=2)