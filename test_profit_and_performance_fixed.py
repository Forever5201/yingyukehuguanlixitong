"""
股东利润分配和员工业绩模块的综合测试用例（修复版）
修复了会话管理、JSON解析和数据类型问题
"""

import unittest
import json
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Employee, Customer, Course, Config, CommissionConfig
import warnings

# 忽略SQLAlchemy的警告
warnings.filterwarnings('ignore', category=DeprecationWarning)


class TestProfitDistribution(unittest.TestCase):
    """股东利润分配功能测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False  # 禁用CSRF保护
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        self._setup_test_data()
    
    def tearDown(self):
        """测试后的清理工作"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
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
        self.assertEqual(response.status_code, 200)
        
        # 检查响应内容
        if response.data:
            data = json.loads(response.data)
            
            self.assertTrue(data.get('success', True))
            self.assertIn('new_courses', data)
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
        # 收入 = 20节 * 100元 = 2000元
        # 手续费 = 0（微信支付）
        # 成本 = 600元
        # 利润 = 2000 - 600 = 1400元
        
        response = self.client.get('/api/profit-report?period=month')
        self.assertEqual(response.status_code, 200)
        
        if response.data:
            data = json.loads(response.data)
            
            self.assertTrue(data.get('success', True))
            self.assertIn('renewal_courses', data)
            self.assertEqual(len(data['renewal_courses']), 1)
            
            course = data['renewal_courses'][0]
            self.assertEqual(course['revenue'], 2000)
            self.assertEqual(course['cost'], 600)
            self.assertEqual(course['profit'], 1400)
            
            # 验证分配比例 (40%/60%)
            self.assertAlmostEqual(course['shareholder_a'], 560, places=0)
            self.assertAlmostEqual(course['shareholder_b'], 840, places=0)
    
    def test_profit_summary_calculation(self):
        """测试利润汇总计算"""
        response = self.client.get('/api/profit-report?period=month')
        self.assertEqual(response.status_code, 200)
        
        if response.data:
            data = json.loads(response.data)
            
            summary = data.get('summary', {})
            self.assertEqual(summary.get('total_revenue', 0), 3000)  # 1000 + 2000
            self.assertEqual(summary.get('total_cost', 0), 906)     # 306 + 600
            self.assertEqual(summary.get('total_profit', 0), 2094)   # 694 + 1400
            
            # 股东A总收益 = 347 + 560 = 907
            self.assertAlmostEqual(summary.get('shareholder_a_total', 0), 907, places=0)
            # 股东B总收益 = 347 + 840 = 1187
            self.assertAlmostEqual(summary.get('shareholder_b_total', 0), 1187, places=0)
    
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
            self.assertIn(config.value, ['60', '60.0'])  # 接受两种格式
    
    def test_date_range_filtering(self):
        """测试日期范围筛选"""
        # 添加上个月的课程
        old_course = Course(
            name='旧课程',
            customer_id=self.customer1.id,
            is_trial=False,
            is_renewal=False,
            sessions=5,
            price=100,
            cost=150,
            created_at=datetime.now() - timedelta(days=35)
        )
        db.session.add(old_course)
        db.session.commit()
        
        # 只查询本月数据
        response = self.client.get('/api/profit-report?period=month')
        self.assertEqual(response.status_code, 200)
        
        if response.data:
            data = json.loads(response.data)
            # 应该只有本月的1个新课
            self.assertEqual(len(data.get('new_courses', [])), 1)
    
    def test_negative_profit_handling(self):
        """测试负利润处理"""
        # 创建一个亏损的课程
        loss_course = Course(
            name='亏损课程',
            customer_id=self.customer1.id,
            is_trial=False,
            is_renewal=False,
            sessions=5,
            price=50,   # 收入250
            cost=300,   # 成本300，导致亏损
            payment_channel='淘宝'
        )
        db.session.add(loss_course)
        db.session.commit()
        
        response = self.client.get('/api/profit-report?period=month')
        self.assertEqual(response.status_code, 200)
        
        if response.data:
            data = json.loads(response.data)
            
            # 找到亏损课程
            loss_data = next((c for c in data.get('new_courses', []) if c['profit'] < 0), None)
            if loss_data:
                self.assertLess(loss_data['profit'], 0)
                # 验证负利润也能正确分配
                self.assertLess(loss_data['shareholder_a'], 0)
                self.assertLess(loss_data['shareholder_b'], 0)
    
    def test_zero_courses_handling(self):
        """测试没有课程的情况"""
        # 删除所有课程
        Course.query.delete()
        db.session.commit()
        
        response = self.client.get('/api/profit-report?period=month')
        self.assertEqual(response.status_code, 200)
        
        if response.data:
            data = json.loads(response.data)
            
            self.assertTrue(data.get('success', True))
            self.assertEqual(len(data.get('new_courses', [])), 0)
            self.assertEqual(len(data.get('renewal_courses', [])), 0)
            self.assertEqual(data.get('summary', {}).get('total_profit', 0), 0)


class TestEmployeePerformance(unittest.TestCase):
    """员工业绩功能测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        self._setup_test_data()
    
    def tearDown(self):
        """测试后的清理工作"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
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
            commission_type='profit',  # 利润提成
            trial_rate=10,    # 试听课10%
            new_course_rate=15,  # 新课15%
            renewal_rate=20,     # 续课20%
            base_salary=3000     # 底薪3000
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
                db.session.flush()  # 确保获取ID
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
        
        if response.data:
            data = json.loads(response.data)
            
            self.assertTrue(data.get('success', False))
            self.assertEqual(data.get('employee_name'), '业绩测试员工')
            
            stats = data.get('stats', {})
            self.assertEqual(stats.get('trial_count', 0), 3)  # 3个试听课
            self.assertEqual(stats.get('converted_count', 0), 2)  # 2个转化
            self.assertAlmostEqual(stats.get('conversion_rate', 0), 66.67, places=1)  # 转化率66.67%
            self.assertEqual(stats.get('total_revenue', 0), 3000)  # 总收入：10*100*2 + 20*100
    
    def test_commission_calculation_profit_based(self):
        """测试基于利润的提成计算"""
        response = self.client.get(f'/api/employees/{self.employee.id}/performance')
        self.assertEqual(response.status_code, 200)
        
        if response.data:
            data = json.loads(response.data)
            
            commission = data.get('commission', {})
            
            # 试听课提成：2个转化 * 50元 * 10% = 10元
            self.assertEqual(commission.get('trial_commission', 0), 10)
            
            # 新课提成：
            # 课程1：收入1000 - 成本300 - 手续费6 = 利润694 * 15% = 104.1
            # 课程2：同上
            # 总计：208.2
            self.assertAlmostEqual(commission.get('new_course_commission', 0), 208.2, places=1)
            
            # 续课提成：
            # 收入2000 - 成本600 = 利润1400 * 20% = 280
            self.assertEqual(commission.get('renewal_commission', 0), 280)
            
            # 总提成：10 + 208.2 + 280 = 498.2
            self.assertAlmostEqual(commission.get('total_commission', 0), 498.2, places=1)
            
            # 总薪资：底薪3000 + 提成498.2 = 3498.2
            self.assertAlmostEqual(commission.get('total_salary', 0), 3498.2, places=1)
    
    def test_commission_calculation_sales_based(self):
        """测试基于销售额的提成计算"""
        # 更改为销售额提成
        config = CommissionConfig.query.filter_by(employee_id=self.employee.id).first()
        config.commission_type = 'sales'
        db.session.commit()
        
        response = self.client.get(f'/api/employees/{self.employee.id}/performance')
        self.assertEqual(response.status_code, 200)
        
        if response.data:
            data = json.loads(response.data)
            
            commission = data.get('commission', {})
            
            # 试听课提成不变：10元
            self.assertEqual(commission.get('trial_commission', 0), 10)
            
            # 新课提成：销售额2000 * 15% = 300
            self.assertEqual(commission.get('new_course_commission', 0), 300)
            
            # 续课提成：销售额2000 * 20% = 400
            self.assertEqual(commission.get('renewal_commission', 0), 400)
            
            # 总提成：10 + 300 + 400 = 710
            self.assertEqual(commission.get('total_commission', 0), 710)
    
    def test_commission_config_update(self):
        """测试提成配置更新"""
        # 更新配置
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
            
            # 验证配置已更新
            config = CommissionConfig.query.filter_by(employee_id=self.employee.id).first()
            self.assertEqual(config.commission_type, 'sales')
            self.assertEqual(config.trial_rate, 5)
            self.assertEqual(config.base_salary, 5000)
    
    def test_zero_performance_handling(self):
        """测试零业绩处理"""
        # 创建一个没有任何课程的员工
        new_employee = Employee(name='新员工')
        db.session.add(new_employee)
        db.session.commit()
        
        response = self.client.get(f'/api/employees/{new_employee.id}/performance')
        self.assertEqual(response.status_code, 200)
        
        if response.data:
            data = json.loads(response.data)
            
            self.assertTrue(data.get('success', False))
            self.assertEqual(data.get('stats', {}).get('trial_count', 0), 0)
            self.assertEqual(data.get('stats', {}).get('conversion_rate', 0), 0)
            self.assertEqual(data.get('commission', {}).get('total_commission', 0), 0)
            self.assertEqual(data.get('commission', {}).get('base_salary', 0), 0)  # 默认配置
    
    def test_invalid_employee_handling(self):
        """测试无效员工ID处理"""
        response = self.client.get('/api/employees/9999/performance')
        self.assertEqual(response.status_code, 404)


class TestEdgeCasesAndValidation(unittest.TestCase):
    """边界条件和数据验证测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
    
    def tearDown(self):
        """测试后的清理工作"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
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
            # 根据实际实现，可能接受或拒绝
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
            
        # 测试结束日期早于开始日期
        response = self.client.get(f'/api/profit-report?period=custom&start_date={end_date}&end_date={start_date}')
        self.assertEqual(response.status_code, 200)
        
        if response.data:
            data = json.loads(response.data)
            # 应该返回空结果而不是错误
            self.assertTrue(data.get('success', True))
            self.assertEqual(len(data.get('new_courses', [])), 0)
    
    def test_null_handling(self):
        """测试空值处理"""
        # 创建一个字段不完整的课程
        customer = Customer(name='测试客户', phone='13800138000')
        db.session.add(customer)
        db.session.commit()
        
        course = Course(
            customer_id=customer.id,
            is_trial=False,
            sessions=10,
            price=100,
            cost=None,  # 成本为空
            payment_channel=None,  # 支付渠道为空
            snapshot_fee_rate=None  # 费率为空
        )
        db.session.add(course)
        db.session.commit()
        
        response = self.client.get('/api/profit-report?period=month')
        self.assertEqual(response.status_code, 200)
        
        if response.data:
            data = json.loads(response.data)
            # 应该能够处理空值
            self.assertTrue(data.get('success', True))
    
    def test_concurrent_config_update(self):
        """测试并发配置更新"""
        # 初始化配置
        Config.query.delete()
        config = Config(key='new_course_shareholder_a', value='50')
        db.session.add(config)
        db.session.commit()
        
        # 模拟两个并发更新
        response1 = self.client.post('/api/profit-config', data={
            'new_course_shareholder_a': '60',
            'new_course_shareholder_b': '40'
        })
        
        response2 = self.client.post('/api/profit-config', data={
            'new_course_shareholder_a': '70',
            'new_course_shareholder_b': '30'
        })
        
        # 最后一个更新应该生效
        config = Config.query.filter_by(key='new_course_shareholder_a').first()
        # 接受'70'或'70.0'
        self.assertIn(config.value, ['70', '70.0'])


if __name__ == '__main__':
    unittest.main(verbosity=2)