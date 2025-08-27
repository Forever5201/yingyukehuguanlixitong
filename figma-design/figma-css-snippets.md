# Figma CSS 代码片段

以下是可以直接从 Figma Code 面板复制的 CSS 代码片段，已经使用 Design Tokens 变量。

## 1. KPI Card 组件

### 基础样式
```css
/* Component / KpiCard / Default */
.kpi-card {
  /* Auto Layout */
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: var(--spacing-lg);
  gap: var(--spacing-sm);
  
  /* Frame */
  width: 316px;
  height: 160px;
  
  /* Style */
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-base);
  box-shadow: var(--shadow-kpi);
  
  /* Transition */
  transition: all var(--duration-normal) var(--easing-smooth);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

/* Hover State */
.kpi-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

/* Title */
.kpi-card__title {
  /* Typography */
  font-family: var(--font-family-base);
  font-size: var(--font-size-small);
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-normal);
  color: var(--color-text-secondary);
}

/* Value */
.kpi-card__value {
  /* Typography */
  font-family: var(--font-family-base);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-tight);
  color: var(--color-text);
}

/* Trend */
.kpi-card__trend {
  /* Auto Layout */
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: var(--spacing-xs);
  
  /* Typography */
  font-size: var(--font-size-caption);
  font-weight: var(--font-weight-medium);
}

.kpi-card__trend--up {
  color: var(--color-success);
}

.kpi-card__trend--down {
  color: var(--color-danger);
}

/* Icon Container */
.kpi-card__icon {
  /* Position */
  position: absolute;
  top: var(--spacing-lg);
  right: var(--spacing-lg);
  
  /* Frame */
  width: 40px;
  height: 40px;
  
  /* Style */
  background: var(--color-primary-400);
  border-radius: var(--radius-full);
  
  /* Flex */
  display: flex;
  align-items: center;
  justify-content: center;
  
  /* Icon Color */
  color: var(--color-primary-600);
}
```

## 2. Data Table 组件

### Table Container
```css
/* Component / DataTable / Container */
.data-table {
  /* Frame */
  width: 100%;
  background: var(--color-background);
  border-radius: var(--radius-base);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

/* Table Header */
.data-table__header {
  /* Auto Layout */
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0 var(--spacing-md);
  height: 48px;
  
  /* Style */
  background: var(--color-background-secondary);
  border-bottom: 1px solid var(--color-border);
  
  /* Typography */
  font-size: var(--font-size-small);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
}

/* Table Row */
.data-table__row {
  /* Auto Layout */
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0 var(--spacing-md);
  height: 48px;
  
  /* Style */
  background: var(--color-background);
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
  transition: background-color var(--duration-fast) var(--easing-smooth);
}

/* Row Hover */
.data-table__row:hover {
  background: var(--color-background-secondary);
}

/* Table Cell */
.data-table__cell {
  /* Typography */
  font-size: var(--font-size-small);
  color: var(--color-text);
  
  /* Layout */
  display: flex;
  align-items: center;
  padding-right: var(--spacing-md);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Cell Widths */
.data-table__cell--name { width: 150px; }
.data-table__cell--phone { width: 150px; }
.data-table__cell--email { width: 200px; }
.data-table__cell--status { width: 100px; }
.data-table__cell--source { width: 120px; }
.data-table__cell--revenue { width: 120px; }
.data-table__cell--region { width: 100px; }
.data-table__cell--date { width: 150px; }
.data-table__cell--actions { width: 40px; }

/* Status Badge */
.status-badge {
  /* Auto Layout */
  display: inline-flex;
  align-items: center;
  padding: var(--spacing-xs) var(--spacing-sm);
  
  /* Style */
  border-radius: var(--radius-full);
  font-size: var(--font-size-caption);
  font-weight: var(--font-weight-medium);
}

.status-badge--active {
  background: var(--color-success-light);
  color: var(--color-success-dark);
}

.status-badge--inactive {
  background: var(--color-gray-100);
  color: var(--color-gray-600);
}

.status-badge--pending {
  background: var(--color-warning-light);
  color: var(--color-warning-dark);
}
```

### Kebab Menu
```css
/* Component / KebabMenu */
.kebab-menu {
  position: relative;
}

.kebab-menu__trigger {
  /* Reset Button */
  background: none;
  border: none;
  padding: var(--spacing-xs);
  cursor: pointer;
  color: var(--color-text-secondary);
  
  /* Hover */
  transition: color var(--duration-fast) var(--easing-smooth);
}

.kebab-menu__trigger:hover {
  color: var(--color-text);
}

.kebab-menu__dropdown {
  /* Position */
  position: absolute;
  right: 0;
  top: 100%;
  margin-top: var(--spacing-xs);
  
  /* Frame */
  min-width: 120px;
  
  /* Style */
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-dropdown);
  
  /* Hidden by default */
  opacity: 0;
  visibility: hidden;
  transform: translateY(-4px);
  transition: all var(--duration-fast) var(--easing-smooth);
}

.kebab-menu__dropdown--open {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.kebab-menu__item {
  /* Auto Layout */
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  
  /* Style */
  background: none;
  border: none;
  width: 100%;
  cursor: pointer;
  
  /* Typography */
  font-size: var(--font-size-small);
  color: var(--color-text);
  text-align: left;
  
  /* Transition */
  transition: background-color var(--duration-fast) var(--easing-smooth);
}

.kebab-menu__item:hover {
  background-color: var(--color-background-secondary);
}

.kebab-menu__item--danger {
  color: var(--color-danger);
}

.kebab-menu__item--danger:hover {
  background-color: var(--color-danger-light);
}
```

## 3. 按钮样式

```css
/* Component / Button / Primary */
.btn {
  /* Auto Layout */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-lg);
  
  /* Style */
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  
  /* Typography */
  font-family: var(--font-family-base);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-normal);
  
  /* Transition */
  transition: all var(--duration-normal) var(--easing-smooth);
}

.btn--primary {
  background: var(--color-primary);
  color: var(--color-white);
}

.btn--primary:hover {
  background: var(--color-primary-600);
  transform: translateY(-2px);
  box-shadow: var(--shadow-base);
}

.btn--secondary {
  background: var(--color-background);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn--secondary:hover {
  background: var(--color-background-secondary);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.btn--success {
  background: var(--color-success);
  color: var(--color-white);
}

.btn--danger {
  background: var(--color-danger);
  color: var(--color-white);
}

/* Button Sizes */
.btn--small {
  padding: var(--spacing-xs) var(--spacing-md);
  font-size: var(--font-size-small);
}

.btn--large {
  padding: var(--spacing-md) var(--spacing-xl);
  font-size: var(--font-size-lg);
}
```

## 4. 表单控件

```css
/* Component / Input */
.form-input {
  /* Frame */
  width: 100%;
  height: 48px;
  padding: 0 var(--spacing-md);
  
  /* Style */
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  
  /* Typography */
  font-family: var(--font-family-base);
  font-size: var(--font-size-base);
  color: var(--color-text);
  
  /* Transition */
  transition: border-color var(--duration-fast) var(--easing-smooth);
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.form-input::placeholder {
  color: var(--color-muted);
}

/* Search Input */
.search-input {
  padding-left: var(--spacing-2xl);
}

.search-input__icon {
  position: absolute;
  left: var(--spacing-md);
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-secondary);
}

/* Filter Chip */
.filter-chip {
  /* Auto Layout */
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-md);
  
  /* Style */
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  
  /* Typography */
  font-size: var(--font-size-small);
  color: var(--color-text);
  
  /* Transition */
  transition: all var(--duration-fast) var(--easing-smooth);
  cursor: pointer;
}

.filter-chip--active {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.filter-chip:hover {
  border-color: var(--color-primary);
}
```

## 5. 响应式布局

```css
/* Dashboard Grid - Desktop */
@media (min-width: 1366px) {
  .dashboard-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--spacing-lg);
  }
  
  .chart-section {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: var(--spacing-lg);
  }
}

/* Dashboard Grid - Tablet */
@media (min-width: 768px) and (max-width: 1365px) {
  .dashboard-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
  }
  
  .chart-section {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }
}

/* Dashboard Grid - Mobile */
@media (max-width: 767px) {
  .dashboard-grid {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  .kpi-card {
    width: 100%;
    height: 120px;
  }
  
  .chart-section {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }
}
```

## 6. 动画与过渡

```css
/* Fade In Animation */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn var(--duration-normal) var(--easing-smooth);
}

/* Slide In Animation */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.animate-slide-in {
  animation: slideIn var(--duration-normal) var(--easing-smooth);
}

/* Pulse Animation */
@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.animate-pulse {
  animation: pulse 2s infinite;
}
```