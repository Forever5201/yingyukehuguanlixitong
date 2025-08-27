/**
 * DataTable Manager - 统一管理所有数据表格实例
 * 支持服务端分页和客户端虚拟滚动两种模式
 */

(function(window) {
    'use strict';

    // 全局配置
    const CONFIG = {
        virtualThreshold: 2000,     // 默认虚拟滚动阈值
        rowHeight: 48,              // 默认行高
        blocksInCluster: 50,        // Clusterize.js 每个块的行数
        scrollDebounce: 100,        // 滚动防抖延迟
        exportBatchSize: 1000,      // 导出时的批处理大小
    };

    // 存储所有表格实例
    const instances = new Map();

    /**
     * DataTable 类 - 单个表格实例
     */
    class DataTable {
        constructor(config) {
            this.config = {
                ...CONFIG,
                ...config
            };
            this.id = config.id;
            this.mode = config.mode;
            this.data = [];
            this.filteredData = [];
            this.clusterize = null;
            this.selectedRows = new Set();
            this.sortColumn = null;
            this.sortDirection = 'asc';
            
            this.init();
        }

        async init() {
            if (this.mode === 'virtual') {
                await this.initVirtualMode();
            } else {
                this.initServerMode();
            }
            
            this.bindEvents();
        }

        /**
         * 初始化虚拟滚动模式
         */
        async initVirtualMode() {
            const container = document.getElementById(`${this.id}-container`);
            const loading = document.getElementById(`${this.id}-loading`);
            const scrollArea = document.getElementById(`${this.id}-scrollArea`);
            
            try {
                // 加载数据
                loading.style.display = 'flex';
                
                if (this.config.dataUrl && this.config.dataUrl !== 'None') {
                    const response = await fetch(this.config.dataUrl);
                    if (!response.ok) throw new Error('Failed to load data');
                    this.data = await response.json();
                } else {
                    // 使用模拟数据
                    this.data = this.generateMockData(5000);
                }
                
                this.filteredData = [...this.data];
                
                // 更新记录数
                const totalSpan = document.getElementById(`${this.id}-total`);
                if (totalSpan) totalSpan.textContent = this.data.length.toLocaleString();
                
                // 决定使用虚拟滚动还是普通渲染
                if (this.data.length > this.config.virtualThreshold) {
                    await this.initClusterize();
                    document.getElementById(`${this.id}-virtual-info`).style.display = 'inline';
                } else {
                    this.renderRegularTable();
                }
                
                loading.style.display = 'none';
                scrollArea.style.display = 'block';
                
            } catch (error) {
                console.error('Failed to initialize virtual mode:', error);
                loading.innerHTML = `
                    <div style="color: var(--color-danger);">
                        <i class="fas fa-exclamation-triangle"></i> 
                        加载失败: ${error.message}
                    </div>
                `;
            }
        }

        /**
         * 初始化 Clusterize.js
         */
        async initClusterize() {
            // 确保 Clusterize.js 已加载
            if (typeof Clusterize === 'undefined') {
                console.warn('Clusterize.js not loaded, loading from CDN...');
                await this.loadClusterizeFromCDN();
            }
            
            const rows = this.generateRowsHTML(this.filteredData);
            
            this.clusterize = new Clusterize({
                rows: rows,
                scrollId: `${this.id}-scrollArea`,
                contentId: `${this.id}-tbody`,
                rows_in_block: this.config.blocksInCluster,
                blocks_in_cluster: 4,
                show_no_data_row: true,
                no_data_text: '<tr><td colspan="' + this.config.columns.length + '" class="empty-message">暂无数据</td></tr>',
                no_data_class: 'no-data',
                keep_parity: true,
                callbacks: {
                    clusterChanged: () => this.onClusterChanged()
                }
            });
        }

        /**
         * 从 CDN 加载 Clusterize.js
         */
        loadClusterizeFromCDN() {
            return new Promise((resolve, reject) => {
                // 加载 CSS
                const css = document.createElement('link');
                css.rel = 'stylesheet';
                css.href = 'https://cdn.jsdelivr.net/npm/clusterize.js@0.18.0/clusterize.min.css';
                document.head.appendChild(css);
                
                // 加载 JS
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/clusterize.js@0.18.0/clusterize.min.js';
                script.onload = resolve;
                script.onerror = () => reject(new Error('Failed to load Clusterize.js'));
                document.head.appendChild(script);
            });
        }

        /**
         * 生成行 HTML
         */
        generateRowsHTML(data) {
            return data.map((row, index) => {
                const cells = this.config.columns.map(col => {
                    const value = row[col.key] || '';
                    const formatted = this.formatCellValue(value, col);
                    return `<td class="${col.className || ''}">${formatted}</td>`;
                }).join('');
                
                const checkbox = this.config.enableSelection ? 
                    `<td class="checkbox-column">
                        <input type="checkbox" class="row-checkbox" value="${row.id || index}">
                    </td>` : '';
                
                return `<tr data-id="${row.id || index}">${checkbox}${cells}</tr>`;
            });
        }

        /**
         * 格式化单元格值
         */
        formatCellValue(value, column) {
            if (value === null || value === undefined) return '';
            
            // 根据列类型格式化
            switch (column.type) {
                case 'date':
                    return this.formatDate(value);
                case 'currency':
                    return this.formatCurrency(value);
                case 'number':
                    return Number(value).toLocaleString();
                case 'status':
                    return this.formatStatus(value);
                default:
                    return this.escapeHtml(String(value));
            }
        }

        /**
         * 普通表格渲染（非虚拟滚动）
         */
        renderRegularTable() {
            const tbody = document.getElementById(`${this.id}-tbody`);
            if (!tbody) return;
            
            tbody.innerHTML = this.generateRowsHTML(this.filteredData).join('');
        }

        /**
         * 初始化服务端模式
         */
        initServerMode() {
            // 服务端模式主要处理分页跳转
            this.updatePaginationInfo();
        }

        /**
         * 绑定事件
         */
        bindEvents() {
            const wrapper = document.getElementById(`${this.id}-wrapper`);
            if (!wrapper) return;
            
            // 全选/取消全选
            const checkAll = wrapper.querySelector(`#${this.id}-check-all`);
            if (checkAll) {
                checkAll.addEventListener('change', (e) => this.toggleSelectAll(e.target.checked));
            }
            
            // 行选择
            wrapper.addEventListener('change', (e) => {
                if (e.target.classList.contains('row-checkbox')) {
                    this.toggleRowSelection(e.target.value, e.target.checked);
                }
            });
            
            // 排序（服务端模式）
            if (this.mode === 'server') {
                wrapper.querySelectorAll('th.sortable').forEach(th => {
                    th.addEventListener('click', () => {
                        const column = th.dataset.sort;
                        this.sortTable(column);
                    });
                });
            }
            
            // 行点击事件
            wrapper.addEventListener('click', (e) => {
                const row = e.target.closest('tr');
                if (row && row.dataset.id && !e.target.closest('.checkbox-column')) {
                    this.onRowClick(row);
                }
            });
        }

        /**
         * Clusterize 更新后的回调
         */
        onClusterChanged() {
            // 重新绑定动态生成的元素事件
            const tbody = document.getElementById(`${this.id}-tbody`);
            if (!tbody) return;
            
            // 恢复选中状态
            tbody.querySelectorAll('.row-checkbox').forEach(checkbox => {
                checkbox.checked = this.selectedRows.has(checkbox.value);
            });
        }

        /**
         * 切换全选
         */
        toggleSelectAll(checked) {
            if (checked) {
                this.filteredData.forEach(row => {
                    this.selectedRows.add(String(row.id || this.data.indexOf(row)));
                });
            } else {
                this.selectedRows.clear();
            }
            
            // 更新UI
            const checkboxes = document.querySelectorAll(`#${this.id}-tbody .row-checkbox`);
            checkboxes.forEach(cb => cb.checked = checked);
        }

        /**
         * 切换行选择
         */
        toggleRowSelection(id, checked) {
            if (checked) {
                this.selectedRows.add(String(id));
            } else {
                this.selectedRows.delete(String(id));
            }
            
            // 更新全选框状态
            const checkAll = document.getElementById(`${this.id}-check-all`);
            if (checkAll) {
                const totalRows = this.filteredData.length;
                const selectedCount = this.selectedRows.size;
                checkAll.checked = selectedCount === totalRows && totalRows > 0;
                checkAll.indeterminate = selectedCount > 0 && selectedCount < totalRows;
            }
        }

        /**
         * 行点击事件
         */
        onRowClick(row) {
            const event = new CustomEvent('rowClick', {
                detail: {
                    id: row.dataset.id,
                    row: row,
                    data: this.data.find(d => String(d.id) === row.dataset.id)
                }
            });
            document.getElementById(`${this.id}-wrapper`).dispatchEvent(event);
        }

        /**
         * 导出表格数据
         */
        exportData() {
            const data = this.selectedRows.size > 0 ? 
                this.filteredData.filter(row => this.selectedRows.has(String(row.id))) :
                this.filteredData;
            
            if (data.length === 0) {
                alert('没有可导出的数据');
                return;
            }
            
            // 生成CSV
            const headers = this.config.columns
                .filter(col => col.key !== 'actions')
                .map(col => col.label);
            
            const rows = data.map(row => {
                return this.config.columns
                    .filter(col => col.key !== 'actions')
                    .map(col => {
                        const value = row[col.key] || '';
                        const formatted = this.formatCellValue(value, col);
                        // CSV转义
                        const escaped = String(formatted).replace(/"/g, '""');
                        return escaped.includes(',') || escaped.includes('"') || escaped.includes('\n') 
                            ? `"${escaped}"` : escaped;
                    });
            });
            
            const csv = [
                headers.join(','),
                ...rows.map(row => row.join(','))
            ].join('\n');
            
            // 下载
            const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `${this.id}_export_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }

        /**
         * 刷新表格
         */
        async refresh() {
            if (this.mode === 'virtual') {
                await this.initVirtualMode();
            } else {
                window.location.reload();
            }
        }

        /**
         * 排序表格（服务端模式）
         */
        sortTable(column) {
            const url = new URL(window.location);
            const currentSort = url.searchParams.get('sort');
            const currentOrder = url.searchParams.get('order') || 'asc';
            
            if (currentSort === column) {
                url.searchParams.set('order', currentOrder === 'asc' ? 'desc' : 'asc');
            } else {
                url.searchParams.set('sort', column);
                url.searchParams.set('order', 'asc');
            }
            
            window.location.href = url.toString();
        }

        /**
         * 工具方法
         */
        formatDate(dateString) {
            try {
                const date = new Date(dateString);
                return date.toLocaleDateString('zh-CN', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            } catch (e) {
                return dateString;
            }
        }

        formatCurrency(value) {
            return '¥' + Number(value).toLocaleString('zh-CN', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }

        formatStatus(status) {
            const statusMap = {
                'active': '<span class="badge badge-success">活跃</span>',
                'pending': '<span class="badge badge-warning">待处理</span>',
                'completed': '<span class="badge badge-info">已完成</span>',
                'cancelled': '<span class="badge badge-danger">已取消</span>'
            };
            return statusMap[status] || status;
        }

        escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }

        /**
         * 生成模拟数据
         */
        generateMockData(count = 5000) {
            const statuses = ['active', 'pending', 'completed', 'cancelled'];
            const firstNames = ['张', '李', '王', '刘', '陈', '杨', '赵', '黄', '周', '吴'];
            const lastNames = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '洋', '艳'];
            
            const data = [];
            for (let i = 1; i <= count; i++) {
                data.push({
                    id: i,
                    name: firstNames[Math.floor(Math.random() * firstNames.length)] + 
                          lastNames[Math.floor(Math.random() * lastNames.length)],
                    email: `user${i}@example.com`,
                    phone: `1${Math.floor(Math.random() * 9) + 1}${Math.random().toString().slice(2, 11)}`,
                    status: statuses[Math.floor(Math.random() * statuses.length)],
                    amount: Math.floor(Math.random() * 50000) + 1000,
                    created_at: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString()
                });
            }
            return data;
        }

        /**
         * 更新分页信息
         */
        updatePaginationInfo() {
            // 服务端模式的分页信息已在模板中渲染
        }
    }

    /**
     * DataTable 管理器
     */
    const DataTableManager = {
        /**
         * 注册表格
         */
        register(config) {
            const instance = new DataTable(config);
            instances.set(config.id, instance);
            return instance;
        },

        /**
         * 获取表格实例
         */
        getInstance(id) {
            return instances.get(id);
        },

        /**
         * 导出表格
         */
        exportTable(id) {
            const instance = instances.get(id);
            if (instance) {
                instance.exportData();
            }
        },

        /**
         * 刷新表格
         */
        refreshTable(id) {
            const instance = instances.get(id);
            if (instance) {
                instance.refresh();
            }
        },

        /**
         * 跳转页面（服务端分页）
         */
        goToPage(id, page) {
            const url = new URL(window.location);
            url.searchParams.set('page', page);
            window.location.href = url.toString();
        },

        /**
         * 改变每页显示数量
         */
        changePerPage(id, perPage) {
            const url = new URL(window.location);
            url.searchParams.set('per_page', perPage);
            url.searchParams.set('page', 1); // 重置到第一页
            window.location.href = url.toString();
        },

        /**
         * 跳转到指定页
         */
        jumpToPage(id, page) {
            const pageNum = parseInt(page);
            if (!isNaN(pageNum) && pageNum > 0) {
                this.goToPage(id, pageNum);
            }
        },

        /**
         * 获取所有实例
         */
        getAllInstances() {
            return Array.from(instances.values());
        }
    };

    // 暴露到全局
    window.DataTableManager = DataTableManager;

    // 处理延迟注册的表格
    document.addEventListener('DOMContentLoaded', function() {
        if (window._pendingDataTables) {
            window._pendingDataTables.forEach(config => {
                DataTableManager.register(config);
            });
            delete window._pendingDataTables;
        }
    });

})(window);