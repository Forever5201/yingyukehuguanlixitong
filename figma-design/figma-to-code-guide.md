# Figma to Code 导出指南

## 1. 从 Figma 导出 Design Tokens 为 JSON

### 方法一：使用 Figma Tokens 插件

1. **安装插件**
   - 在 Figma 中打开插件面板
   - 搜索 "Figma Tokens" by Jan Six
   - 安装并运行插件

2. **配置 Tokens**
   ```json
   {
     "global": {
       "color": {
         "primary": {
           "value": "#4A90E2",
           "type": "color"
         },
         "primary-600": {
           "value": "#357ABD",
           "type": "color"
         }
       },
       "spacing": {
         "xs": {
           "value": "4",
           "type": "spacing"
         },
         "sm": {
           "value": "8",
           "type": "spacing"
         }
       }
     }
   }
   ```

3. **导出步骤**
   - 点击插件中的 "Export" 按钮
   - 选择 "JSON" 格式
   - 保存为 `tokens.json`

### 方法二：使用 Figma API

1. **获取 Personal Access Token**
   - 访问 Figma Settings → Account → Personal access tokens
   - 生成新的 token

2. **使用脚本导出**
   ```javascript
   // export-tokens.js
   const FIGMA_TOKEN = 'your-token-here';
   const FILE_KEY = 'your-file-key';
   
   async function exportTokens() {
     const response = await fetch(
       `https://api.figma.com/v1/files/${FILE_KEY}/styles`,
       {
         headers: {
           'X-Figma-Token': FIGMA_TOKEN
         }
       }
     );
     
     const data = await response.json();
     
     // 处理颜色样式
     const colors = {};
     data.meta.styles.forEach(style => {
       if (style.style_type === 'FILL') {
         colors[style.name] = style.description;
       }
     });
     
     // 保存为 JSON
     fs.writeFileSync('tokens.json', JSON.stringify({
       color: colors,
       // ... 其他 tokens
     }, null, 2));
   }
   ```

### 方法三：手动映射

从 Figma 的 Inspect 面板复制值并创建 JSON：

```json
{
  "color": {
    "primary": "#4A90E2",
    "primary-600": "#357ABD",
    "success": "#52C41A",
    "warning": "#FFC107",
    "danger": "#DC3545"
  },
  "spacing": {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32
  },
  "typography": {
    "fontSize": {
      "h1": 32,
      "h2": 24,
      "h3": 20,
      "body": 16,
      "small": 14,
      "caption": 12
    }
  }
}
```

## 2. 在项目中集成 Tokens

### Step 1: 创建 Token 转换器

```javascript
// build-tokens.js
const tokens = require('./tokens.json');
const fs = require('fs');

// 生成 CSS 变量
function generateCSSVariables(tokens, prefix = '') {
  let css = ':root {\n';
  
  function processTokens(obj, currentPrefix) {
    Object.entries(obj).forEach(([key, value]) => {
      if (typeof value === 'object' && !value.value) {
        processTokens(value, `${currentPrefix}-${key}`);
      } else {
        const varName = `--${currentPrefix}-${key}`.replace(/^--/, '--');
        const varValue = value.value || value;
        css += `  ${varName}: ${varValue};\n`;
      }
    });
  }
  
  processTokens(tokens, prefix);
  css += '}\n';
  
  return css;
}

// 生成 TypeScript 类型
function generateTypeScript(tokens) {
  return `
export interface DesignTokens {
  color: {
    primary: string;
    'primary-600': string;
    success: string;
    // ... 其他颜色
  };
  spacing: {
    xs: number;
    sm: number;
    // ... 其他间距
  };
  // ... 其他 token 类型
}

export const tokens: DesignTokens = ${JSON.stringify(tokens, null, 2)};
`;
}

// 写入文件
fs.writeFileSync('src/styles/tokens.css', generateCSSVariables(tokens));
fs.writeFileSync('src/design/tokens.ts', generateTypeScript(tokens));
```

### Step 2: 在 React 项目中使用

```tsx
// App.tsx
import './styles/tokens.css';
import { tokens } from './design/tokens';

// 使用 CSS 变量
const StyledCard = styled.div`
  background: var(--color-background);
  border: 1px solid var(--color-border);
  padding: var(--spacing-lg);
  border-radius: var(--radius-base);
`;

// 或直接使用 JS 对象
const cardStyles = {
  background: tokens.color.background,
  padding: `${tokens.spacing.lg}px`,
  borderRadius: `${tokens.radius.base}px`
};
```

## 3. Figma Code Panel 配置

### 为 CSS 输出配置

在 Figma 中选择组件，右侧 Inspect 面板会显示 CSS：

```css
/* KPI Card */
.kpi-card {
  /* Auto Layout */
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 24px;
  gap: 8px;
  
  /* Style */
  background: #FFFFFF;
  border: 1px solid #DEE2E6;
  border-radius: 8px;
  box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.08);
}
```

### 转换为使用 Design Tokens

```css
/* KPI Card with Tokens */
.kpi-card {
  /* Auto Layout */
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: var(--spacing-lg);
  gap: var(--spacing-sm);
  
  /* Style */
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-base);
  box-shadow: var(--shadow-kpi);
}
```

## 4. 组件导出最佳实践

### 导出 React 组件

1. **从 Figma 复制 SVG**
   - 选择图标或简单图形
   - 右键 → Copy as SVG

2. **转换为 React 组件**
   ```tsx
   // Icon.tsx
   export const TrendUpIcon = () => (
     <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
       <path 
         d="M2 12L6 8L9 11L14 6" 
         stroke="currentColor" 
         strokeWidth="2"
       />
     </svg>
   );
   ```

### 导出复杂组件

```tsx
// 从 Figma 生成的组件结构
export const KpiCard = ({ title, value, trend, icon }) => {
  return (
    <div className="kpi-card">
      <div className="kpi-header">
        <span className="kpi-title">{title}</span>
        {icon && <div className="kpi-icon">{icon}</div>}
      </div>
      <div className="kpi-value">{value}</div>
      {trend && (
        <div className={`kpi-trend ${trend.isPositive ? 'up' : 'down'}`}>
          <TrendIcon />
          <span>{trend.value}%</span>
        </div>
      )}
    </div>
  );
};
```

## 5. 自动化工作流

### 使用 Style Dictionary

1. **安装**
   ```bash
   npm install --save-dev style-dictionary
   ```

2. **配置 `config.json`**
   ```json
   {
     "source": ["tokens.json"],
     "platforms": {
       "css": {
         "transformGroup": "css",
         "buildPath": "src/styles/",
         "files": [{
           "destination": "tokens.css",
           "format": "css/variables"
         }]
       },
       "js": {
         "transformGroup": "js",
         "buildPath": "src/design/",
         "files": [{
           "destination": "tokens.js",
           "format": "javascript/es6"
         }]
       }
     }
   }
   ```

3. **运行构建**
   ```bash
   npx style-dictionary build
   ```

## 6. 验证清单

### ✅ Token 导出验证
- [ ] 所有颜色都有对应的 token 名称
- [ ] 间距值符合 8px 网格系统
- [ ] 字体大小有对应的语义名称
- [ ] 阴影效果正确导出

### ✅ 代码集成验证
- [ ] CSS 变量正确生成
- [ ] TypeScript 类型定义完整
- [ ] 组件可以访问所有 tokens
- [ ] 构建过程无错误

### ✅ 视觉一致性验证
- [ ] 实现效果与设计稿一致
- [ ] 响应式断点正确应用
- [ ] 交互状态（hover、focus）正确
- [ ] 动画时长符合规范

## 7. 常见问题解决

### Q: Figma 中的颜色值与代码不一致？
A: 检查颜色空间设置，确保 Figma 使用 sRGB 颜色空间。

### Q: 如何处理 Figma 中的渐变？
A: 导出为 CSS gradient：
```css
background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
```

### Q: Auto Layout 如何转换为 CSS？
A: 使用 Flexbox 或 Grid：
```css
/* Figma Auto Layout → CSS Flexbox */
display: flex;
flex-direction: column;
gap: 8px;
padding: 24px;
align-items: flex-start;
```