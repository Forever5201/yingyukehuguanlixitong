# Bug 修复报告：GET /None 404 错误

## 问题描述
访问首页时出现 `GET /None HTTP/1.1" 404` 错误。

## 根本原因
在 `data_table.html` 组件中，当 `data_url` 参数为 `None`（Python 的空值）时：
1. 模板会渲染 `data-url="None"` 到 HTML 属性中
2. JavaScript 配置会生成 `dataUrl: 'None'`
3. JavaScript 代码尝试 fetch `'None'` 字符串作为 URL，导致访问 `/None`

## 修复方案

### 1. 模板层面修复
在 `data_table.html` 中添加条件判断：

```jinja2
<!-- HTML 属性 -->
{% if data_url %}data-url="{{ data_url }}"{% endif %}

<!-- JavaScript 配置 -->
{% if data_url %}dataUrl: '{{ data_url }}',{% endif %}
```

### 2. JavaScript 层面修复
在 `data-table.js` 中增强判断：

```javascript
if (this.config.dataUrl && this.config.dataUrl !== 'None') {
    // 只有在有效 URL 时才 fetch
}
```

## 已修改的文件
1. `/app/templates/components/data_table.html` - 行 200 和 243
2. `/app/static/js/data-table.js` - 行 64

## 验证方法
1. 重启 Flask 应用
2. 访问首页 http://localhost:5000/
3. 检查浏览器控制台，确认没有 404 错误
4. 检查服务器日志，确认没有 `/None` 请求

## 预防措施
1. 在模板中处理可能为 None 的变量时，始终添加条件判断
2. 在 JavaScript 中处理来自服务器的数据时，进行有效性检查
3. 考虑使用默认值或显式的空值处理策略

## 影响范围
此修复不会影响正常的数据表格功能，只是防止了无效的网络请求。