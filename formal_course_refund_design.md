# 正课退费功能设计方案

## 一、业务需求分析

### 1.1 核心需求
- 支持正课部分退费（按节数退费）
- 退费金额按照原始售价计算
- 退费节数不能超过购买节数
- 自动重新计算该客户的利润
- 保留完整的退费记录用于审计

### 1.2 退费场景
- 学生因个人原因无法继续上课
- 教学质量问题导致的退费
- 其他特殊情况的退费

## 二、数据库设计

### 2.1 Course表扩展字段
```sql
-- 在现有Course表中添加以下字段
ALTER TABLE course ADD COLUMN refunded_sessions INTEGER DEFAULT 0;  -- 已退费节数
ALTER TABLE course ADD COLUMN refund_records TEXT;  -- 退费记录JSON
ALTER TABLE course ADD COLUMN course_status VARCHAR(20) DEFAULT 'active';  -- 课程状态：active/partial_refunded/fully_refunded
```

### 2.2 新建CourseRefund表（推荐方案）
```sql
CREATE TABLE course_refund (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    refund_sessions INTEGER NOT NULL,  -- 退费节数
    refund_amount FLOAT NOT NULL,  -- 退费金额
    refund_reason VARCHAR(200),  -- 退费原因
    refund_channel VARCHAR(50),  -- 退费渠道
    refund_fee FLOAT DEFAULT 0,  -- 退费手续费
    operator_id INTEGER,  -- 操作员ID
    operator_name VARCHAR(100),  -- 操作员姓名
    refund_date DATETIME,  -- 退费日期
    status VARCHAR(20) DEFAULT 'pending',  -- pending/completed/cancelled
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES course(id),
    FOREIGN KEY (operator_id) REFERENCES employee(id)
);
```

## 三、业务逻辑设计

### 3.1 退费规则
1. **退费节数限制**
   - 可退费节数 = 购买节数 - 已退费节数
   - 不能退赠送节数

2. **退费金额计算**
   ```python
   退费金额 = 退费节数 × 原始单价
   实际退款 = 退费金额 - 退费手续费（如有）
   ```

3. **利润重新计算**
   ```python
   # 原始利润计算
   原始收入 = 购买节数 × 单价
   原始成本 = 总成本 + 手续费
   原始利润 = 原始收入 - 原始成本
   
   # 退费后利润计算
   实际收入 = (购买节数 - 退费节数) × 单价
   实际成本 = 总成本 × (实际节数 / 原购买节数) + 手续费
   实际利润 = 实际收入 - 实际成本
   ```

### 3.2 状态管理
- **active**: 正常状态
- **partial_refunded**: 部分退费
- **fully_refunded**: 全部退费

## 四、接口设计

### 4.1 退费申请接口
```python
@main_bp.route('/api/courses/<int:course_id>/refund', methods=['POST'])
def apply_course_refund(course_id):
    """
    申请正课退费
    请求参数：
    {
        "refund_sessions": 5,  # 退费节数
        "refund_reason": "个人原因",  # 退费原因
        "refund_channel": "微信",  # 退费渠道
        "refund_fee": 0  # 手续费
    }
    """
```

### 4.2 退费记录查询接口
```python
@main_bp.route('/api/courses/<int:course_id>/refund-history', methods=['GET'])
def get_refund_history(course_id):
    """获取课程退费历史"""
```

### 4.3 退费统计接口
```python
@main_bp.route('/api/refund-statistics', methods=['GET'])
def get_refund_statistics():
    """获取退费统计数据"""
```

## 五、前端界面设计

### 5.1 正课管理页面改进
1. 在正课列表中显示退费状态标签
2. 添加"申请退费"按钮（仅对active状态的课程显示）
3. 显示剩余可退费节数

### 5.2 退费申请弹窗
```html
<!-- 退费申请表单 -->
<div class="modal" id="refundModal">
    <form id="refundForm">
        <div class="form-group">
            <label>可退费节数：<span id="refundableSessions"></span></label>
            <input type="number" name="refund_sessions" min="1" required>
        </div>
        <div class="form-group">
            <label>退费原因</label>
            <select name="refund_reason">
                <option>个人原因</option>
                <option>教学质量问题</option>
                <option>其他</option>
            </select>
        </div>
        <div class="form-group">
            <label>退费渠道</label>
            <select name="refund_channel">
                <option>原路退回</option>
                <option>微信</option>
                <option>支付宝</option>
                <option>银行转账</option>
            </select>
        </div>
        <div class="form-group">
            <label>退费金额：¥<span id="refundAmount">0.00</span></label>
        </div>
    </form>
</div>
```

### 5.3 退费历史页面
显示所有退费记录，包括退费日期、节数、金额、原因等信息。

## 六、利润报表调整

### 6.1 利润计算调整
```python
def calculate_course_profit_with_refund(course):
    """计算考虑退费后的课程利润"""
    # 获取退费记录
    refunds = CourseRefund.query.filter_by(
        course_id=course.id, 
        status='completed'
    ).all()
    
    total_refunded_sessions = sum(r.refund_sessions for r in refunds)
    total_refunded_amount = sum(r.refund_amount for r in refunds)
    
    # 实际收入 = 原始收入 - 退费金额
    actual_sessions = course.sessions - total_refunded_sessions
    actual_revenue = course.sessions * course.price - total_refunded_amount
    
    # 按比例调整成本
    cost_ratio = actual_sessions / course.sessions if course.sessions > 0 else 0
    actual_cost = course.cost * cost_ratio
    
    # 手续费保持不变（已经支付的）
    fee = 0
    if course.payment_channel == '淘宝':
        fee_rate = course.snapshot_fee_rate or 0.006
        fee = course.sessions * course.price * fee_rate
    
    # 计算实际利润
    actual_profit = actual_revenue - actual_cost - fee
    
    return {
        'original_profit': calculate_course_profit(course),
        'actual_profit': actual_profit,
        'refunded_amount': total_refunded_amount,
        'refunded_sessions': total_refunded_sessions
    }
```

### 6.2 报表显示调整
- 在利润报表中区分显示原始利润和实际利润
- 添加退费统计汇总
- 支持按退费状态筛选课程

## 七、实现步骤

### 第一阶段：基础功能
1. 创建数据库迁移脚本
2. 实现退费申请API
3. 更新利润计算逻辑
4. 添加基础UI界面

### 第二阶段：完善功能
1. 实现退费审批流程（可选）
2. 添加退费通知功能
3. 完善退费统计报表
4. 添加退费导出功能

### 第三阶段：优化提升
1. 批量退费功能
2. 退费模板管理
3. 退费预警提醒
4. 退费数据分析

## 八、注意事项

### 8.1 数据一致性
- 使用数据库事务确保退费操作的原子性
- 退费后自动更新相关统计数据

### 8.2 权限控制
- 只有特定角色可以执行退费操作
- 记录所有退费操作日志

### 8.3 财务对账
- 退费记录需要与财务系统对接
- 生成退费凭证用于财务审计

### 8.4 性能优化
- 大量退费数据时考虑分页和缓存
- 利润重算考虑异步处理

## 九、测试要点

1. **功能测试**
   - 正常退费流程
   - 边界条件（退费节数等于购买节数）
   - 异常情况处理（重复退费、超额退费）

2. **数据准确性测试**
   - 利润计算准确性
   - 统计数据一致性
   - 并发退费处理

3. **性能测试**
   - 大量退费记录查询
   - 批量利润重算

## 十、扩展考虑

1. **退费审批流程**：大额退费需要管理员审批
2. **退费限制**：设置退费时间限制（如购买后30天内）
3. **部分消费退费**：已消费部分节数后的退费计算
4. **退费原因分析**：定期分析退费原因，改进服务质量