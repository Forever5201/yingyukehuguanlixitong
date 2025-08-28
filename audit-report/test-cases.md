# 验收测试用例

## 1. 颜色对比度测试

### 测试用例 TC001: 警告颜色对比度
**前置条件**: 更新 design-tokens.json 中的 warning 颜色
**测试步骤**:
1. 打开 Chrome DevTools
2. 选择包含警告文本的元素
3. 在 Styles 面板查看颜色对比度

**预期结果**: 
- 对比度 ≥ 4.5:1
- 显示 "AA" 或 "AAA" 标记

**自动化测试**:
```javascript
// Jest + @testing-library/react
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

test('警告颜色符合 WCAG AA 标准', async () => {
  const { container } = render(
    <div style={{ color: '#B87900', backgroundColor: '#FFFFFF' }}>
      警告文本
    </div>
  );
  
  const results = await axe(container, {
    rules: {
      'color-contrast': { enabled: true }
    }
  });
  
  expect(results).toHaveNoViolations();
});
```

## 2. 键盘导航测试

### 测试用例 TC002: 虚拟表格键盘导航
**测试步骤**:
1. 使用 Tab 键聚焦到表格
2. 使用方向键上下导航
3. 使用 PageUp/PageDown 快速导航
4. 按 Enter 键选择行

**预期结果**:
- 焦点可见且清晰
- 导航流畅无卡顿
- 正确触发行点击事件

**自动化测试**:
```javascript
import { render, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('表格支持键盘导航', async () => {
  const user = userEvent.setup();
  const onRowClick = jest.fn();
  
  const { getByRole } = render(
    <CustomerTable data={mockData} onRowClick={onRowClick} />
  );
  
  const table = getByRole('grid');
  
  // Tab 聚焦
  await user.tab();
  expect(table).toHaveFocus();
  
  // 方向键导航
  await user.keyboard('{ArrowDown}');
  await user.keyboard('{Enter}');
  
  expect(onRowClick).toHaveBeenCalledWith(mockData[0]);
});
```

## 3. ARIA 属性测试

### 测试用例 TC003: Kebab 菜单 ARIA 属性
**测试步骤**:
1. 使用屏幕阅读器（NVDA）
2. 导航到 Kebab 菜单按钮
3. 激活菜单
4. 导航菜单项

**预期朗读内容**:
- "更多操作 按钮 折叠"
- "展开"（激活后）
- "菜单 3 项"
- "查看 菜单项"

**自动化测试**:
```javascript
test('Kebab 菜单包含正确的 ARIA 属性', () => {
  const { getByLabelText, getByRole } = render(<KebabMenu />);
  
  const button = getByLabelText(/更多操作/);
  expect(button).toHaveAttribute('aria-haspopup', 'true');
  expect(button).toHaveAttribute('aria-expanded', 'false');
  
  fireEvent.click(button);
  
  expect(button).toHaveAttribute('aria-expanded', 'true');
  
  const menu = getByRole('menu');
  expect(menu).toBeInTheDocument();
  
  const menuItems = getAllByRole('menuitem');
  expect(menuItems).toHaveLength(3);
});
```

## 4. 性能测试

### 测试用例 TC004: 10k 数据虚拟滚动性能
**测试工具**: Chrome Performance Profiler
**测试步骤**:
1. 加载 10,000 条数据
2. 开始性能记录
3. 快速滚动到底部
4. 停止记录并分析

**预期结果**:
- 帧率 ≥ 60fps (16.67ms/帧)
- 无明显卡顿
- 内存使用 < 100MB

**自动化性能测试**:
```javascript
// Playwright 性能测试
import { test, expect } from '@playwright/test';

test('大数据集滚动性能', async ({ page }) => {
  await page.goto('/customers?mock=10000');
  
  // 启动性能分析
  await page.evaluateHandle(() => {
    window.performanceMarks = [];
    const observer = new PerformanceObserver((list) => {
      window.performanceMarks.push(...list.getEntries());
    });
    observer.observe({ entryTypes: ['measure'] });
  });
  
  // 执行滚动
  await page.evaluate(() => {
    performance.mark('scroll-start');
    const container = document.querySelector('.table-container');
    container.scrollTop = container.scrollHeight;
    performance.mark('scroll-end');
    performance.measure('scroll-duration', 'scroll-start', 'scroll-end');
  });
  
  // 验证性能
  const duration = await page.evaluate(() => {
    const measure = window.performanceMarks.find(m => m.name === 'scroll-duration');
    return measure?.duration;
  });
  
  expect(duration).toBeLessThan(1000); // 滚动应在1秒内完成
});
```

## 5. 安全性测试

### 测试用例 TC005: 数据导出脱敏
**测试步骤**:
1. 选择客户数据
2. 点击导出按钮
3. 确认导出提示
4. 检查导出文件

**预期结果**:
- 显示隐私提醒弹窗
- 电话号码格式：138****5678
- 邮箱格式：u***r@example.com

**自动化测试**:
```javascript
test('导出数据已脱敏', async () => {
  const mockData = [
    { name: '张三', phone: '13812345678', email: 'user@test.com' }
  ];
  
  const maskedData = maskSensitiveData(mockData, ['phone', 'email']);
  
  expect(maskedData[0].phone).toBe('138****5678');
  expect(maskedData[0].email).toBe('u***r@test.com');
});
```

## 集成测试脚本

```bash
#!/bin/bash
# run-a11y-tests.sh

echo "运行可访问性测试套件..."

# 1. 单元测试
npm run test:a11y

# 2. E2E 测试
npm run test:e2e:a11y

# 3. Lighthouse CI
npx lighthouse-ci autorun \
  --collect.url=http://localhost:3000 \
  --assert.preset=lighthouse:recommended \
  --assert.assertions.categories:accessibility=0.95

# 4. axe-core 扫描
npx axe http://localhost:3000 --tags wcag2a,wcag2aa

echo "测试完成！"
```

## 验收标准总结

### 必须通过 ✅
1. 所有自动化测试用例
2. axe DevTools 0 错误，0 警告
3. Lighthouse 可访问性得分 ≥ 95
4. 真实屏幕阅读器测试

### 性能基准 ⚡
1. FCP < 1.8s
2. TTI < 3.8s
3. 60fps 滚动
4. 内存使用 < 100MB

### 安全要求 🔒
1. 敏感数据脱敏
2. 导出日志记录
3. 隐私提醒显示