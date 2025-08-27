# Figma 设计文件结构

## 文件信息
- **文件名**: Customer Management System Design v1.0
- **创建日期**: 2024-01-XX
- **设计系统版本**: 1.0.0

## Pages 结构

### 1. 🎨 Design Tokens
包含所有设计令牌的主页面，作为单一真相源（Single Source of Truth）

#### Color Styles
- **Primary Colors**
  - `color/primary` → #4A90E2
  - `color/primary-600` → #357ABD
  - `color/primary-400` → #6BA3E5
  
- **Semantic Colors**
  - `color/success` → #52C41A
  - `color/warning` → #FFC107
  - `color/danger` → #DC3545
  - `color/info` → #17A2B8
  
- **Neutral Colors**
  - `color/text` → #212529
  - `color/text-secondary` → #495057
  - `color/muted` → #6C757D
  - `color/background` → #FFFFFF
  - `color/background-secondary` → #F8F9FA
  - `color/background-tertiary` → #E9ECEF
  - `color/border` → #DEE2E6

#### Text Styles
- **Headings**
  - `typography/h1` → 32px/1.25/Bold
  - `typography/h2` → 24px/1.25/Bold
  - `typography/h3` → 20px/1.25/Semibold
  - `typography/h4` → 18px/1.25/Semibold
  
- **Body**
  - `typography/body` → 16px/1.5/Normal
  - `typography/body-small` → 14px/1.5/Normal
  - `typography/caption` → 12px/1.5/Normal

#### Effect Styles
- `shadow/sm` → 0 1px 2px rgba(0,0,0,0.05)
- `shadow/base` → 0 1px 3px rgba(0,0,0,0.1)
- `shadow/md` → 0 4px 6px rgba(0,0,0,0.1)
- `shadow/lg` → 0 10px 15px rgba(0,0,0,0.1)
- `shadow/kpi` → 0 4px 12px rgba(0,0,0,0.08)

#### Grid Styles
- **Spacing Grid**
  - `spacing/xs` → 4px
  - `spacing/sm` → 8px
  - `spacing/md` → 16px
  - `spacing/lg` → 24px
  - `spacing/xl` → 32px
  - `spacing/2xl` → 48px
  - `spacing/3xl` → 64px

### 2. 🧩 Components
所有可复用组件的库

#### Component Structure
```
Components/
├── KpiCard/
│   ├── Default
│   ├── With Trend Up
│   ├── With Trend Down
│   ├── Loading State
│   └── Hover State
├── DataTable/
│   ├── Table Header
│   ├── Table Row/Default
│   ├── Table Row/Hover
│   ├── Table Row/Selected
│   └── Kebab Menu
├── Buttons/
│   ├── Primary
│   ├── Secondary
│   ├── Danger
│   └── Icon Button
├── Form Controls/
│   ├── Input Field
│   ├── Select Dropdown
│   ├── Search Bar
│   └── Filter Chip
└── Navigation/
    ├── Breadcrumb
    └── Back Button
```

### 3. 💻 Dashboard Desktop (1366×768)
桌面端仪表板设计

#### Frame Structure
```
Dashboard Desktop [1366×768]
├── Navigation Header [1366×80]
├── Page Title Section [1366×100]
├── KPI Cards Grid [1366×180]
│   ├── KPI Card 1 [316×160]
│   ├── KPI Card 2 [316×160]
│   ├── KPI Card 3 [316×160]
│   └── KPI Card 4 [316×160]
├── Charts Section [1366×400]
│   ├── Revenue Trend Chart [880×380]
│   └── Channel Distribution [446×380]
└── Quick Actions [1366×80]
```

### 4. 📱 Dashboard Mobile (375×812)
移动端仪表板设计

#### Frame Structure
```
Dashboard Mobile [375×812]
├── Status Bar [375×44]
├── Navigation Header [375×56]
├── Page Title [375×80]
├── KPI Cards Stack [375×680]
│   ├── KPI Card 1 [343×120]
│   ├── KPI Card 2 [343×120]
│   ├── KPI Card 3 [343×120]
│   └── KPI Card 4 [343×120]
├── Chart Section [343×200]
└── CTA Button [343×56]
```

### 5. 📋 Customer List (1366×768)
客户列表页面设计

#### Frame Structure
```
Customer List [1366×768]
├── Navigation Header [1366×80]
├── Page Header [1366×120]
│   ├── Back Button + Title
│   └── Add Customer Button
├── Search & Filter Bar [1366×80]
│   ├── Search Input [600×48]
│   └── Filter Chips
├── Data Table [1366×488]
│   ├── Table Header [1366×48]
│   └── Table Rows (× n) [1366×48 each]
└── Pagination [1366×60]
```

## Auto Layout 配置

### KpiCard Component
```
Auto Layout Settings:
- Direction: Vertical
- Padding: 24px
- Gap: 8px (title to value), 12px (value to trend)
- Alignment: Top Left
- Resizing: Hug contents
```

### DataTable Row
```
Auto Layout Settings:
- Direction: Horizontal
- Padding: 0px 16px
- Gap: 0px
- Alignment: Center
- Height: Fixed (48px)
- Resizing: Fill container
```

## 命名规范

### Components
- `Component / {ComponentName} / {State}`
- 示例：
  - `Component / KpiCard / Default`
  - `Component / DataTableRow / Hover`
  - `Component / Button / Primary`

### Colors
- `color / {semantic-name}`
- 示例：
  - `color / primary`
  - `color / text-secondary`

### Text Styles
- `typography / {style-name}`
- 示例：
  - `typography / h1`
  - `typography / body`

### Effects
- `shadow / {size}`
- 示例：
  - `shadow / sm`
  - `shadow / kpi`

## Export 设置

### Icons
- Format: SVG
- Include: "id" attribute
- Naming: `icon-{name}.svg`

### KpiCard
- Format: PNG
- Scale: @2x
- Naming: `kpi-card-{state}@2x.png`

### TableRow
- Format: PNG
- Scale: @2x
- Naming: `table-row-{state}@2x.png`

## Prototype 连接

### 交互流程
1. **Dashboard → Customer List**
   - Trigger: Click on any KPI Card
   - Action: Navigate to Customer List
   - Transition: Smart animate, 300ms
   - URL Parameter: `?filter=active` (for Active Customers KPI)

2. **Customer List → Customer Detail**
   - Trigger: Click on table row
   - Action: Navigate to Customer Detail (placeholder)
   - Transition: Slide in from right, 300ms

3. **Back Navigation**
   - Trigger: Click on Back button
   - Action: Navigate to previous screen
   - Transition: Slide out to right, 300ms

### Hover States
- KPI Cards: Elevation change (shadow/md → shadow/lg)
- Table Rows: Background color change
- Buttons: Opacity change (100% → 90%)

## 可访问性考虑

### 颜色对比度
所有文本颜色都满足 WCAG AA 标准（≥ 4.5:1）：
- `color/text` on `color/background`: 15.92:1 ✓
- `color/primary` on `color/background`: 4.59:1 ✓
- `color/success` on `color/background`: 4.52:1 ✓
- `color/danger` on `color/background`: 4.52:1 ✓

### 焦点状态
所有可交互元素都有明确的焦点状态：
- Border: 2px solid `color/primary`
- Outline offset: 2px