# 退费功能实现分析报告

## 一、现有系统分析

通过对现有代码的深入分析，我发现以下关键点：

### 1.1 利润计算逻辑
- **正课利润** = 收入 - 成本 - 手续费
- **收入** = 课程节数 × 单价
- **成本** = 基础成本 + 手续费（在汇总时手续费被计入成本）
- **股东分配**：新课50/50，续课40/60

### 1.2 员工业绩计算
- 基于课程的 `assigned_employee_id` 字段
- 提成可按利润或销售额计算
- 包含试听课提成、新课提成、续课提成

### 1.3 统计报表
- 所有统计都是基于课程创建时间
- 直接从Course表计算总收入、总成本、总利润

## 二、设计方案的问题分析

### 2.1 ❌ 无缝兼容性问题

**问题1：现有统计查询不会自动包含退费数据**
```python
# 现有代码直接查询Course表
total_revenue = sum(c.sessions * c.price for c in formal_courses)
```
这种计算方式不会考虑退费，需要修改所有相关的统计逻辑。

**问题2：员工业绩计算需要调整**
```python
# 现有员工业绩计算
for course in formal_courses:
    revenue = sessions * price
    # 没有考虑退费
```

### 2.2 ❌ 利润计算的复杂性

**问题1：手续费处理**
- 原设计中手续费不退，但实际上手续费是按原始金额计算的
- 如果部分退费，手续费应该如何处理？

**问题2：成本分摊**
- 固定成本（如其他成本）是否应该按比例退还？
- 课时成本如何准确分摊？

### 2.3 ❌ 数据一致性风险

**问题1：分布式数据更新**
- 退费后需要更新Course表的refunded_sessions
- 同时需要在CourseRefund表创建记录
- 如果其中一个失败，会导致数据不一致

**问题2：并发问题**
- 多人同时申请退费可能导致超退

## 三、改进后的实现方案

### 3.1 ✅ 数据库设计优化

#### 方案A：最小侵入式（推荐）
```sql
-- 只创建退费表，不修改Course表
CREATE TABLE course_refund (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    refund_sessions INTEGER NOT NULL,
    refund_amount DECIMAL(10,2) NOT NULL,
    refund_reason VARCHAR(200),
    refund_channel VARCHAR(50),
    refund_fee DECIMAL(10,2) DEFAULT 0,
    refund_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'completed',
    operator_name VARCHAR(100),
    remark TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES course(id)
);

CREATE INDEX idx_course_refund_course_id ON course_refund(course_id);
CREATE INDEX idx_course_refund_status ON course_refund(status);
```

### 3.2 ✅ 利润计算函数改造

创建一个统一的利润计算函数，所有地方都调用它：

```python
def calculate_course_profit_with_refund(course, include_refund=True):
    """统一的课程利润计算函数"""
    # 原始计算
    sessions = safe_int(course.sessions, 0)
    price = safe_float(course.price, 0)
    revenue = sessions * price
    
    # 计算手续费（基于原始收入）
    fee = 0
    if course.payment_channel == '淘宝':
        fee_rate = course.snapshot_fee_rate if course.snapshot_fee_rate else 0.006
        fee = revenue * fee_rate
    
    # 原始成本
    cost = safe_float(course.cost, 0)
    
    if include_refund:
        # 获取退费记录
        refunds = CourseRefund.query.filter_by(
            course_id=course.id,
            status='completed'
        ).all()
        
        if refunds:
            total_refunded_sessions = sum(r.refund_sessions for r in refunds)
            total_refunded_amount = sum(r.refund_amount for r in refunds)
            
            # 实际收入 = 原始收入 - 退费金额
            actual_revenue = revenue - total_refunded_amount
            
            # 成本按比例调整（不包括手续费）
            actual_sessions = sessions - total_refunded_sessions
            if sessions > 0:
                # 分离固定成本和变动成本
                other_cost = safe_float(course.other_cost, 0)  # 固定成本
                course_cost = cost - other_cost  # 变动成本
                
                # 变动成本按比例，固定成本不变
                actual_cost = (course_cost * actual_sessions / sessions) + other_cost
            else:
                actual_cost = cost  # 全部退费时保留成本
            
            # 利润 = 实际收入 - 实际成本 - 手续费（手续费不退）
            profit = actual_revenue - actual_cost - fee
            
            return {
                'revenue': actual_revenue,
                'cost': actual_cost + fee,  # 为了兼容现有逻辑，成本包含手续费
                'profit': profit,
                'has_refund': True,
                'refund_info': {
                    'sessions': total_refunded_sessions,
                    'amount': total_refunded_amount
                }
            }
        else:
            # 没有退费，返回原始数据
            return {
                'revenue': revenue,
                'cost': cost + fee,
                'profit': revenue - cost - fee,
                'has_refund': False
            }
    else:
        # 不考虑退费的原始计算
        return {
            'revenue': revenue,
            'cost': cost + fee,
            'profit': revenue - cost - fee,
            'has_refund': False
        }
```

### 3.3 ✅ 修改现有统计逻辑

#### 1. 利润报表 (`get_profit_report`)
```python
# 修改循环中的计算逻辑
for course in new_courses:
    profit_info = calculate_course_profit_with_refund(course)
    
    revenue = profit_info['revenue']
    cost = profit_info['cost']
    profit = profit_info['profit']
    
    new_course_profit_total += profit
    
    shareholder_a = profit * profit_config['new_course_shareholder_a'] / 100
    shareholder_b = profit * profit_config['new_course_shareholder_b'] / 100
    
    new_course_data.append({
        'customer_name': course.customer.name,
        'course_type': course.course_type,
        'revenue': revenue,
        'cost': cost,
        'profit': profit,
        'has_refund': profit_info['has_refund'],
        'shareholder_a': shareholder_a,
        'shareholder_b': shareholder_b,
        'date': course.created_at.strftime('%Y-%m-%d')
    })
```

#### 2. 员工业绩 (`get_employee_performance`)
```python
# 修改正课提成计算
for course in formal_courses:
    profit_info = calculate_course_profit_with_refund(course)
    
    if config.commission_type == 'profit':
        base_amount = profit_info['profit']
    else:
        base_amount = profit_info['revenue']
    
    # 根据课程类型计算提成
    if course.is_renewal:
        renewal_commission += base_amount * (config.renewal_rate / 100)
    else:
        new_course_commission += base_amount * (config.new_course_rate / 100)
```

#### 3. 正课统计 (`api_formal_courses_stats`)
```python
for course in courses:
    profit_info = calculate_course_profit_with_refund(course)
    
    revenue = profit_info['revenue']
    cost = profit_info['cost']
    profit = profit_info['profit']
    
    # 累加统计
    total_revenue += revenue
    total_cost += cost
    total_profit += profit
```

### 3.4 ✅ 退费API实现

```python
@main_bp.route('/api/courses/<int:course_id>/refund', methods=['POST'])
def apply_course_refund(course_id):
    """申请正课退费"""
    try:
        # 获取课程
        course = Course.query.get(course_id)
        if not course or course.is_trial:
            return jsonify({'success': False, 'message': '课程不存在或不是正课'}), 404
        
        # 获取请求数据
        data = request.get_json()
        refund_sessions = int(data.get('refund_sessions', 0))
        refund_reason = data.get('refund_reason', '')
        refund_channel = data.get('refund_channel', '原路退回')
        refund_fee = float(data.get('refund_fee', 0))
        remark = data.get('remark', '')
        
        # 验证退费节数
        existing_refunds = CourseRefund.query.filter_by(
            course_id=course_id,
            status='completed'
        ).all()
        
        total_refunded = sum(r.refund_sessions for r in existing_refunds)
        refundable_sessions = course.sessions - total_refunded
        
        if refund_sessions <= 0 or refund_sessions > refundable_sessions:
            return jsonify({
                'success': False, 
                'message': f'退费节数无效，可退费节数为{refundable_sessions}'
            }), 400
        
        # 计算退费金额
        refund_amount = refund_sessions * course.price
        
        # 使用数据库事务
        try:
            # 创建退费记录
            refund = CourseRefund(
                course_id=course_id,
                refund_sessions=refund_sessions,
                refund_amount=refund_amount,
                refund_reason=refund_reason,
                refund_channel=refund_channel,
                refund_fee=refund_fee,
                refund_date=datetime.now(),
                status='completed',
                operator_name=session.get('user_name', 'System'),
                remark=remark
            )
            
            db.session.add(refund)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': {
                    'refund_id': refund.id,
                    'refund_amount': refund_amount,
                    'actual_refund': refund_amount - refund_fee,
                    'remaining_sessions': refundable_sessions - refund_sessions
                }
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': '数据库操作失败'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
```

### 3.5 ✅ 前端集成

在正课管理页面添加退费按钮：

```javascript
// 修改操作按钮组，添加退费按钮
function addRefundButton(courseId, refundableSessions) {
    if (refundableSessions > 0) {
        return `
            <button onclick="showRefundModal(${courseId})" 
                    class="btn btn-sm btn-outline-warning action-btn" 
                    title="申请退费">
                <i class="fas fa-undo"></i>
                <span class="btn-text">退费</span>
            </button>
        `;
    }
    return '';
}
```

## 四、实施建议

### 4.1 分阶段实施

**第一阶段：基础退费功能**
1. 创建CourseRefund表
2. 实现退费API
3. 添加退费界面
4. 测试基本退费流程

**第二阶段：统计集成**
1. 修改利润计算函数
2. 更新所有统计接口
3. 测试数据准确性

**第三阶段：完善功能**
1. 添加退费历史查询
2. 实现退费统计报表
3. 优化用户体验

### 4.2 关键测试点

1. **退费计算准确性**
   - 部分退费的利润计算
   - 全额退费的处理
   - 多次退费的累计

2. **统计数据一致性**
   - 总收入 = Σ(原始收入 - 退费金额)
   - 总成本 = Σ(调整后成本 + 手续费)
   - 总利润 = 总收入 - 总成本

3. **员工业绩准确性**
   - 退费后的提成调整
   - 利润型和销售型提成的不同处理

4. **并发安全性**
   - 多人同时退费
   - 退费金额超限检查

## 五、风险与对策

### 5.1 技术风险
- **风险**：修改核心利润计算可能影响现有功能
- **对策**：使用参数控制是否包含退费，逐步迁移

### 5.2 业务风险
- **风险**：退费规则可能随业务变化
- **对策**：将规则参数化，便于调整

### 5.3 数据风险
- **风险**：历史数据的退费处理
- **对策**：只对新数据应用退费功能，历史数据保持不变

## 六、结论

经过深入分析，原设计方案存在以下主要问题：

1. **无法无缝兼容**：需要修改多处核心计算逻辑
2. **成本分摊复杂**：固定成本和变动成本的处理需要明确
3. **手续费处理**：已支付的手续费不应退还

**改进后的方案**：
1. 使用最小侵入式设计，只增加退费表
2. 创建统一的利润计算函数，包含退费逻辑
3. 分阶段实施，确保系统稳定性
4. 充分测试各种场景，确保数据准确性

这样可以在保证现有功能正常的前提下，逐步添加退费功能。