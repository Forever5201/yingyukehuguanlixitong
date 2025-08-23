
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
