/**
 * Unified Chart.js Configuration and Utilities
 * Provides consistent styling and functionality for all charts
 */

// Import token colors from CSS
const getTokenColor = (token) => {
    const style = getComputedStyle(document.documentElement);
    return style.getPropertyValue(token).trim();
};

// Chart color palette using design tokens
const CHART_COLORS = {
    primary: getTokenColor('--color-primary') || '#0056B3',
    success: getTokenColor('--color-success') || '#155724',
    warning: getTokenColor('--color-warning') || '#856404',
    danger: getTokenColor('--color-danger') || '#721C24',
    muted: getTokenColor('--color-muted') || '#6C757D',
    series: [
        '#0056B3', // Primary
        '#155724', // Success
        '#856404', // Warning
        '#721C24', // Danger
        '#6C757D', // Muted
        '#17A2B8', // Info
        '#6F42C1', // Purple
        '#E83E8C'  // Pink
    ]
};

// Default chart options
const DEFAULT_OPTIONS = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                padding: 15,
                font: {
                    size: 12,
                    family: getTokenColor('--font-family-base') || 'sans-serif'
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            padding: 12,
            cornerRadius: 6,
            titleFont: {
                size: 14,
                weight: 600
            },
            bodyFont: {
                size: 13
            },
            callbacks: {
                label: function(context) {
                    let label = context.dataset.label || '';
                    if (label) {
                        label += ': ';
                    }
                    
                    // Format value based on dataset type
                    const value = context.parsed.y !== undefined ? context.parsed.y : context.parsed;
                    if (context.dataset.isCurrency) {
                        label += formatCurrency(value);
                    } else if (context.dataset.isPercentage) {
                        label += value.toFixed(1) + '%';
                    } else {
                        label += value.toLocaleString();
                    }
                    
                    return label;
                }
            }
        }
    },
    scales: {
        x: {
            grid: {
                display: false
            },
            ticks: {
                font: {
                    size: 11
                }
            }
        },
        y: {
            beginAtZero: true,
            grid: {
                color: 'rgba(0, 0, 0, 0.05)'
            },
            ticks: {
                font: {
                    size: 11
                }
            }
        }
    }
};

/**
 * Initialize a trend chart (line/area chart)
 * @param {string} canvasId - The ID of the canvas element
 * @param {Object} data - Chart data
 * @param {Object} options - Additional chart options
 * @returns {Chart} Chart instance
 */
function initTrendChart(canvasId, data, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas element ${canvasId} not found`);
        return null;
    }

    const ctx = canvas.getContext('2d');
    
    // Merge default options with custom options
    const chartOptions = deepMerge(DEFAULT_OPTIONS, {
        plugins: {
            ...DEFAULT_OPTIONS.plugins,
            tooltip: {
                ...DEFAULT_OPTIONS.plugins.tooltip,
                callbacks: {
                    ...DEFAULT_OPTIONS.plugins.tooltip.callbacks,
                    title: function(tooltipItems) {
                        // Format date for tooltip title
                        const date = tooltipItems[0].label;
                        return formatDate(date);
                    },
                    afterLabel: function(context) {
                        // Add additional info if available
                        const dataPoint = context.dataset.data[context.dataIndex];
                        if (dataPoint.metadata) {
                            const lines = [];
                            if (dataPoint.metadata.count) {
                                lines.push(`数量: ${dataPoint.metadata.count}`);
                            }
                            if (dataPoint.metadata.average) {
                                lines.push(`平均: ${formatCurrency(dataPoint.metadata.average)}`);
                            }
                            return lines;
                        }
                        return null;
                    }
                }
            }
        },
        scales: {
            ...DEFAULT_OPTIONS.scales,
            x: {
                ...DEFAULT_OPTIONS.scales.x,
                type: 'time',
                time: {
                    unit: 'day',
                    displayFormats: {
                        day: 'MM-dd',
                        week: 'MM-dd',
                        month: 'yyyy-MM'
                    }
                }
            },
            y: {
                ...DEFAULT_OPTIONS.scales.y,
                ticks: {
                    ...DEFAULT_OPTIONS.scales.y.ticks,
                    callback: function(value) {
                        // Format y-axis labels
                        if (this.chart.data.datasets[0].isCurrency) {
                            return formatCurrency(value);
                        }
                        return value.toLocaleString();
                    }
                }
            }
        }
    }, options);

    // Process data - ensure datasets have colors
    data.datasets = data.datasets.map((dataset, index) => ({
        ...dataset,
        borderColor: dataset.borderColor || CHART_COLORS.series[index % CHART_COLORS.series.length],
        backgroundColor: dataset.backgroundColor || (dataset.fill ? 
            hexToRgba(CHART_COLORS.series[index % CHART_COLORS.series.length], 0.1) : 
            'transparent'),
        tension: dataset.tension !== undefined ? dataset.tension : 0.2,
        borderWidth: dataset.borderWidth || 2,
        pointRadius: dataset.pointRadius || 3,
        pointHoverRadius: dataset.pointHoverRadius || 5
    }));

    return new Chart(ctx, {
        type: 'line',
        data: data,
        options: chartOptions
    });
}

/**
 * Initialize a pie or doughnut chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {Object} data - Chart data
 * @param {Object} options - Additional chart options
 * @returns {Chart} Chart instance
 */
function initPieChart(canvasId, data, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas element ${canvasId} not found`);
        return null;
    }

    const ctx = canvas.getContext('2d');
    
    // Merge options
    const chartOptions = deepMerge(DEFAULT_OPTIONS, {
        scales: {}, // Remove scales for pie charts
        plugins: {
            ...DEFAULT_OPTIONS.plugins,
            tooltip: {
                ...DEFAULT_OPTIONS.plugins.tooltip,
                callbacks: {
                    label: function(context) {
                        const label = context.label || '';
                        const value = context.parsed;
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = ((value / total) * 100).toFixed(1);
                        
                        return `${label}: ${formatCurrency(value)} (${percentage}%)`;
                    }
                }
            }
        }
    }, options);

    // Assign colors to data
    data.datasets = data.datasets.map(dataset => ({
        ...dataset,
        backgroundColor: dataset.backgroundColor || CHART_COLORS.series,
        borderWidth: dataset.borderWidth || 2,
        borderColor: dataset.borderColor || '#fff'
    }));

    return new Chart(ctx, {
        type: options.type || 'doughnut',
        data: data,
        options: chartOptions
    });
}

/**
 * Initialize a bar chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {Object} data - Chart data
 * @param {Object} options - Additional chart options
 * @returns {Chart} Chart instance
 */
function initBarChart(canvasId, data, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas element ${canvasId} not found`);
        return null;
    }

    const ctx = canvas.getContext('2d');
    
    // Merge options
    const chartOptions = deepMerge(DEFAULT_OPTIONS, options);

    // Assign colors to datasets
    data.datasets = data.datasets.map((dataset, index) => ({
        ...dataset,
        backgroundColor: dataset.backgroundColor || CHART_COLORS.series[index % CHART_COLORS.series.length],
        borderColor: dataset.borderColor || CHART_COLORS.series[index % CHART_COLORS.series.length],
        borderWidth: dataset.borderWidth || 1
    }));

    return new Chart(ctx, {
        type: 'bar',
        data: data,
        options: chartOptions
    });
}

/**
 * Export chart data as CSV
 * @param {Chart} chartInstance - The Chart.js instance
 * @param {string} filename - The filename for the CSV export
 */
function exportChartDataAsCSV(chartInstance, filename = 'chart_data') {
    if (!chartInstance || !chartInstance.data) {
        console.error('Invalid chart instance');
        return;
    }

    const data = chartInstance.data;
    const labels = data.labels || [];
    const datasets = data.datasets || [];

    if (labels.length === 0 || datasets.length === 0) {
        alert('没有可导出的数据');
        return;
    }

    // Build CSV header
    const headers = ['时间/类别', ...datasets.map(d => d.label || 'Series ' + (datasets.indexOf(d) + 1))];
    
    // Build CSV rows
    const rows = labels.map((label, index) => {
        const row = [formatExportLabel(label)];
        datasets.forEach(dataset => {
            const value = dataset.data[index];
            if (typeof value === 'object' && value.y !== undefined) {
                row.push(value.y);
            } else {
                row.push(value || 0);
            }
        });
        return row;
    });

    // Convert to CSV string
    const csv = [
        headers.join(','),
        ...rows.map(row => row.join(','))
    ].join('\n');

    // Download CSV
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${filename}_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Update chart data dynamically
 * @param {Chart} chartInstance - The Chart.js instance
 * @param {Object} newData - New data to update the chart with
 */
function updateChartData(chartInstance, newData) {
    if (!chartInstance) return;

    chartInstance.data = newData;
    chartInstance.update();
}

/**
 * Destroy a chart instance
 * @param {Chart} chartInstance - The Chart.js instance to destroy
 */
function destroyChart(chartInstance) {
    if (chartInstance) {
        chartInstance.destroy();
    }
}

/**
 * Utility functions
 */
function formatCurrency(value) {
    return '¥' + Number(value).toLocaleString('zh-CN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    } catch (e) {
        return dateString;
    }
}

function formatExportLabel(label) {
    if (label instanceof Date) {
        return label.toISOString().split('T')[0];
    }
    return String(label);
}

function hexToRgba(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function deepMerge(target, source) {
    const output = Object.assign({}, target);
    if (isObject(target) && isObject(source)) {
        Object.keys(source).forEach(key => {
            if (isObject(source[key])) {
                if (!(key in target))
                    Object.assign(output, { [key]: source[key] });
                else
                    output[key] = deepMerge(target[key], source[key]);
            } else {
                Object.assign(output, { [key]: source[key] });
            }
        });
    }
    return output;
}

function isObject(item) {
    return item && typeof item === 'object' && !Array.isArray(item);
}

// Export functions for global use
window.initTrendChart = initTrendChart;
window.initPieChart = initPieChart;
window.initBarChart = initBarChart;
window.exportChartDataAsCSV = exportChartDataAsCSV;
window.updateChartData = updateChartData;
window.destroyChart = destroyChart;