# Dashboard 数据可视化组件文档

## 概述

本文档包含三个专为客户管理系统Dashboard设计的交互式图表组件：
- **TrendChart**: 趋势折线图
- **ChannelChart**: 渠道饼图/环形图
- **FunnelChart**: 转化漏斗图

## 组件详细说明

### 1. TrendChart（趋势折线图）

#### 用途
展示收入、客户数等指标随时间的变化趋势，支持多数据系列对比。

#### API
```tsx
<TrendChart
  data={trendData}
  timeRange="month"
  onPointClick={(point) => navigateToDetail(point)}
  onRangeChange={(range) => updateDateRange(range)}
  height={300}
  loading={false}
  showLegend={true}
  enableZoom={true}
  maxPoints={1000}
  exportFileName="revenue-trend"
/>
```

#### Props
| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| data | TrendDataPoint[] | required | 时间序列数据 |
| timeRange | 'day' \| 'week' \| 'month' \| 'quarter' \| 'year' | required | 时间聚合粒度 |
| onPointClick | (point: TrendDataPoint) => void | undefined | 数据点点击回调 |
| onRangeChange | (range: {start: Date, end: Date}) => void | undefined | 缩放范围变更回调 |
| height | number | 300 | 图表高度 |
| loading | boolean | false | 加载状态 |
| showLegend | boolean | true | 是否显示图例 |
| enableZoom | boolean | true | 是否启用缩放 |
| maxPoints | number | 1000 | 最大显示点数（性能优化） |
| exportFileName | string | 'trend-chart' | 导出文件名前缀 |

#### 数据格式
```typescript
interface TrendDataPoint {
  timestamp: string; // ISO 8601格式
  value: number;
  series: string; // 数据系列名称
  metadata?: {
    count?: number;
    average?: number;
    [key: string]: any;
  };
}
```

#### 交互功能
1. **点击数据点**: 触发onPointClick回调，可用于钻取详情
2. **拖拽缩放**: 支持X轴拖拽选择时间范围
3. **滚轮缩放**: 鼠标滚轮放大/缩小
4. **悬停提示**: 显示日期、数值、数量、平均值等信息
5. **图例交互**: 点击图例显示/隐藏数据系列

### 2. ChannelChart（渠道分布图）

#### 用途
展示不同渠道的收入/客户分布情况，支持饼图和环形图两种形式。

#### API
```tsx
<ChannelChart
  data={channelData}
  type="doughnut"
  onSegmentClick={(segment) => filterByChannel(segment)}
  height={300}
  loading={false}
  showLegend={true}
  showPercentage={true}
  exportFileName="channel-distribution"
  colorScheme="default"
/>
```

#### Props
| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| data | ChannelDataPoint[] | required | 渠道数据 |
| type | 'pie' \| 'doughnut' | 'doughnut' | 图表类型 |
| onSegmentClick | (segment: ChannelDataPoint) => void | undefined | 扇区点击回调 |
| height | number | 300 | 图表高度 |
| loading | boolean | false | 加载状态 |
| showLegend | boolean | true | 是否显示图例 |
| showPercentage | boolean | true | 是否显示百分比 |
| exportFileName | string | 'channel-distribution' | 导出文件名前缀 |
| colorScheme | 'default' \| 'warm' \| 'cool' \| 'custom' | 'default' | 配色方案 |
| customColors | string[] | undefined | 自定义颜色数组 |

#### 数据格式
```typescript
interface ChannelDataPoint {
  channel: string;
  value: number;
  percentage: number;
  metadata?: {
    customers?: number;
    averageValue?: number;
    conversionRate?: number;
    [key: string]: any;
  };
}
```

#### 交互功能
1. **点击扇区**: 触发onSegmentClick回调，可用于筛选该渠道数据
2. **悬停效果**: 扇区突出显示，展示详细信息
3. **图例交互**: 点击图例项显示/隐藏对应扇区
4. **中心统计**: 环形图中心显示总计数值

### 3. FunnelChart（转化漏斗图）

#### 用途
展示客户转化流程中各阶段的转化情况和流失分析。

#### API
```tsx
<FunnelChart
  data={funnelData}
  onStageClick={(stage, dropoffData) => analyzeStage(stage)}
  height={400}
  loading={false}
  showValues={true}
  showPercentage={true}
  showConversionRate={true}
  orientation="vertical"
  exportFileName="conversion-funnel"
  colorGradient={true}
/>
```

#### Props
| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| data | FunnelStage[] | required | 漏斗阶段数据 |
| onStageClick | (stage: FunnelStage, dropoff?: any) => void | undefined | 阶段点击回调 |
| height | number | 400 | 图表高度 |
| loading | boolean | false | 加载状态 |
| showValues | boolean | true | 是否显示数值 |
| showPercentage | boolean | true | 是否显示百分比 |
| showConversionRate | boolean | true | 是否显示转化率 |
| orientation | 'vertical' \| 'horizontal' | 'vertical' | 漏斗方向 |
| exportFileName | string | 'conversion-funnel' | 导出文件名前缀 |
| colorGradient | boolean | true | 是否使用渐变色 |

#### 数据格式
```typescript
interface FunnelStage {
  stage: string;
  value: number;
  percentage: number;
  conversionRate?: number;
  metadata?: {
    duration?: number; // 平均停留时间（天）
    dropoffReasons?: string[]; // 流失原因
    averageValue?: number; // 平均价值
    [key: string]: any;
  };
}
```

#### 交互功能
1. **点击阶段**: 触发onStageClick回调，传递阶段数据和流失分析
2. **悬停效果**: 高亮显示阶段，展示流失分析面板
3. **流失分析**: 自动计算并显示阶段间的流失数据和原因

## 性能优化建议

### 1. 数据量优化
- **降采样策略**: 当数据点超过1000个时，建议后端实现降采样
  ```javascript
  // 后端降采样示例
  function downsample(data, maxPoints = 1000) {
    if (data.length <= maxPoints) return data;
    const factor = Math.ceil(data.length / maxPoints);
    return data.filter((_, index) => index % factor === 0);
  }
  ```

- **前端虚拟化**: TrendChart组件已内置降采样逻辑
  ```typescript
  const downsampledData = useMemo(() => {
    if (data.length <= maxPoints) return data;
    const factor = Math.ceil(data.length / maxPoints);
    return data.filter((_, index) => index % factor === 0);
  }, [data, maxPoints]);
  ```

### 2. 渲染优化
- 使用React.memo包装组件避免不必要的重渲染
- 图表实例缓存，仅在数据变化时重新创建
- Canvas渲染而非SVG，提升大数据量性能

### 3. 懒加载
- Chart.js按需加载
  ```javascript
  const Chart = React.lazy(() => import('chart.js/auto'));
  ```

## 无障碍支持

### 1. 键盘导航
- Tab键遍历图表元素
- Enter/Space键触发点击事件
- 方向键在数据点间导航

### 2. 屏幕阅读器
- 每个图表都包含隐藏的表格版本
- 完整的ARIA标签
- 角色和描述属性

### 3. 替代文本
```html
<canvas role="img" aria-label="收入趋势图表" />
<table class="sr-only">
  <caption>收入趋势数据表</caption>
  <!-- 完整的表格数据 -->
</table>
```

## 导出功能

所有图表都支持两种导出格式：

### 1. PNG图片导出
- 保持当前图表的视觉样式
- 文件名包含日期戳
- 支持高DPI屏幕

### 2. CSV数据导出
- 包含完整的原始数据
- UTF-8编码，支持中文
- Excel友好格式

## 验收标准

✅ **视觉占比**: 在1366px宽度下，每个图表占Dashboard宽度的30-50%
✅ **Tooltip信息**: 显示至少3个关键字段（value, series/channel/stage, timestamp/metadata）
✅ **交互响应**: 所有图表支持点击交互和数据钻取
✅ **数据导出**: PNG和CSV导出功能正常工作
✅ **性能表现**: 10k数据点降采样后流畅渲染（<100ms）
✅ **响应式设计**: 支持移动端自适应布局
✅ **无障碍**: 通过WCAG 2.1 AA级别测试

## 使用示例

### 完整的Dashboard集成
```tsx
import { TrendChart, ChannelChart, FunnelChart } from './charts';
import { generateMockTrendData, generateMockChannelData, generateMockFunnelData } from './charts';

function Dashboard() {
  const [timeRange, setTimeRange] = useState('month');
  const trendData = generateMockTrendData(30);
  const channelData = generateMockChannelData();
  const funnelData = generateMockFunnelData();

  return (
    <div className="dashboard-charts">
      <div className="chart-row">
        <div className="chart-col" style={{ width: '50%' }}>
          <h3>收入趋势</h3>
          <TrendChart
            data={trendData}
            timeRange={timeRange}
            onPointClick={(point) => {
              console.log('Navigate to:', point);
              // 跳转到客户列表，带上时间筛选
              window.location.href = `/customers?date=${point.timestamp}&series=${point.series}`;
            }}
          />
        </div>
        <div className="chart-col" style={{ width: '50%' }}>
          <h3>渠道分布</h3>
          <ChannelChart
            data={channelData}
            onSegmentClick={(segment) => {
              console.log('Filter by channel:', segment);
              // 跳转到客户列表，带上渠道筛选
              window.location.href = `/customers?channel=${segment.channel}`;
            }}
          />
        </div>
      </div>
      <div className="chart-row">
        <div className="chart-col" style={{ width: '100%' }}>
          <h3>转化漏斗</h3>
          <FunnelChart
            data={funnelData}
            onStageClick={(stage, dropoff) => {
              console.log('Analyze stage:', stage, dropoff);
              // 显示该阶段的详细分析
              showStageAnalysis(stage);
            }}
          />
        </div>
      </div>
    </div>
  );
}
```

## 注意事项

1. **数据更新频率**: 建议使用WebSocket或轮询更新实时数据，但不要过于频繁（建议5-10秒）
2. **内存管理**: 组件卸载时会自动销毁图表实例，避免内存泄漏
3. **错误处理**: 所有组件都有loading和错误状态处理
4. **浏览器兼容**: 需要支持Canvas API的现代浏览器（Chrome 60+, Firefox 55+, Safari 11+）