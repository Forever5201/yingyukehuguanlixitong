// 虚拟滚动实现 - 适用于现有的 Flask 系统

class VirtualScrollTable {
    constructor(options) {
        this.container = options.container;
        this.rowHeight = options.rowHeight || 48;
        this.data = options.data || [];
        this.columns = options.columns || [];
        this.visibleRows = options.visibleRows || 20;
        
        this.scrollTop = 0;
        this.startIndex = 0;
        this.endIndex = this.visibleRows;
        
        this.init();
    }
    
    init() {
        // 创建表格结构
        this.wrapper = document.createElement('div');
        this.wrapper.className = 'virtual-scroll-wrapper';
        this.wrapper.style.height = `${this.rowHeight * this.visibleRows}px`;
        this.wrapper.style.overflow = 'auto';
        this.wrapper.style.position = 'relative';
        
        // 创建占位元素（撑开滚动高度）
        this.spacer = document.createElement('div');
        this.spacer.style.height = `${this.rowHeight * this.data.length}px`;
        this.spacer.style.position = 'relative';
        
        // 创建表格容器
        this.tableContainer = document.createElement('div');
        this.tableContainer.style.position = 'absolute';
        this.tableContainer.style.top = '0';
        this.tableContainer.style.left = '0';
        this.tableContainer.style.right = '0';
        
        // 创建表格
        this.table = document.createElement('table');
        this.table.className = 'virtual-scroll-table';
        
        // 添加表头
        this.createHeader();
        
        // 添加表体
        this.tbody = document.createElement('tbody');
        this.table.appendChild(this.tbody);
        
        // 组装DOM
        this.tableContainer.appendChild(this.table);
        this.spacer.appendChild(this.tableContainer);
        this.wrapper.appendChild(this.spacer);
        this.container.appendChild(this.wrapper);
        
        // 绑定滚动事件
        this.wrapper.addEventListener('scroll', this.handleScroll.bind(this));
        
        // 初始渲染
        this.render();
    }
    
    createHeader() {
        const thead = document.createElement('thead');
        const tr = document.createElement('tr');
        
        this.columns.forEach(column => {
            const th = document.createElement('th');
            th.textContent = column.title;
            th.style.width = column.width || 'auto';
            tr.appendChild(th);
        });
        
        thead.appendChild(tr);
        this.table.appendChild(thead);
    }
    
    handleScroll() {
        this.scrollTop = this.wrapper.scrollTop;
        this.startIndex = Math.floor(this.scrollTop / this.rowHeight);
        this.endIndex = Math.min(
            this.startIndex + this.visibleRows + 5, // 多渲染5行作为缓冲
            this.data.length
        );
        
        // 更新表格位置
        this.tableContainer.style.transform = `translateY(${this.startIndex * this.rowHeight}px)`;
        
        // 重新渲染可见行
        this.render();
    }
    
    render() {
        // 清空现有行
        this.tbody.innerHTML = '';
        
        // 渲染可见行
        for (let i = this.startIndex; i < this.endIndex; i++) {
            const row = this.createRow(this.data[i], i);
            this.tbody.appendChild(row);
        }
    }
    
    createRow(item, index) {
        const tr = document.createElement('tr');
        tr.style.height = `${this.rowHeight}px`;
        
        this.columns.forEach(column => {
            const td = document.createElement('td');
            
            // 处理渲染函数
            if (column.render) {
                td.innerHTML = column.render(item[column.key], item, index);
            } else {
                td.textContent = item[column.key] || '';
            }
            
            tr.appendChild(td);
        });
        
        // 添加点击事件
        if (this.options.onRowClick) {
            tr.style.cursor = 'pointer';
            tr.addEventListener('click', () => {
                this.options.onRowClick(item, index);
            });
        }
        
        return tr;
    }
    
    // 更新数据
    updateData(newData) {
        this.data = newData;
        this.spacer.style.height = `${this.rowHeight * this.data.length}px`;
        this.render();
    }
    
    // 滚动到指定行
    scrollToRow(index) {
        const scrollTop = index * this.rowHeight;
        this.wrapper.scrollTop = scrollTop;
    }
}

// 使用示例
function initVirtualScrollTable() {
    // 获取数据（可以从API加载）
    fetch('/api/customers?limit=10000')
        .then(res => res.json())
        .then(data => {
            const table = new VirtualScrollTable({
                container: document.getElementById('customer-table-container'),
                data: data,
                rowHeight: 48,
                visibleRows: 20,
                columns: [
                    { 
                        key: 'name', 
                        title: '客户姓名',
                        width: '150px'
                    },
                    { 
                        key: 'phone', 
                        title: '电话',
                        width: '150px'
                    },
                    { 
                        key: 'status', 
                        title: '状态',
                        width: '100px',
                        render: (value) => {
                            const statusMap = {
                                'active': '<span class="badge badge-success">活跃</span>',
                                'inactive': '<span class="badge badge-secondary">非活跃</span>',
                                'pending': '<span class="badge badge-warning">待处理</span>'
                            };
                            return statusMap[value] || value;
                        }
                    },
                    {
                        key: 'revenue',
                        title: '收入',
                        width: '120px',
                        render: (value) => `¥${Number(value).toLocaleString()}`
                    }
                ],
                onRowClick: (item) => {
                    window.location.href = `/customers/${item.id}`;
                }
            });
        });
}

// CSS 样式
const virtualScrollStyles = `
<style>
.virtual-scroll-wrapper {
    border: 1px solid var(--color-border);
    border-radius: 8px;
    background: white;
}

.virtual-scroll-table {
    width: 100%;
    border-collapse: collapse;
}

.virtual-scroll-table thead {
    position: sticky;
    top: 0;
    background: var(--color-background-secondary);
    z-index: 10;
}

.virtual-scroll-table th {
    padding: 12px 16px;
    text-align: left;
    font-weight: 600;
    border-bottom: 2px solid var(--color-border);
}

.virtual-scroll-table td {
    padding: 12px 16px;
    border-bottom: 1px solid var(--color-border-secondary);
}

.virtual-scroll-table tr:hover {
    background: var(--color-background-secondary);
}
</style>
`;