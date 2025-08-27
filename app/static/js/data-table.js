/**
 * Data Table Virtual Scroll Implementation
 * Uses Clusterize.js for efficient rendering of large datasets
 */

// Global configuration
const TABLE_CONFIG = {
    virtualScrollThreshold: 2000,  // Switch to virtual scroll above this count
    rowHeight: 48,  // Approximate row height in pixels
    blocksInCluster: 50,  // Rows to render at once
    showNoDataText: '暂无数据',
    showLoadingText: '加载中...'
};

// Store table instances
const tableInstances = {};

/**
 * Initialize virtual scroll table
 * @param {string} tableId - The ID of the table element
 * @param {string|Array} dataSource - URL to fetch JSON data or array of data
 * @param {Object} options - Additional options
 */
async function initVirtualTable(tableId, dataSource, options = {}) {
    const container = document.getElementById(`${tableId}-container`);
    if (!container) {
        console.error(`Table container ${tableId}-container not found`);
        return;
    }

    // Show loading state
    showTableLoading(tableId, true);

    try {
        // Load data
        let data = [];
        if (typeof dataSource === 'string') {
            const response = await fetch(dataSource);
            data = await response.json();
        } else if (Array.isArray(dataSource)) {
            data = dataSource;
        }

        // Update count
        const countElem = document.getElementById(`${tableId}-count`);
        if (countElem) {
            countElem.textContent = data.length.toLocaleString();
        }

        // Decide whether to use virtual scroll
        if (data.length > TABLE_CONFIG.virtualScrollThreshold) {
            initClusterize(tableId, data, options);
        } else {
            renderRegularTable(tableId, data, options);
        }

    } catch (error) {
        console.error('Failed to initialize table:', error);
        showTableError(tableId, '数据加载失败');
    } finally {
        showTableLoading(tableId, false);
    }
}

/**
 * Initialize Clusterize.js for virtual scrolling
 */
function initClusterize(tableId, data, options) {
    const scrollElem = document.getElementById(`${tableId}-scroll`);
    const contentElem = document.getElementById(`${tableId}-content`);
    
    if (!scrollElem || !contentElem) {
        console.error('Clusterize elements not found');
        return;
    }

    // Generate rows HTML
    const rows = data.map(item => generateRowHtml(item, options.columns || []));

    // Initialize Clusterize
    const clusterize = new Clusterize({
        rows: rows,
        scrollId: `${tableId}-scroll`,
        contentId: `${tableId}-content`,
        rows_in_block: TABLE_CONFIG.blocksInCluster,
        blocks_in_cluster: 4,
        show_no_data_row: true,
        no_data_text: TABLE_CONFIG.showNoDataText,
        callbacks: {
            clusterChanged: function() {
                // Apply any row event handlers
                attachRowEventHandlers(tableId);
            }
        }
    });

    // Store instance for later use
    tableInstances[tableId] = {
        type: 'virtual',
        instance: clusterize,
        data: data
    };
}

/**
 * Generate HTML for a single row
 */
function generateRowHtml(rowData, columns) {
    const cells = columns.map(col => {
        const value = rowData[col.key] || '';
        const displayValue = col.render ? col.render(value, rowData) : formatCellValue(value, col.type);
        return `<td>${displayValue}</td>`;
    }).join('');
    
    return `<tr data-id="${rowData.id || ''}">${cells}</tr>`;
}

/**
 * Format cell value based on type
 */
function formatCellValue(value, type) {
    if (value === null || value === undefined) return '';
    
    switch (type) {
        case 'date':
            return formatDate(value);
        case 'currency':
            return formatCurrency(value);
        case 'number':
            return Number(value).toLocaleString();
        case 'status':
            return formatStatus(value);
        default:
            return escapeHtml(String(value));
    }
}

/**
 * Render regular table without virtual scrolling
 */
function renderRegularTable(tableId, data, options) {
    const tableBody = document.querySelector(`#${tableId} tbody`);
    if (!tableBody) return;

    // Clear existing rows
    tableBody.innerHTML = '';

    // Render rows
    data.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = generateRowHtml(item, options.columns || []);
        tableBody.appendChild(tr.firstElementChild);
    });

    // Store instance
    tableInstances[tableId] = {
        type: 'regular',
        data: data
    };

    // Attach event handlers
    attachRowEventHandlers(tableId);
}

/**
 * Attach event handlers to table rows
 */
function attachRowEventHandlers(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    // Row click handler
    table.addEventListener('click', function(e) {
        const row = e.target.closest('tr');
        if (row && row.dataset.id) {
            const event = new CustomEvent('rowClick', {
                detail: { id: row.dataset.id, row: row }
            });
            table.dispatchEvent(event);
        }
    });
}

/**
 * Export table data to CSV
 */
function exportTableData(tableId) {
    const instance = tableInstances[tableId];
    if (!instance || !instance.data) {
        alert('没有可导出的数据');
        return;
    }

    const data = instance.data;
    if (data.length === 0) {
        alert('没有可导出的数据');
        return;
    }

    // Get headers
    const headers = Object.keys(data[0]);
    
    // Convert to CSV
    const csv = [
        headers.join(','),
        ...data.map(row => 
            headers.map(header => {
                const value = row[header];
                // Escape quotes and wrap in quotes if contains comma
                const escaped = String(value || '').replace(/"/g, '""');
                return escaped.includes(',') ? `"${escaped}"` : escaped;
            }).join(',')
        )
    ].join('\n');

    // Download
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${tableId}_export_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Server-side pagination navigation
 */
function goToPage(page) {
    const url = new URL(window.location);
    url.searchParams.set('page', page);
    window.location.href = url.toString();
}

/**
 * Utility functions
 */
function showTableLoading(tableId, show) {
    const wrapper = document.getElementById(`${tableId}-wrapper`);
    if (!wrapper) return;

    if (show) {
        const loadingHtml = `
            <div class="table-loading">
                <i class="fas fa-spinner fa-spin"></i>
                <span>${TABLE_CONFIG.showLoadingText}</span>
            </div>
        `;
        wrapper.insertAdjacentHTML('beforeend', loadingHtml);
    } else {
        const loading = wrapper.querySelector('.table-loading');
        if (loading) loading.remove();
    }
}

function showTableError(tableId, message) {
    const wrapper = document.getElementById(`${tableId}-wrapper`);
    if (!wrapper) return;

    wrapper.innerHTML = `
        <div class="table-error" style="padding: var(--space-2xl); text-align: center; color: var(--color-danger);">
            <i class="fas fa-exclamation-triangle"></i>
            <span>${message}</span>
        </div>
    `;
}

function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-CN');
    } catch (e) {
        return dateString;
    }
}

function formatCurrency(value) {
    return '¥' + Number(value).toLocaleString('zh-CN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function formatStatus(status) {
    const statusMap = {
        'active': '<span class="badge badge-success">活跃</span>',
        'pending': '<span class="badge badge-warning">待处理</span>',
        'completed': '<span class="badge badge-info">已完成</span>',
        'cancelled': '<span class="badge badge-danger">已取消</span>'
    };
    return statusMap[status] || status;
}

function escapeHtml(text) {
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
 * Generate mock data for testing
 */
function generateMockData(count = 5000) {
    const statuses = ['active', 'pending', 'completed', 'cancelled'];
    const sources = ['taobao', 'wechat', 'douyin', 'xiaohongshu'];
    const names = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十'];
    
    const data = [];
    for (let i = 1; i <= count; i++) {
        data.push({
            id: i,
            name: names[Math.floor(Math.random() * names.length)] + i,
            phone: `138${String(Math.floor(Math.random() * 100000000)).padStart(8, '0')}`,
            email: `user${i}@example.com`,
            status: statuses[Math.floor(Math.random() * statuses.length)],
            source: sources[Math.floor(Math.random() * sources.length)],
            revenue: Math.floor(Math.random() * 50000) + 1000,
            created_at: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString()
        });
    }
    return data;
}

// Export functions for global use
window.initVirtualTable = initVirtualTable;
window.exportTableData = exportTableData;
window.goToPage = goToPage;
window.generateMockData = generateMockData;