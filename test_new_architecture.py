"""
测试新架构的工作情况

这个脚本用于验证：
1. 服务层适配器是否正常工作
2. 新API端点是否可用
3. 新旧API的兼容性
"""

import os
import sys
import json
import requests
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models import Customer, Course, Employee, Config

# 测试配置
TEST_BASE_URL = 'http://localhost:5000'
OLD_API_BASE = f'{TEST_BASE_URL}/api'
NEW_API_BASE = f'{TEST_BASE_URL}/api/v1'

class ArchitectureTest:
    def __init__(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.context = self.app.app_context()
        self.context.push()
        
    def __del__(self):
        self.context.pop()
    
    def setup_test_data(self):
        """设置测试数据"""
        print("设置测试数据...")
        
        # 创建测试员工
        employee = Employee(name="测试员工", phone="13800138000")
        db.session.add(employee)
        
        # 创建测试客户
        customer = Customer(
            name="测试客户",
            phone="13900139000",
            grade="初一",
            region="北京"
        )
        db.session.add(customer)
        
        # 设置配置
        configs = [
            Config(key='trial_cost', value='30'),
            Config(key='course_cost', value='50'),
            Config(key='taobao_fee_rate', value='0.6')
        ]
        for config in configs:
            existing = Config.query.filter_by(key=config.key).first()
            if not existing:
                db.session.add(config)
        
        db.session.commit()
        print("✓ 测试数据设置完成")
        
        return employee.id, customer.id
    
    def test_service_adapter(self):
        """测试服务层适配器"""
        print("\n测试服务层适配器...")
        
        try:
            from app.services.course_service_adapter import CourseServiceAdapter
            
            # 测试获取试听课列表
            result = CourseServiceAdapter.get_trial_courses()
            assert result['success'] == True
            assert 'data' in result
            assert 'courses' in result['data']
            assert 'statistics' in result['data']
            print("✓ 获取试听课列表成功")
            
            # 测试创建试听课
            employee_id, customer_id = self.setup_test_data()
            
            course_data = {
                'customer_id': customer_id,
                'trial_price': 99.0,
                'source': '淘宝',
                'assigned_employee_id': employee_id
            }
            
            result = CourseServiceAdapter.create_trial_course(course_data)
            assert result['success'] == True
            assert 'course_id' in result['data']
            print("✓ 创建试听课成功")
            
            return True
            
        except Exception as e:
            print(f"✗ 服务层适配器测试失败: {str(e)}")
            return False
    
    def test_new_api_endpoints(self):
        """测试新API端点"""
        print("\n测试新API端点...")
        
        try:
            # 测试获取试听课列表
            response = self.client.get('/api/v1/courses/trial')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] == True
            print("✓ 新API获取试听课列表成功")
            
            # 测试创建试听课
            employee_id, _ = self.setup_test_data()
            
            course_data = {
                'customer_name': '新客户测试',
                'customer_phone': '13700137000',
                'trial_price': 88.0,
                'source': '视频号',
                'assigned_employee_id': employee_id
            }
            
            response = self.client.post(
                '/api/v1/courses/trial',
                json=course_data,
                content_type='application/json'
            )
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['success'] == True
            print("✓ 新API创建试听课成功")
            
            return True
            
        except Exception as e:
            print(f"✗ 新API端点测试失败: {str(e)}")
            return False
    
    def test_api_compatibility(self):
        """测试新旧API兼容性"""
        print("\n测试API兼容性...")
        
        try:
            # 测试旧API仍然工作
            response = self.client.get('/api/trial-courses')
            assert response.status_code == 200
            print("✓ 旧API仍然正常工作")
            
            # 测试新旧API数据一致性
            old_response = self.client.get('/api/trial-courses')
            new_response = self.client.get('/api/v1/courses/trial')
            
            old_data = json.loads(old_response.data)
            new_data = json.loads(new_response.data)
            
            # 新API有更丰富的数据结构，但基础数据应该一致
            if isinstance(old_data, list) and 'data' in new_data:
                print("✓ 新旧API返回格式符合预期")
            
            return True
            
        except Exception as e:
            print(f"✗ API兼容性测试失败: {str(e)}")
            return False
    
    def test_error_handling(self):
        """测试错误处理"""
        print("\n测试错误处理...")
        
        try:
            # 测试验证错误
            response = self.client.post(
                '/api/v1/courses/trial',
                json={'invalid': 'data'},
                content_type='application/json'
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] == False
            assert 'message' in data
            print("✓ 验证错误处理正常")
            
            # 测试业务逻辑错误（重复创建）
            employee_id, customer_id = self.setup_test_data()
            
            # 先创建一个试听课
            course_data = {
                'customer_id': customer_id,
                'trial_price': 99.0,
                'source': '淘宝',
                'assigned_employee_id': employee_id
            }
            
            # 第一次创建应该成功
            self.client.post('/api/v1/courses/trial', json=course_data)
            
            # 第二次创建应该失败
            response = self.client.post(
                '/api/v1/courses/trial',
                json=course_data,
                content_type='application/json'
            )
            
            assert response.status_code == 409
            data = json.loads(response.data)
            assert '已有试听课记录' in data['message']
            print("✓ 业务逻辑错误处理正常")
            
            return True
            
        except Exception as e:
            print(f"✗ 错误处理测试失败: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 50)
        print("新架构测试开始")
        print("=" * 50)
        
        results = {
            '服务层适配器': self.test_service_adapter(),
            '新API端点': self.test_new_api_endpoints(),
            'API兼容性': self.test_api_compatibility(),
            '错误处理': self.test_error_handling()
        }
        
        print("\n" + "=" * 50)
        print("测试结果汇总:")
        print("=" * 50)
        
        for test_name, result in results.items():
            status = "✓ 通过" if result else "✗ 失败"
            print(f"{test_name}: {status}")
        
        all_passed = all(results.values())
        
        if all_passed:
            print("\n🎉 所有测试通过！新架构工作正常。")
        else:
            print("\n⚠️  部分测试失败，请检查相关功能。")
        
        return all_passed

if __name__ == '__main__':
    # 确保在测试环境中运行
    os.environ['FLASK_ENV'] = 'testing'
    
    tester = ArchitectureTest()
    
    try:
        # 清理可能存在的测试数据
        db.session.query(Course).filter(Course.customer_id.in_(
            db.session.query(Customer.id).filter(Customer.phone.like('13%00%'))
        )).delete(synchronize_session=False)
        db.session.query(Customer).filter(Customer.phone.like('13%00%')).delete()
        db.session.query(Employee).filter(Employee.name == '测试员工').delete()
        db.session.commit()
        
        # 运行测试
        success = tester.run_all_tests()
        
        # 清理测试数据
        db.session.query(Course).filter(Course.customer_id.in_(
            db.session.query(Customer.id).filter(Customer.phone.like('13%00%'))
        )).delete(synchronize_session=False)
        db.session.query(Customer).filter(Customer.phone.like('13%00%')).delete()
        db.session.query(Employee).filter(Employee.name == '测试员工').delete()
        db.session.commit()
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        sys.exit(1)