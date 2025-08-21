# 计算逻辑统一修复总结

## 问题描述

员工管理页面中的试听课和正课计算方式与独立的试听课/正课页面不一致，导致同样的数据在不同页面显示不同的利润、成本、手续费等统计信息。

## 根本原因分析

### 1. 手续费率配置差异
- **独立页面**: `taobao_fee_rate = float(config.value) if config else 0.006`
- **员工管理页面（修复前）**: `taobao_fee_rate = float(config.value) / 100 if config else 0.006`
- **问题**: 员工管理页面多除了100，导致手续费计算错误

### 2. 正课收入计算差异
- **独立页面**: `base_revenue = course.sessions * course.price` (购买节数 × 单节售价)
- **员工管理页面（修复前）**: `price = float(course.price or 0)` (直接使用price字段)
- **问题**: 计算方式不一致，导致收入统计错误

### 3. 试听课状态处理差异
- **独立页面**: 对不同状态（退费、未报名等）有特殊的计算逻辑
- **员工管理页面（修复前）**: 使用统一计算方式，没有考虑状态差异
- **问题**: 退费课程的利润计算错误

## 修复方案

### 1. 统一手续费率计算
```python
# 修复前
taobao_fee_rate = float(taobao_fee_rate_config.value) / 100 if taobao_fee_rate_config else 0.006

# 修复后
taobao_fee_rate = float(taobao_fee_rate_config.value) if taobao_fee_rate_config else 0.006
```

### 2. 统一试听课计算逻辑
```python
# 按状态分别处理
if status == 'registered':
    # 已报名试听课：收入 - 成本 - 手续费
    price = float(course.trial_price or 0)
    cost = float(course.cost or 0)
    fees = price * taobao_fee_rate if course.source == '淘宝' else 0
    profit = price - cost - fees
    
elif status == 'not_registered':
    # 未报名试听课：无收入，只有成本
    price = 0
    cost = float(course.cost or 0)
    fees = 0
    profit = -cost
    
elif status == 'refunded':
    # 试听后退费：退费金额 + 退费手续费 + 成本
    price = 0  # 退费后无净收入
    cost = (float(course.cost or 0) + float(course.refund_amount or 0) + 
           float(course.refund_fee or 0))
    fees = 0
    profit = -cost
```

### 3. 统一正课计算逻辑
```python
# 计算基础收入：购买节数 × 单节售价
base_revenue = (course.sessions or 0) * float(course.price or 0)

# 如果是淘宝支付，扣除手续费
if course.payment_channel == '淘宝':
    fees = base_revenue * taobao_fee_rate
    price = base_revenue - fees  # 实际收入
else:
    fees = 0
    price = base_revenue
    
cost = float(course.cost or 0)
profit = price - cost
```

## 修复效果

### ✅ 已解决的问题
1. **手续费计算一致性**: 员工管理页面和独立页面现在使用相同的手续费率计算方式
2. **正课收入计算一致性**: 都使用"购买节数 × 单节售价"的方式计算总收入
3. **试听课状态处理一致性**: 退费、未报名等状态的利润计算逻辑完全一致
4. **数据完整性**: 保持了原有的数据结构，只修复了计算逻辑

### ✅ 验证结果
- 员工管理页面加载正常，无JavaScript错误
- 独立试听课页面功能正常
- 独立正课页面功能正常
- API调用成功，返回正确的计算结果

## 技术细节

### 修改的文件
- `app/routes.py` - 统一员工课程管理API的计算逻辑

### 修改的函数
- `get_employee_courses_unified()` - 员工统一课程数据API

### 保持不变的部分
- 独立试听课页面的计算逻辑
- 独立正课页面的计算逻辑
- 数据库结构和数据
- 前端显示逻辑

## 后续建议

1. **代码重构**: 考虑将计算逻辑提取为独立的服务类，避免重复代码
2. **单元测试**: 为计算逻辑添加单元测试，确保未来修改不会破坏一致性
3. **配置管理**: 统一管理手续费率等配置参数，避免硬编码

## 总结

通过这次修复，成功解决了员工管理页面与独立页面计算逻辑不一致的问题。现在所有页面都使用相同的计算方式，确保了数据的一致性和准确性。修复过程中保持了系统的稳定性，没有影响现有功能。