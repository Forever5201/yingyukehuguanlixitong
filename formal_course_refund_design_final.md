# 正课退费功能设计方案（最终版）

## 一、需求背景与目标

### 1.1 业务需求
- 支持正课按节数退费
- 退费金额按原始售价计算
- 退费节数不超过剩余可退节数
- 自动重新计算利润、股东分配、员工业绩

### 1.2 设计目标
- **最小侵入**：不破坏现有功能
- **数据准确**：确保财务数据正确
- **易于实施**：分阶段逐步完成
- **可追溯性**：保留完整退费记录

## 二、技术方案

### 2.1 数据库设计（最小侵入式）

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

### 2.2 核心计算逻辑

#### 2.2.1 统一的利润计算函数

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
            
            # 成本按比例调整
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
                'cost': actual_cost + fee,  # 为了兼容现有逻辑
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

#### 2.2.2 退费业务规则

```python
def calculate_refundable_sessions(course):
    """计算可退费节数"""
    # 获取已退费记录
    existing_refunds = CourseRefund.query.filter_by(
        course_id=course.id,
        status='completed'
    ).all()
    
    total_refunded = sum(r.refund_sessions for r in existing_refunds)
    
    # 可退费节数 = 购买节数 - 已退费节数
    # 注意：赠送节数不参与退费
    refundable = course.sessions - total_refunded
    
    return max(0, refundable)
```

### 2.3 API接口实现

#### 2.3.1 获取退费信息

```python
@main_bp.route('/api/courses/<int:course_id>/refund-info', methods=['GET'])
def get_refund_info(course_id):
    """获取课程的可退费信息"""
    try:
        course = Course.query.get(course_id)
        if not course or course.is_trial:
            return jsonify({'success': False, 'message': '课程不存在或不是正课'}), 404
        
        # 计算可退费信息
        refundable_sessions = calculate_refundable_sessions(course)
        
        # 获取退费历史
        refund_history = CourseRefund.query.filter_by(
            course_id=course_id
        ).order_by(CourseRefund.refund_date.desc()).all()
        
        return jsonify({
            'success': True,
            'data': {
                'course_id': course.id,
                'customer_name': course.customer.name,
                'course_type': course.course_type,
                'purchased_sessions': course.sessions,
                'refunded_sessions': course.sessions - refundable_sessions,
                'refundable_sessions': refundable_sessions,
                'unit_price': course.price,
                'max_refund_amount': refundable_sessions * course.price,
                'refund_history': [{
                    'id': r.id,
                    'sessions': r.refund_sessions,
                    'amount': r.refund_amount,
                    'reason': r.refund_reason,
                    'date': r.refund_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': r.status
                } for r in refund_history]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
```

#### 2.3.2 申请退费

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
        refundable_sessions = calculate_refundable_sessions(course)
        
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

#### 2.3.3 退费历史查询

```python
@main_bp.route('/api/courses/<int:course_id>/refund-history', methods=['GET'])
def get_refund_history(course_id):
    """获取课程退费历史"""
    try:
        refunds = CourseRefund.query.filter_by(
            course_id=course_id
        ).order_by(CourseRefund.refund_date.desc()).all()
        
        return jsonify({
            'success': True,
            'refunds': [{
                'id': r.id,
                'refund_sessions': r.refund_sessions,
                'refund_amount': r.refund_amount,
                'refund_reason': r.refund_reason,
                'refund_channel': r.refund_channel,
                'refund_fee': r.refund_fee,
                'actual_refund': r.refund_amount - r.refund_fee,
                'refund_date': r.refund_date.strftime('%Y-%m-%d %H:%M:%S'),
                'status': r.status,
                'operator_name': r.operator_name,
                'remark': r.remark
            } for r in refunds]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
```

### 2.4 核心功能改造

#### 2.4.1 利润报表改造

```python
# 在 get_profit_report 函数中修改计算逻辑
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
        'refund_amount': profit_info.get('refund_info', {}).get('amount', 0),
        'shareholder_a': shareholder_a,
        'shareholder_b': shareholder_b,
        'date': course.created_at.strftime('%Y-%m-%d')
    })
```

#### 2.4.2 员工业绩改造

```python
# 在 get_employee_performance 函数中修改
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

#### 2.4.3 正课统计改造

```python
# 在 api_formal_courses_stats 函数中修改
for course in courses:
    profit_info = calculate_course_profit_with_refund(course)
    
    revenue = profit_info['revenue']
    cost = profit_info['cost']
    profit = profit_info['profit']
    
    # 累加统计
    total_revenue += revenue
    total_cost += cost
    total_profit += profit
    
    # 构建行数据
    rows.append({
        'id': course.id,
        'customer_id': course.customer.id,
        'customer_name': course.customer.name,
        'course_type': course.course_type,
        'sessions': course.sessions,
        'revenue': revenue,
        'cost': cost,
        'profit': profit,
        'has_refund': profit_info['has_refund'],
        'refund_amount': profit_info.get('refund_info', {}).get('amount', 0),
        'created_at': course.created_at.isoformat()
    })
```

## 三、前端实现

### 3.1 正课列表页面改造

在 `app/templates/formal_courses.html` 的操作按钮组中添加退费按钮：

```html
<!-- 在续课按钮后添加退费按钮 -->
{% if course.refund_status != 'full' %}
<button onclick="showRefundModal({{ course.id }})" 
        class="btn btn-sm btn-outline-warning action-btn" 
        title="申请退费">
    <i class="fas fa-undo"></i>
    <span class="btn-text">退费</span>
</button>
{% endif %}
```

### 3.2 退费模态框

```html
<!-- 退费模态框 -->
<div id="refundModal" class="modal">
    <div class="modal-content" style="max-width: 600px;">
        <div class="modal-header">
            <h2>申请退费</h2>
            <span class="close" onclick="closeRefundModal()">&times;</span>
        </div>
        
        <div class="modal-body">
            <!-- 课程信息展示 -->
            <div class="info-section">
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
                        <span id="refund_refundable_sessions" class="text-primary font-weight-bold"></span>
                    </div>
                    <div class="info-item">
                        <label>单节价格：</label>
                        <span id="refund_unit_price"></span>
                    </div>
                </div>
            </div>
            
            <!-- 退费表单 -->
            <form id="refundForm" class="mt-4">
                <input type="hidden" id="refund_course_id" name="course_id">
                
                <div class="form-group">
                    <label for="refund_sessions">退费节数 <span class="text-danger">*</span></label>
                    <input type="number" 
                           class="form-control" 
                           id="refund_sessions" 
                           name="refund_sessions" 
                           min="1" 
                           required
                           onchange="calculateRefundAmount()">
                    <small class="form-text text-muted">请输入要退费的节数</small>
                </div>
                
                <div class="form-group">
                    <label for="refund_reason">退费原因 <span class="text-danger">*</span></label>
                    <select class="form-control" id="refund_reason" name="refund_reason" required>
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
                    <label for="refund_channel">退费渠道 <span class="text-danger">*</span></label>
                    <select class="form-control" id="refund_channel" name="refund_channel" required>
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
                           class="form-control" 
                           id="refund_fee" 
                           name="refund_fee" 
                           step="0.01" 
                           min="0" 
                           value="0"
                           onchange="calculateRefundAmount()">
                    <small class="form-text text-muted">如有手续费请填写</small>
                </div>
                
                <div class="form-group">
                    <label for="refund_remark">备注说明</label>
                    <textarea class="form-control" 
                              id="refund_remark" 
                              name="remark" 
                              rows="3" 
                              placeholder="请填写详细的退费说明..."></textarea>
                </div>
                
                <!-- 退费金额计算展示 -->
                <div class="refund-calculation card">
                    <div class="card-body">
                        <h5 class="card-title">退费金额计算</h5>
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
                        <hr>
                        <div class="calculation-item font-weight-bold">
                            <span>实际退款：</span>
                            <span id="calc_actual_amount" class="text-danger">¥0.00</span>
                        </div>
                    </div>
                </div>
            </form>
            
            <!-- 退费历史 -->
            <div id="refundHistorySection" class="mt-4" style="display: none;">
                <h4>退费历史</h4>
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>退费日期</th>
                            <th>退费节数</th>
                            <th>退费金额</th>
                            <th>退费原因</th>
                            <th>状态</th>
                        </tr>
                    </thead>
                    <tbody id="refundHistoryBody">
                        <!-- 动态加载 -->
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="modal-footer">
            <button type="button" class="btn btn-secondary" onclick="closeRefundModal()">取消</button>
            <button type="button" class="btn btn-warning" onclick="submitRefund()">
                <i class="fas fa-check"></i> 提交退费申请
            </button>
        </div>
    </div>
</div>
```

### 3.3 JavaScript功能实现

```javascript
// 全局变量
let currentRefundCourse = null;

// 显示退费模态框
function showRefundModal(courseId) {
    // 显示加载状态
    showLoading();
    
    // 获取课程退费信息
    fetch(`/api/courses/${courseId}/refund-info`)
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            if (data.success) {
                currentRefundCourse = data.data;
                
                // 填充课程信息
                document.getElementById('refund_course_id').value = courseId;
                document.getElementById('refund_customer_name').textContent = currentRefundCourse.customer_name;
                document.getElementById('refund_course_type').textContent = currentRefundCourse.course_type;
                document.getElementById('refund_purchased_sessions').textContent = currentRefundCourse.purchased_sessions;
                document.getElementById('refund_refunded_sessions').textContent = currentRefundCourse.refunded_sessions;
                document.getElementById('refund_refundable_sessions').textContent = currentRefundCourse.refundable_sessions;
                document.getElementById('refund_unit_price').textContent = `¥${currentRefundCourse.unit_price.toFixed(2)}`;
                
                // 设置最大可退费节数
                document.getElementById('refund_sessions').max = currentRefundCourse.refundable_sessions;
                
                // 显示退费历史
                if (currentRefundCourse.refund_history && currentRefundCourse.refund_history.length > 0) {
                    showRefundHistory(currentRefundCourse.refund_history);
                }
                
                // 显示模态框
                document.getElementById('refundModal').style.display = 'block';
            } else {
                showError('获取退费信息失败：' + data.message);
            }
        })
        .catch(error => {
            hideLoading();
            showError('获取退费信息失败');
            console.error('Error:', error);
        });
}

// 计算退费金额
function calculateRefundAmount() {
    if (!currentRefundCourse) return;
    
    const sessions = parseInt(document.getElementById('refund_sessions').value) || 0;
    const fee = parseFloat(document.getElementById('refund_fee').value) || 0;
    const unitPrice = currentRefundCourse.unit_price;
    
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
    
    // 验证表单
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // 获取表单数据
    const formData = new FormData(form);
    const data = {
        refund_sessions: parseInt(formData.get('refund_sessions')),
        refund_reason: formData.get('refund_reason'),
        refund_channel: formData.get('refund_channel'),
        refund_fee: parseFloat(formData.get('refund_fee')) || 0,
        remark: formData.get('remark')
    };
    
    const courseId = formData.get('course_id');
    
    // 计算金额用于确认
    const refundAmount = data.refund_sessions * currentRefundCourse.unit_price;
    const actualAmount = refundAmount - data.refund_fee;
    
    // 确认退费
    if (!confirm(`确认要退费吗？\n\n退费节数：${data.refund_sessions} 节\n退费金额：¥${refundAmount.toFixed(2)}\n手续费：¥${data.refund_fee.toFixed(2)}\n实际退款：¥${actualAmount.toFixed(2)}`)) {
        return;
    }
    
    // 显示加载状态
    showLoading();
    
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
        hideLoading();
        
        if (result.success) {
            showSuccess('退费申请提交成功！');
            closeRefundModal();
            
            // 刷新页面数据
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            showError('退费申请失败：' + result.message);
        }
    })
    .catch(error => {
        hideLoading();
        showError('提交退费申请时发生错误');
        console.error('Error:', error);
    });
}

// 显示退费历史
function showRefundHistory(history) {
    const historySection = document.getElementById('refundHistorySection');
    const historyBody = document.getElementById('refundHistoryBody');
    
    historyBody.innerHTML = '';
    
    history.forEach(refund => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${refund.date}</td>
            <td>${refund.sessions}</td>
            <td>¥${refund.amount.toFixed(2)}</td>
            <td>${refund.reason}</td>
            <td><span class="badge badge-${refund.status === 'completed' ? 'success' : 'warning'}">${refund.status}</span></td>
        `;
        historyBody.appendChild(tr);
    });
    
    historySection.style.display = 'block';
}

// 关闭退费模态框
function closeRefundModal() {
    document.getElementById('refundModal').style.display = 'none';
    document.getElementById('refundForm').reset();
    document.getElementById('refundHistorySection').style.display = 'none';
    currentRefundCourse = null;
}

// 工具函数
function showLoading() {
    // 实现加载提示
}

function hideLoading() {
    // 隐藏加载提示
}

function showSuccess(message) {
    // 显示成功消息
    alert(message);
}

function showError(message) {
    // 显示错误消息
    alert(message);
}
```

### 3.4 样式优化

```css
/* 退费相关样式 */
.info-section {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 5px;
    margin-bottom: 20px;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
}

.info-item {
    display: flex;
    align-items: center;
}

.info-item label {
    font-weight: 600;
    margin-right: 10px;
    min-width: 100px;
}

.refund-calculation {
    background: #f8f9fa;
    margin-top: 20px;
}

.calculation-item {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
}

.calculation-item span:first-child {
    font-weight: 600;
}

/* 退费按钮样式 */
.btn-outline-warning {
    color: #ffc107;
    border-color: #ffc107;
}

.btn-outline-warning:hover {
    color: #fff;
    background-color: #ffc107;
    border-color: #ffc107;
}
```

## 四、实施计划

### 4.1 第一阶段：基础功能（3-5天）

1. **数据库准备**
   - 创建course_refund表
   - 添加必要的索引

2. **后端开发**
   - 实现退费信息查询API
   - 实现退费申请API
   - 实现退费历史查询API

3. **前端开发**
   - 添加退费按钮
   - 实现退费模态框
   - 完成基本交互功能

4. **基础测试**
   - 单次退费测试
   - 多次退费测试
   - 边界条件测试

### 4.2 第二阶段：核心集成（5-7天）

1. **利润计算改造**
   - 实现calculate_course_profit_with_refund函数
   - 修改利润报表逻辑
   - 测试数据准确性

2. **员工业绩集成**
   - 修改员工业绩计算
   - 处理退费对提成的影响
   - 测试各种场景

3. **统计报表更新**
   - 更新正课统计API
   - 修改前端统计展示
   - 验证数据一致性

### 4.3 第三阶段：完善优化（3-5天）

1. **功能完善**
   - 退费统计报表
   - 退费原因分析
   - 批量退费功能（可选）

2. **性能优化**
   - 查询优化
   - 缓存策略
   - 大数据量测试

3. **用户体验**
   - 操作提示优化
   - 错误处理完善
   - 界面美化

## 五、测试方案

### 5.1 功能测试

1. **退费流程测试**
   - 正常退费流程
   - 部分退费
   - 全额退费
   - 多次退费

2. **边界测试**
   - 退费节数=购买节数
   - 退费节数超限
   - 并发退费

3. **异常测试**
   - 网络异常
   - 数据异常
   - 权限异常

### 5.2 数据测试

1. **利润计算准确性**
   ```
   原始收入: 10节 × 200元 = 2000元
   退费: 3节 × 200元 = 600元
   实际收入: 2000 - 600 = 1400元
   
   原始成本: 1000元（含其他成本200元）
   变动成本: 800元
   调整后成本: 800 × 7/10 + 200 = 760元
   
   手续费: 2000 × 0.6% = 12元（不退）
   
   实际利润: 1400 - 760 - 12 = 628元
   ```

2. **股东分配测试**
   - 新课利润分配（50/50）
   - 续课利润分配（40/60）
   - 退费后重新分配

3. **员工提成测试**
   - 利润型提成
   - 销售型提成
   - 退费影响

### 5.3 性能测试

1. **并发测试**
   - 多人同时退费
   - 大量退费记录查询
   - 统计报表生成

2. **压力测试**
   - 1000+退费记录
   - 复杂查询性能
   - 响应时间测试

## 六、风险控制

### 6.1 技术风险

| 风险 | 影响 | 对策 |
|------|------|------|
| 修改核心计算逻辑 | 可能影响现有功能 | 使用参数控制，逐步迁移 |
| 数据一致性 | 统计数据错误 | 充分测试，数据校验 |
| 性能问题 | 系统响应慢 | 优化查询，添加缓存 |

### 6.2 业务风险

| 风险 | 影响 | 对策 |
|------|------|------|
| 恶意退费 | 财务损失 | 设置退费限制规则 |
| 操作错误 | 数据错误 | 操作确认，日志记录 |
| 规则变更 | 系统改动大 | 规则参数化配置 |

## 七、注意事项

1. **数据安全**
   - 所有退费操作记录日志
   - 敏感操作需要确认
   - 定期备份数据

2. **财务准确**
   - 退费金额必须准确
   - 保留审计轨迹
   - 支持对账导出

3. **用户体验**
   - 清晰的操作流程
   - 实时的金额计算
   - 友好的错误提示

4. **扩展预留**
   - 审批流程接口
   - 自定义规则
   - 第三方支付集成

## 八、总结

本方案采用最小侵入式设计，主要特点：

1. **数据独立**：只增加退费表，不修改原表结构
2. **逐步实施**：分阶段完成，降低风险
3. **统一计算**：所有利润计算调用同一函数
4. **完整追溯**：保留所有退费记录
5. **灵活扩展**：预留扩展接口

通过这种设计，可以在保证现有系统稳定的前提下，逐步实现完整的退费功能。