# 组件状态规范

## KPI Card 状态

### Default (默认状态)
```
背景: color/background (#FFFFFF)
边框: 1px solid color/border (#DEE2E6)
阴影: shadow/kpi
内边距: spacing/lg (24px)
圆角: radius/base (8px)
```

### Hover (悬停状态)
```
背景: color/background (#FFFFFF)
边框: 1px solid color/border (#DEE2E6)
阴影: shadow/lg (提升效果)
变换: translateY(-2px)
过渡: all 300ms ease
```

### Loading (加载状态)
```
背景: color/background (#FFFFFF)
边框: 1px solid color/border (#DEE2E6)
内容: 骨架屏效果
- 标题: color/gray-200 (#E9ECEF), 60% 宽度
- 数值: color/gray-200 (#E9ECEF), 80% 宽度
```

### With Trend Up (上升趋势)
```
趋势文字: color/success (#52C41A)
趋势图标: TrendingUp Icon
图标颜色: color/success (#52C41A)
```

### With Trend Down (下降趋势)
```
趋势文字: color/danger (#DC3545)
趋势图标: TrendingDown Icon
图标颜色: color/danger (#DC3545)
```

## Data Table Row 状态

### Default (默认状态)
```
背景: color/background (#FFFFFF)
高度: 48px (固定)
边框底部: 1px solid color/border (#DEE2E6)
内边距: 0 spacing/md (16px)
```

### Hover (悬停状态)
```
背景: color/background-secondary (#F8F9FA)
鼠标指针: pointer
过渡: background-color 150ms ease
```

### Selected (选中状态)
```
背景: color/primary-light (#E7F3FF)
左边框: 3px solid color/primary (#4A90E2)
```

### Loading (加载状态)
```
背景: color/background (#FFFFFF)
内容: 闪烁动画
动画: pulse 2s infinite
```

## Button 状态

### Primary Button
#### Default
```
背景: color/primary (#4A90E2)
文字: color/white (#FFFFFF)
内边距: spacing/sm spacing/lg (8px 24px)
圆角: radius/sm (4px)
```

#### Hover
```
背景: color/primary-600 (#357ABD)
阴影: shadow/base
变换: translateY(-2px)
```

#### Active
```
背景: color/primary-600 (#357ABD)
变换: translateY(0)
```

#### Disabled
```
背景: color/gray-300 (#DEE2E6)
文字: color/gray-500 (#ADB5BD)
鼠标: not-allowed
```

### Secondary Button
#### Default
```
背景: color/background (#FFFFFF)
文字: color/text (#212529)
边框: 1px solid color/border (#DEE2E6)
```

#### Hover
```
背景: color/background-secondary (#F8F9FA)
边框: 1px solid color/primary (#4A90E2)
文字: color/primary (#4A90E2)
```

## Form Input 状态

### Default
```
背景: color/background (#FFFFFF)
边框: 1px solid color/border (#DEE2E6)
高度: 48px
内边距: 0 spacing/md (16px)
圆角: radius/sm (4px)
```

### Focus
```
边框: 1px solid color/primary (#4A90E2)
轮廓: 2px solid color/primary-light (#E7F3FF)
轮廓偏移: 2px
```

### Error
```
边框: 1px solid color/danger (#DC3545)
背景: color/danger-light (#FFF1F0)
```

### Disabled
```
背景: color/background-tertiary (#E9ECEF)
文字: color/muted (#6C757D)
鼠标: not-allowed
```

## Kebab Menu 状态

### Trigger Button
#### Default
```
背景: transparent
图标: MoreVertical (16×16px)
颜色: color/text-secondary (#495057)
内边距: spacing/xs (4px)
```

#### Hover
```
背景: color/background-secondary (#F8F9FA)
颜色: color/text (#212529)
圆角: radius/sm (4px)
```

### Dropdown Menu
#### Closed
```
显示: none
透明度: 0
变换: translateY(-4px)
```

#### Open
```
显示: block
透明度: 1
变换: translateY(0)
背景: color/background (#FFFFFF)
边框: 1px solid color/border (#DEE2E6)
阴影: shadow/dropdown
圆角: radius/sm (4px)
过渡: all 150ms ease
```

### Menu Item
#### Default
```
内边距: spacing/sm spacing/md (8px 16px)
文字: color/text (#212529)
字号: font-size/small (14px)
```

#### Hover
```
背景: color/background-secondary (#F8F9FA)
```

#### Danger Item
```
文字: color/danger (#DC3545)
```

#### Danger Hover
```
背景: color/danger-light (#FFF1F0)
```

## 响应式状态

### Mobile Breakpoint (< 768px)
```
KPI Card:
- 宽度: 100%
- 高度: 120px
- 内边距: spacing/md (16px)

Data Table:
- 横向滚动
- 最小宽度: 800px

Buttons:
- 宽度: 100% (堆叠布局)
- 间距: spacing/sm (8px)
```

### Tablet Breakpoint (768px - 1024px)
```
KPI Card:
- 网格: 2列
- 间距: spacing/md (16px)

Charts:
- 垂直堆叠
- 宽度: 100%
```

### Desktop Breakpoint (> 1024px)
```
KPI Card:
- 网格: 4列
- 间距: spacing/lg (24px)

Charts:
- 并排显示
- 比例: 2:1 (趋势图:分布图)
```

## 动画与过渡

### 标准过渡时长
```
快速: duration/fast (150ms) - 悬停效果
正常: duration/normal (300ms) - 页面切换
缓慢: duration/slow (500ms) - 复杂动画
```

### 缓动函数
```
平滑: easing/smooth - cubic-bezier(0.4, 0, 0.2, 1)
线性: easing/linear - linear
缓入: easing/easeIn - ease-in
缓出: easing/easeOut - ease-out
```

### 常用动画
```css
/* 淡入 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 滑入 */
@keyframes slideIn {
  from { opacity: 0; transform: translateX(-20px); }
  to { opacity: 1; transform: translateX(0); }
}

/* 脉冲 */
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
```