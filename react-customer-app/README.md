# React Customer Management App

## 项目概述

这是一个使用 React 18 + TypeScript + Vite 构建的客户管理系统前端应用。项目实现了 Dashboard 和客户列表两个核心页面，并包含了完整的设计系统和组件库。

## 技术栈

- **React 18**: 用户界面库
- **TypeScript**: 类型安全的 JavaScript
- **Vite**: 快速的开发构建工具
- **React Router v6**: 路由管理
- **react-window**: 虚拟滚动实现
- **Lucide React**: 图标库

## 项目结构

```
src/
├── api/
│   └── mockData.ts          # 模拟 API 和 200 条示例数据
├── components/
│   ├── KpiCard.tsx          # KPI 卡片组件
│   ├── CustomerTable.tsx    # 虚拟化客户表格组件
│   └── __tests__/
│       └── KpiCard.test.tsx # 单元测试示例
├── design/
│   └── tokens.json          # 设计令牌系统
├── pages/
│   ├── Dashboard.tsx        # 仪表板页面
│   └── CustomerList.tsx     # 客户列表页面
├── App.tsx                  # 应用主组件
├── App.css                  # CSS 变量定义
└── main.tsx                 # 应用入口
```

## 快速开始

### 安装依赖

```bash
npm install
# 或
yarn install
# 或
pnpm install
```

### 开发模式

```bash
npm run dev
# 或
yarn dev
# 或
pnpm dev
```

应用将在 http://localhost:5173 启动

### 构建生产版本

```bash
npm run build
# 或
yarn build
# 或
pnpm build
```

### 运行测试

```bash
npm run test
# 或
yarn test
# 或
pnpm test
```

## 核心功能

### 1. Dashboard 页面
- 4 个 KPI 卡片展示关键指标（总客户数、活跃客户、总收入、转化率）
- 点击 KPI 卡片可跳转到带筛选条件的客户列表
- 收入趋势图表（7天数据）
- 渠道分布图表

### 2. 客户列表页面
- 虚拟滚动支持 10k+ 数据流畅展示
- 行高固定 48px
- 支持列折叠（邮箱、来源、地区列可折叠）
- 操作列使用 Kebab Menu（查看/编辑/删除）
- 支持搜索和状态筛选
- URL 参数同步筛选状态

### 3. 设计系统
- 完整的颜色系统（对比度 ≥ 4.5:1）
- 间距、字体、圆角、阴影等设计令牌
- CSS 变量支持
- 响应式设计

## 组件说明

### KpiCard 组件

```tsx
<KpiCard
  title="总客户数"
  value="1,234"
  trend={{ value: 12.5, isPositive: true }}
  icon={<Users />}
  onClick={() => navigate('/customers')}
  loading={false}
/>
```

### CustomerTable 组件

```tsx
<CustomerTable
  data={customers}
  loading={false}
  onRowClick={(customer) => navigate(`/customers/${customer.id}`)}
  onAction={(action, customer) => handleAction(action, customer)}
/>
```

特性：
- 使用 react-window 实现虚拟滚动
- 支持排序、列折叠
- Kebab menu 操作菜单
- 响应式设计

## API 契约

项目包含完整的 Mock API 实现：

```typescript
// 获取客户列表
api.getCustomers({ page: 1, pageSize: 50, status: 'active' })

// 获取 KPI 统计
api.getKpiStats()

// 获取趋势数据
api.getTrendData('week')

// 获取渠道数据
api.getChannelData()
```

## 测试

项目包含 KpiCard 组件的完整单元测试示例：

```bash
# 运行测试
npm run test

# 测试覆盖率
npm run test:coverage
```

## Storybook（可选）

如需使用 Storybook 进行组件开发：

```bash
# 安装 Storybook
npx storybook@latest init

# 运行 Storybook
npm run storybook
```

## 性能优化

1. **虚拟滚动**: CustomerTable 使用 react-window 处理大数据集
2. **React.memo**: 组件使用 memo 优化重渲染
3. **懒加载**: 路由级别的代码分割
4. **CSS 变量**: 减少运行时样式计算

## 浏览器兼容性

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 部署

构建后的文件在 `dist` 目录：

```bash
npm run build
npm run preview # 本地预览生产版本
```

## 注意事项

1. 如需连接真实后端 API，修改 `src/api/mockData.ts` 中的实现
2. 如需使用 Ant Design，安装并在组件中引入：
   ```bash
   npm install antd@5.x
   ```
   注意：使用 Ant Design 时需要注意样式优先级，避免覆盖设计令牌

3. 如需使用 @tanstack/react-virtual 替代 react-window：
   ```bash
   npm install @tanstack/react-virtual
   ```
   参考 CustomerTable.tsx 中的注释进行替换

## License

MIT