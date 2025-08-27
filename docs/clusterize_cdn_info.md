# Clusterize.js CDN 信息

## 官方 CDN 链接

### 版本 0.18.0（推荐）

**CSS 文件：**
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/clusterize.js@0.18.0/clusterize.min.css">
```

**JavaScript 文件：**
```html
<script src="https://cdn.jsdelivr.net/npm/clusterize.js@0.18.0/clusterize.min.js"></script>
```

### 其他 CDN 源

**unpkg:**
```html
<link rel="stylesheet" href="https://unpkg.com/clusterize.js@0.18.0/clusterize.min.css">
<script src="https://unpkg.com/clusterize.js@0.18.0/clusterize.min.js"></script>
```

**cdnjs:**
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/clusterize.js/0.18.0/clusterize.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/clusterize.js/0.18.0/clusterize.min.js"></script>
```

## 完整性校验

**CSS 文件 (SHA-256):**
```
integrity="sha256-6aQJpXCjXzqH1cyqYa1H1OqZbYNR7RjJZ9J8LPuXoq8="
```

**JS 文件 (SHA-256):**
```
integrity="sha256-aXXJVkfqN0CrcUW1PdJVkKVkryuPdN5mkSkXBpwVvKc="
```

使用示例：
```html
<script 
    src="https://cdn.jsdelivr.net/npm/clusterize.js@0.18.0/clusterize.min.js"
    integrity="sha256-aXXJVkfqN0CrcUW1PdJVkKVkryuPdN5mkSkXBpwVvKc="
    crossorigin="anonymous">
</script>
```

## 下载到本地

如果需要下载到本地使用：

```bash
# 创建 vendor 目录
mkdir -p app/static/vendor

# 下载文件
curl -o app/static/vendor/clusterize.min.js https://cdn.jsdelivr.net/npm/clusterize.js@0.18.0/clusterize.min.js
curl -o app/static/vendor/clusterize.min.css https://cdn.jsdelivr.net/npm/clusterize.js@0.18.0/clusterize.min.css
```

## 版本信息

- **当前版本**: 0.18.0
- **发布日期**: 2017-11-04
- **文件大小**: JS ~6KB (minified), CSS ~1KB
- **许可证**: GPLv3
- **官方仓库**: https://github.com/NeXTs/Clusterize.js

## 浏览器兼容性

- Chrome: ✓
- Firefox: ✓
- Safari: ✓
- Edge: ✓
- IE: 9+

## 注意事项

1. Clusterize.js 是轻量级的虚拟滚动库，适合处理大量数据
2. 建议在数据量超过 1000 条时使用
3. 如果 CDN 不可用，组件会自动尝试从备用 CDN 加载