# Flask + Jinja2 设计系统集成指南

## 1. base.html 修改

在 `app/templates/base.html` 的 `<head>` 部分添加以下内容：

```html
<!-- 在现有 CSS 之后添加 -->
<!-- Design System Tokens -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/tokens.css') }}">

<!-- Clusterize.js for virtual scrolling -->
<link rel="stylesheet" href="{{ url_for('static', filename='vendor/clusterize.css') }}">

<!-- 在 jQuery 和 Chart.js 之后添加 -->
<!-- Clusterize.js -->
<script src="{{ url_for('static', filename='vendor/clusterize.min.js') }}"></script>

<!-- Data Table Virtual Scroll -->
<script src="{{ url_for('static', filename='js/data-table.js') }}"></script>

<!-- Unified Charts Configuration -->
<script src="{{ url_for('static', filename='js/charts.js') }}"></script>
```

完整的修改示例：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}客户管理系统{% endblock %}</title>
    
    <!-- 原有样式 -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    
    <!-- 现代化UI增强样式 -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/modern-ui.css') }}">
    
    <!-- 教育培训系统专属样式 -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/education-ui.css') }}">
    
    <!-- Design System Tokens (新增) -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/tokens.css') }}">
    
    <!-- 第三方库 -->
    <link rel="stylesheet" href="{{ url_for('static', filename='vendor/fontawesome/all.min.css') }}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">
    
    <!-- Clusterize.js CSS (新增) -->
    <link rel="stylesheet" href="{{ url_for('static', filename='vendor/clusterize.css') }}">
    
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    
    <!-- Chart.js for data visualization -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    
    {% block head %}{% endblock %}
</head>
<body>
    <!-- 原有 body 内容保持不变 -->
    
    <!-- 在原有 scripts 之后添加 -->
    <script src="{{ url_for('static', filename='js/notification.js') }}"></script>
    <script src="{{ url_for('static', filename='js/course-management.js') }}" defer></script>
    <script src="{{ url_for('static', filename='js/app.js') }}" defer></script>
    
    <!-- 新增的脚本 -->
    <script src="{{ url_for('static', filename='vendor/clusterize.min.js') }}"></script>
    <script src="{{ url_for('static', filename='js/data-table.js') }}"></script>
    <script src="{{ url_for('static', filename='js/charts.js') }}"></script>
</body>
</html>
```

## 2. 文件目录结构

请按照以下结构放置文件：

```
app/
├── static/
│   ├── css/
│   │   └── tokens.css              # 设计令牌 CSS
│   ├── js/
│   │   ├── data-table.js           # 数据表格虚拟滚动逻辑
│   │   └── charts.js               # 统一图表配置
│   └── vendor/
│       ├── clusterize.min.js       # Clusterize.js 库
│       └── clusterize.css          # Clusterize.js 样式
├── templates/
│   ├── components/
│   │   ├── kpi_card.html           # KPI 卡片组件
│   │   ├── filter_panel.html       # 筛选面板组件
│   │   └── data_table.html         # 数据表格组件
│   └── example_dashboard.html      # 示例仪表板页面
```

## 3. 在现有页面中使用组件

### 使用 KPI 卡片

```jinja2
{% from 'components/kpi_card.html' import kpi_card %}

<div class="kpi-grid">
    {{ kpi_card('1,234', '总客户数', 12.5, 'fa-users') }}
    {{ kpi_card('¥89,456', '本月收入', -3.2, 'fa-dollar-sign') }}
</div>
```

### 使用筛选面板

```jinja2
{% include 'components/filter_panel.html' %}
```

### 使用数据表格（服务端分页）

```jinja2
{% from 'components/data_table.html' import data_table %}

{{ data_table(
    columns=[
        {'key': 'name', 'label': '姓名', 'sortable': True},
        {'key': 'phone', 'label': '电话'},
        {'key': 'status', 'label': '状态', 'type': 'status'}
    ],
    rows=customers,  # 从后端传入的数据
    page=current_page,
    total_count=total_customers,
    per_page=50
) }}
```

### 使用数据表格（虚拟滚动）

```jinja2
{{ data_table(
    columns=[...],
    mode='virtual',
    table_id='myVirtualTable'
) }}

<script>
document.addEventListener('DOMContentLoaded', function() {
    // 从 JSON 文件加载数据
    initVirtualTable('myVirtualTable', '/static/json/customers.json');
    
    // 或使用内联数据
    const data = {{ customers_json | tojson | safe }};
    initVirtualTable('myVirtualTable', data);
});
</script>
```

### 使用统一图表

```jinja2
<canvas id="revenueChart"></canvas>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const data = {
        labels: {{ chart_labels | tojson | safe }},
        datasets: [{
            label: '收入',
            data: {{ chart_data | tojson | safe }},
            isCurrency: true
        }]
    };
    
    const chart = initTrendChart('revenueChart', data);
    
    // 导出按钮
    document.getElementById('exportBtn').onclick = function() {
        exportChartDataAsCSV(chart, 'revenue_report');
    };
});
</script>
```

## 4. 后端数据准备

### 服务端分页示例

```python
@app.route('/customers')
def customers():
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # 应用筛选
    query = Customer.query
    if request.args.get('status'):
        query = query.filter_by(status=request.args.get('status'))
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page)
    
    return render_template('customers.html',
        customers=pagination.items,
        current_page=page,
        total_customers=pagination.total
    )
```

### 虚拟滚动数据准备

```python
@app.route('/api/customers/all')
def customers_all():
    customers = Customer.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'phone': c.phone,
        'status': c.status,
        'created_at': c.created_at.isoformat()
    } for c in customers])
```

## 5. 本地测试

### 启动 Flask 开发服务器

```bash
cd /path/to/your/project
python run.py
```

### 访问测试页面

- 示例仪表板：http://localhost:5000/example_dashboard
- 其他集成了组件的页面：根据您的路由配置访问

### 添加示例路由（如果需要）

在 `app/routes.py` 中添加：

```python
@main_bp.route('/example_dashboard')
def example_dashboard():
    return render_template('example_dashboard.html')
```

## 6. 性能优化建议

1. **大数据集处理**：
   - 数据量 < 2000 条：使用服务端分页
   - 数据量 > 2000 条：使用虚拟滚动
   - 数据量 > 10000 条：考虑后端数据聚合

2. **图表优化**：
   - 使用 `decimation` 插件减少数据点
   - 限制时间范围
   - 使用聚合数据而非原始数据

3. **缓存策略**：
   - 静态资源设置合适的缓存头
   - 考虑使用 Redis 缓存频繁查询的数据

## 7. 故障排除

### 常见问题

1. **Clusterize.js 不工作**
   - 检查是否正确引入了 CSS 和 JS 文件
   - 确保表格结构符合要求（需要 thead 和 tbody）
   - 查看浏览器控制台错误

2. **图表不显示**
   - 确保 Canvas 元素有明确的高度
   - 检查数据格式是否正确
   - 验证 Chart.js 是否正确加载

3. **样式冲突**
   - tokens.css 应在其他样式之后加载
   - 使用浏览器开发工具检查 CSS 优先级
   - 必要时使用更具体的选择器

### 调试模式

在浏览器控制台运行：

```javascript
// 检查组件是否正确加载
console.log('Clusterize loaded:', typeof Clusterize);
console.log('Chart.js loaded:', typeof Chart);
console.log('Virtual table function:', typeof initVirtualTable);
```