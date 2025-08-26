# 业务规范实现文档

## 核心业务规范

### 1. 试听课转正课规范

**规范要求：**
- 必须现有试听课
- 试听课转化后才能把该客户分配给员工
- 正课必须分配给同一个员工

**实现方式：**

#### 1.1 试听课转正课流程 (`/convert-trial/<trial_id>`)
```python
# 创建正课记录时继承试听课的员工分配
formal_course = Course(
    # ... 其他字段
    assigned_employee_id=trial_course.assigned_employee_id,  # 继承试听课的员工分配
    converted_from_trial=trial_id,  # 记录转化关系
    # ... 其他字段
)

# 更新试听课记录，标记已转化
trial_course.converted_to_course = formal_course.id
trial_course.trial_status = 'converted'
```

#### 1.2 直接创建正课API限制 (`/api/formal-courses`)
```python
# 业务规范检查：必须从试听课转化
trial_id = data.get('converted_from_trial')
if not trial_id:
    return {'error': '正课必须从试听课转化而来，请提供converted_from_trial参数'}, 400

# 验证试听课是否存在且属于该客户
trial_course = Course.query.filter_by(
    id=trial_id,
    customer_id=data['customer_id'],
    is_trial=True
).first()

# 业务规范：正课必须分配给试听课的同一个员工
assigned_employee_id = trial_course.assigned_employee_id
if not assigned_employee_id:
    return {'error': '试听课未分配员工，无法创建正课。请先分配试听课给员工'}, 400
```

### 2. 员工业绩统计规范

**规范要求：**
- 只统计试听课和正课都分配给同一个员工的记录
- 确保业务逻辑一致性：正课都是从试听课转化来的

**实现方式：**

#### 2.1 员工业绩详情API (`/api/employees/<employee_id>/performance`)
```python
# 获取正课记录 - 只显示试听课和正课都分配给该员工的记录
formal_courses = []
for trial_course in trial_courses:
    if trial_course.converted_to_course:
        # 查找对应的正课
        formal_course = Course.query.get(trial_course.converted_to_course)
        if formal_course and formal_course.assigned_employee_id == employee_id:
            formal_courses.append(formal_course)
```

#### 2.2 员工列表页面统计 (`/employee-performance`)
```python
# 本月业绩（正课）- 只计算试听课和正课都分配给该员工的记录
monthly_courses = []
for trial_course in trial_courses:
    if trial_course.converted_to_course:
        # 查找对应的正课
        formal_course = Course.query.get(trial_course.converted_to_course)
        if (formal_course and 
            formal_course.assigned_employee_id == employee.id and
            formal_course.created_at >= start_of_month):
            monthly_courses.append(formal_course)
```

### 3. 续课规范

**规范要求：**
- 续课继承原课程的员工分配
- 续课不要求试听课转化

**实现方式：**
```python
# 处理员工分配
if assigned_employee_id and assigned_employee_id.strip():
    assigned_employee_id = int(assigned_employee_id)
else:
    assigned_employee_id = course.assigned_employee_id  # 继承原课程的员工
```

## 数据验证规则

### 1. 试听课分配验证
- 试听课可以分配给员工或保持未分配状态
- 只有分配的试听课才能转化为正课

### 2. 正课创建验证
- 正课必须从试听课转化而来
- 正课必须分配给试听课的同一个员工
- 试听课必须已分配员工才能创建正课

### 3. 转化关系验证
- 一个试听课只能转化为一个正课
- 转化关系通过 `converted_from_trial` 和 `converted_to_course` 字段维护

## 错误处理

### 1. 业务规范违反错误
- 尝试直接创建正课而不从试听课转化：返回400错误
- 试听课未分配员工时尝试创建正课：返回400错误
- 试听课已转化时再次尝试转化：返回400错误

### 2. 数据一致性错误
- 试听课和正课分配不同员工：在员工业绩统计中过滤掉
- 缺少转化关系的正课：在员工业绩统计中不显示

## 前端界面规范

### 1. 试听课管理
- 显示试听课分配状态
- 只有未转化的试听课可以转正课
- 提供员工分配功能

### 2. 正课管理
- 显示正课的转化来源
- 显示正课的员工分配
- 提供续课功能

### 3. 员工业绩
- 显示试听课和正课数量
- 确保试听课数量 = 正课数量（符合业务逻辑）
- 显示转化率和业绩统计

## 测试用例

### 1. 正常流程测试
- 创建试听课并分配员工
- 试听课转正课，验证员工分配继承
- 查看员工业绩，验证数据一致性

### 2. 异常流程测试
- 尝试直接创建正课（应该失败）
- 试听课未分配员工时转正课（应该失败）
- 已转化的试听课再次转正课（应该失败）

### 3. 数据一致性测试
- 试听课和正课分配不同员工时的显示
- 缺少转化关系的正课在员工业绩中的处理
- 续课功能的员工分配继承

