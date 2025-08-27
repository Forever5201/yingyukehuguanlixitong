# DataTable 组件集成指南

## 概述

DataTable 组件是一个功能强大的表格组件，支持两种运行模式：
- **服务端分页模式（Server-side Pagination）**：适用于数据量大但每次只需要显示部分数据的场景
- **客户端虚拟滚动模式（Virtual Scrolling）**：适用于需要在客户端展示大量数据的场景

组件会根据数据量自动选择最优的渲染方式：
- 数据量 < 2000 条：使用普通 DOM 渲染
- 数据量 ≥ 2000 条：使用 Clusterize.js 虚拟滚动

## 快速开始

### 1. 引入必要文件

在 `base.html` 中添加：

```html
<!-- 在 <head> 部分 -->
<!-- 如果使用本地文件 -->
<link rel="stylesheet" href="{{ url_for('static', filename='vendor/clusterize.css') }}">

<!-- 或使用 CDN -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/clusterize.js@0.18.0/clusterize.min.css">

<!-- 在 </body> 之前 -->
<!-- 如果使用本地文件 -->
<script src="{{ url_for('static', filename='vendor/clusterize.min.js') }}"></script>

<!-- 或使用 CDN -->
<script src="https://cdn.jsdelivr.net/npm/clusterize.js@0.18.0/clusterize.min.js"></script>

<!-- DataTable 管理器 -->
<script src="{{ url_for('static', filename='js/data-table.js') }}"></script>
```

### 2. 在模板中使用

```jinja2
{% from 'components/data_table.html' import data_table %}

<!-- 服务端分页模式 -->
{{ data_table(
    columns=[
        {'key': 'name', 'label': '姓名', 'sortable': True},
        {'key': 'phone', 'label': '电话', 'width': '150px'},
        {'key': 'email', 'label': '邮箱', 'type': 'email'},
        {'key': 'status', 'label': '状态', 'type': 'status', 'width': '100px'},
        {'key': 'created_at', 'label': '创建时间', 'type': 'date', 'sortable': True}
    ],
    rows=customers,
    mode='server',
    page=current_page,
    total_count=total_customers,
    per_page=50,
    table_id='customerTable'
) }}

<!-- 虚拟滚动模式 -->
{{ data_table(
    columns=[...],
    mode='virtual',
    data_url='/api/customers/all',
    virtual_threshold=2000,
    table_id='virtualTable'
) }}
```

## Flask 后端实现

### 服务端分页模式

```python
from flask import request, render_template, jsonify
from app.models import Customer
from app import db

@app.route('/customers')
def customers():
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # 获取排序参数
    sort = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    
    # 获取筛选参数
    search = request.args.get('search', '')
    status = request.args.get('status')
    
    # 构建查询
    query = Customer.query
    
    # 应用筛选
    if search:
        query = query.filter(
            db.or_(
                Customer.name.contains(search),
                Customer.phone.contains(search),
                Customer.email.contains(search)
            )
        )
    
    if status:
        query = query.filter(Customer.status == status)
    
    # 应用排序
    if hasattr(Customer, sort):
        sort_column = getattr(Customer, sort)
        if order == 'desc':
            sort_column = sort_column.desc()
        query = query.order_by(sort_column)
    
    # 执行分页查询
    pagination = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    # 准备数据
    customers_data = [{
        'id': c.id,
        'name': c.name,
        'phone': c.phone,
        'email': c.email,
        'status': c.status,
        'created_at': c.created_at.isoformat() if c.created_at else None
    } for c in pagination.items]
    
    return render_template('customers.html',
        customers=customers_data,
        current_page=page,
        total_customers=pagination.total,
        per_page=per_page
    )
```

### 虚拟滚动模式 - 返回所有数据

```python
@app.route('/api/customers/all')
def api_customers_all():
    # 获取所有客户数据
    # 注意：对于超大数据集，考虑分批加载或使用流式响应
    customers = Customer.query.order_by(Customer.created_at.desc()).all()
    
    # 转换为 JSON 格式
    data = [{
        'id': c.id,
        'name': c.name,
        'phone': c.phone,
        'email': c.email,
        'status': c.status,
        'amount': c.total_amount,
        'created_at': c.created_at.isoformat() if c.created_at else None
    } for c in customers]
    
    return jsonify(data)
```

### 优化建议 - 大数据集处理

```python
@app.route('/api/customers/stream')
def api_customers_stream():
    """流式返回大数据集，减少内存占用"""
    def generate():
        # 使用 yield_per 减少内存占用
        query = Customer.query.order_by(Customer.id)
        
        yield '['  # JSON 数组开始
        first = True
        
        for customer in query.yield_per(100):
            if not first:
                yield ','
            else:
                first = False
                
            yield json.dumps({
                'id': customer.id,
                'name': customer.name,
                'phone': customer.phone,
                'email': customer.email,
                'status': customer.status,
                'created_at': customer.created_at.isoformat() if customer.created_at else None
            })
        
        yield ']'  # JSON 数组结束
    
    return Response(generate(), mimetype='application/json')
```

## 组件参数详解

### 基础参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| columns | Array | 必需 | 列定义数组 |
| mode | String | 'server' | 运行模式：'server' 或 'virtual' |
| table_id | String | 'dataTable' | 表格唯一标识符 |
| enable_export | Boolean | true | 是否启用导出功能 |
| enable_selection | Boolean | false | 是否启用行选择功能 |

### 服务端分页参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| rows | Array | None | 当前页的数据行 |
| page | Integer | 1 | 当前页码 |
| total_count | Integer | 0 | 总记录数 |
| per_page | Integer | 50 | 每页显示数量 |

### 虚拟滚动参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| data_url | String | None | 数据源 URL |
| virtual_threshold | Integer | 2000 | 虚拟滚动触发阈值 |
| row_height | Integer | 48 | 行高（像素） |

### 列定义格式

```javascript
{
    key: 'name',           // 数据字段名
    label: '姓名',         // 显示标题
    type: 'text',          // 数据类型：text/date/currency/number/status
    width: '150px',        // 列宽度（可选）
    sortable: true,        // 是否可排序（服务端模式）
    className: 'text-center'  // 自定义 CSS 类（可选）
}
```

## 事件监听

```javascript
// 监听行点击事件
document.getElementById('customerTable-wrapper').addEventListener('rowClick', function(e) {
    console.log('Row clicked:', e.detail);
    // e.detail 包含: { id, row, data }
});

// 获取选中的行
const instance = DataTableManager.getInstance('customerTable');
const selectedIds = Array.from(instance.selectedRows);
```

## 生成模拟数据

### 方法 1：使用内置生成器

```javascript
// 在浏览器控制台执行
const mockData = DataTableManager.getInstance('virtualTable').generateMockData(5000);
console.log(JSON.stringify(mockData));
```

### 方法 2：Python 脚本生成

创建 `generate_mock_data.py`：

```python
import json
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('zh_CN')

def generate_mock_customers(count=5000):
    statuses = ['active', 'pending', 'completed', 'cancelled']
    data = []
    
    for i in range(1, count + 1):
        created_at = datetime.now() - timedelta(
            days=random.randint(0, 365),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        data.append({
            'id': i,
            'name': fake.name(),
            'phone': fake.phone_number(),
            'email': fake.email(),
            'status': random.choice(statuses),
            'amount': round(random.uniform(1000, 50000), 2),
            'address': fake.address(),
            'created_at': created_at.isoformat()
        })
    
    return data

# 生成数据并保存
mock_data = generate_mock_customers(5000)

with open('static/json/mock_customers.json', 'w', encoding='utf-8') as f:
    json.dump(mock_data, f, ensure_ascii=False, indent=2)

print(f"Generated {len(mock_data)} mock records")
```

### 方法 3：直接创建 JSON 文件

创建 `/static/json/mock_rows.json`：

```json
[
  {
    "id": 1,
    "name": "张三",
    "phone": "13800138001",
    "email": "zhangsan@example.com",
    "status": "active",
    "amount": 12500.00,
    "created_at": "2024-01-15T10:30:00"
  },
  // ... 重复 5000 条
]
```

## 性能测试和验证

### 1. Chrome Performance Profile

1. 打开示例页面，确保虚拟滚动表格已加载 5000 条数据
2. 打开 Chrome DevTools (F12)
3. 切换到 Performance 标签
4. 点击录制按钮（圆形按钮）
5. 在表格中快速上下滚动 10 秒
6. 停止录制
7. 分析结果：
   - FPS 应保持在 50-60
   - Scripting 时间应该较少
   - 没有明显的长任务（黄色块）

### 2. 内存使用测试

1. 打开 Chrome DevTools > Memory 标签
2. 拍摄堆快照（Take heap snapshot）
3. 滚动表格
4. 再次拍摄堆快照
5. 比较两个快照，内存增长应该很小

### 3. 手动测试检查点

- [ ] 快速滚动流畅无卡顿
- [ ] 滚动停止后数据正确显示
- [ ] 选择功能正常工作
- [ ] 导出功能可以导出所有数据
- [ ] 窗口调整大小后表格正常显示

### 4. 控制台验证命令

```javascript
// 检查 Clusterize 是否启用
const instance = DataTableManager.getInstance('virtualTable');
console.log('Clusterize enabled:', instance.clusterize !== null);
console.log('Total rows:', instance.data.length);
console.log('Filtered rows:', instance.filteredData.length);

// 测试性能
console.time('Scroll to bottom');
document.getElementById('virtualTable-scrollArea').scrollTop = 999999;
console.timeEnd('Scroll to bottom');

// 验证可见行数
const visibleRows = document.querySelectorAll('#virtualTable-tbody tr').length;
console.log('Visible rows in DOM:', visibleRows); // 应该远少于总行数
```

## 常见问题

### Q: Clusterize.js 未加载怎么办？

A: 组件会自动从 CDN 加载。如果需要使用本地文件：

1. 下载 Clusterize.js：
   ```bash
   wget https://cdn.jsdelivr.net/npm/clusterize.js@0.18.0/clusterize.min.js
   wget https://cdn.jsdelivr.net/npm/clusterize.js@0.18.0/clusterize.min.css
   ```

2. 放置到 `/static/vendor/` 目录

3. 在 base.html 中引入本地文件

### Q: 如何处理超大数据集（10万+）？

A: 建议采用以下策略：

1. **服务端分页**：对于分析型应用，使用服务端分页
2. **数据聚合**：在后端进行数据聚合，只返回必要的汇总数据
3. **懒加载**：实现滚动到底部时加载更多数据
4. **Web Worker**：对于复杂的数据处理，使用 Web Worker 避免阻塞主线程

### Q: 如何自定义单元格渲染？

A: 在列定义中使用 type 或在 JavaScript 中扩展 formatCellValue 方法：

```javascript
// 扩展格式化方法
const instance = DataTableManager.getInstance('myTable');
const originalFormat = instance.formatCellValue.bind(instance);

instance.formatCellValue = function(value, column) {
    if (column.key === 'custom_field') {
        return `<span class="custom">${value}</span>`;
    }
    return originalFormat(value, column);
};
```

## 最佳实践

1. **选择合适的模式**
   - 数据频繁更新：使用服务端分页
   - 需要客户端筛选/排序：使用虚拟滚动
   - 数据量 < 1000：可以使用任一模式

2. **优化数据传输**
   - 只传输必要的字段
   - 使用 gzip 压缩
   - 考虑使用 WebSocket 实时更新

3. **提升用户体验**
   - 显示加载进度
   - 提供清晰的空状态
   - 保存用户的筛选/排序偏好

4. **安全考虑**
   - 验证分页参数防止 SQL 注入
   - 限制每页最大数量
   - 对敏感数据进行权限检查