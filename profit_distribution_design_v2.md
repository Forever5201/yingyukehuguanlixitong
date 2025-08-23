# 股东利润分配系统设计方案 V2

## 一、业务场景分析

### 当前阶段（无员工）
- 两位股东直接运营
- 新课利润：股东A 50%，股东B 50%
- 续课利润：股东A 40%，股东B 60%

### 未来阶段（有员工）
- 员工负责的业务产生的利润，扣除员工成本后：股东A 50%，股东B 50%
- 股东直接负责的业务保持原有分配比例

## 二、利润计算逻辑设计

### 1. 核心概念
```
业务归属 = 股东直接负责 | 员工负责
利润来源 = 新课 | 续课
```

### 2. 利润计算公式

#### 无员工阶段（当前）
```
课程收入 = 试听课收入 + 正课收入
课程成本 = 课程基础成本 + 支付手续费
课程利润 = 课程收入 - 课程成本

新课利润分配：
- 股东A = 新课利润 × 50%
- 股东B = 新课利润 × 50%

续课利润分配：
- 股东A = 续课利润 × 40%
- 股东B = 续课利润 × 60%
```

#### 有员工阶段（未来）
```
员工创造收入 = 员工负责的（试听课收入 + 正课收入）
员工相关成本 = 课程成本 + 员工底薪 + 员工提成
员工创造利润 = 员工创造收入 - 员工相关成本

员工业务利润分配：
- 股东A = 员工创造利润 × 50%
- 股东B = 员工创造利润 × 50%

股东直接业务保持原分配比例
```

## 三、数据库设计优化

### 1. 扩展课程表 (course) - 添加归属信息
```sql
ALTER TABLE course ADD COLUMN attribution_type VARCHAR(20) DEFAULT 'shareholder'; -- shareholder/employee
ALTER TABLE course ADD COLUMN attribution_id INTEGER; -- 具体归属人ID
```

### 2. 创建利润分配规则表 (profit_rule)
```sql
CREATE TABLE profit_rule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name VARCHAR(100) NOT NULL,           -- 规则名称
    business_type VARCHAR(50) NOT NULL,        -- new_course/renewal
    attribution_type VARCHAR(20) NOT NULL,     -- shareholder/employee
    shareholder_a_ratio FLOAT NOT NULL,        -- 股东A比例
    shareholder_b_ratio FLOAT NOT NULL,        -- 股东B比例
    effective_date DATE NOT NULL,              -- 生效日期
    expiry_date DATE,                          -- 失效日期
    is_active BOOLEAN DEFAULT TRUE,            -- 是否启用
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- 插入初始规则
INSERT INTO profit_rule (rule_name, business_type, attribution_type, shareholder_a_ratio, shareholder_b_ratio, effective_date) VALUES
('股东新课分配', 'new_course', 'shareholder', 50, 50, '2024-01-01'),
('股东续课分配', 'renewal', 'shareholder', 40, 60, '2024-01-01'),
('员工业务分配', 'all', 'employee', 50, 50, '2024-01-01');
```

### 3. 创建月度利润明细表 (monthly_profit_detail)
```sql
CREATE TABLE monthly_profit_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    course_id INTEGER NOT NULL,                -- 关联课程
    customer_name VARCHAR(100),                -- 客户姓名
    course_type VARCHAR(50),                   -- 课程类型
    is_renewal BOOLEAN DEFAULT FALSE,          -- 是否续课
    attribution_type VARCHAR(20),              -- 归属类型
    attribution_name VARCHAR(100),             -- 归属人名称
    
    -- 财务数据
    revenue FLOAT DEFAULT 0,                   -- 收入
    course_cost FLOAT DEFAULT 0,               -- 课程成本
    payment_fee FLOAT DEFAULT 0,               -- 支付手续费
    employee_salary FLOAT DEFAULT 0,           -- 员工底薪（分摊）
    employee_commission FLOAT DEFAULT 0,       -- 员工提成
    other_cost FLOAT DEFAULT 0,               -- 其他成本
    
    -- 利润计算
    gross_profit FLOAT DEFAULT 0,             -- 毛利润
    net_profit FLOAT DEFAULT 0,               -- 净利润
    
    -- 分配信息
    applied_rule_id INTEGER,                   -- 应用的规则ID
    shareholder_a_ratio FLOAT,                 -- 股东A比例
    shareholder_b_ratio FLOAT,                 -- 股东B比例
    shareholder_a_amount FLOAT,                -- 股东A金额
    shareholder_b_amount FLOAT,                -- 股东B金额
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES course(id),
    FOREIGN KEY (applied_rule_id) REFERENCES profit_rule(id)
);
```

### 4. 月度汇总表简化版 (monthly_profit_summary)
```sql
CREATE TABLE monthly_profit_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    
    -- 按归属类型统计
    shareholder_revenue FLOAT DEFAULT 0,       -- 股东直接收入
    shareholder_profit FLOAT DEFAULT 0,        -- 股东直接利润
    employee_revenue FLOAT DEFAULT 0,          -- 员工创造收入
    employee_profit FLOAT DEFAULT 0,           -- 员工创造利润
    
    -- 按业务类型统计
    new_course_profit FLOAT DEFAULT 0,         -- 新课利润
    renewal_profit FLOAT DEFAULT 0,            -- 续课利润
    
    -- 总计
    total_revenue FLOAT DEFAULT 0,             -- 总收入
    total_cost FLOAT DEFAULT 0,                -- 总成本
    total_profit FLOAT DEFAULT 0,              -- 总利润
    
    -- 最终分配
    shareholder_a_total FLOAT DEFAULT 0,       -- 股东A总计
    shareholder_b_total FLOAT DEFAULT 0,       -- 股东B总计
    
    status VARCHAR(20) DEFAULT 'draft',        -- 状态
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    confirmed_at DATETIME,
    notes TEXT,
    UNIQUE(year, month)
);
```

## 四、实现逻辑

### 1. 课程录入时
```python
def create_course(course_data):
    # 确定归属
    if has_employees() and course_data.get('assigned_employee_id'):
        course.attribution_type = 'employee'
        course.attribution_id = course_data['assigned_employee_id']
    else:
        course.attribution_type = 'shareholder'
        course.attribution_id = None  # 或者记录具体哪个股东
```

### 2. 月度结算时
```python
def calculate_monthly_profit(year, month):
    # 1. 获取当月所有课程
    courses = get_courses_by_month(year, month)
    
    # 2. 初始化统计数据
    shareholder_new_profit = 0
    shareholder_renewal_profit = 0
    employee_profit = 0
    
    # 3. 逐个计算每个课程的利润
    for course in courses:
        # 计算基础利润
        revenue = calculate_revenue(course)
        cost = calculate_cost(course)
        
        if course.attribution_type == 'employee':
            # 员工业务需要扣除员工成本
            employee_cost = calculate_employee_cost(course)
            profit = revenue - cost - employee_cost
            employee_profit += profit
            
            # 应用员工业务分配规则（50%/50%）
            shareholder_a_amount = profit * 0.5
            shareholder_b_amount = profit * 0.5
        else:
            # 股东直接业务
            profit = revenue - cost
            
            if course.is_renewal:
                # 续课（40%/60%）
                shareholder_renewal_profit += profit
                shareholder_a_amount = profit * 0.4
                shareholder_b_amount = profit * 0.6
            else:
                # 新课（50%/50%）
                shareholder_new_profit += profit
                shareholder_a_amount = profit * 0.5
                shareholder_b_amount = profit * 0.5
        
        # 保存明细
        save_profit_detail(course, profit, shareholder_a_amount, shareholder_b_amount)
    
    # 4. 保存月度汇总
    save_monthly_summary(year, month, totals)
```

### 3. 员工成本计算
```python
def calculate_employee_cost(course):
    """计算单个课程应分摊的员工成本"""
    employee = course.assigned_employee
    if not employee:
        return 0
    
    # 获取员工当月所有课程
    monthly_courses = get_employee_monthly_courses(employee, course.created_at)
    course_count = len(monthly_courses)
    
    # 底薪分摊（按课程数量）
    salary_per_course = employee.base_salary / course_count if course_count > 0 else 0
    
    # 该课程的提成
    commission = calculate_course_commission(course, employee)
    
    return salary_per_course + commission
```

## 五、界面设计

### 1. 利润分配规则管理
```
┌─────────────────────────────────────────┐
│ 利润分配规则设置                         │
├─────────────────────────────────────────┤
│ 当前规则：                              │
│                                         │
│ ▼ 股东直接业务                          │
│   • 新课：股东A 50% | 股东B 50%         │
│   • 续课：股东A 40% | 股东B 60%         │
│                                         │
│ ▼ 员工负责业务                          │
│   • 所有：股东A 50% | 股东B 50%         │
│                                         │
│ [添加规则] [修改规则] [查看历史]         │
└─────────────────────────────────────────┘
```

### 2. 月度利润报表
```
┌─────────────────────────────────────────┐
│ 2024年11月 利润分配报表                  │
├─────────────────────────────────────────┤
│ ▼ 股东直接业务                          │
│   新课利润：¥50,000                     │
│   - 股东A (50%)：¥25,000               │
│   - 股东B (50%)：¥25,000               │
│                                         │
│   续课利润：¥30,000                     │
│   - 股东A (40%)：¥12,000               │
│   - 股东B (60%)：¥18,000               │
│                                         │
│ ▼ 员工负责业务                          │
│   净利润：¥20,000                       │
│   - 股东A (50%)：¥10,000               │
│   - 股东B (50%)：¥10,000               │
│                                         │
│ ─────────────────────────────────────── │
│ 总计：                                  │
│   股东A：¥47,000                        │
│   股东B：¥53,000                        │
│                                         │
│ [查看明细] [导出Excel] [确认分配]        │
└─────────────────────────────────────────┘
```

### 3. 课程归属查看
```
┌─────────────────────────────────────────┐
│ 课程列表                                │
├─────────────────────────────────────────┤
│ 客户  课程  金额  归属    利润  分配     │
│ 张三  语法  5000  股东    2000  50/50   │
│ 李四  续课  8000  股东    3200  40/60   │
│ 王五  单词  6000  员工A   1500  50/50   │
└─────────────────────────────────────────┘
```

## 六、优势分析

### 1. 灵活性
- 规则可配置，适应业务变化
- 支持按时间段设置不同规则
- 员工加入后无需修改核心逻辑

### 2. 可追溯性
- 每笔业务都记录归属和分配规则
- 历史数据完整保留
- 便于审计和对账

### 3. 扩展性
- 支持多个股东
- 支持复杂的分配规则
- 可以加入更多维度（如地区、课程类型等）

### 4. 准确性
- 自动计算，减少人为错误
- 规则明确，避免争议
- 实时查看分配结果

## 七、实施步骤

### 第一步：基础实施（1-2天）
1. 创建数据库表
2. 在课程录入时添加归属选择
3. 实现基础的利润计算

### 第二步：规则管理（2-3天）
1. 开发规则配置界面
2. 实现规则应用逻辑
3. 测试不同场景

### 第三步：报表完善（2-3天）
1. 开发月度结算功能
2. 实现明细和汇总报表
3. 添加导出功能

### 第四步：优化提升（持续）
1. 添加图表展示
2. 优化性能
3. 增加更多分析维度

这个方案既满足了您当前的需求，又为未来扩展预留了空间。最重要的是，逻辑清晰、易于理解和维护。