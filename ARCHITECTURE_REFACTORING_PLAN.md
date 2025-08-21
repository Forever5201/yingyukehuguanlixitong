# 系统架构重构方案

## 当前问题分析

### 1. API设计问题
- 多个相似功能的API端点（trial-courses, formal-courses, courses-unified）
- 业务逻辑分散在路由层
- 数据访问逻辑重复

### 2. 数据一致性问题
- 员工管理中的课程数据与独立课程管理使用相同数据源
- 缺乏统一的数据访问接口
- 业务规则分散在多个地方

## 规范化解决方案

### 1. 服务层架构（Service Layer Pattern）

```python
# services/course_service.py
class CourseService:
    @staticmethod
    def get_courses(employee_id=None, course_type=None, status=None, **filters):
        """统一的课程查询接口"""
        query = db.session.query(Course, Customer).join(Customer)
        
        if employee_id:
            query = query.filter(Course.assigned_employee_id == employee_id)
        if course_type:
            query = query.filter(Course.is_trial == (course_type == 'trial'))
        if status:
            query = query.filter(Course.trial_status == status)
            
        return query.all()
    
    @staticmethod
    def calculate_performance(courses):
        """统一的业绩计算逻辑"""
        # 统一的计算逻辑，避免重复
        pass
    
    @staticmethod
    def update_course(course_id, data):
        """统一的课程更新接口"""
        # 包含业务规则验证
        pass

# services/employee_service.py  
class EmployeeService:
    @staticmethod
    def get_employee_courses(employee_id, course_type=None):
        """获取员工课程，委托给CourseService"""
        return CourseService.get_courses(employee_id=employee_id, course_type=course_type)
```

### 2. 统一API设计

```python
# 替换多个分散的API
@app.route('/api/courses')
def get_courses():
    """统一的课程查询API"""
    employee_id = request.args.get('employee_id', type=int)
    course_type = request.args.get('type')  # 'trial', 'formal', 'all'
    status = request.args.get('status')
    
    courses = CourseService.get_courses(
        employee_id=employee_id,
        course_type=course_type,
        status=status
    )
    
    return jsonify({
        'courses': courses,
        'performance': CourseService.calculate_performance(courses)
    })

# 员工专用API（如果需要特殊业务逻辑）
@app.route('/api/employees/<int:employee_id>/courses')
def get_employee_courses(employee_id):
    """员工课程API，委托给统一服务"""
    course_type = request.args.get('type', 'all')
    return EmployeeService.get_employee_courses(employee_id, course_type)
```

### 3. 数据一致性保证

#### 3.1 事务边界明确化
```python
class CourseService:
    @staticmethod
    @db.transaction
    def assign_course_to_employee(course_id, employee_id):
        """原子操作：课程分配"""
        course = Course.query.get_or_404(course_id)
        employee = Employee.query.get_or_404(employee_id)
        
        # 业务规则验证
        if not employee.can_handle_course(course):
            raise BusinessRuleError("员工无法处理此类课程")
            
        course.assigned_employee_id = employee_id
        db.session.commit()
        
        # 发布事件（如果需要）
        EventBus.publish('course_assigned', {
            'course_id': course_id,
            'employee_id': employee_id
        })
```

#### 3.2 领域模型强化
```python
class Course(db.Model):
    # ... 现有字段
    
    def assign_to_employee(self, employee):
        """领域方法：课程分配业务逻辑"""
        if not employee.can_handle_course(self):
            raise BusinessRuleError("员工无法处理此类课程")
        self.assigned_employee_id = employee.id
        
    def calculate_profit(self):
        """领域方法：利润计算"""
        revenue = float(self.price or 0)
        cost = float(self.cost or 0) + float(self.other_cost or 0)
        fees = self.calculate_fees()
        return revenue - cost - fees
        
    def calculate_fees(self):
        """领域方法：手续费计算"""
        if self.payment_channel == '淘宝':
            return float(self.price or 0) * 0.006
        return 0

class Employee(db.Model):
    # ... 现有字段
    
    def can_handle_course(self, course):
        """业务规则：员工是否能处理课程"""
        # 实现具体的业务规则
        return True
        
    def get_performance_stats(self):
        """获取员工业绩统计"""
        courses = CourseService.get_courses(employee_id=self.id)
        return CourseService.calculate_performance(courses)
```

### 4. 前端统一化

#### 4.1 统一的数据访问层
```javascript
// static/js/api-client.js
class ApiClient {
    static async getCourses(filters = {}) {
        const params = new URLSearchParams(filters);
        const response = await fetch(`/api/courses?${params}`);
        return response.json();
    }
    
    static async getEmployeeCourses(employeeId, type = 'all') {
        return this.getCourses({ employee_id: employeeId, type });
    }
    
    static async updateCourse(courseId, data) {
        const response = await fetch(`/api/courses/${courseId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    }
}

// 替换CourseManager中的重复代码
class CourseManager {
    static async loadEmployeeCourses(employeeId, type) {
        try {
            const data = await ApiClient.getEmployeeCourses(employeeId, type);
            this.renderCourses(data.courses);
            this.updatePerformanceStats(data.performance);
        } catch (error) {
            console.error('加载课程失败:', error);
        }
    }
}
```

### 5. 配置管理规范化

```python
# config/business_rules.py
class BusinessRules:
    TAOBAO_FEE_RATE = 0.006
    STATUS_MAPPING = {
        'registered': '已报名试听课',
        'not_registered': '未报名试听课',
        'refunded': '试听后退费',
        'converted': '试听后转正课',
        'no_action': '试听后无操作'
    }
    
    @classmethod
    def get_fee_rate(cls, payment_channel):
        if payment_channel == '淘宝':
            return cls.TAOBAO_FEE_RATE
        return 0
```

## 实施计划

### 阶段1：服务层重构
1. 创建CourseService和EmployeeService
2. 将业务逻辑从路由层迁移到服务层
3. 统一数据访问接口

### 阶段2：API统一化
1. 创建统一的/api/courses接口
2. 逐步迁移现有API调用
3. 保持向后兼容性

### 阶段3：前端重构
1. 创建统一的ApiClient
2. 重构CourseManager，消除重复代码
3. 统一错误处理和加载状态

### 阶段4：数据模型强化
1. 在模型中添加业务方法
2. 强化业务规则验证
3. 优化数据库查询

## 预期收益

1. **代码复用性提升**：消除重复的业务逻辑
2. **维护性改善**：业务规则集中管理
3. **数据一致性保证**：统一的数据访问层
4. **扩展性增强**：清晰的架构边界
5. **测试性提升**：独立的服务层便于单元测试