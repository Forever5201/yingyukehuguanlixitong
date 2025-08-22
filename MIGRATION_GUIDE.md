# 系统架构迁移指南

## 概述

本指南说明如何从当前的单体架构逐步迁移到基于正规软件开发规范的分层架构。

## 迁移策略

### 1. 渐进式迁移（推荐）

采用"绞杀者模式"（Strangler Fig Pattern），逐步替换旧功能：

```
旧系统 ←→ 新系统
   ↓        ↓
逐步减少 → 逐步增加
```

### 2. 迁移阶段

#### 阶段1：基础设施搭建 ✅
- [x] 创建服务层 (`CourseService`)
- [x] 创建统一API控制器 (`CourseController`)
- [x] 创建前端API客户端 (`ApiClient`)
- [x] 创建重构后的课程管理器 (`CourseManagerV2`)

#### 阶段2：API统一化（当前阶段）
- [ ] 测试新API端点
- [ ] 验证数据一致性
- [ ] 性能对比测试

#### 阶段3：前端迁移
- [ ] 更新员工管理页面使用新API
- [ ] 更新试听课管理页面
- [ ] 更新正式课管理页面

#### 阶段4：旧代码清理
- [ ] 移除重复的API端点
- [ ] 清理旧的JavaScript代码
- [ ] 更新文档

## 新旧API对比

### 员工课程相关API

| 功能 | 旧API | 新API | 状态 |
|------|-------|-------|------|
| 员工试听课列表 | `/api/employees/<id>/trial-courses` | `/api/v1/employees/<id>/courses?type=trial` | ✅ 可用 |
| 员工正式课列表 | `/api/employees/<id>/formal-courses` | `/api/v1/employees/<id>/courses?type=formal` | ✅ 可用 |
| 员工课程汇总 | `/api/employees/<id>/courses-unified` | `/api/v1/employees/<id>/courses?summary=true` | ✅ 可用 |
| 员工业绩统计 | 分散在各个API中 | `/api/v1/employees/<id>/courses/performance` | ✅ 可用 |
| 课程分配 | `/api/courses/<id>/assign` | `/api/v1/courses/<id>/assign` | ✅ 可用 |

### 通用课程API

| 功能 | 旧API | 新API | 状态 |
|------|-------|-------|------|
| 课程列表 | 分散在多个端点 | `/api/v1/courses` | ✅ 可用 |
| 状态映射 | 硬编码在前端 | `/api/v1/courses/status-mapping` | ✅ 可用 |

## 使用新系统

### 1. 在HTML中引入新的JavaScript文件

```html
<!-- 在页面头部引入 -->
<script src="{{ url_for('static', filename='js/api-client.js') }}"></script>
<script src="{{ url_for('static', filename='js/course-manager-v2.js') }}"></script>
```

### 2. 使用新的CourseManagerV2

```javascript
// 旧方式
CourseManager.loadTrialCourses(employeeId);

// 新方式
courseManagerV2.updateEmployeeCoursesTable(employeeId, 'trial-courses-table', 'trial');
```

### 3. 使用统一的API客户端

```javascript
// 直接使用API服务
const data = await courseApiService.getEmployeeCourses(employeeId, {
    type: 'trial',
    include_customer: true
});

// 使用错误处理
try {
    const result = await courseApiService.assignCourse(courseId, employeeId);
    errorHandler.showSuccess('分配成功');
} catch (error) {
    errorHandler.showError(error);
}
```

## 测试新系统

### 1. API测试

```bash
# 测试员工课程API
curl "http://localhost:5000/api/v1/employees/1/courses?type=trial"

# 测试课程分配API
curl -X POST "http://localhost:5000/api/v1/courses/1/assign" \
     -H "Content-Type: application/json" \
     -d '{"employee_id": 1}'
```

### 2. 前端测试

在浏览器控制台中测试：

```javascript
// 测试API客户端
courseApiService.getEmployeeCourses(1, {type: 'trial'})
    .then(data => console.log('成功:', data))
    .catch(error => console.error('失败:', error));

// 测试课程管理器
courseManagerV2.updateEmployeeCoursesTable(1, 'test-table', 'trial');
```

## 数据一致性验证

### 1. 对比测试脚本

创建测试脚本对比新旧API的返回结果：

```python
import requests
import json

def compare_apis():
    employee_id = 1
    
    # 旧API
    old_response = requests.get(f'/api/employees/{employee_id}/trial-courses')
    
    # 新API
    new_response = requests.get(f'/api/v1/employees/{employee_id}/courses?type=trial')
    
    # 对比数据
    # ... 实现对比逻辑
```

### 2. 业绩计算验证

确保新系统的业绩计算与旧系统一致：

- 收入计算
- 成本计算
- 手续费计算
- 利润计算

## 性能优化

### 1. 数据库查询优化

新的`CourseService`使用了更高效的查询：

```python
# 旧方式：多次查询
trial_courses = Course.query.filter_by(is_trial=True).all()
for course in trial_courses:
    customer = Customer.query.get(course.customer_id)

# 新方式：联表查询
courses = db.session.query(Course, Customer).join(Customer).filter(Course.is_trial == True).all()
```

### 2. 前端性能优化

- 统一的加载状态管理
- 错误处理标准化
- 减少重复的API调用

## 回滚策略

如果新系统出现问题，可以快速回滚：

### 1. API级别回滚

在`app/__init__.py`中注释掉新API的注册：

```python
# 注册新的统一API蓝图
# try:
#     from .api.course_controller import course_api
#     app.register_blueprint(course_api)
# except ImportError:
#     pass
```

### 2. 前端级别回滚

移除新JavaScript文件的引用，恢复使用旧的`CourseManager`。

## 监控和日志

### 1. API监控

监控新API的：
- 响应时间
- 错误率
- 调用频率

### 2. 错误日志

新系统包含完整的错误日志：

```python
logger.error(f"获取课程列表失败: {str(e)}")
```

## 最佳实践

### 1. 代码规范

- 使用类型提示
- 添加文档字符串
- 遵循PEP 8规范

### 2. 测试驱动

- 为每个服务方法编写单元测试
- API集成测试
- 前端功能测试

### 3. 持续集成

- 自动化测试
- 代码质量检查
- 性能回归测试

## 常见问题

### Q: 新旧系统如何共存？

A: 通过蓝图注册机制，新旧API可以同时存在。新API使用`/api/v1`前缀，旧API保持原有路径。

### Q: 数据会不会不一致？

A: 新旧系统使用相同的数据库和模型，只是业务逻辑层不同。`CourseService`确保了业务逻辑的一致性。

### Q: 性能会不会下降？

A: 新系统通过联表查询和统一的业务逻辑，实际上会提升性能。

### Q: 如何确保迁移成功？

A: 通过渐进式迁移、充分测试和监控，确保每个阶段都稳定后再进行下一步。

## 下一步行动

1. **立即可做**：测试新API端点的功能和性能
2. **本周内**：在开发环境中完整测试新系统
3. **下周**：开始迁移一个页面（建议从员工管理页面开始）
4. **月内**：完成所有页面的迁移

## 联系支持

如果在迁移过程中遇到问题，请：

1. 查看错误日志
2. 检查浏览器控制台
3. 对比新旧API的返回结果
4. 参考本指南的故障排除部分

## 试听课统计与状态计算规则（最终版）

本节定义“试听课管理”的统一统计口径，供前后端与运营对齐。所有金额展示保留两位小数，累计计算使用全精度。

### 1. 统一前提
- 基础试听成本：只用系统配置中的“基础试听成本”（记为 C），每条记录都用同一成本 C。
- 手续费率：按渠道从配置读取（百分比→小数后计算，记为 R）。
- 退款计入汇总（方案A，推荐），用于真实反映损益。

### 2. 计入汇总的状态（方案A）
- 计入：已报名（registered）、转正（converted）、无操作（no_action）、退费（refunded）
- 不计入：未报名（not_registered）、误操作（mis_operation）

说明：未报名/误操作完全排除；退费计入汇总但收入为0、手续费规则特殊（见下）。

### 3. 全局“汇总卡片”口径
设参与汇总集合为 S（含退款），每条记录售价为 P，费率为 R。

- 试听课总数：|S|
- 总收入：对非退款记录求和（退款收入=0）
  - 总收入 = Σ P（仅非退款）
- 总手续费：逐条计算后求和
  - 非退款：手续费 = P × R
  - 退款：见第5条“退费规则”
  - 总手续费 = Σ 手续费
- 总成本：基础成本合计 + 总手续费
  - 基础成本合计 = |S| × C
  - 总成本 = |S| × C + 总手续费
- 总利润：总收入 − 总成本

说明：按你的要求，总成本已包含“基础成本 + 总手续费”，因此总利润=总收入−总成本。

### 4. 逐条记录计算（用于行展示与分状态统计）
对单条记录（售价 P、费率 R、基础成本 C）：

- 已报名（registered）
  - 收入 = P
  - 手续费 = P × R
  - 成本 = C
  - 利润 = 收入 − 成本 − 手续费

- 转正（converted）
  - 收入 = P
  - 手续费 = P × R
  - 成本 = C
  - 利润 = 收入 − 成本 − 手续费
  - 说明：试听本条的口径不变；正课收入在正课模块单独核算。

- 无操作（no_action）
  - 收入 = P（视为成交）
  - 手续费 = P × R
  - 成本 = C
  - 利润 = 收入 − 成本 − 手续费

- 退费（refunded）
  - 收入 = 0
  - 手续费：
    - 淘宝原路退：0（未产生这笔交易）
    - 微信等非原路退：P × R
  - 成本 = C（资源已占用）
  - 利润 = − 成本 − 手续费

- 未报名（not_registered）/ 误操作（mis_operation）
  - 不计入汇总（收入/手续费/成本/利润均为0）

### 5. 渠道与退款手续费规则
- 正常成交：按渠道配置费率 R 计算手续费（淘宝/抖音/小红书/视频号/转介绍/其他）。
- 退款：是否产生手续费取决于退款渠道：
  - 淘宝原路退：手续费=0
  - 非原路（如微信）：手续费=P × R

### 6. 数据校验与默认值
- 新建默认状态设为“已报名（registered）”，避免空状态。
- 售价 P ≥ 0；渠道必选；退款需记录“退款渠道”（淘宝/微信等），以保证手续费正确。
- 前端只做展示与交互，汇总数据以后端计算为准。