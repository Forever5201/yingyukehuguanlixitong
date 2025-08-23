"""
股东利润分配和员工业绩模块的综合测试用例
包含功能测试、边界条件测试、异常处理测试等
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
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self._setup_test_data()
    
    def tearDown(self):
        """测试后的清理工作"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
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
        with self.app.app_context():
            # 收入 = 10节 * 100元 = 1000元
            # 手续费 = 1000 * 0.006 = 6元
            # 成本 = 300 + 6 = 306元
            # 利润 = 1000 - 306 = 694元
            
            response = self.client.get('/api/profit-report?period=month')
            data = json.loads(response.data)
            
            self.assertTrue(data['success'])
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
        with self.app.app_context():
            # 收入 = 20节 * 100元 = 2000元
            # 手续费 = 0（微信支付）
            # 成本 = 600元
            # 利润 = 2000 - 600 = 1400元
            
            response = self.client.get('/api/profit-report?period=month')
            data = json.loads(response.data)
            
            self.assertTrue(data['success'])
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
        with self.app.app_context():
            response = self.client.get('/api/profit-report?period=month')
            data = json.loads(response.data)
            
            summary = data['summary']
            self.assertEqual(summary['total_revenue'], 3000)  # 1000 + 2000
            self.assertEqual(summary['total_cost'], 906)     # 306 + 600
            self.assertEqual(summary['total_profit'], 2094)   # 694 + 1400
            
            # 股东A总收益 = 347 + 560 = 907
            self.assertAlmostEqual(summary['shareholder_a_total'], 907, places=0)
            # 股东B总收益 = 347 + 840 = 1187
            self.assertAlmostEqual(summary['shareholder_b_total'], 1187, places=0)
    
    def test_profit_config_update(self):
        """测试利润分配配置更新"""
        with self.app.app_context():
            # 更新配置
            response = self.client.post('/api/profit-config', data={
                'new_course_shareholder_a': '60',
                'new_course_shareholder_b': '40',
                'renewal_shareholder_a': '30',
                'renewal_shareholder_b': '70'
            })
            
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            
            # 验证配置已更新
            config = Config.query.filter_by(key='new_course_shareholder_a').first()
            self.assertEqual(config.value, '60')
    
    def test_date_range_filtering(self):
        """测试日期范围筛选"""
        with self.app.app_context():
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
            data = json.loads(response.data)
            
            # 应该只有本月的1个新课
            self.assertEqual(len(data['new_courses']), 1)
    
    def test_negative_profit_handling(self):
        """测试负利润处理"""
        with self.app.app_context():
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
            data = json.loads(response.data)
            
            # 找到亏损课程
            loss_data = next((c for c in data['new_courses'] if c['profit'] < 0), None)
            self.assertIsNotNone(loss_data)
            self.assertLess(loss_data['profit'], 0)
            
            # 验证负利润也能正确分配
            self.assertLess(loss_data['shareholder_a'], 0)
            self.assertLess(loss_data['shareholder_b'], 0)
    
    def test_zero_courses_handling(self):
        """测试没有课程的情况"""
        with self.app.app_context():
            # 删除所有课程
            Course.query.delete()
            db.session.commit()
            
            response = self.client.get('/api/profit-report?period=month')
            data = json.loads(response.data)
            
            self.assertTrue(data['success'])
            self.assertEqual(len(data['new_courses']), 0)
            self.assertEqual(len(data['renewal_courses']), 0)
            self.assertEqual(data['summary']['total_profit'], 0)


class TestEmployeePerformance(unittest.TestCase):
    """员工业绩功能测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self._setup_test_data()
    
    def tearDown(self):
        """测试后的清理工作"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def _setup_test_data(self):
        """设置测试数据"""
        # 创建员工
        self.employee = Employee(name='业绩测试员工')
        db.session.add(self.employee)
        
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
        with self.app.app_context():
            response = self.client.get(f'/api/employees/{self.employee.id}/performance')
            data = json.loads(response.data)
            
            self.assertTrue(data['success'])
            self.assertEqual(data['employee_name'], '业绩测试员工')
            
            stats = data['stats']
            self.assertEqual(stats['trial_count'], 3)  # 3个试听课
            self.assertEqual(stats['converted_count'], 2)  # 2个转化
            self.assertAlmostEqual(stats['conversion_rate'], 66.67, places=1)  # 转化率66.67%
            self.assertEqual(stats['total_revenue'], 3000)  # 总收入：10*100*2 + 20*100
    
    def test_commission_calculation_profit_based(self):
        """测试基于利润的提成计算"""
        with self.app.app_context():
            response = self.client.get(f'/api/employees/{self.employee.id}/performance')
            data = json.loads(response.data)
            
            commission = data['commission']
            
            # 试听课提成：2个转化 * 50元 * 10% = 10元
            self.assertEqual(commission['trial_commission'], 10)
            
            # 新课提成：
            # 课程1：收入1000 - 成本300 - 手续费6 = 利润694 * 15% = 104.1
            # 课程2：同上
            # 总计：208.2
            self.assertAlmostEqual(commission['new_course_commission'], 208.2, places=1)
            
            # 续课提成：
            # 收入2000 - 成本600 = 利润1400 * 20% = 280
            self.assertEqual(commission['renewal_commission'], 280)
            
            # 总提成：10 + 208.2 + 280 = 498.2
            self.assertAlmostEqual(commission['total_commission'], 498.2, places=1)
            
            # 总薪资：底薪3000 + 提成498.2 = 3498.2
            self.assertAlmostEqual(commission['total_salary'], 3498.2, places=1)
    
    def test_commission_calculation_sales_based(self):
        """测试基于销售额的提成计算"""
        with self.app.app_context():
            # 更改为销售额提成
            config = CommissionConfig.query.filter_by(employee_id=self.employee.id).first()
            config.commission_type = 'sales'
            db.session.commit()
            
            response = self.client.get(f'/api/employees/{self.employee.id}/performance')
            data = json.loads(response.data)
            
            commission = data['commission']
            
            # 试听课提成不变：10元
            self.assertEqual(commission['trial_commission'], 10)
            
            # 新课提成：销售额2000 * 15% = 300
            self.assertEqual(commission['new_course_commission'], 300)
            
            # 续课提成：销售额2000 * 20% = 400
            self.assertEqual(commission['renewal_commission'], 400)
            
            # 总提成：10 + 300 + 400 = 710
            self.assertEqual(commission['total_commission'], 710)
    
    def test_commission_config_update(self):
        """测试提成配置更新"""
        with self.app.app_context():
            # 更新配置
            response = self.client.post(f'/api/employees/{self.employee.id}/commission-config', 
                                      json={
                                          'commission_type': 'sales',
                                          'trial_rate': 5,
                                          'new_course_rate': 10,
                                          'renewal_rate': 15,
                                          'base_salary': 5000
                                      })
            
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            
            # 验证配置已更新
            config = CommissionConfig.query.filter_by(employee_id=self.employee.id).first()
            self.assertEqual(config.commission_type, 'sales')
            self.assertEqual(config.trial_rate, 5)
            self.assertEqual(config.base_salary, 5000)
    
    def test_zero_performance_handling(self):
        """测试零业绩处理"""
        with self.app.app_context():
            # 创建一个没有任何课程的员工
            new_employee = Employee(name='新员工')
            db.session.add(new_employee)
            db.session.commit()
            
            response = self.client.get(f'/api/employees/{new_employee.id}/performance')
            data = json.loads(response.data)
            
            self.assertTrue(data['success'])
            self.assertEqual(data['stats']['trial_count'], 0)
            self.assertEqual(data['stats']['conversion_rate'], 0)
            self.assertEqual(data['commission']['total_commission'], 0)
            self.assertEqual(data['commission']['base_salary'], 0)  # 默认配置
    
    def test_invalid_employee_handling(self):
        """测试无效员工ID处理"""
        with self.app.app_context():
            response = self.client.get('/api/employees/9999/performance')
            self.assertEqual(response.status_code, 404)


class TestEdgeCasesAndValidation(unittest.TestCase):
    """边界条件和数据验证测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """测试后的清理工作"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_profit_config_validation(self):
        """测试利润配置验证"""
        with self.app.app_context():
            # 测试负数比例
            response = self.client.post('/api/profit-config', data={
                'new_course_shareholder_a': '-10',
                'new_course_shareholder_b': '110'
            })
            
            # 应该接受但在前端验证
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            
            # 测试超过100的比例
            response = self.client.post('/api/profit-config', data={
                'new_course_shareholder_a': '150',
                'new_course_shareholder_b': '-50'
            })
            
            data = json.loads(response.data)
            self.assertTrue(data['success'])
    
    def test_date_edge_cases(self):
        """测试日期边界条件"""
        with self.app.app_context():
            # 测试自定义日期范围
            start_date = '2024-01-01'
            end_date = '2024-12-31'
            
            response = self.client.get(f'/api/profit-report?period=custom&start_date={start_date}&end_date={end_date}')
            data = json.loads(response.data)
            
            self.assertTrue(data['success'])
            
            # 测试结束日期早于开始日期
            response = self.client.get(f'/api/profit-report?period=custom&start_date={end_date}&end_date={start_date}')
            data = json.loads(response.data)
            
            # 应该返回空结果而不是错误
            self.assertTrue(data['success'])
            self.assertEqual(len(data['new_courses']), 0)
    
    def test_null_handling(self):
        """测试空值处理"""
        with self.app.app_context():
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
            data = json.loads(response.data)
            
            # 应该能够处理空值
            self.assertTrue(data['success'])
    
    def test_concurrent_config_update(self):
        """测试并发配置更新"""
        with self.app.app_context():
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
            self.assertEqual(config.value, '70')


def create_code_fixes():
    """创建代码修复文件"""
    fixes = """
# 代码问题修复建议

## 1. 利润分配模块问题修复

### 问题1：缺少输入验证
**位置**: `/api/profit-config` 路由
**修复**:
```python
@app.route('/api/profit-config', methods=['POST'])
def save_profit_config():
    try:
        # 添加输入验证
        for key in ['new_course_shareholder_a', 'renewal_shareholder_a']:
            if key in request.form:
                value = float(request.form[key])
                if value < 0 or value > 100:
                    return jsonify({'success': False, 'message': f'{key}必须在0-100之间'})
                
                # 自动计算B的比例
                b_key = key.replace('_a', '_b')
                b_value = 100 - value
                
                # 保存A和B的配置
                save_config(key, str(value))
                save_config(b_key, str(b_value))
```

### 问题2：空值处理
**位置**: `get_profit_report` 函数
**修复**:
```python
# 在计算成本时添加空值检查
cost = (course.cost or 0) + fee
```

### 问题3：除零错误防护
**位置**: 转化率计算
**修复**:
```python
conversion_rate = (converted_count / trial_count * 100) if trial_count > 0 else 0
```

## 2. 员工业绩模块问题修复

### 问题1：缺少事务处理
**位置**: 提成配置更新
**修复**:
```python
@app.route('/api/employees/<int:employee_id>/commission-config', methods=['POST'])
def save_commission_config(employee_id):
    try:
        data = request.get_json()
        
        # 使用事务
        config = CommissionConfig.query.filter_by(employee_id=employee_id).first()
        if not config:
            config = CommissionConfig(employee_id=employee_id)
            db.session.add(config)
        
        # 更新配置
        for field in ['commission_type', 'trial_rate', 'new_course_rate', 'renewal_rate', 'base_salary']:
            if field in data:
                setattr(config, field, data[field])
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
```

### 问题2：性能优化
**位置**: 员工业绩查询
**修复**: 使用联表查询而不是多次查询
```python
# 使用join一次性获取所有数据
courses = db.session.query(Course).join(Customer).filter(
    Course.assigned_employee_id == employee_id
).all()
```

## 3. 通用改进建议

1. **添加日志记录**：
   - 记录所有配置更改
   - 记录异常情况
   - 记录重要的业务操作

2. **添加缓存**：
   - 缓存配置数据
   - 缓存计算结果

3. **添加权限控制**：
   - 只有管理员能修改利润分配配置
   - 员工只能查看自己的业绩

4. **添加数据备份**：
   - 定期备份配置数据
   - 备份计算结果
"""
    
    with open('/workspace/code_fixes.md', 'w', encoding='utf-8') as f:
        f.write(fixes)


if __name__ == '__main__':
    # 创建修复文档
    create_code_fixes()
    
    # 运行测试
    unittest.main(verbosity=2)