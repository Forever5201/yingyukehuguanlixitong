/**
 * Charts.js - 统一的 Chart.js 配置和管理
 * 
 * 功能：
 * - 提供默认配置选项
 * - 统一的图表初始化函数
 * - CSV 导出功能
 * - 时区支持
 */

(function(window) {
    'use strict';

    // 获取 CSS 变量值
    const getCSSVariable = (variable) => {
        return getComputedStyle(document.documentElement).getPropertyValue(variable).trim();
    };

    // 默认颜色方案
    const CHART_COLORS = {
        primary: getCSSVariable('--color-primary') || '#0056B3',
        success: getCSSVariable('--color-success') || '#155724',
        warning: getCSSVariable('--color-warning') || '#856404',
        danger: getCSSVariable('--color-danger') || '#721C24',
        info: '#17A2B8',
        secondary: getCSSVariable('--color-muted') || '#6C757D',
        // 扩展颜色系列
        series: [
            '#0056B3', // Primary
            '#155724', // Success
            '#856404', // Warning
            '#721C24', // Danger
            '#17A2B8', // Info
            '#6C757D', // Secondary
            '#6F42C1', // Purple
            '#E83E8C', // Pink
            '#FD7E14', // Orange
            '#20C997'  // Teal
        ]
    };

    // 默认字体配置
    const FONT_CONFIG = {
        family: getCSSVariable('--font-family-base') || '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        size: {
            small: 11,
            medium: 13,
            large: 15
        }
    };

    // 时区配置
    const TIMEZONE_CONFIG = {
        default: 'Asia/Shanghai',
        format: 'YYYY-MM-DD HH:mm:ss'
    };

    /**
     * 默认图表配置
     */
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false
        },
        plugins: {
            title: {
                display: false,
                font: {
                    size: FONT_CONFIG.size.large,
                    family: FONT_CONFIG.family,
                    weight: 600
                }
            },
            legend: {
                display: true,
                position: 'bottom',
                labels: {
                    padding: 15,
                    font: {
                        size: FONT_CONFIG.size.medium,
                        family: FONT_CONFIG.family
                    },
                    usePointStyle: true,
                    boxWidth: 8
                }
            },
            tooltip: {
                enabled: true,
                backgroundColor: 'rgba(0, 0, 0, 0.9)',
                titleColor: '#fff',
                bodyColor: '#fff',
                borderColor: '#333',
                borderWidth: 1,
                padding: 12,
                cornerRadius: 6,
                displayColors: true,
                titleFont: {
                    size: FONT_CONFIG.size.medium,
                    family: FONT_CONFIG.family,
                    weight: 600
                },
                bodyFont: {
                    size: FONT_CONFIG.size.small,
                    family: FONT_CONFIG.family
                },
                callbacks: {
                    title: function(tooltipItems) {
                        // 格式化时间戳
                        if (tooltipItems.length > 0) {
                            const item = tooltipItems[0];
                            const label = item.label;
                            
                            // 检查是否为时间戳
                            if (isValidDate(label)) {
                                return formatTimestamp(label, TIMEZONE_CONFIG.default);
                            }
                            return label;
                        }
                        return '';
                    },
                    label: function(context) {
                        let label = context.dataset.label || '';
                        
                        if (label) {
                            label += ': ';
                        }
                        
                        // 获取值
                        const value = context.parsed.y !== undefined ? context.parsed.y : context.parsed;
                        
                        // 根据数据集类型格式化值
                        if (context.dataset.isCurrency || context.chart.options.scales?.y?.isCurrency) {
                            label += formatCurrency(value);
                        } else if (context.dataset.isPercentage) {
                            label += formatPercentage(value);
                        } else {
                            label += formatNumber(value);
                        }
                        
                        // 添加额外信息
                        if (context.dataset.additionalData && context.dataset.additionalData[context.dataIndex]) {
                            const additional = context.dataset.additionalData[context.dataIndex];
                            Object.keys(additional).forEach(key => {
                                label += `\n${key}: ${additional[key]}`;
                            });
                        }
                        
                        return label;
                    },
                    footer: function(tooltipItems) {
                        // 可以添加汇总信息
                        let sum = 0;
                        tooltipItems.forEach(function(tooltipItem) {
                            sum += tooltipItem.parsed.y || tooltipItem.parsed || 0;
                        });
                        
                        if (tooltipItems.length > 1) {
                            return '总计: ' + formatNumber(sum);
                        }
                        return '';
                    }
                }
            }
        },
        animation: {
            duration: 750,
            easing: 'easeInOutQuart'
        }
    };

    /**
     * 初始化趋势图（折线图/面积图）
     * @param {string} canvasId - Canvas 元素 ID
     * @param {object} data - 图表数据
     * @param {object} customOptions - 自定义配置
     * @param {string} timezone - 时区（可选）
     * @returns {Chart} Chart 实例
     */
    function initTrendChart(canvasId, data, customOptions = {}, timezone = TIMEZONE_CONFIG.default) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            console.error(`Canvas element ${canvasId} not found`);
            return null;
        }

        // 处理数据集
        data.datasets = data.datasets.map((dataset, index) => ({
            ...dataset,
            borderColor: dataset.borderColor || CHART_COLORS.series[index % CHART_COLORS.series.length],
            backgroundColor: dataset.backgroundColor || 
                (dataset.fill ? hexToRgba(CHART_COLORS.series[index % CHART_COLORS.series.length], 0.1) : 'transparent'),
            borderWidth: dataset.borderWidth || 2,
            tension: dataset.tension !== undefined ? dataset.tension : 0.1,
            pointRadius: dataset.pointRadius || 3,
            pointHoverRadius: dataset.pointHoverRadius || 5,
            pointBackgroundColor: dataset.pointBackgroundColor || '#fff',
            pointBorderWidth: dataset.pointBorderWidth || 2
        }));

        // 合并配置
        const config = {
            type: customOptions.type || 'line',
            data: data,
            options: deepMerge(defaultOptions, {
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            font: {
                                size: FONT_CONFIG.size.small,
                                family: FONT_CONFIG.family
                            },
                            callback: function(value, index) {
                                // 如果是时间轴，格式化显示
                                const label = this.getLabelForValue(value);
                                if (isValidDate(label)) {
                                    const date = new Date(label);
                                    return formatDateShort(date);
                                }
                                return label;
                            }
                        }
                    },
                    y: {
                        display: true,
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            font: {
                                size: FONT_CONFIG.size.small,
                                family: FONT_CONFIG.family
                            },
                            callback: function(value) {
                                if (this.chart.options.scales.y.isCurrency) {
                                    return formatCurrency(value);
                                } else if (this.chart.options.scales.y.isPercentage) {
                                    return formatPercentage(value);
                                }
                                return formatNumber(value);
                            }
                        }
                    }
                },
                ...customOptions
            })
        };

        // 存储时区信息
        config.options.timezone = timezone;

        return new Chart(ctx, config);
    }

    /**
     * 初始化饼图/圆环图
     * @param {string} canvasId - Canvas 元素 ID
     * @param {object} data - 图表数据
     * @param {object} customOptions - 自定义配置
     * @returns {Chart} Chart 实例
     */
    function initPieChart(canvasId, data, customOptions = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            console.error(`Canvas element ${canvasId} not found`);
            return null;
        }

        // 处理数据集
        data.datasets = data.datasets.map(dataset => ({
            ...dataset,
            backgroundColor: dataset.backgroundColor || CHART_COLORS.series,
            borderColor: dataset.borderColor || '#fff',
            borderWidth: dataset.borderWidth || 2,
            hoverOffset: dataset.hoverOffset || 4
        }));

        // 合并配置
        const config = {
            type: customOptions.type || 'doughnut',
            data: data,
            options: deepMerge(defaultOptions, {
                scales: {}, // 饼图不需要坐标轴
                plugins: {
                    ...defaultOptions.plugins,
                    tooltip: {
                        ...defaultOptions.plugins.tooltip,
                        callbacks: {
                            title: function() {
                                return ''; // 饼图不需要标题
                            },
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const dataset = context.dataset;
                                const total = dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                
                                let result = label + ': ';
                                
                                if (dataset.isCurrency) {
                                    result += formatCurrency(value);
                                } else {
                                    result += formatNumber(value);
                                }
                                
                                result += ` (${percentage}%)`;
                                
                                return result;
                            }
                        }
                    }
                },
                ...customOptions
            })
        };

        return new Chart(ctx, config);
    }

    /**
     * 初始化柱状图
     * @param {string} canvasId - Canvas 元素 ID
     * @param {object} data - 图表数据
     * @param {object} customOptions - 自定义配置
     * @returns {Chart} Chart 实例
     */
    function initBarChart(canvasId, data, customOptions = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            console.error(`Canvas element ${canvasId} not found`);
            return null;
        }

        // 处理数据集
        data.datasets = data.datasets.map((dataset, index) => ({
            ...dataset,
            backgroundColor: dataset.backgroundColor || 
                CHART_COLORS.series[index % CHART_COLORS.series.length],
            borderColor: dataset.borderColor || 
                CHART_COLORS.series[index % CHART_COLORS.series.length],
            borderWidth: dataset.borderWidth || 1,
            borderRadius: dataset.borderRadius || 4,
            borderSkipped: dataset.borderSkipped || 'bottom'
        }));

        // 合并配置
        const config = {
            type: 'bar',
            data: data,
            options: deepMerge(defaultOptions, customOptions)
        };

        return new Chart(ctx, config);
    }

    /**
     * 导出图表数据为 CSV
     * @param {Chart} chartInstance - Chart.js 实例
     * @param {string} filename - 文件名（不含扩展名）
     * @param {object} options - 导出选项
     */
    function exportChartDataAsCSV(chartInstance, filename = 'chart_data', options = {}) {
        if (!chartInstance || !chartInstance.data) {
            console.error('Invalid chart instance');
            return;
        }

        const { 
            includeTimestamp = true,
            dateFormat = 'YYYY-MM-DD HH:mm:ss',
            timezone = TIMEZONE_CONFIG.default
        } = options;

        const data = chartInstance.data;
        const datasets = data.datasets || [];
        const labels = data.labels || [];

        if (labels.length === 0 || datasets.length === 0) {
            alert('没有可导出的数据');
            return;
        }

        // 构建 CSV 表头
        const headers = ['序号'];
        
        // 添加标签列（通常是时间或类别）
        headers.push('标签');
        
        // 添加每个数据集的列
        datasets.forEach(dataset => {
            headers.push(dataset.label || `数据集${datasets.indexOf(dataset) + 1}`);
        });

        // 如果需要时间戳
        if (includeTimestamp) {
            headers.push('导出时间');
        }

        // 构建数据行
        const rows = [];
        labels.forEach((label, index) => {
            const row = [index + 1]; // 序号
            
            // 格式化标签（如果是日期）
            if (isValidDate(label)) {
                row.push(formatTimestamp(label, timezone, dateFormat));
            } else {
                row.push(label);
            }
            
            // 添加每个数据集的值
            datasets.forEach(dataset => {
                const value = dataset.data[index];
                if (typeof value === 'object' && value !== null) {
                    // 处理对象类型的数据点（如 {x, y}）
                    row.push(value.y !== undefined ? value.y : value.x || 0);
                } else {
                    row.push(value || 0);
                }
            });
            
            // 添加导出时间戳
            if (includeTimestamp) {
                row.push(formatTimestamp(new Date(), timezone, dateFormat));
            }
            
            rows.push(row);
        });

        // 添加汇总行（可选）
        if (options.includeSummary) {
            const summaryRow = ['汇总', ''];
            datasets.forEach(dataset => {
                const sum = dataset.data.reduce((acc, val) => {
                    const v = typeof val === 'object' ? (val.y || val.x || 0) : val;
                    return acc + (parseFloat(v) || 0);
                }, 0);
                summaryRow.push(sum);
            });
            if (includeTimestamp) {
                summaryRow.push('');
            }
            rows.push(summaryRow);
        }

        // 转换为 CSV 格式
        const csvContent = [
            headers.join(','),
            ...rows.map(row => row.map(cell => {
                // 处理包含逗号或引号的单元格
                const cellStr = String(cell);
                if (cellStr.includes(',') || cellStr.includes('"') || cellStr.includes('\n')) {
                    return `"${cellStr.replace(/"/g, '""')}"`;
                }
                return cellStr;
            }).join(','))
        ].join('\n');

        // 添加 BOM 以支持 Excel 正确显示中文
        const BOM = '\uFEFF';
        const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' });
        
        // 创建下载链接
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${filename}_${formatDateForFilename(new Date())}.csv`;
        
        // 触发下载
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // 清理
        setTimeout(() => URL.revokeObjectURL(url), 100);
    }

    /**
     * 更新图表数据
     * @param {Chart} chartInstance - Chart.js 实例
     * @param {object} newData - 新数据
     * @param {boolean} animate - 是否动画
     */
    function updateChartData(chartInstance, newData, animate = true) {
        if (!chartInstance) return;

        // 更新数据
        chartInstance.data = newData;
        
        // 更新图表
        chartInstance.update(animate ? 'default' : 'none');
    }

    /**
     * 销毁图表实例
     * @param {Chart} chartInstance - Chart.js 实例
     */
    function destroyChart(chartInstance) {
        if (chartInstance) {
            chartInstance.destroy();
        }
    }

    /**
     * 设置默认时区
     * @param {string} timezone - 时区
     */
    function setDefaultTimezone(timezone) {
        TIMEZONE_CONFIG.default = timezone;
    }

    /**
     * 工具函数
     */
    
    // 检查是否为有效日期
    function isValidDate(dateString) {
        if (!dateString) return false;
        const date = new Date(dateString);
        return date instanceof Date && !isNaN(date);
    }

    // 格式化时间戳
    function formatTimestamp(date, timezone, format = TIMEZONE_CONFIG.format) {
        if (typeof date === 'string') {
            date = new Date(date);
        }
        
        // 简单的时区处理（实际项目中可能需要使用 moment.js 或 date-fns）
        const options = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false,
            timeZone: timezone
        };
        
        return date.toLocaleString('zh-CN', options);
    }

    // 格式化短日期
    function formatDateShort(date) {
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        return `${month}-${day}`;
    }

    // 格式化文件名日期
    function formatDateForFilename(date) {
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        const hour = date.getHours().toString().padStart(2, '0');
        const minute = date.getMinutes().toString().padStart(2, '0');
        return `${year}${month}${day}_${hour}${minute}`;
    }

    // 格式化货币
    function formatCurrency(value) {
        return '¥' + parseFloat(value).toLocaleString('zh-CN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    // 格式化百分比
    function formatPercentage(value) {
        return value.toFixed(1) + '%';
    }

    // 格式化数字
    function formatNumber(value) {
        return parseFloat(value).toLocaleString('zh-CN');
    }

    // 十六进制颜色转 RGBA
    function hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    // 深度合并对象
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

    // 检查是否为对象
    function isObject(item) {
        return item && typeof item === 'object' && !Array.isArray(item);
    }

    // 暴露 API
    window.ChartManager = {
        // 配置
        defaultOptions,
        colors: CHART_COLORS,
        
        // 初始化函数
        initTrendChart,
        initPieChart,
        initBarChart,
        
        // 工具函数
        exportChartDataAsCSV,
        updateChartData,
        destroyChart,
        setDefaultTimezone,
        
        // 格式化函数（供外部使用）
        formatters: {
            currency: formatCurrency,
            percentage: formatPercentage,
            number: formatNumber,
            timestamp: formatTimestamp
        }
    };

    // 兼容旧版本调用
    window.initTrendChart = initTrendChart;
    window.initPieChart = initPieChart;
    window.initBarChart = initBarChart;
    window.exportChartDataAsCSV = exportChartDataAsCSV;

})(window);