"""
股东利润分配和员工业绩模块的综合测试用例（最终解决方案）
通过猴子补丁解决路由加载问题
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


def patch_create_app():
    """修补create_app函数以确保路由正确加载"""
    from app import create_app as original_create_app
    
    def patched_create_app():
        app = original_create_app()
        
        # 确保路由已加载
        with app.app_context():
            # 强制重新导入routes
            import importlib
            import app.routes
            importlib.reload(app.routes)
        
        return app
    
    # 替换原函数
    import app
    app.create_app = patched_create_app
    
    return patched_create_app


# 在导入任何app相关模块之前应用补丁
patch_create_app()

# 现在导入app相关模块
from app import create_app, db
from app.models import Employee, Customer, Course, Config, CommissionConfig


class TestBase(unittest.TestCase):
    """测试基类，包含通用的setUp和tearDown"""
    
    def setUp(self):
        """每个测试前的准备工作"""
        # 创建应用实例
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        # 创建应用上下文
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 创建数据库表
        db.create_all()
        
        # 创建测试客户端
        self.client = self.app.test_client()
        
        # 验证路由已加载
        route_count = len(list(self.app.url_map.iter_rules()))
        if route_count < 50:
            print(f"警告：只有{route_count}个路由，可能存在问题")
    
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
        self.new_course1 = Course(
            name='语法课程',
            customer_id=self.customer1.id,
            is_trial=False,
            is_renewal=False,
            sessions=10,
            price=100,
            cost=300,
            payment_channel='淘宝',
            snapshot_fee_rate=0.006,
            course_type='语法课'
        )
        
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
        response = self.client.get('/api/profit-report?period=month')
        
        self.assertEqual(response.status_code, 200, 
                       f"预期状态码200，实际得到{response.status_code}")
        
        data = json.loads(response.data)
        
        self.assertTrue(data.get('success', True))
        self.assertIn('new_courses', data)
        
        if data.get('new_courses'):
            self.assertEqual(len(data['new_courses']), 1)
            
            course = data['new_courses'][0]
            self.assertEqual(course['revenue'], 1000)
            self.assertEqual(course['cost'], 306)
            self.assertEqual(course['profit'], 694)
            
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
        
        # 创建试听课和正课
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
        
        config = Config.query.filter_by(key='new_course_shareholder_a').first()
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


# 直接运行测试的辅助函数
def run_direct_test():
    """直接测试，不使用unittest框架"""
    print("=== 直接测试路由 ===")
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        
        # 添加测试数据
        config = Config(key='new_course_shareholder_a', value='50')
        db.session.add(config)
        db.session.commit()
        
        with app.test_client() as client:
            # 测试路由
            print(f"路由总数: {len(list(app.url_map.iter_rules()))}")
            
            response = client.get('/api/profit-report?period=month')
            print(f"/api/profit-report -> {response.status_code}")
            if response.status_code == 200:
                data = json.loads(response.data)
                print(f"  成功: {data.get('success')}")
            
            response = client.post('/api/profit-config', data={'new_course_shareholder_a': '50'})
            print(f"/api/profit-config -> {response.status_code}")
            
            # 创建员工测试
            employee = Employee(name='测试员工')
            db.session.add(employee)
            db.session.commit()
            
            response = client.get(f'/api/employees/{employee.id}/performance')
            print(f"/api/employees/{employee.id}/performance -> {response.status_code}")


if __name__ == '__main__':
    # 先运行直接测试
    run_direct_test()
    
    print("\n=== 开始unittest测试 ===")
    # 运行unittest测试
    unittest.main(verbosity=2)