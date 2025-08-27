# 设计规范（Design Specification）

## 设计系统概览

本设计系统基于教育培训行业的视觉需求，强调专业性、可信度和成长感。所有设计决策都经过精心考虑，确保在不同设备和使用场景下的一致性和可用性。

## 1. 颜色系统 (Color System)

### 主色调 (Primary Colors)
| Token 名称 | 值 | CSS 变量 | 使用场景 |
|-----------|-----|----------|---------|
| `color/primary` | #4A90E2 | `var(--color-primary)` | 主要按钮、链接、选中状态 |
| `color/primary-600` | #357ABD | `var(--color-primary-600)` | 按钮悬停、激活状态 |
| `color/primary-400` | #6BA3E5 | `var(--color-primary-400)` | 禁用状态、背景色 |

**使用示例：**
```css
.btn-primary {
  background-color: var(--color-primary);
}
.btn-primary:hover {
  background-color: var(--color-primary-600);
}
```

### 语义颜色 (Semantic Colors)
| Token 名称 | 值 | CSS 变量 | 使用场景 |
|-----------|-----|----------|---------|
| `color/success` | #52C41A | `var(--color-success)` | 成功提示、正增长 |
| `color/warning` | #FFC107 | `var(--color-warning)` | 警告信息、待处理状态 |
| `color/danger` | #DC3545 | `var(--color-danger)` | 错误提示、负增长 |
| `color/info` | #17A2B8 | `var(--color-info)` | 信息提示、帮助文本 |

### 中性色 (Neutral Colors)
| Token 名称 | 值 | CSS 变量 | 使用场景 |
|-----------|-----|----------|---------|
| `color/text` | #212529 | `var(--color-text)` | 主要文本 |
| `color/text-secondary` | #495057 | `var(--color-text-secondary)` | 次要文本、标签 |
| `color/muted` | #6C757D | `var(--color-muted)` | 禁用文本、提示文本 |
| `color/background` | #FFFFFF | `var(--color-background)` | 主背景 |
| `color/background-secondary` | #F8F9FA | `var(--color-background-secondary)` | 卡片背景、斑马纹 |
| `color/border` | #DEE2E6 | `var(--color-border)` | 边框、分割线 |

## 2. 间距系统 (Spacing System)

基于 8px 网格系统，确保视觉韵律和一致性。

| Token 名称 | 值 | CSS 变量 | 使用场景 |
|-----------|-----|----------|---------|
| `spacing/xs` | 4px | `var(--spacing-xs)` | 图标与文字间距 |
| `spacing/sm` | 8px | `var(--spacing-sm)` | 元素内部间距 |
| `spacing/md` | 16px | `var(--spacing-md)` | 卡片内边距 |
| `spacing/lg` | 24px | `var(--spacing-lg)` | 区块间距 |
| `spacing/xl` | 32px | `var(--spacing-xl)` | 页面section间距 |
| `spacing/2xl` | 48px | `var(--spacing-2xl)` | 大区块间距 |

**使用示例：**
```css
.card {
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-md);
}
```

## 3. 字体系统 (Typography System)

### 字体家族
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', 'Microsoft YaHei', sans-serif;
```

### 字体大小与行高
| Token 名称 | 字号 | 行高 | CSS 变量 | 使用场景 |
|-----------|------|------|----------|---------|
| `typography/h1` | 32px | 1.25 | `var(--font-size-h1)` | 页面标题 |
| `typography/h2` | 24px | 1.25 | `var(--font-size-h2)` | 区块标题 |
| `typography/h3` | 20px | 1.25 | `var(--font-size-h3)` | 卡片标题 |
| `typography/body` | 16px | 1.5 | `var(--font-size-body)` | 正文内容 |
| `typography/small` | 14px | 1.5 | `var(--font-size-small)` | 辅助文字 |
| `typography/caption` | 12px | 1.5 | `var(--font-size-caption)` | 标签、提示 |

### 字重
| Token 名称 | 值 | 使用场景 |
|-----------|-----|---------|
| `fontWeight/normal` | 400 | 正文 |
| `fontWeight/medium` | 500 | 强调文字 |
| `fontWeight/semibold` | 600 | 副标题 |
| `fontWeight/bold` | 700 | 标题、数值 |

## 4. 圆角系统 (Border Radius)

| Token 名称 | 值 | CSS 变量 | 使用场景 |
|-----------|-----|----------|---------|
| `radius/sm` | 4px | `var(--radius-sm)` | 按钮、输入框 |
| `radius/base` | 8px | `var(--radius-base)` | 卡片、容器 |
| `radius/md` | 12px | `var(--radius-md)` | 模态框 |
| `radius/lg` | 16px | `var(--radius-lg)` | 大卡片 |
| `radius/full` | 9999px | `var(--radius-full)` | 徽章、头像 |

## 5. 阴影系统 (Shadow System)

| Token 名称 | 值 | 使用场景 |
|-----------|-----|---------|
| `shadow/sm` | 0 1px 2px rgba(0,0,0,0.05) | 默认卡片 |
| `shadow/base` | 0 1px 3px rgba(0,0,0,0.1) | 悬停卡片 |
| `shadow/md` | 0 4px 6px rgba(0,0,0,0.1) | 弹出菜单 |
| `shadow/lg` | 0 10px 15px rgba(0,0,0,0.1) | 模态框 |
| `shadow/kpi` | 0 4px 12px rgba(0,0,0,0.08) | KPI卡片专用 |

## 6. 组件规范

### KPI Card 组件
```
尺寸：
- Desktop: 316px × 160px
- Mobile: 100% × 120px

内边距：24px
圆角：radius/base (8px)
阴影：shadow/kpi
背景：color/background

结构：
├── 标题 (typography/small, color/text-secondary)
├── 数值 (typography/h2, color/text, fontWeight/bold)
├── 趋势 (typography/caption, color/success 或 color/danger)
└── 图标区域 (40×40px, 右上角定位)
```

### Data Table Row 组件
```
高度：48px (固定)
内边距：0 16px
背景：
- 默认：color/background
- 悬停：color/background-secondary
边框：底部 1px solid color/border

列宽分配：
- 姓名：150px
- 电话：150px
- 邮箱：200px (可折叠)
- 状态：100px
- 来源：120px (可折叠)
- 收入：120px
- 地区：100px (可折叠)
- 创建时间：150px
- 操作：40px
```

## 7. 响应式断点

| 断点名称 | 值 | 设备类型 |
|---------|-----|---------|
| `breakpoint/sm` | 640px | 手机横屏 |
| `breakpoint/md` | 768px | 平板竖屏 |
| `breakpoint/lg` | 1024px | 平板横屏 |
| `breakpoint/xl` | 1280px | 笔记本 |
| `breakpoint/2xl` | 1536px | 桌面显示器 |

## 8. 动画规范

| Token 名称 | 值 | 使用场景 |
|-----------|-----|---------|
| `duration/fast` | 150ms | 悬停效果 |
| `duration/normal` | 300ms | 页面过渡 |
| `duration/slow` | 500ms | 复杂动画 |
| `easing/smooth` | cubic-bezier(0.4,0,0.2,1) | 所有过渡 |

## 9. 可访问性规范

### 颜色对比度要求
- 普通文本：最小 4.5:1
- 大文本（18px+）：最小 3:1
- 所有主要颜色均已验证符合 WCAG AA 标准

### 焦点状态
```css
:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
```

### 可点击区域
- 最小尺寸：44×44px (移动端)
- 最小尺寸：32×32px (桌面端)

## 10. 导出规范

### 图标导出
- 格式：SVG
- 命名：`icon-{name}.svg`
- 尺寸：24×24px (默认)

### 组件截图
- 格式：PNG
- 分辨率：@2x
- 命名规范：
  - `component-{name}-{state}@2x.png`
  - 示例：`kpi-card-default@2x.png`

### 切片导出
- KPI Cards: 包含完整阴影
- Table Rows: 不包含边框
- Buttons: 包含所有状态