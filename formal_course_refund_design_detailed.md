# 正课退费功能详细设计方案

## 一、背景与需求分析

### 1.1 业务背景
在客户管理系统中，部分学员在购买正课后，由于各种原因（如时间冲突、教学质量、个人原因等）需要申请退费。系统需要支持灵活的退费管理，同时确保财务数据的准确性和完整性。

### 1.2 核心需求
1. **退费管理**
   - 支持按节数进行部分退费
   - 退费金额按照原始售价计算
   - 退费节数不能超过剩余未消耗节数
   - 支持多次部分退费

2. **财务影响**
   - 自动重新计算课程实际利润
   - 更新股东利润分配数据
   - 保持财务数据的一致性和可追溯性

3. **数据完整性**
   - 保留完整的退费历史记录
   - 不修改原始课程数据
   - 支持退费审计和统计分析

### 1.3 约束条件
- 已退费的节数不能再次退费
- 赠送的课时不参与退费
- 退费后需要重新计算员工提成（如有）
- 退费操作需要记录操作人员和时间

## 二、数据库设计

### 2.1 新增CourseRefund表
```sql
CREATE TABLE course_refund (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,                    -- 关联的课程ID
    refund_sessions INTEGER NOT NULL,              -- 退费节数
    refund_amount DECIMAL(10,2) NOT NULL,          -- 退费金额
    refund_reason VARCHAR(200),                    -- 退费原因
    refund_type VARCHAR(50) DEFAULT 'partial',     -- 退费类型：partial/full
    refund_channel VARCHAR(50),                    -- 退费渠道：原路退回/微信/支付宝/银行转账
    refund_fee DECIMAL(10,2) DEFAULT 0,            -- 退费手续费
    actual_refund_amount DECIMAL(10,2),            -- 实际退款金额（扣除手续费后）
    operator_id INTEGER,                           -- 操作员ID
    operator_name VARCHAR(100),                    -- 操作员姓名
    refund_date DATETIME,                          -- 退费日期
    status VARCHAR(20) DEFAULT 'pending',          -- 状态：pending/approved/completed/cancelled
    approved_by INTEGER,                           -- 审批人ID（如需审批）
    approved_at DATETIME,                          -- 审批时间
    completed_at DATETIME,                         -- 完成时间
    remark TEXT,                                   -- 备注
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES course(id),
    FOREIGN KEY (operator_id) REFERENCES employee(id),
    FOREIGN KEY (approved_by) REFERENCES employee(id)
);

-- 创建索引以优化查询性能
CREATE INDEX idx_course_refund_course_id ON course_refund(course_id);
CREATE INDEX idx_course_refund_status ON course_refund(status);
CREATE INDEX idx_course_refund_refund_date ON course_refund(refund_date);
```

### 2.2 Course表扩展字段
```sql
-- 在Course表中添加退费相关字段
ALTER TABLE course ADD COLUMN refunded_sessions INTEGER DEFAULT 0;        -- 已退费节数
ALTER TABLE course ADD COLUMN refund_status VARCHAR(20) DEFAULT 'none';   -- 退费状态：none/partial/full
ALTER TABLE course ADD COLUMN last_refund_date DATETIME;                  -- 最后退费时间
```

### 2.3 数据关系图
```
Course (1) -----> (N) CourseRefund
   |
   |---> refunded_sessions (汇总)
   |---> refund_status
   |---> last_refund_date
```

## 三、业务逻辑设计

### 3.1 退费规则引擎

#### 3.1.1 可退费节数计算
```python
def calculate_refundable_sessions(course):
    """计算可退费节数"""
    # 购买的节数（不含赠送）
    purchased_sessions = course.sessions
    
    # 已退费节数
    refunded_sessions = course.refunded_sessions or 0
    
    # 已消耗节数（如果系统有课时消耗记录）
    consumed_sessions = get_consumed_sessions(course.id)  # 需要实现
    
    # 可退费节数 = 购买节数 - 已退费节数 - 已消耗节数
    refundable = purchased_sessions - refunded_sessions - consumed_sessions
    
    return max(0, refundable)
```

#### 3.1.2 退费金额计算
```python
def calculate_refund_amount(course, refund_sessions):
    """计算退费金额"""
    # 原始单价
    unit_price = course.price
    
    # 退费金额 = 退费节数 × 原始单价
    refund_amount = refund_sessions * unit_price
    
    # 如果有优惠，需要按比例计算
    if course.meta:
        meta_data = json.loads(course.meta)
        discount_rate = meta_data.get('discount_rate', 1.0)
        refund_amount = refund_amount * discount_rate
    
    return refund_amount
```

#### 3.1.3 利润重新计算
```python
def recalculate_course_profit(course):
    """重新计算考虑退费后的课程利润"""
    # 获取所有已完成的退费记录
    refunds = CourseRefund.query.filter_by(
        course_id=course.id,
        status='completed'
    ).all()
    
    # 计算退费汇总
    total_refunded_sessions = sum(r.refund_sessions for r in refunds)
    total_refunded_amount = sum(r.refund_amount for r in refunds)
    
    # 实际收入 = 原始收入 - 退费金额
    original_revenue = course.sessions * course.price
    actual_revenue = original_revenue - total_refunded_amount
    
    # 实际节数
    actual_sessions = course.sessions - total_refunded_sessions
    
    # 成本调整策略
    if actual_sessions > 0:
        # 策略1：按比例调整成本
        cost_ratio = actual_sessions / course.sessions
        actual_cost = course.cost * cost_ratio
        
        # 策略2：固定成本不变，只调整变动成本
        # fixed_cost = course.other_cost or 0
        # variable_cost = (course.cost - fixed_cost) * cost_ratio
        # actual_cost = fixed_cost + variable_cost
    else:
        actual_cost = 0
    
    # 手续费（已支付的不退）
    fee = 0
    if course.payment_channel == '淘宝':
        fee_rate = course.snapshot_fee_rate or 0.006
        fee = original_revenue * fee_rate
    
    # 实际利润
    actual_profit = actual_revenue - actual_cost - fee
    
    return {
        'original_revenue': original_revenue,
        'actual_revenue': actual_revenue,
        'original_cost': course.cost,
        'actual_cost': actual_cost,
        'fee': fee,
        'original_profit': original_revenue - course.cost - fee,
        'actual_profit': actual_profit,
        'refunded_amount': total_refunded_amount,
        'refunded_sessions': total_refunded_sessions
    }
```

### 3.2 退费流程设计

#### 3.2.1 退费申请流程
```
1. 用户发起退费申请
   ↓
2. 系统验证退费条件
   - 检查可退费节数
   - 计算退费金额
   ↓
3. 创建退费记录（pending状态）
   ↓
4. [可选] 审批流程
   - 小额自动审批
   - 大额人工审批
   ↓
5. 执行退费
   - 更新退费记录状态
   - 更新课程退费信息
   - 记录操作日志
   ↓
6. 财务处理
   - 实际退款操作
   - 更新利润数据
   - 通知相关人员
```

#### 3.2.2 状态机设计
```
pending（待处理）
    ↓ approve
approved（已审批）
    ↓ complete
completed（已完成）
    
pending/approved
    ↓ cancel
cancelled（已取消）
```

## 四、API接口设计

### 4.1 退费相关接口

#### 4.1.1 检查可退费信息
```python
@main_bp.route('/api/courses/<int:course_id>/refund-info', methods=['GET'])
def get_refund_info(course_id):
    """
    获取课程的可退费信息
    
    返回：
    {
        "success": true,
        "data": {
            "course_id": 123,
            "customer_name": "张三",
            "course_type": "一对一",
            "purchased_sessions": 20,
            "refunded_sessions": 0,
            "consumed_sessions": 5,
            "refundable_sessions": 15,
            "unit_price": 200.00,
            "max_refund_amount": 3000.00,
            "refund_history": []
        }
    }
    """
```

#### 4.1.2 申请退费
```python
@main_bp.route('/api/courses/<int:course_id>/refund', methods=['POST'])
def apply_course_refund(course_id):
    """
    申请正课退费
    
    请求参数：
    {
        "refund_sessions": 5,           # 退费节数
        "refund_reason": "个人原因",    # 退费原因
        "refund_channel": "原路退回",   # 退费渠道
        "refund_fee": 0,               # 手续费
        "remark": "学生出国留学"        # 备注
    }
    
    返回：
    {
        "success": true,
        "data": {
            "refund_id": 456,
            "refund_amount": 1000.00,
            "status": "pending"
        }
    }
    """
```

#### 4.1.3 退费审批（可选）
```python
@main_bp.route('/api/refunds/<int:refund_id>/approve', methods=['POST'])
def approve_refund(refund_id):
    """审批退费申请"""
```

#### 4.1.4 完成退费
```python
@main_bp.route('/api/refunds/<int:refund_id>/complete', methods=['POST'])
def complete_refund(refund_id):
    """完成退费（财务确认）"""
```

#### 4.1.5 取消退费
```python
@main_bp.route('/api/refunds/<int:refund_id>/cancel', methods=['POST'])
def cancel_refund(refund_id):
    """取消退费申请"""
```

#### 4.1.6 查询退费历史
```python
@main_bp.route('/api/courses/<int:course_id>/refund-history', methods=['GET'])
def get_refund_history(course_id):
    """获取课程的退费历史"""
```

#### 4.1.7 退费统计
```python
@main_bp.route('/api/refund-statistics', methods=['GET'])
def get_refund_statistics():
    """
    获取退费统计数据
    
    参数：
    - start_date: 开始日期
    - end_date: 结束日期
    - group_by: month/quarter/year
    """
```

## 五、前端界面设计

### 5.1 正课管理页面改进

#### 5.1.1 列表页面增强
在现有的正课列表中添加：
1. 退费状态标识（使用不同颜色的标签）
2. 剩余可退费节数显示
3. 退费操作按钮（根据状态显示）

```html
<!-- 在操作按钮组中添加退费按钮 -->
<button onclick="showRefundModal({{ course.id }})" 
        class="btn btn-sm btn-outline-warning action-btn" 
        title="申请退费"
        {% if course.refundable_sessions <= 0 %}disabled{% endif %}>
    <i class="fas fa-undo"></i>
    <span class="btn-text">退费</span>
</button>

<!-- 退费状态标签 -->
{% if course.refund_status == 'partial' %}
    <span class="badge badge-warning">部分退费</span>
{% elif course.refund_status == 'full' %}
    <span class="badge badge-danger">全额退费</span>
{% endif %}
```

#### 5.1.2 退费申请模态框
```html
<div id="refundModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h2>申请退费</h2>
            <span class="close">&times;</span>
        </div>
        
        <div class="modal-body">
            <!-- 课程信息展示 -->
            <div class="refund-info-section">
                <h3>课程信息</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <label>学员姓名：</label>
                        <span id="refund_customer_name"></span>
                    </div>
                    <div class="info-item">
                        <label>课程类型：</label>
                        <span id="refund_course_type"></span>
                    </div>
                    <div class="info-item">
                        <label>购买节数：</label>
                        <span id="refund_purchased_sessions"></span>
                    </div>
                    <div class="info-item">
                        <label>已退费节数：</label>
                        <span id="refund_refunded_sessions"></span>
                    </div>
                    <div class="info-item">
                        <label>可退费节数：</label>
                        <span id="refund_refundable_sessions" class="highlight"></span>
                    </div>
                    <div class="info-item">
                        <label>单节价格：</label>
                        <span id="refund_unit_price"></span>
                    </div>
                </div>
            </div>
            
            <!-- 退费表单 -->
            <form id="refundForm">
                <input type="hidden" id="refund_course_id" name="course_id">
                
                <div class="form-group">
                    <label for="refund_sessions">退费节数 *</label>
                    <input type="number" 
                           id="refund_sessions" 
                           name="refund_sessions" 
                           min="1" 
                           required
                           onchange="calculateRefundAmount()">
                    <small class="form-text">请输入要退费的节数</small>
                </div>
                
                <div class="form-group">
                    <label for="refund_reason">退费原因 *</label>
                    <select id="refund_reason" name="refund_reason" required>
                        <option value="">请选择退费原因</option>
                        <option value="个人原因">个人原因</option>
                        <option value="时间冲突">时间冲突</option>
                        <option value="教学质量">教学质量问题</option>
                        <option value="搬家">搬家/地址变更</option>
                        <option value="经济原因">经济原因</option>
                        <option value="其他">其他原因</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="refund_channel">退费渠道 *</label>
                    <select id="refund_channel" name="refund_channel" required>
                        <option value="原路退回">原路退回</option>
                        <option value="微信">微信转账</option>
                        <option value="支付宝">支付宝转账</option>
                        <option value="银行转账">银行转账</option>
                        <option value="现金">现金退款</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="refund_fee">手续费</label>
                    <input type="number" 
                           id="refund_fee" 
                           name="refund_fee" 
                           step="0.01" 
                           min="0" 
                           value="0"
                           onchange="calculateRefundAmount()">
                    <small class="form-text">如有手续费请填写</small>
                </div>
                
                <div class="form-group">
                    <label for="refund_remark">备注说明</label>
                    <textarea id="refund_remark" 
                              name="remark" 
                              rows="3" 
                              placeholder="请填写详细的退费说明..."></textarea>
                </div>
                
                <!-- 退费金额计算展示 -->
                <div class="refund-calculation">
                    <h4>退费金额计算</h4>
                    <div class="calculation-item">
                        <span>退费节数：</span>
                        <span id="calc_sessions">0</span> 节
                    </div>
                    <div class="calculation-item">
                        <span>单节价格：</span>
                        <span id="calc_unit_price">¥0.00</span>
                    </div>
                    <div class="calculation-item">
                        <span>退费金额：</span>
                        <span id="calc_refund_amount">¥0.00</span>
                    </div>
                    <div class="calculation-item">
                        <span>手续费：</span>
                        <span id="calc_fee">¥0.00</span>
                    </div>
                    <div class="calculation-item total">
                        <span>实际退款：</span>
                        <span id="calc_actual_amount">¥0.00</span>
                    </div>
                </div>
            </form>
        </div>
        
        <div class="modal-footer">
            <button type="button" class="btn btn-secondary" onclick="closeRefundModal()">取消</button>
            <button type="button" class="btn btn-warning" onclick="submitRefund()">提交退费申请</button>
        </div>
    </div>
</div>
```

### 5.2 退费历史页面

```html
<div class="refund-history-section">
    <h3>退费历史记录</h3>
    <table class="table">
        <thead>
            <tr>
                <th>退费日期</th>
                <th>退费节数</th>
                <th>退费金额</th>
                <th>退费原因</th>
                <th>退费渠道</th>
                <th>状态</th>
                <th>操作员</th>
                <th>操作</th>
            </tr>
        </thead>
        <tbody id="refundHistoryBody">
            <!-- 动态加载退费记录 -->
        </tbody>
    </table>
</div>
```

### 5.3 退费统计仪表板

```html
<div class="refund-dashboard">
    <div class="stat-cards">
        <div class="stat-card">
            <h4>本月退费总额</h4>
            <p class="stat-value">¥<span id="monthly_refund_amount">0.00</span></p>
        </div>
        <div class="stat-card">
            <h4>本月退费笔数</h4>
            <p class="stat-value"><span id="monthly_refund_count">0</span></p>
        </div>
        <div class="stat-card">
            <h4>退费率</h4>
            <p class="stat-value"><span id="refund_rate">0.00</span>%</p>
        </div>
    </div>
    
    <!-- 退费趋势图表 -->
    <div class="chart-container">
        <canvas id="refundTrendChart"></canvas>
    </div>
</div>
```

## 六、JavaScript实现

### 6.1 退费相关函数

```javascript
// 显示退费模态框
function showRefundModal(courseId) {
    // 先获取课程的退费信息
    fetch(`/api/courses/${courseId}/refund-info`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const info = data.data;
                
                // 填充课程信息
                document.getElementById('refund_course_id').value = courseId;
                document.getElementById('refund_customer_name').textContent = info.customer_name;
                document.getElementById('refund_course_type').textContent = info.course_type;
                document.getElementById('refund_purchased_sessions').textContent = info.purchased_sessions;
                document.getElementById('refund_refunded_sessions').textContent = info.refunded_sessions;
                document.getElementById('refund_refundable_sessions').textContent = info.refundable_sessions;
                document.getElementById('refund_unit_price').textContent = `¥${info.unit_price.toFixed(2)}`;
                
                // 设置最大可退费节数
                document.getElementById('refund_sessions').max = info.refundable_sessions;
                
                // 保存单价供计算使用
                window.currentRefundUnitPrice = info.unit_price;
                
                // 显示模态框
                document.getElementById('refundModal').style.display = 'flex';
            } else {
                alert('获取退费信息失败：' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('获取退费信息失败');
        });
}

// 计算退费金额
function calculateRefundAmount() {
    const sessions = parseInt(document.getElementById('refund_sessions').value) || 0;
    const fee = parseFloat(document.getElementById('refund_fee').value) || 0;
    const unitPrice = window.currentRefundUnitPrice || 0;
    
    const refundAmount = sessions * unitPrice;
    const actualAmount = refundAmount - fee;
    
    // 更新显示
    document.getElementById('calc_sessions').textContent = sessions;
    document.getElementById('calc_unit_price').textContent = `¥${unitPrice.toFixed(2)}`;
    document.getElementById('calc_refund_amount').textContent = `¥${refundAmount.toFixed(2)}`;
    document.getElementById('calc_fee').textContent = `¥${fee.toFixed(2)}`;
    document.getElementById('calc_actual_amount').textContent = `¥${actualAmount.toFixed(2)}`;
}

// 提交退费申请
function submitRefund() {
    const form = document.getElementById('refundForm');
    const formData = new FormData(form);
    
    // 验证表单
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // 构建请求数据
    const data = {
        refund_sessions: parseInt(formData.get('refund_sessions')),
        refund_reason: formData.get('refund_reason'),
        refund_channel: formData.get('refund_channel'),
        refund_fee: parseFloat(formData.get('refund_fee')) || 0,
        remark: formData.get('remark')
    };
    
    const courseId = formData.get('course_id');
    
    // 确认退费
    const refundAmount = data.refund_sessions * window.currentRefundUnitPrice;
    const actualAmount = refundAmount - data.refund_fee;
    
    if (!confirm(`确认要退费 ${data.refund_sessions} 节课吗？\n退费金额：¥${refundAmount.toFixed(2)}\n实际退款：¥${actualAmount.toFixed(2)}`)) {
        return;
    }
    
    // 提交退费申请
    fetch(`/api/courses/${courseId}/refund`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('退费申请提交成功！');
            closeRefundModal();
            location.reload(); // 刷新页面
        } else {
            alert('退费申请失败：' + result.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('提交退费申请时发生错误');
    });
}

// 关闭退费模态框
function closeRefundModal() {
    document.getElementById('refundModal').style.display = 'none';
    document.getElementById('refundForm').reset();
}

// 加载退费历史
function loadRefundHistory(courseId) {
    fetch(`/api/courses/${courseId}/refund-history`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const tbody = document.getElementById('refundHistoryBody');
                tbody.innerHTML = '';
                
                data.refunds.forEach(refund => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${new Date(refund.refund_date).toLocaleDateString('zh-CN')}</td>
                        <td>${refund.refund_sessions}</td>
                        <td>¥${refund.refund_amount.toFixed(2)}</td>
                        <td>${refund.refund_reason}</td>
                        <td>${refund.refund_channel}</td>
                        <td>${getRefundStatusBadge(refund.status)}</td>
                        <td>${refund.operator_name}</td>
                        <td>${getRefundActions(refund)}</td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        })
        .catch(error => {
            console.error('Error loading refund history:', error);
        });
}

// 获取退费状态标签
function getRefundStatusBadge(status) {
    const badges = {
        'pending': '<span class="badge badge-warning">待处理</span>',
        'approved': '<span class="badge badge-info">已审批</span>',
        'completed': '<span class="badge badge-success">已完成</span>',
        'cancelled': '<span class="badge badge-secondary">已取消</span>'
    };
    return badges[status] || status;
}

// 获取退费操作按钮
function getRefundActions(refund) {
    if (refund.status === 'pending') {
        return `
            <button onclick="completeRefund(${refund.id})" class="btn btn-sm btn-success">完成</button>
            <button onclick="cancelRefund(${refund.id})" class="btn btn-sm btn-danger">取消</button>
        `;
    }
    return '-';
}
```

## 七、利润报表调整

### 7.1 修改利润计算逻辑

在 `app/routes.py` 中修改 `get_profit_report` 函数：

```python
def calculate_course_profit_with_refund(course):
    """计算考虑退费后的课程利润"""
    # 获取退费记录
    refunds = CourseRefund.query.filter_by(
        course_id=course.id,
        status='completed'
    ).all()
    
    # 计算退费汇总
    total_refunded_sessions = sum(r.refund_sessions for r in refunds)
    total_refunded_amount = sum(r.refund_amount for r in refunds)
    
    # 原始数据
    sessions = safe_int(course.sessions, 0)
    price = safe_float(course.price, 0)
    original_revenue = sessions * price
    
    # 实际收入（扣除退费）
    actual_revenue = original_revenue - total_refunded_amount
    
    # 计算手续费（基于原始收入）
    fee = 0
    if course.payment_channel == '淘宝':
        fee_rate = course.snapshot_fee_rate if course.snapshot_fee_rate else 0.006
        fee = original_revenue * fee_rate
    
    # 成本计算（按比例调整）
    original_cost = safe_float(course.cost, 0)
    if sessions > 0 and total_refunded_sessions < sessions:
        cost_ratio = (sessions - total_refunded_sessions) / sessions
        actual_cost = original_cost * cost_ratio
    else:
        actual_cost = 0
    
    # 实际利润
    actual_profit = actual_revenue - actual_cost - fee
    
    return {
        'original_profit': original_revenue - original_cost - fee,
        'actual_profit': actual_profit,
        'has_refund': len(refunds) > 0,
        'refund_amount': total_refunded_amount,
        'refund_sessions': total_refunded_sessions
    }
```

### 7.2 报表展示调整

在利润报表中增加退费相关信息：

```python
# 在正课数据中添加退费信息
for course in new_courses:
    profit_info = calculate_course_profit_with_refund(course)
    
    new_course_data.append({
        'customer_name': course.customer.name,
        'course_type': course.course_type,
        'revenue': revenue,
        'cost': cost,
        'original_profit': profit_info['original_profit'],
        'actual_profit': profit_info['actual_profit'],
        'has_refund': profit_info['has_refund'],
        'refund_amount': profit_info['refund_amount'],
        'shareholder_a': profit_info['actual_profit'] * profit_config['new_course_shareholder_a'] / 100,
        'shareholder_b': profit_info['actual_profit'] * profit_config['new_course_shareholder_b'] / 100,
        'date': course.created_at.strftime('%Y-%m-%d')
    })
```

## 八、实现路线图

### 第一阶段：核心功能（1-2周）
1. **数据库准备**
   - 创建 CourseRefund 表
   - 更新 Course 表结构
   - 编写数据库迁移脚本

2. **后端API开发**
   - 实现退费信息查询接口
   - 实现退费申请接口
   - 实现退费完成接口
   - 更新利润计算逻辑

3. **前端基础功能**
   - 添加退费按钮和模态框
   - 实现退费申请表单
   - 显示退费状态

### 第二阶段：完善功能（1周）
1. **退费管理**
   - 退费历史查询
   - 退费统计报表
   - 批量退费功能

2. **权限控制**
   - 退费权限管理
   - 操作日志记录

3. **通知功能**
   - 退费申请通知
   - 退费完成通知

### 第三阶段：优化提升（1周）
1. **用户体验**
   - 退费进度跟踪
   - 退费原因分析
   - 退费预警提醒

2. **性能优化**
   - 大数据量分页
   - 报表缓存优化
   - 异步处理机制

## 九、测试计划

### 9.1 单元测试
```python
def test_refund_calculation():
    """测试退费金额计算"""
    course = create_test_course(sessions=20, price=200)
    
    # 测试部分退费
    refund_amount = calculate_refund_amount(course, 5)
    assert refund_amount == 1000
    
    # 测试边界条件
    refundable = calculate_refundable_sessions(course)
    assert refundable == 20

def test_profit_recalculation():
    """测试利润重算"""
    course = create_test_course(sessions=20, price=200, cost=2000)
    
    # 添加退费记录
    create_refund(course, sessions=5, amount=1000)
    
    # 重算利润
    profit_info = recalculate_course_profit(course)
    assert profit_info['actual_revenue'] == 3000
    assert profit_info['actual_profit'] == 1500
```

### 9.2 集成测试
1. 完整退费流程测试
2. 并发退费测试
3. 数据一致性测试
4. 权限控制测试

### 9.3 性能测试
1. 大量退费记录查询
2. 批量利润重算
3. 报表生成性能

## 十、注意事项与最佳实践

### 10.1 数据安全
- 所有退费操作必须记录日志
- 敏感操作需要二次确认
- 定期备份退费相关数据

### 10.2 财务合规
- 退费金额必须准确无误
- 保留完整的审计轨迹
- 支持财务对账导出

### 10.3 用户体验
- 清晰的退费流程指引
- 实时的金额计算展示
- 友好的错误提示信息

### 10.4 扩展性考虑
- 预留审批流程接口
- 支持自定义退费规则
- 便于集成第三方支付

## 十一、风险控制

### 11.1 业务风险
- 设置退费时限（如30天内）
- 大额退费需要审批
- 异常退费行为监控

### 11.2 技术风险
- 使用数据库事务保证一致性
- 实施乐观锁防止并发问题
- 定期数据校验和修复

### 11.3 操作风险
- 权限分级管理
- 操作日志审计
- 异常操作告警

## 十二、总结

本方案设计了一个完整的正课退费功能，主要特点：

1. **数据完整性**：通过独立的退费表记录所有退费历史，不修改原始数据
2. **灵活性**：支持部分退费、多次退费，满足各种业务场景
3. **准确性**：自动重算利润，确保财务数据准确
4. **可追溯性**：完整的操作日志和审计轨迹
5. **用户友好**：清晰的界面设计和操作流程
6. **可扩展**：预留了审批、通知等扩展接口

该方案充分考虑了现有系统的架构特点，在不影响原有功能的基础上，通过模块化设计实现了退费功能的平滑集成。