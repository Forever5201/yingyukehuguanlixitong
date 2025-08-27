# Chart.js 统一配置集成指南

## 概述

`charts.js` 提供了统一的 Chart.js 配置和管理功能，包括：
- 默认配置选项（颜色、字体、动画等）
- 三种图表类型的初始化函数（趋势图、饼图、柱状图）
- 强大的 tooltip 显示（value + series + timestamp）
- CSV 导出功能
- 时区支持

## 快速开始

### 1. 在 base.html 中引入

```html
<!-- 在 Chart.js 之后引入 -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
<script src="{{ url_for('static', filename='js/charts.js') }}"></script>
```

### 2. 在模板中使用

#### 趋势图（折线图/面积图）

```html
<!-- HTML -->
<div class="chart-container" style="position: relative; height: 300px;">
    <canvas id="revenueChart"></canvas>
</div>
<button onclick="exportChartDataAsCSV(revenueChart, 'revenue_report')">导出CSV</button>

<!-- JavaScript -->
<script>
// 准备数据
const revenueData = {
    labels: {{ dates | tojson }},  // ['2024-01-01', '2024-01-02', ...]
    datasets: [{
        label: '收入',
        data: {{ revenues | tojson }},  // [1000, 1500, 1200, ...]
        isCurrency: true,  // 标记为货币类型
        fill: true  // 填充区域
    }, {
        label: '订单数',
        data: {{ orders | tojson }},
        fill: false,
        yAxisID: 'y1'  // 使用右侧 Y 轴
    }]
};

// 自定义配置
const revenueOptions = {
    scales: {
        y: {
            position: 'left',
            isCurrency: true  // Y轴格式化为货币
        },
        y1: {
            position: 'right',
            grid: {
                drawOnChartArea: false
            }
        }
    },
    plugins: {
        title: {
            display: true,
            text: '收入趋势分析'
        }
    }
};

// 初始化图表
const revenueChart = initTrendChart('revenueChart', revenueData, revenueOptions);
</script>
```

#### 饼图/圆环图

```html
<!-- HTML -->
<div class="chart-container" style="position: relative; height: 300px; width: 300px;">
    <canvas id="channelChart"></canvas>
</div>

<!-- JavaScript -->
<script>
const channelData = {
    labels: ['淘宝', '微信', '抖音', '小红书', '其他'],
    datasets: [{
        data: [35, 25, 20, 15, 5],
        isCurrency: false  // 显示数值而非货币
    }]
};

// 初始化为圆环图
const channelChart = initPieChart('channelChart', channelData, {
    type: 'doughnut',  // 或 'pie' 饼图
    plugins: {
        title: {
            display: true,
            text: '渠道分布'
        }
    }
});
</script>
```

#### 柱状图

```html
<!-- HTML -->
<div class="chart-container" style="position: relative; height: 300px;">
    <canvas id="performanceChart"></canvas>
</div>

<!-- JavaScript -->
<script>
const performanceData = {
    labels: ['张三', '李四', '王五', '赵六'],
    datasets: [{
        label: '本月业绩',
        data: [45000, 38000, 52000, 41000],
        isCurrency: true
    }, {
        label: '上月业绩',
        data: [42000, 40000, 48000, 39000],
        isCurrency: true
    }]
};

const performanceChart = initBarChart('performanceChart', performanceData, {
    plugins: {
        title: {
            display: true,
            text: '员工业绩对比'
        }
    }
});
</script>
```

## 从现有代码迁移

### 迁移前（分散的配置）

```javascript
// 原始代码
const ctx = document.getElementById('myChart').getContext('2d');
const myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: dates,
        datasets: [{
            label: '销售额',
            data: sales,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return '¥' + context.parsed.y;
                    }
                }
            }
        }
    }
});
```

### 迁移后（使用 charts.js）

```javascript
// 新代码
const salesData = {
    labels: dates,
    datasets: [{
        label: '销售额',
        data: sales,
        isCurrency: true  // 自动格式化为货币
    }]
};

const salesChart = initTrendChart('myChart', salesData);

// 导出功能
document.getElementById('exportBtn').onclick = () => {
    exportChartDataAsCSV(salesChart, 'sales_report');
};
```

## 高级功能

### 1. 时区支持

```javascript
// 设置默认时区
ChartManager.setDefaultTimezone('America/New_York');

// 或在初始化时指定
const chart = initTrendChart('chart1', data, options, 'Europe/London');
```

### 2. 自定义 Tooltip

```javascript
const data = {
    labels: dates,
    datasets: [{
        label: '订单',
        data: orders,
        // 添加额外数据
        additionalData: orders.map(order => ({
            '客户数': order.customerCount,
            '平均金额': order.avgAmount
        }))
    }]
};
```

### 3. CSV 导出选项

```javascript
exportChartDataAsCSV(chart, 'report', {
    includeTimestamp: true,      // 包含导出时间戳
    includeSummary: true,        // 包含汇总行
    dateFormat: 'YYYY-MM-DD',    // 日期格式
    timezone: 'Asia/Shanghai'    // 时区
});
```

### 4. 动态更新数据

```javascript
// 获取新数据
const newData = {
    labels: newDates,
    datasets: [{
        label: '新数据',
        data: newValues
    }]
};

// 更新图表
ChartManager.updateChartData(myChart, newData, true);  // true = 带动画
```

### 5. 多 Y 轴配置

```javascript
const multiAxisData = {
    labels: dates,
    datasets: [{
        label: '销售额（元）',
        data: sales,
        yAxisID: 'y',
        isCurrency: true
    }, {
        label: '转化率（%）',
        data: conversionRates,
        yAxisID: 'y1',
        isPercentage: true
    }]
};

const options = {
    scales: {
        y: {
            type: 'linear',
            display: true,
            position: 'left',
            isCurrency: true
        },
        y1: {
            type: 'linear',
            display: true,
            position: 'right',
            isPercentage: true,
            grid: {
                drawOnChartArea: false
            }
        }
    }
};

const multiAxisChart = initTrendChart('multiChart', multiAxisData, options);
```

## 完整的 Jinja2 模板示例

```jinja2
{% extends "base.html" %}

{% block content %}
<div class="dashboard">
    <!-- 收入趋势图 -->
    <div class="card">
        <div class="card-header">
            <h3>收入趋势</h3>
            <button class="btn btn-sm" onclick="exportChartDataAsCSV(revenueTrend, 'revenue')">
                <i class="fas fa-download"></i> 导出
            </button>
        </div>
        <div class="card-body">
            <canvas id="revenueTrend" style="height: 300px;"></canvas>
        </div>
    </div>

    <!-- 渠道分布 -->
    <div class="card">
        <div class="card-header">
            <h3>渠道分布</h3>
        </div>
        <div class="card-body">
            <canvas id="channelPie" style="height: 300px;"></canvas>
        </div>
    </div>
</div>

<script>
// 从后端传入的数据
const chartData = {
    revenue: {
        labels: {{ revenue_dates | tojson }},
        values: {{ revenue_values | tojson }}
    },
    channels: {
        labels: {{ channel_names | tojson }},
        values: {{ channel_values | tojson }}
    }
};

// 初始化图表
let revenueTrend, channelPie;

document.addEventListener('DOMContentLoaded', function() {
    // 收入趋势图
    revenueTrend = initTrendChart('revenueTrend', {
        labels: chartData.revenue.labels,
        datasets: [{
            label: '日收入',
            data: chartData.revenue.values,
            isCurrency: true,
            fill: true
        }]
    }, {
        plugins: {
            title: {
                display: true,
                text: '最近30天收入趋势'
            }
        }
    });

    // 渠道分布图
    channelPie = initPieChart('channelPie', {
        labels: chartData.channels.labels,
        datasets: [{
            data: chartData.channels.values,
            isCurrency: true
        }]
    });
});

// 页面卸载时清理
window.addEventListener('beforeunload', function() {
    if (revenueTrend) ChartManager.destroyChart(revenueTrend);
    if (channelPie) ChartManager.destroyChart(channelPie);
});
</script>
{% endblock %}
```

## Flask 后端数据准备

```python
from datetime import datetime, timedelta
import json

@app.route('/dashboard')
def dashboard():
    # 准备最近30天的数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # 查询收入数据
    revenue_data = db.session.query(
        func.date(Order.created_at).label('date'),
        func.sum(Order.amount).label('total')
    ).filter(
        Order.created_at.between(start_date, end_date)
    ).group_by(
        func.date(Order.created_at)
    ).all()
    
    # 格式化数据
    revenue_dates = []
    revenue_values = []
    
    for data in revenue_data:
        revenue_dates.append(data.date.isoformat())
        revenue_values.append(float(data.total))
    
    # 查询渠道数据
    channel_data = db.session.query(
        Customer.source,
        func.count(Customer.id).label('count')
    ).group_by(Customer.source).all()
    
    channel_names = [c.source for c in channel_data]
    channel_values = [c.count for c in channel_data]
    
    return render_template('dashboard.html',
        revenue_dates=revenue_dates,
        revenue_values=revenue_values,
        channel_names=channel_names,
        channel_values=channel_values
    )
```

## 性能优化建议

### 1. 大数据集处理

```javascript
// 对于超过 1000 个数据点，考虑数据抽样
const sampleData = (data, maxPoints = 500) => {
    if (data.length <= maxPoints) return data;
    
    const step = Math.ceil(data.length / maxPoints);
    return data.filter((_, index) => index % step === 0);
};

// 使用
const sampledData = {
    labels: sampleData(allDates),
    datasets: [{
        label: '销售额',
        data: sampleData(allSales)
    }]
};
```

### 2. 延迟加载

```javascript
// 使用 Intersection Observer 延迟加载图表
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const chartId = entry.target.id;
            initializeChart(chartId);
            observer.unobserve(entry.target);
        }
    });
});

// 观察所有图表容器
document.querySelectorAll('.chart-container canvas').forEach(canvas => {
    observer.observe(canvas);
});
```

### 3. 响应式处理

```javascript
// 窗口大小改变时重新渲染
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        // 重新渲染所有图表
        Chart.instances.forEach(chart => {
            chart.resize();
        });
    }, 250);
});
```

## 常见问题

### Q: 如何显示中文时间格式？

```javascript
// 在 options 中配置
const options = {
    scales: {
        x: {
            adapters: {
                date: {
                    locale: 'zh-CN'
                }
            }
        }
    }
};
```

### Q: 如何处理空数据？

```javascript
// 在数据中添加 null 值
const data = {
    labels: ['1月', '2月', '3月', '4月'],
    datasets: [{
        data: [100, null, 150, 200],  // 2月无数据
        spanGaps: true  // 连接断点
    }]
};
```

### Q: 如何自定义颜色主题？

```javascript
// 修改默认颜色
ChartManager.colors.series = [
    '#FF6384',
    '#36A2EB',
    '#FFCE56',
    // ... 更多颜色
];

// 或在数据集中指定
const data = {
    datasets: [{
        backgroundColor: '#FF6384',
        borderColor: '#FF6384'
    }]
};
```

## 浏览器兼容性

- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

注意：需要支持 ES6 特性（const, let, arrow functions 等）