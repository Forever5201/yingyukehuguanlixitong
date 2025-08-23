# 股东利润分配系统设计方案

## 一、数据库设计

### 1. 新增支出管理表 (expense)

```sql
CREATE TABLE expense (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_type VARCHAR(50) NOT NULL,  -- 支出类型：salary/rent/utility/marketing/other
    category VARCHAR(50),               -- 细分类别
    amount FLOAT NOT NULL,              -- 金额
    description TEXT,                   -- 说明
    expense_date DATE NOT NULL,         -- 支出日期
    employee_id INTEGER,                -- 相关员工（如果是薪资）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,                 -- 创建人
    FOREIGN KEY (employee_id) REFERENCES employee(id)
);
```

### 2. 扩展员工表 (employee) - 添加薪资信息

```sql
ALTER TABLE employee ADD COLUMN base_salary FLOAT DEFAULT 0;  -- 底薪
ALTER TABLE employee ADD COLUMN salary_start_date DATE;        -- 入职日期
ALTER TABLE employee ADD COLUMN is_active BOOLEAN DEFAULT TRUE; -- 是否在职
```

### 3. 新增月度结算表 (monthly_settlement)

```sql
CREATE TABLE monthly_settlement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    -- 收入部分
    trial_revenue FLOAT DEFAULT 0,      -- 试听课收入
    course_revenue FLOAT DEFAULT 0,     -- 正课收入
    renewal_revenue FLOAT DEFAULT 0,    -- 续课收入
    other_revenue FLOAT DEFAULT 0,      -- 其他收入
    -- 成本部分
    course_cost FLOAT DEFAULT 0,        -- 课程成本
    payment_fee FLOAT DEFAULT 0,        -- 支付手续费
    -- 人力成本
    total_salary FLOAT DEFAULT 0,       -- 底薪总额
    total_commission FLOAT DEFAULT 0,   -- 提成总额
    -- 运营支出
    rent_expense FLOAT DEFAULT 0,       -- 房租
    utility_expense FLOAT DEFAULT 0,    -- 水电费
    marketing_expense FLOAT DEFAULT 0,  -- 营销费用
    other_expense FLOAT DEFAULT 0,      -- 其他支出
    -- 利润计算
    gross_profit FLOAT DEFAULT 0,       -- 毛利润
    net_profit FLOAT DEFAULT 0,         -- 净利润
    -- 分配信息
    shareholder_a_ratio FLOAT,          -- 股东A分配比例
    shareholder_b_ratio FLOAT,          -- 股东B分配比例
    shareholder_a_amount FLOAT,         -- 股东A分配金额
    shareholder_b_amount FLOAT,         -- 股东B分配金额
    reserve_amount FLOAT DEFAULT 0,     -- 预留资金
    -- 状态
    status VARCHAR(20) DEFAULT 'draft', -- draft/confirmed/distributed
    settled_at DATETIME,                -- 结算时间
    distributed_at DATETIME,            -- 分配时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,                         -- 备注
    UNIQUE(year, month)
);
```

### 4. 新增支出类别配置表 (expense_category)

```sql
CREATE TABLE expense_category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type VARCHAR(50) NOT NULL,          -- salary/rent/utility/marketing/other
    name VARCHAR(100) NOT NULL,         -- 类别名称
    description TEXT,                   -- 说明
    is_active BOOLEAN DEFAULT TRUE,     -- 是否启用
    sort_order INTEGER DEFAULT 0        -- 排序
);
```

## 二、功能设计

### 1. 支出管理模块

#### 功能列表：
- **日常支出录入**：记录各类运营支出
- **批量导入**：支持Excel导入支出记录
- **支出统计**：按类别、时间统计支出
- **支出审核**：支出录入后需要审核确认

#### 页面设计：
```
/expenses              - 支出管理主页
/api/expenses          - 支出CRUD接口
/api/expenses/import   - 批量导入接口
/api/expenses/stats    - 统计接口
```

### 2. 员工成本管理

#### 功能列表：
- **底薪设置**：在员工管理页面设置底薪
- **提成计算**：自动计算每月提成
- **薪资发放**：记录实际发放情况
- **成本统计**：统计人力成本占比

### 3. 月度结算模块

#### 功能列表：
- **自动汇总**：每月自动汇总所有收入和支出
- **手动调整**：支持手动调整特殊项目
- **利润计算**：自动计算各级利润
- **分配方案**：根据配置计算股东分配
- **结算确认**：需要股东确认后才能分配

#### 页面设计：
```
/monthly-settlement           - 月度结算主页
/api/monthly-settlement       - 结算数据接口
/api/monthly-settlement/calc  - 自动计算接口
/api/monthly-settlement/confirm - 确认结算
```

### 4. 利润分配优化

#### 新的分配规则：
1. **基础分配比例**：可按不同业务类型设置
2. **业绩奖励**：超过目标利润可以有额外分配
3. **预留资金**：可设置每月预留比例用于发展
4. **分配时机**：可选择月度/季度/年度分配

## 三、实现步骤

### 第一阶段：基础架构
1. 创建数据库表
2. 实现支出管理CRUD
3. 更新员工管理加入薪资信息

### 第二阶段：成本计算
1. 实现员工成本自动计算
2. 整合各类支出统计
3. 优化利润计算公式

### 第三阶段：结算系统
1. 实现月度自动结算
2. 开发结算审核流程
3. 完善分配方案管理

### 第四阶段：报表优化
1. 开发综合利润报表
2. 添加成本分析图表
3. 实现数据导出功能

## 四、界面设计示例

### 1. 支出管理界面
```
┌─────────────────────────────────────┐
│ 支出管理                             │
├─────────────────────────────────────┤
│ [添加支出] [批量导入] [导出报表]      │
│                                     │
│ 筛选: [支出类型▼] [日期范围] [搜索] │
│                                     │
│ ┌───┬────┬────┬────┬────┬────┐   │
│ │类型│金额 │说明 │日期 │状态│操作│   │
│ ├───┼────┼────┼────┼────┼────┤   │
│ │房租│8000│11月 │11/1│已审│编辑│   │
│ │水电│1200│11月 │11/5│待审│审核│   │
│ └───┴────┴────┴────┴────┴────┘   │
└─────────────────────────────────────┘
```

### 2. 月度结算界面
```
┌─────────────────────────────────────┐
│ 2024年11月 结算报表                  │
├─────────────────────────────────────┤
│ 收入明细                收入金额     │
│ ├─ 试听课收入          ¥12,000      │
│ ├─ 正课收入            ¥85,000      │
│ └─ 续课收入            ¥32,000      │
│ 总收入                 ¥129,000     │
│                                     │
│ 成本明细                成本金额     │
│ ├─ 课程成本            ¥25,000      │
│ ├─ 支付手续费          ¥1,200       │
│ ├─ 员工底薪            ¥35,000      │
│ ├─ 员工提成            ¥18,000      │
│ ├─ 房租水电            ¥9,200       │
│ └─ 其他支出            ¥5,600       │
│ 总成本                 ¥94,000      │
│                                     │
│ 净利润                 ¥35,000      │
│                                     │
│ 股东分配方案                         │
│ ├─ 股东A (60%)         ¥21,000      │
│ └─ 股东B (40%)         ¥14,000      │
│                                     │
│ [确认结算] [导出报表] [调整数据]      │
└─────────────────────────────────────┘
```

## 五、配置参数扩展

新增配置项：
- `reserve_ratio` - 利润预留比例（如10%）
- `min_distribution_amount` - 最低分配金额
- `distribution_cycle` - 分配周期（月/季/年）
- `auto_calculate_day` - 自动结算日（每月几号）

## 六、注意事项

1. **数据准确性**：支出录入需要严格审核
2. **权限控制**：只有管理员能查看利润分配
3. **审计追踪**：所有修改需要记录日志
4. **备份机制**：结算数据需要定期备份
5. **法律合规**：分配方案需要符合公司章程

## 七、预期效果

实施后可以：
- 准确计算真实净利润
- 合理分配股东收益
- 掌握成本结构
- 优化运营效率
- 支持业务决策