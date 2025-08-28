# Figma 导出步骤说明

## 准备工作

1. **确保所有组件都使用了 Design Tokens**
   - 检查颜色是否都来自 Color Styles
   - 检查间距是否符合 8px 网格
   - 检查文字样式是否使用 Text Styles

2. **命名规范检查**
   - 组件：`Component / {Name} / {State}`
   - 颜色：`color / {semantic-name}`
   - 文字：`typography / {style-name}`
   - 效果：`shadow / {size}`

## 导出流程

### 第 1 步：导出 Design Tokens

#### 方法 A：使用 Figma Tokens 插件

1. 打开 Figma 文件
2. 运行 Figma Tokens 插件 (`Plugins > Figma Tokens`)
3. 在插件界面中：
   ```
   ├── 点击 "Settings" 齿轮图标
   ├── 选择 "Export"
   ├── 选择格式 "JSON"
   └── 点击 "Export to file"
   ```
4. 保存文件为 `design-tokens.json`

#### 方法 B：手动导出

1. **导出颜色**
   - 打开右侧面板的 "Local Styles"
   - 点击颜色样式旁的 "Edit style" 图标
   - 复制颜色值和名称
   - 创建 JSON 结构：
   ```json
   {
     "color": {
       "primary": "#4A90E2",
       "primary-600": "#357ABD"
     }
   }
   ```

2. **导出文字样式**
   - 在 Local Styles 中找到文字样式
   - 记录字号、行高、字重
   - 添加到 JSON：
   ```json
   {
     "typography": {
       "h1": {
         "fontSize": 32,
         "lineHeight": 1.25,
         "fontWeight": 700
       }
     }
   }
   ```

### 第 2 步：导出组件截图

1. **选择要导出的组件**
   - KPI Card (所有状态)
   - Data Table Row (默认、悬停、选中)
   - Buttons (所有类型和状态)
   - Form Controls

2. **设置导出选项**
   ```
   选中组件 > 右侧面板 > Export
   ├── 添加导出设置 (+)
   ├── 格式: PNG
   ├── 倍数: 2x
   └── 后缀: @2x
   ```

3. **批量导出**
   - 使用 `Cmd/Ctrl + Shift + E` 打开导出面板
   - 确认所有选中的元素
   - 点击 "Export [N] layers"

### 第 3 步：导出图标

1. **准备图标**
   - 确保所有图标是 24×24px
   - 移除所有颜色，使用 `currentColor`
   - 轮廓化所有描边

2. **导出为 SVG**
   ```
   选中图标 > Export
   ├── 格式: SVG
   ├── Include "id" attribute: ✓
   └── Simplify stroke: ✓
   ```

3. **优化 SVG**
   ```xml
   <!-- 原始导出 -->
   <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
     <path d="..." fill="#4A90E2"/>
   </svg>
   
   <!-- 优化后 -->
   <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
     <path d="..." fill="currentColor"/>
   </svg>
   ```

### 第 4 步：导出原型链接

1. **创建原型连接**
   - 选择 Dashboard 的 KPI Card
   - 拖拽连接线到 Customer List 页面
   - 设置交互：
     ```
     Trigger: On click
     Action: Navigate to
     Destination: Customer List
     Animation: Smart animate
     Duration: 300ms
     ```

2. **添加 URL 参数**
   - 在 Prototype 设置中
   - 为不同的 KPI Card 设置不同的参数：
     - 总客户数 → `/customers`
     - 活跃客户 → `/customers?status=active`
     - 总收入 → `/customers?sort=revenue`

3. **分享原型**
   - 点击右上角 "Share prototype"
   - 获取分享链接
   - 设置权限为 "Anyone with the link can view"

### 第 5 步：生成交付文档

1. **创建设计规范页面**
   ```
   新建 Page > 命名为 "Design Specs"
   ├── Token 使用说明
   ├── 组件状态说明
   ├── 响应式断点说明
   └── 导出资源清单
   ```

2. **导出 PDF 文档**
   - 选择 Design Specs 页面
   - `File > Export Frames to PDF`
   - 包含所有画板

### 第 6 步：整理交付文件

创建以下文件结构：
```
figma-export/
├── tokens/
│   ├── design-tokens.json
│   ├── tokens.css (生成的)
│   └── tokens.ts (生成的)
├── components/
│   ├── kpi-card-default@2x.png
│   ├── kpi-card-hover@2x.png
│   ├── table-row-default@2x.png
│   └── table-row-hover@2x.png
├── icons/
│   ├── icon-users.svg
│   ├── icon-trending-up.svg
│   └── icon-more-vertical.svg
├── documentation/
│   ├── design-specs.pdf
│   ├── component-states.md
│   └── implementation-guide.md
└── prototype/
    └── prototype-links.txt
```

## 验证清单

### ✅ Tokens 验证
- [ ] 所有颜色都有语义化命名
- [ ] 间距值遵循 8px 网格
- [ ] 文字样式完整（标题、正文、标签）
- [ ] 阴影效果正确命名

### ✅ 组件验证
- [ ] 所有状态都已导出
- [ ] 命名规范一致
- [ ] Auto Layout 设置正确
- [ ] 响应式变体完整

### ✅ 导出验证
- [ ] PNG 文件是 @2x 分辨率
- [ ] SVG 图标可缩放
- [ ] 原型链接可访问
- [ ] 文档完整清晰

## 在代码中使用

### 1. 导入 Tokens
```javascript
// 将 design-tokens.json 复制到项目
import tokens from './design/design-tokens.json';

// 或使用生成的文件
import './styles/tokens.css';
```

### 2. 应用样式
```css
.kpi-card {
  background: var(--color-background);
  padding: var(--spacing-lg);
  border-radius: var(--radius-base);
  box-shadow: var(--shadow-kpi);
}
```

### 3. 使用组件截图作为参考
- 将 PNG 文件放在项目文档中
- 开发时对照实现
- 使用浏览器开发工具验证样式

## 自动化提示

可以使用以下工具自动化导出流程：

1. **Figma API**
   ```bash
   # 获取文件样式
   curl -H "X-FIGMA-TOKEN: $TOKEN" \
     "https://api.figma.com/v1/files/$FILE_KEY/styles"
   ```

2. **Design Tokens 构建**
   ```bash
   # 使用 Style Dictionary
   npx style-dictionary build
   ```

3. **SVG 优化**
   ```bash
   # 使用 SVGO
   npx svgo -f ./icons -o ./icons/optimized
   ```